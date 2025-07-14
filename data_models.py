"""
Enhanced data models for Agent Delegation Protocol.
Provides comprehensive data structures with validation, serialization, and lifecycle management.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import json
import uuid
import jwt
from enum import Enum
from config import config


class AgentStatus(Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class DelegationStatus(Enum):
    """Delegation status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"


class TokenType(Enum):
    """Token type enumeration."""
    DELEGATION = "delegation"
    ACCESS = "access"


@dataclass
class Agent:
    """Enhanced Agent data model with validation and lifecycle management."""
    id: str
    name: str
    description: str = ""
    scopes: List[str] = field(default_factory=list)
    status: str = AgentStatus.ACTIVE.value
    created_at: str = ""
    last_used: Optional[str] = None
    delegation_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        
        # Validate status
        if self.status not in [s.value for s in AgentStatus]:
            raise ValueError(f"Invalid agent status: {self.status}")
        
        # Validate required fields
        if not self.id or not self.name:
            raise ValueError("Agent ID and name are required")
        
        # Ensure scopes is a list
        if not isinstance(self.scopes, list):
            self.scopes = []
    
    def update_last_used(self):
        """Update the last used timestamp."""
        self.last_used = datetime.utcnow().isoformat()
    
    def increment_delegation_count(self):
        """Increment the delegation count."""
        self.delegation_count += 1
        self.update_last_used()
    
    def is_active(self) -> bool:
        """Check if agent is active."""
        return self.status == AgentStatus.ACTIVE.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create Agent from dictionary."""
        return cls(**data)


@dataclass
class Delegation:
    """Enhanced Delegation data model with token lifecycle management."""
    id: str
    agent_id: str
    agent_name: str
    user_id: str
    scopes: List[str]
    status: str = DelegationStatus.PENDING.value
    created_at: str = ""
    approved_at: Optional[str] = None
    expires_at: str = ""
    delegation_token: Optional[str] = None
    access_token: Optional[str] = None
    revoked_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation and setup."""
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        
        if not self.expires_at:
            self.expires_at = (
                datetime.utcnow() + timedelta(minutes=config.delegation_token_expiry)
            ).isoformat()
        
        # Validate status
        if self.status not in [s.value for s in DelegationStatus]:
            raise ValueError(f"Invalid delegation status: {self.status}")
        
        # Validate required fields
        if not all([self.id, self.agent_id, self.user_id]):
            raise ValueError("Delegation ID, agent ID, and user ID are required")
        
        # Ensure scopes is a list
        if not isinstance(self.scopes, list):
            self.scopes = []
    
    def approve(self) -> str:
        """Approve the delegation and generate delegation token."""
        if self.status != DelegationStatus.PENDING.value:
            raise ValueError("Only pending delegations can be approved")
        
        self.status = DelegationStatus.APPROVED.value
        self.approved_at = datetime.utcnow().isoformat()
        
        # Generate delegation token
        delegation_claims = {
            "iss": config.auth_server_url,
            "sub": self.agent_id,
            "delegator": self.user_id,
            "scope": self.scopes,
            "exp": datetime.utcnow() + timedelta(minutes=config.delegation_token_expiry),
            "iat": datetime.utcnow(),
            "delegation_id": self.id,
            "jti": f"del-{uuid.uuid4().hex[:8]}"
        }
        
        self.delegation_token = jwt.encode(
            delegation_claims, 
            config.jwt_secret, 
            algorithm=config.jwt_algorithm
        )
        
        return self.delegation_token
    
    def deny(self):
        """Deny the delegation."""
        if self.status != DelegationStatus.PENDING.value:
            raise ValueError("Only pending delegations can be denied")
        
        self.status = DelegationStatus.DENIED.value
    
    def revoke(self):
        """Revoke the delegation."""
        if self.status not in [DelegationStatus.APPROVED.value, DelegationStatus.PENDING.value]:
            raise ValueError("Only approved or pending delegations can be revoked")
        
        self.status = DelegationStatus.REVOKED.value
        self.revoked_at = datetime.utcnow().isoformat()
    
    def is_expired(self) -> bool:
        """Check if delegation has expired."""
        if not self.expires_at:
            return False
        
        expiry_time = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        return datetime.utcnow() > expiry_time
    
    def is_active(self) -> bool:
        """Check if delegation is active (approved and not expired)."""
        return (
            self.status == DelegationStatus.APPROVED.value and 
            not self.is_expired()
        )
    
    def generate_access_token(self) -> str:
        """Generate access token from approved delegation."""
        if not self.is_active():
            raise ValueError("Cannot generate access token for inactive delegation")
        
        access_claims = {
            "iss": config.auth_server_url,
            "sub": self.user_id,
            "actor": self.agent_id,
            "scope": self.scopes,
            "exp": datetime.utcnow() + timedelta(minutes=config.access_token_expiry),
            "iat": datetime.utcnow(),
            "delegation_id": self.id,
            "jti": f"acc-{uuid.uuid4().hex[:8]}"
        }
        
        self.access_token = jwt.encode(
            access_claims,
            config.jwt_secret,
            algorithm=config.jwt_algorithm
        )
        
        return self.access_token
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Delegation':
        """Create Delegation from dictionary."""
        return cls(**data)


@dataclass
class TokenInfo:
    """Token information and analysis."""
    token: str
    token_type: str
    claims: Dict[str, Any]
    is_valid: bool
    is_expired: bool
    is_revoked: bool
    expires_at: str
    issued_at: str
    time_to_expiry_seconds: int
    subject: str
    scopes: List[str] = field(default_factory=list)
    
    @classmethod
    def from_token(cls, token: str, revoked_tokens: set) -> 'TokenInfo':
        """Create TokenInfo from JWT token."""
        try:
            # Decode without verification first to get claims
            unverified_claims = jwt.decode(token, options={"verify_signature": False})
            
            # Then verify signature
            verified_claims = jwt.decode(
                token, 
                config.jwt_secret, 
                algorithms=[config.jwt_algorithm]
            )
            
            # Determine token type
            token_type = TokenType.ACCESS.value if "actor" in verified_claims else TokenType.DELEGATION.value
            
            # Check expiration
            exp_timestamp = verified_claims.get('exp', 0)
            exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
            is_expired = exp_datetime <= datetime.utcnow()
            
            # Check revocation
            is_revoked = token in revoked_tokens
            
            # Calculate validity
            is_valid = not is_expired and not is_revoked
            
            # Calculate time to expiry
            time_to_expiry = max(0, int((exp_datetime - datetime.utcnow()).total_seconds()))
            
            return cls(
                token=token,
                token_type=token_type,
                claims=verified_claims,
                is_valid=is_valid,
                is_expired=is_expired,
                is_revoked=is_revoked,
                expires_at=exp_datetime.isoformat(),
                issued_at=datetime.utcfromtimestamp(verified_claims.get('iat', 0)).isoformat(),
                time_to_expiry_seconds=time_to_expiry,
                subject=verified_claims.get('sub', ''),
                scopes=verified_claims.get('scope', [])
            )
            
        except jwt.ExpiredSignatureError:
            return cls(
                token=token,
                token_type="unknown",
                claims=unverified_claims,
                is_valid=False,
                is_expired=True,
                is_revoked=False,
                expires_at=datetime.utcfromtimestamp(unverified_claims.get('exp', 0)).isoformat(),
                issued_at=datetime.utcfromtimestamp(unverified_claims.get('iat', 0)).isoformat(),
                time_to_expiry_seconds=0,
                subject=unverified_claims.get('sub', ''),
                scopes=unverified_claims.get('scope', [])
            )
        except jwt.InvalidTokenError:
            return cls(
                token=token,
                token_type="invalid",
                claims={},
                is_valid=False,
                is_expired=False,
                is_revoked=False,
                expires_at="",
                issued_at="",
                time_to_expiry_seconds=0,
                subject="",
                scopes=[]
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SystemActivity:
    """System activity log entry."""
    id: str
    timestamp: str
    action: str
    details: Dict[str, Any]
    user: Optional[str] = None
    agent_id: Optional[str] = None
    delegation_id: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not self.id:
            self.id = f"activity-{uuid.uuid4().hex[:8]}"
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemActivity':
        """Create SystemActivity from dictionary."""
        return cls(**data)


@dataclass
class SystemStats:
    """System statistics."""
    total_agents: int = 0
    active_agents: int = 0
    inactive_agents: int = 0
    suspended_agents: int = 0
    total_delegations: int = 0
    pending_delegations: int = 0
    approved_delegations: int = 0
    denied_delegations: int = 0
    revoked_delegations: int = 0
    expired_delegations: int = 0
    active_tokens: int = 0
    revoked_tokens: int = 0
    total_users: int = 0
    timestamp: str = ""
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
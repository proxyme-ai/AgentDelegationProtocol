"""
Storage manager for Agent Delegation Protocol.
Provides comprehensive data persistence, retrieval, and lifecycle management.
"""

import json
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
import uuid
from pathlib import Path

from data_models import (
    Agent, Delegation, TokenInfo, SystemActivity, SystemStats,
    AgentStatus, DelegationStatus
)
from config import config
from logging_config import get_logger

logger = get_logger('storage_manager')


class StorageManager:
    """Comprehensive storage manager for all data persistence needs."""
    
    def __init__(self):
        """Initialize storage manager."""
        self._lock = threading.RLock()
        self._agents: Dict[str, Agent] = {}
        self._users: Dict[str, str] = {}
        self._delegations: Dict[str, Delegation] = {}
        self._active_tokens: List[str] = []
        self._revoked_tokens: set = set()
        self._system_activities: List[SystemActivity] = []
        
        # File paths
        self.agents_file = Path(config.agents_file)
        self.users_file = Path(config.users_file)
        self.delegations_file = Path("delegations.json")
        self.tokens_file = Path("tokens.json")
        self.activities_file = Path("activities.json")
        
        # Load existing data
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all data from storage files."""
        with self._lock:
            self._load_agents()
            self._load_users()
            self._load_delegations()
            self._load_tokens()
            self._load_activities()
    
    def _load_agents(self):
        """Load agents from storage."""
        try:
            if self.agents_file.exists():
                with open(self.agents_file, 'r') as f:
                    data = json.load(f)
                    
                for agent_id, agent_data in data.items():
                    try:
                        # Handle both old and new format
                        if isinstance(agent_data, dict):
                            # Ensure all required fields exist
                            agent_data.setdefault('id', agent_id)
                            agent_data.setdefault('description', '')
                            agent_data.setdefault('scopes', [])
                            agent_data.setdefault('status', AgentStatus.ACTIVE.value)
                            agent_data.setdefault('created_at', datetime.utcnow().isoformat())
                            agent_data.setdefault('delegation_count', 0)
                            agent_data.setdefault('metadata', {})
                            
                            self._agents[agent_id] = Agent.from_dict(agent_data)
                        else:
                            # Old format - just name
                            self._agents[agent_id] = Agent(
                                id=agent_id,
                                name=str(agent_data),
                                description="",
                                scopes=[],
                                status=AgentStatus.ACTIVE.value
                            )
                    except Exception as e:
                        logger.error(f"Error loading agent {agent_id}: {e}")
                        continue
            else:
                # Create default agent
                default_agent = Agent(
                    id="agent-client-id",
                    name="CalendarAgent",
                    description="Default calendar agent for demonstration",
                    scopes=["read:calendar", "write:calendar"]
                )
                self._agents[default_agent.id] = default_agent
                self._save_agents()
                
        except Exception as e:
            logger.error(f"Error loading agents: {e}")
    
    def _load_users(self):
        """Load users from storage."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r') as f:
                    self._users = json.load(f)
            else:
                # Create default user
                self._users = {"alice": "password123"}
                self._save_users()
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            self._users = {"alice": "password123"}
    
    def _load_delegations(self):
        """Load delegations from storage."""
        try:
            if self.delegations_file.exists():
                with open(self.delegations_file, 'r') as f:
                    data = json.load(f)
                    
                for delegation_id, delegation_data in data.items():
                    try:
                        delegation_data.setdefault('id', delegation_id)
                        self._delegations[delegation_id] = Delegation.from_dict(delegation_data)
                    except Exception as e:
                        logger.error(f"Error loading delegation {delegation_id}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error loading delegations: {e}")
    
    def _load_tokens(self):
        """Load token data from storage."""
        try:
            if self.tokens_file.exists():
                with open(self.tokens_file, 'r') as f:
                    data = json.load(f)
                    self._active_tokens = data.get('active_tokens', [])
                    self._revoked_tokens = set(data.get('revoked_tokens', []))
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
    
    def _load_activities(self):
        """Load system activities from storage."""
        try:
            if self.activities_file.exists():
                with open(self.activities_file, 'r') as f:
                    data = json.load(f)
                    
                for activity_data in data:
                    try:
                        self._system_activities.append(SystemActivity.from_dict(activity_data))
                    except Exception as e:
                        logger.error(f"Error loading activity: {e}")
                        continue
                        
                # Keep only recent activities (last 1000)
                if len(self._system_activities) > 1000:
                    self._system_activities = self._system_activities[-1000:]
        except Exception as e:
            logger.error(f"Error loading activities: {e}")
    
    def _save_agents(self):
        """Save agents to storage."""
        try:
            data = {}
            for agent_id, agent in self._agents.items():
                data[agent_id] = agent.to_dict()
            
            with open(self.agents_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving agents: {e}")
    
    def _save_users(self):
        """Save users to storage."""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self._users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def _save_delegations(self):
        """Save delegations to storage."""
        try:
            data = {}
            for delegation_id, delegation in self._delegations.items():
                data[delegation_id] = delegation.to_dict()
            
            with open(self.delegations_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving delegations: {e}")
    
    def _save_tokens(self):
        """Save token data to storage."""
        try:
            data = {
                'active_tokens': self._active_tokens,
                'revoked_tokens': list(self._revoked_tokens)
            }
            
            with open(self.tokens_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
    
    def _save_activities(self):
        """Save system activities to storage."""
        try:
            data = [activity.to_dict() for activity in self._system_activities]
            
            with open(self.activities_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving activities: {e}")
    
    # ============================================================================
    # AGENT MANAGEMENT
    # ============================================================================
    
    def create_agent(self, agent_data: Dict[str, Any]) -> Agent:
        """Create a new agent."""
        with self._lock:
            agent_id = agent_data.get('id') or f"agent-{uuid.uuid4().hex[:8]}"
            
            if agent_id in self._agents:
                raise ValueError(f"Agent with ID {agent_id} already exists")
            
            agent_data['id'] = agent_id
            agent = Agent.from_dict(agent_data)
            
            self._agents[agent_id] = agent
            self._save_agents()
            
            self.log_activity(
                action="agent_created",
                details={"agent_id": agent_id, "name": agent.name},
                agent_id=agent_id
            )
            
            return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        with self._lock:
            return self._agents.get(agent_id)
    
    def list_agents(self, status_filter: Optional[str] = None, 
                   search: Optional[str] = None) -> List[Agent]:
        """List agents with optional filtering."""
        with self._lock:
            agents = list(self._agents.values())
            
            if status_filter:
                agents = [a for a in agents if a.status == status_filter]
            
            if search:
                search_lower = search.lower()
                agents = [
                    a for a in agents 
                    if search_lower in a.name.lower() or search_lower in a.description.lower()
                ]
            
            return sorted(agents, key=lambda x: x.created_at, reverse=True)
    
    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Agent:
        """Update agent."""
        with self._lock:
            if agent_id not in self._agents:
                raise ValueError(f"Agent {agent_id} not found")
            
            agent = self._agents[agent_id]
            
            # Update allowed fields
            for field, value in updates.items():
                if hasattr(agent, field) and field != 'id':
                    setattr(agent, field, value)
            
            self._save_agents()
            
            self.log_activity(
                action="agent_updated",
                details={"agent_id": agent_id, "updates": updates},
                agent_id=agent_id
            )
            
            return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete agent."""
        with self._lock:
            if agent_id not in self._agents:
                return False
            
            agent_name = self._agents[agent_id].name
            del self._agents[agent_id]
            self._save_agents()
            
            # Also revoke all delegations for this agent
            for delegation in self._delegations.values():
                if delegation.agent_id == agent_id and delegation.status == DelegationStatus.APPROVED.value:
                    delegation.revoke()
            self._save_delegations()
            
            self.log_activity(
                action="agent_deleted",
                details={"agent_id": agent_id, "name": agent_name},
                agent_id=agent_id
            )
            
            return True
    
    # ============================================================================
    # USER MANAGEMENT
    # ============================================================================
    
    def create_user(self, username: str, password: str) -> bool:
        """Create a new user."""
        with self._lock:
            if username in self._users:
                return False
            
            self._users[username] = password
            self._save_users()
            
            self.log_activity(
                action="user_created",
                details={"username": username},
                user=username
            )
            
            return True
    
    def get_user(self, username: str) -> Optional[str]:
        """Get user password."""
        with self._lock:
            return self._users.get(username)
    
    def list_users(self) -> List[str]:
        """List all usernames."""
        with self._lock:
            return list(self._users.keys())
    
    def validate_user(self, username: str, password: str) -> bool:
        """Validate user credentials."""
        with self._lock:
            return self._users.get(username) == password
    
    # ============================================================================
    # DELEGATION MANAGEMENT
    # ============================================================================
    
    def create_delegation(self, delegation_data: Dict[str, Any]) -> Delegation:
        """Create a new delegation."""
        with self._lock:
            delegation_id = f"delegation-{uuid.uuid4().hex[:8]}"
            delegation_data['id'] = delegation_id
            
            # Validate agent and user exist
            if delegation_data['agent_id'] not in self._agents:
                raise ValueError("Agent not found")
            
            if delegation_data['user_id'] not in self._users:
                raise ValueError("User not found")
            
            # Set agent name
            delegation_data['agent_name'] = self._agents[delegation_data['agent_id']].name
            
            delegation = Delegation.from_dict(delegation_data)
            self._delegations[delegation_id] = delegation
            self._save_delegations()
            
            self.log_activity(
                action="delegation_created",
                details={
                    "delegation_id": delegation_id,
                    "agent_id": delegation.agent_id,
                    "user_id": delegation.user_id,
                    "scopes": delegation.scopes
                },
                user=delegation.user_id,
                agent_id=delegation.agent_id,
                delegation_id=delegation_id
            )
            
            return delegation
    
    def get_delegation(self, delegation_id: str) -> Optional[Delegation]:
        """Get delegation by ID."""
        with self._lock:
            return self._delegations.get(delegation_id)
    
    def list_delegations(self, status_filter: Optional[str] = None,
                        agent_id_filter: Optional[str] = None,
                        user_id_filter: Optional[str] = None) -> List[Delegation]:
        """List delegations with optional filtering."""
        with self._lock:
            delegations = list(self._delegations.values())
            
            if status_filter:
                delegations = [d for d in delegations if d.status == status_filter]
            
            if agent_id_filter:
                delegations = [d for d in delegations if d.agent_id == agent_id_filter]
            
            if user_id_filter:
                delegations = [d for d in delegations if d.user_id == user_id_filter]
            
            return sorted(delegations, key=lambda x: x.created_at, reverse=True)
    
    def approve_delegation(self, delegation_id: str) -> str:
        """Approve a delegation and return delegation token."""
        with self._lock:
            if delegation_id not in self._delegations:
                raise ValueError("Delegation not found")
            
            delegation = self._delegations[delegation_id]
            delegation_token = delegation.approve()
            
            # Update agent delegation count
            if delegation.agent_id in self._agents:
                self._agents[delegation.agent_id].increment_delegation_count()
                self._save_agents()
            
            self._save_delegations()
            
            self.log_activity(
                action="delegation_approved",
                details={"delegation_id": delegation_id},
                user=delegation.user_id,
                agent_id=delegation.agent_id,
                delegation_id=delegation_id
            )
            
            return delegation_token
    
    def deny_delegation(self, delegation_id: str) -> bool:
        """Deny a delegation."""
        with self._lock:
            if delegation_id not in self._delegations:
                return False
            
            delegation = self._delegations[delegation_id]
            delegation.deny()
            self._save_delegations()
            
            self.log_activity(
                action="delegation_denied",
                details={"delegation_id": delegation_id},
                user=delegation.user_id,
                agent_id=delegation.agent_id,
                delegation_id=delegation_id
            )
            
            return True
    
    def revoke_delegation(self, delegation_id: str) -> bool:
        """Revoke a delegation."""
        with self._lock:
            if delegation_id not in self._delegations:
                return False
            
            delegation = self._delegations[delegation_id]
            
            # Add tokens to revoked list
            if delegation.delegation_token:
                self._revoked_tokens.add(delegation.delegation_token)
            if delegation.access_token:
                self._revoked_tokens.add(delegation.access_token)
            
            delegation.revoke()
            self._save_delegations()
            self._save_tokens()
            
            self.log_activity(
                action="delegation_revoked",
                details={"delegation_id": delegation_id},
                user=delegation.user_id,
                agent_id=delegation.agent_id,
                delegation_id=delegation_id
            )
            
            return True
    
    # ============================================================================
    # TOKEN MANAGEMENT
    # ============================================================================
    
    def add_active_token(self, token: str):
        """Add token to active tokens list."""
        with self._lock:
            if token not in self._active_tokens:
                self._active_tokens.append(token)
                self._save_tokens()
    
    def revoke_token(self, token: str):
        """Revoke a specific token."""
        with self._lock:
            self._revoked_tokens.add(token)
            self._save_tokens()
            
            self.log_activity(
                action="token_revoked",
                details={"token_preview": token[:20] + "..."}
            )
    
    def is_token_revoked(self, token: str) -> bool:
        """Check if token is revoked."""
        with self._lock:
            return token in self._revoked_tokens
    
    def get_active_tokens(self) -> List[TokenInfo]:
        """Get list of active tokens with analysis."""
        with self._lock:
            active_tokens = []
            
            for token in self._active_tokens:
                if token not in self._revoked_tokens:
                    token_info = TokenInfo.from_token(token, self._revoked_tokens)
                    if token_info.is_valid:
                        active_tokens.append(token_info)
            
            return active_tokens
    
    def introspect_token(self, token: str) -> TokenInfo:
        """Perform detailed token analysis."""
        with self._lock:
            return TokenInfo.from_token(token, self._revoked_tokens)
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from active list."""
        with self._lock:
            valid_tokens = []
            
            for token in self._active_tokens:
                token_info = TokenInfo.from_token(token, self._revoked_tokens)
                if not token_info.is_expired:
                    valid_tokens.append(token)
            
            if len(valid_tokens) != len(self._active_tokens):
                self._active_tokens = valid_tokens
                self._save_tokens()
                
                self.log_activity(
                    action="tokens_cleaned",
                    details={"removed_count": len(self._active_tokens) - len(valid_tokens)}
                )
    
    # ============================================================================
    # ACTIVITY LOGGING
    # ============================================================================
    
    def log_activity(self, action: str, details: Dict[str, Any], 
                    user: Optional[str] = None, agent_id: Optional[str] = None,
                    delegation_id: Optional[str] = None):
        """Log system activity."""
        with self._lock:
            activity = SystemActivity(
                id=f"activity-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.utcnow().isoformat(),
                action=action,
                details=details,
                user=user,
                agent_id=agent_id,
                delegation_id=delegation_id
            )
            
            self._system_activities.append(activity)
            
            # Keep only last 1000 activities
            if len(self._system_activities) > 1000:
                self._system_activities = self._system_activities[-1000:]
            
            self._save_activities()
    
    def get_activities(self, limit: int = 50) -> List[SystemActivity]:
        """Get recent system activities."""
        with self._lock:
            limit = min(limit, 100)  # Cap at 100
            return self._system_activities[-limit:] if self._system_activities else []
    
    # ============================================================================
    # STATISTICS
    # ============================================================================
    
    def get_system_stats(self) -> SystemStats:
        """Get comprehensive system statistics."""
        with self._lock:
            # Agent stats
            agent_statuses = [agent.status for agent in self._agents.values()]
            
            # Delegation stats
            delegation_statuses = [delegation.status for delegation in self._delegations.values()]
            
            # Token stats
            active_token_count = len([
                t for t in self._active_tokens 
                if t not in self._revoked_tokens and 
                TokenInfo.from_token(t, self._revoked_tokens).is_valid
            ])
            
            return SystemStats(
                total_agents=len(self._agents),
                active_agents=agent_statuses.count(AgentStatus.ACTIVE.value),
                inactive_agents=agent_statuses.count(AgentStatus.INACTIVE.value),
                suspended_agents=agent_statuses.count(AgentStatus.SUSPENDED.value),
                total_delegations=len(self._delegations),
                pending_delegations=delegation_statuses.count(DelegationStatus.PENDING.value),
                approved_delegations=delegation_statuses.count(DelegationStatus.APPROVED.value),
                denied_delegations=delegation_statuses.count(DelegationStatus.DENIED.value),
                revoked_delegations=delegation_statuses.count(DelegationStatus.REVOKED.value),
                expired_delegations=delegation_statuses.count(DelegationStatus.EXPIRED.value),
                active_tokens=active_token_count,
                revoked_tokens=len(self._revoked_tokens),
                total_users=len(self._users)
            )


# Global storage manager instance
storage_manager = StorageManager()
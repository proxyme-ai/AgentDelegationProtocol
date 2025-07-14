"""
Enhanced API Server for Agent Delegation Protocol Frontend
Provides comprehensive REST API endpoints for agent management, delegation management, and system status.
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import json
import os
import uuid
import functools
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from config import config
from logging_config import get_logger

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
cors_origins = config.cors_origins if config.cors_origins else ["http://localhost:3000", "http://localhost:7000"]
CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize logger
logger = get_logger('api_server')

# Global data stores
AGENTS = {}
USERS = {}
DELEGATIONS = {}
ACTIVE_TOKENS = []
REVOKED_TOKENS = set()
SYSTEM_LOGS = []

@dataclass
class Agent:
    """Enhanced Agent data model."""
    id: str
    name: str
    description: str = ""
    scopes: List[str] = None
    status: str = "active"  # active, inactive, suspended
    created_at: str = ""
    last_used: Optional[str] = None
    delegation_count: int = 0
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = []
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

@dataclass
class Delegation:
    """Enhanced Delegation data model."""
    id: str
    agent_id: str
    agent_name: str
    user_id: str
    scopes: List[str]
    status: str = "pending"  # pending, approved, denied, expired, revoked
    created_at: str = ""
    approved_at: Optional[str] = None
    expires_at: str = ""
    delegation_token: Optional[str] = None
    access_token: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.expires_at:
            self.expires_at = (datetime.utcnow() + timedelta(minutes=config.delegation_token_expiry)).isoformat()

def load_data():
    """Load data from JSON files."""
    global AGENTS, USERS
    
    # Load agents
    if os.path.exists(config.agents_file):
        with open(config.agents_file) as f:
            agent_data = json.load(f)
            # Convert old format to new format
            for agent_id, agent_info in agent_data.items():
                if isinstance(agent_info, dict) and 'name' in agent_info:
                    AGENTS[agent_id] = Agent(
                        id=agent_id,
                        name=agent_info['name'],
                        description=agent_info.get('description', ''),
                        scopes=agent_info.get('scopes', []),
                        status=agent_info.get('status', 'active'),
                        created_at=agent_info.get('created_at', datetime.utcnow().isoformat()),
                        last_used=agent_info.get('last_used'),
                        delegation_count=agent_info.get('delegation_count', 0)
                    )
    
    # Load users
    if os.path.exists(config.users_file):
        with open(config.users_file) as f:
            USERS.update(json.load(f))

def save_data():
    """Save data to JSON files."""
    # Save agents
    agent_data = {}
    for agent_id, agent in AGENTS.items():
        agent_data[agent_id] = asdict(agent)
    
    with open(config.agents_file, 'w') as f:
        json.dump(agent_data, f, indent=2)
    
    # Save users
    with open(config.users_file, 'w') as f:
        json.dump(USERS, f, indent=2)

def log_activity(action: str, details: Dict[str, Any], user: str = None):
    """Log system activity."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "details": details,
        "user": user
    }
    SYSTEM_LOGS.append(log_entry)
    # Keep only last 1000 logs
    if len(SYSTEM_LOGS) > 1000:
        SYSTEM_LOGS.pop(0)

def validate_json(required_fields: List[str]):
    """Decorator to validate JSON request data."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Content-Type must be application/json"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON data"}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    "error": "Missing required fields",
                    "missing_fields": missing_fields
                }), 400
            
            g.json_data = data
            return f(*args, **kwargs)
        return wrapper
    return decorator

def handle_errors(f):
    """Decorator for consistent error handling."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error in {f.__name__}: {str(e)}")
            return jsonify({
                "error": "Validation error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat()
            }), 500
    return wrapper

# Initialize data on startup
load_data()

# ============================================================================
# AGENT MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/agents', methods=['GET'])
@handle_errors
def list_agents():
    """List all registered agents with filtering and search."""
    status_filter = request.args.get('status')
    search = request.args.get('search', '').lower()
    
    agents = []
    for agent in AGENTS.values():
        agent_dict = asdict(agent)
        
        # Apply status filter
        if status_filter and agent.status != status_filter:
            continue
        
        # Apply search filter
        if search and search not in agent.name.lower() and search not in agent.description.lower():
            continue
        
        agents.append(agent_dict)
    
    return jsonify({
        "agents": agents,
        "total": len(agents),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/agents', methods=['POST'])
@validate_json(['name'])
@handle_errors
def create_agent():
    """Register a new agent."""
    data = g.json_data
    
    # Generate unique agent ID
    agent_id = data.get('id') or f"agent-{uuid.uuid4().hex[:8]}"
    
    if agent_id in AGENTS:
        return jsonify({"error": "Agent ID already exists"}), 409
    
    # Create new agent
    agent = Agent(
        id=agent_id,
        name=data['name'],
        description=data.get('description', ''),
        scopes=data.get('scopes', []),
        status=data.get('status', 'active')
    )
    
    AGENTS[agent_id] = agent
    save_data()
    
    log_activity("agent_created", {"agent_id": agent_id, "name": agent.name})
    
    return jsonify({
        "message": "Agent created successfully",
        "agent": asdict(agent)
    }), 201

@app.route('/api/agents/<agent_id>', methods=['GET'])
@handle_errors
def get_agent(agent_id):
    """Get agent details."""
    if agent_id not in AGENTS:
        return jsonify({"error": "Agent not found"}), 404
    
    agent = AGENTS[agent_id]
    agent_dict = asdict(agent)
    
    # Add delegation history
    agent_delegations = [
        asdict(delegation) for delegation in DELEGATIONS.values()
        if delegation.agent_id == agent_id
    ]
    agent_dict['delegations'] = agent_delegations
    
    return jsonify(agent_dict)

@app.route('/api/agents/<agent_id>', methods=['PUT'])
@validate_json([])
@handle_errors
def update_agent(agent_id):
    """Update agent details."""
    if agent_id not in AGENTS:
        return jsonify({"error": "Agent not found"}), 404
    
    data = g.json_data
    agent = AGENTS[agent_id]
    
    # Update allowed fields
    if 'name' in data:
        agent.name = data['name']
    if 'description' in data:
        agent.description = data['description']
    if 'scopes' in data:
        agent.scopes = data['scopes']
    if 'status' in data:
        if data['status'] not in ['active', 'inactive', 'suspended']:
            return jsonify({"error": "Invalid status"}), 400
        agent.status = data['status']
    
    save_data()
    log_activity("agent_updated", {"agent_id": agent_id, "changes": data})
    
    return jsonify({
        "message": "Agent updated successfully",
        "agent": asdict(agent)
    })

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
@handle_errors
def delete_agent(agent_id):
    """Delete an agent."""
    if agent_id not in AGENTS:
        return jsonify({"error": "Agent not found"}), 404
    
    agent_name = AGENTS[agent_id].name
    del AGENTS[agent_id]
    save_data()
    
    log_activity("agent_deleted", {"agent_id": agent_id, "name": agent_name})
    
    return jsonify({"message": "Agent deleted successfully"})

# ============================================================================
# DELEGATION MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/delegations', methods=['GET'])
@handle_errors
def list_delegations():
    """List delegations with filtering."""
    status_filter = request.args.get('status')
    agent_id_filter = request.args.get('agent_id')
    user_id_filter = request.args.get('user_id')
    
    delegations = []
    for delegation in DELEGATIONS.values():
        delegation_dict = asdict(delegation)
        
        # Apply filters
        if status_filter and delegation.status != status_filter:
            continue
        if agent_id_filter and delegation.agent_id != agent_id_filter:
            continue
        if user_id_filter and delegation.user_id != user_id_filter:
            continue
        
        delegations.append(delegation_dict)
    
    # Sort by created_at descending
    delegations.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        "delegations": delegations,
        "total": len(delegations),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/delegations', methods=['POST'])
@validate_json(['agent_id', 'user_id', 'scopes'])
@handle_errors
def create_delegation():
    """Create a new delegation request."""
    data = g.json_data
    
    agent_id = data['agent_id']
    user_id = data['user_id']
    
    # Validate agent exists
    if agent_id not in AGENTS:
        return jsonify({"error": "Agent not found"}), 404
    
    # Validate user exists
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
    
    # Create delegation
    delegation_id = f"delegation-{uuid.uuid4().hex[:8]}"
    delegation = Delegation(
        id=delegation_id,
        agent_id=agent_id,
        agent_name=AGENTS[agent_id].name,
        user_id=user_id,
        scopes=data['scopes']
    )
    
    DELEGATIONS[delegation_id] = delegation
    log_activity("delegation_created", {
        "delegation_id": delegation_id,
        "agent_id": agent_id,
        "user_id": user_id,
        "scopes": data['scopes']
    })
    
    return jsonify({
        "message": "Delegation created successfully",
        "delegation": asdict(delegation)
    }), 201

@app.route('/api/delegations/<delegation_id>', methods=['GET'])
@handle_errors
def get_delegation(delegation_id):
    """Get delegation details."""
    if delegation_id not in DELEGATIONS:
        return jsonify({"error": "Delegation not found"}), 404
    
    delegation = DELEGATIONS[delegation_id]
    return jsonify(asdict(delegation))

@app.route('/api/delegations/<delegation_id>/approve', methods=['PUT'])
@handle_errors
def approve_delegation(delegation_id):
    """Approve a delegation request."""
    if delegation_id not in DELEGATIONS:
        return jsonify({"error": "Delegation not found"}), 404
    
    delegation = DELEGATIONS[delegation_id]
    
    if delegation.status != 'pending':
        return jsonify({"error": "Delegation is not pending"}), 400
    
    # Generate delegation token
    delegation_claims = {
        "iss": config.auth_server_url,
        "sub": delegation.agent_id,
        "delegator": delegation.user_id,
        "scope": delegation.scopes,
        "exp": datetime.utcnow() + timedelta(minutes=config.delegation_token_expiry),
        "iat": datetime.utcnow(),
        "delegation_id": delegation_id
    }
    
    delegation_token = jwt.encode(delegation_claims, config.jwt_secret, algorithm=config.jwt_algorithm)
    
    # Update delegation
    delegation.status = 'approved'
    delegation.approved_at = datetime.utcnow().isoformat()
    delegation.delegation_token = delegation_token
    
    # Update agent delegation count
    if delegation.agent_id in AGENTS:
        AGENTS[delegation.agent_id].delegation_count += 1
        AGENTS[delegation.agent_id].last_used = datetime.utcnow().isoformat()
    
    log_activity("delegation_approved", {"delegation_id": delegation_id})
    
    return jsonify({
        "message": "Delegation approved successfully",
        "delegation": asdict(delegation)
    })

@app.route('/api/delegations/<delegation_id>/deny', methods=['PUT'])
@handle_errors
def deny_delegation(delegation_id):
    """Deny a delegation request."""
    if delegation_id not in DELEGATIONS:
        return jsonify({"error": "Delegation not found"}), 404
    
    delegation = DELEGATIONS[delegation_id]
    
    if delegation.status != 'pending':
        return jsonify({"error": "Delegation is not pending"}), 400
    
    delegation.status = 'denied'
    log_activity("delegation_denied", {"delegation_id": delegation_id})
    
    return jsonify({
        "message": "Delegation denied successfully",
        "delegation": asdict(delegation)
    })

@app.route('/api/delegations/<delegation_id>', methods=['DELETE'])
@handle_errors
def revoke_delegation(delegation_id):
    """Revoke a delegation."""
    if delegation_id not in DELEGATIONS:
        return jsonify({"error": "Delegation not found"}), 404
    
    delegation = DELEGATIONS[delegation_id]
    delegation.status = 'revoked'
    
    # Revoke associated tokens
    if delegation.delegation_token:
        REVOKED_TOKENS.add(delegation.delegation_token)
    if delegation.access_token:
        REVOKED_TOKENS.add(delegation.access_token)
    
    log_activity("delegation_revoked", {"delegation_id": delegation_id})
    
    return jsonify({"message": "Delegation revoked successfully"})

# ============================================================================
# TOKEN MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/tokens/active', methods=['GET'])
@handle_errors
def list_active_tokens():
    """List active tokens."""
    active_tokens = []
    
    for token in ACTIVE_TOKENS:
        if token not in REVOKED_TOKENS:
            try:
                decoded = jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algorithm])
                if datetime.utcfromtimestamp(decoded['exp']) > datetime.utcnow():
                    active_tokens.append({
                        "token": token[:20] + "...",  # Truncated for security
                        "type": "access" if "actor" in decoded else "delegation",
                        "subject": decoded.get('sub'),
                        "expires_at": datetime.utcfromtimestamp(decoded['exp']).isoformat(),
                        "issued_at": datetime.utcfromtimestamp(decoded['iat']).isoformat(),
                        "scopes": decoded.get('scope', [])
                    })
            except jwt.InvalidTokenError:
                continue
    
    return jsonify({
        "active_tokens": active_tokens,
        "total": len(active_tokens),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/tokens/introspect', methods=['POST'])
@validate_json(['token'])
@handle_errors
def introspect_token():
    """Detailed token analysis."""
    token = g.json_data['token']
    
    try:
        # Decode without verification first to get claims
        unverified = jwt.decode(token, options={"verify_signature": False})
        
        # Then verify
        verified = jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algorithm])
        
        is_revoked = token in REVOKED_TOKENS
        is_expired = datetime.utcfromtimestamp(verified['exp']) <= datetime.utcnow()
        is_valid = not is_revoked and not is_expired
        
        time_to_expiry = datetime.utcfromtimestamp(verified['exp']) - datetime.utcnow()
        
        return jsonify({
            "token_info": {
                "type": "access" if "actor" in verified else "delegation",
                "claims": verified,
                "is_valid": is_valid,
                "is_revoked": is_revoked,
                "is_expired": is_expired,
                "expires_at": datetime.utcfromtimestamp(verified['exp']).isoformat(),
                "issued_at": datetime.utcfromtimestamp(verified['iat']).isoformat(),
                "time_to_expiry_seconds": int(time_to_expiry.total_seconds()) if not is_expired else 0
            }
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({
            "token_info": {
                "claims": unverified,
                "is_valid": False,
                "is_expired": True,
                "error": "Token has expired"
            }
        })
    except jwt.InvalidTokenError as e:
        return jsonify({
            "token_info": {
                "is_valid": False,
                "error": f"Invalid token: {str(e)}"
            }
        }), 400

@app.route('/api/tokens/revoke', methods=['POST'])
@validate_json(['token'])
@handle_errors
def revoke_token():
    """Revoke a specific token."""
    token = g.json_data['token']
    REVOKED_TOKENS.add(token)
    
    log_activity("token_revoked", {"token_preview": token[:20] + "..."})
    
    return jsonify({"message": "Token revoked successfully"})

# ============================================================================
# DEMO & SIMULATION ENDPOINTS
# ============================================================================

@app.route('/api/demo/run', methods=['POST'])
@handle_errors
def run_demo():
    """Execute complete demo flow."""
    try:
        # Step 1: Get or create demo agent
        demo_agent_id = "demo-agent"
        if demo_agent_id not in AGENTS:
            AGENTS[demo_agent_id] = Agent(
                id=demo_agent_id,
                name="Demo Agent",
                description="Agent for demonstration purposes",
                scopes=["read:data", "write:data"]
            )
            save_data()
        
        # Step 2: Create delegation
        delegation_id = f"demo-delegation-{uuid.uuid4().hex[:8]}"
        delegation = Delegation(
            id=delegation_id,
            agent_id=demo_agent_id,
            agent_name="Demo Agent",
            user_id="alice",
            scopes=["read:data"]
        )
        DELEGATIONS[delegation_id] = delegation
        
        # Step 3: Auto-approve delegation
        delegation_claims = {
            "iss": config.auth_server_url,
            "sub": demo_agent_id,
            "delegator": "alice",
            "scope": ["read:data"],
            "exp": datetime.utcnow() + timedelta(minutes=config.delegation_token_expiry),
            "iat": datetime.utcnow(),
            "delegation_id": delegation_id
        }
        delegation_token = jwt.encode(delegation_claims, config.jwt_secret, algorithm=config.jwt_algorithm)
        
        delegation.status = 'approved'
        delegation.approved_at = datetime.utcnow().isoformat()
        delegation.delegation_token = delegation_token
        
        # Step 4: Exchange for access token
        access_claims = {
            "iss": config.auth_server_url,
            "sub": "alice",
            "actor": demo_agent_id,
            "scope": ["read:data"],
            "exp": datetime.utcnow() + timedelta(minutes=config.access_token_expiry),
            "iat": datetime.utcnow(),
            "jti": f"demo-token-{len(ACTIVE_TOKENS)+1}"
        }
        access_token = jwt.encode(access_claims, config.jwt_secret, algorithm=config.jwt_algorithm)
        ACTIVE_TOKENS.append(access_token)
        delegation.access_token = access_token
        
        log_activity("demo_executed", {"delegation_id": delegation_id})
        
        return jsonify({
            "demo_result": {
                "step": "complete",
                "delegation_token": delegation_token,
                "access_token": access_token,
                "delegation_id": delegation_id,
                "agent_id": demo_agent_id,
                "user_id": "alice",
                "scopes": ["read:data"],
                "message": "Demo flow completed successfully"
            }
        })
        
    except Exception as e:
        logger.error(f"Demo execution failed: {str(e)}")
        return jsonify({
            "error": "Demo execution failed",
            "message": str(e)
        }), 500

@app.route('/api/simulate/scenarios', methods=['GET'])
@handle_errors
def list_scenarios():
    """List available simulation scenarios."""
    scenarios = [
        {
            "id": "happy_path",
            "name": "Happy Path Flow",
            "description": "Normal delegation flow with successful token exchange"
        },
        {
            "id": "token_expiry",
            "name": "Token Expiry Scenario",
            "description": "Simulate token expiration and handling"
        },
        {
            "id": "revocation",
            "name": "Token Revocation",
            "description": "Simulate token revocation and access denial"
        },
        {
            "id": "invalid_agent",
            "name": "Invalid Agent",
            "description": "Attempt delegation with unregistered agent"
        }
    ]
    
    return jsonify({"scenarios": scenarios})

@app.route('/api/simulate/<scenario_id>', methods=['POST'])
@handle_errors
def run_simulation(scenario_id):
    """Run specific simulation scenario."""
    # This is a simplified implementation - in a real system, 
    # you'd have more complex simulation logic
    
    if scenario_id == "happy_path":
        return jsonify({
            "simulation_result": {
                "scenario": "happy_path",
                "status": "success",
                "steps": [
                    {"step": 1, "action": "Agent registration", "result": "success"},
                    {"step": 2, "action": "Delegation request", "result": "success"},
                    {"step": 3, "action": "Token exchange", "result": "success"},
                    {"step": 4, "action": "Resource access", "result": "success"}
                ],
                "message": "Happy path simulation completed successfully"
            }
        })
    
    elif scenario_id == "token_expiry":
        return jsonify({
            "simulation_result": {
                "scenario": "token_expiry",
                "status": "expected_failure",
                "steps": [
                    {"step": 1, "action": "Token generation", "result": "success"},
                    {"step": 2, "action": "Wait for expiry", "result": "success"},
                    {"step": 3, "action": "Access attempt", "result": "failed - token expired"}
                ],
                "message": "Token expiry scenario completed as expected"
            }
        })
    
    else:
        return jsonify({"error": "Unknown scenario"}), 404

# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================

@app.route('/api/status', methods=['GET'])
@handle_errors
def system_status():
    """Get system health and statistics."""
    active_token_count = len([t for t in ACTIVE_TOKENS if t not in REVOKED_TOKENS])
    
    return jsonify({
        "status": "healthy",
        "service": "api-server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": {
            "total_agents": len(AGENTS),
            "active_agents": len([a for a in AGENTS.values() if a.status == 'active']),
            "total_delegations": len(DELEGATIONS),
            "pending_delegations": len([d for d in DELEGATIONS.values() if d.status == 'pending']),
            "active_delegations": len([d for d in DELEGATIONS.values() if d.status == 'approved']),
            "active_tokens": active_token_count,
            "revoked_tokens": len(REVOKED_TOKENS)
        }
    })

@app.route('/api/logs', methods=['GET'])
@handle_errors
def get_logs():
    """Get recent system activity logs."""
    limit = min(int(request.args.get('limit', 50)), 100)
    logs = SYSTEM_LOGS[-limit:] if SYSTEM_LOGS else []
    
    return jsonify({
        "logs": logs,
        "total": len(logs),
        "timestamp": datetime.utcnow().isoformat()
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",
        "message": "The requested resource was not found",
        "timestamp": datetime.utcnow().isoformat()
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed",
        "message": "The requested method is not allowed for this resource",
        "timestamp": datetime.utcnow().isoformat()
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.utcnow().isoformat()
    }), 500

def main():
    """Main entry point for the API server."""
    logger.info(f"Starting API Server on port {config.frontend_port}")
    logger.info(f"CORS origins: {cors_origins}")
    
    app.run(
        host="0.0.0.0",
        port=config.frontend_port,
        debug=False
    )

if __name__ == '__main__':
    main()
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
from dataclasses import asdict
from config import config
from logging_config import get_logger
from storage_manager import storage_manager
from data_models import Agent, Delegation, TokenInfo, SystemActivity, AgentStatus, DelegationStatus

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
cors_origins = config.cors_origins if config.cors_origins else ["http://localhost:3000", "http://localhost:7000"]
CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize logger
logger = get_logger('api_server')

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

# ============================================================================
# AGENT MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/agents', methods=['GET'])
@handle_errors
def list_agents():
    """List all registered agents with filtering and search."""
    status_filter = request.args.get('status')
    search = request.args.get('search', '')
    
    agents = storage_manager.list_agents(status_filter=status_filter, search=search)
    agent_dicts = [agent.to_dict() for agent in agents]
    
    return jsonify({
        "agents": agent_dicts,
        "total": len(agent_dicts),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/agents', methods=['POST'])
@validate_json(['name'])
@handle_errors
def create_agent():
    """Register a new agent."""
    data = g.json_data
    
    # Create agent using storage manager
    agent = storage_manager.create_agent(data)
    
    return jsonify({
        "message": "Agent created successfully",
        "agent": agent.to_dict()
    }), 201

@app.route('/api/agents/<agent_id>', methods=['GET'])
@handle_errors
def get_agent(agent_id):
    """Get agent details."""
    agent = storage_manager.get_agent(agent_id)
    if not agent:
        return jsonify({"error": "Agent not found"}), 404
    
    agent_dict = agent.to_dict()
    
    # Add delegation history
    agent_delegations = storage_manager.list_delegations(agent_id_filter=agent_id)
    agent_dict['delegations'] = [delegation.to_dict() for delegation in agent_delegations]
    
    return jsonify(agent_dict)

@app.route('/api/agents/<agent_id>', methods=['PUT'])
@validate_json([])
@handle_errors
def update_agent(agent_id):
    """Update agent details."""
    data = g.json_data
    
    # Update agent using storage manager
    agent = storage_manager.update_agent(agent_id, data)
    
    return jsonify({
        "message": "Agent updated successfully",
        "agent": agent.to_dict()
    })

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
@handle_errors
def delete_agent(agent_id):
    """Delete an agent."""
    if not storage_manager.delete_agent(agent_id):
        return jsonify({"error": "Agent not found"}), 404
    
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
    
    delegations = storage_manager.list_delegations(
        status_filter=status_filter,
        agent_id_filter=agent_id_filter,
        user_id_filter=user_id_filter
    )
    
    delegation_dicts = [delegation.to_dict() for delegation in delegations]
    
    return jsonify({
        "delegations": delegation_dicts,
        "total": len(delegation_dicts),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/delegations', methods=['POST'])
@validate_json(['agent_id', 'user_id', 'scopes'])
@handle_errors
def create_delegation():
    """Create a new delegation request."""
    data = g.json_data
    
    # Create delegation using storage manager
    delegation = storage_manager.create_delegation(data)
    
    return jsonify({
        "message": "Delegation created successfully",
        "delegation": delegation.to_dict()
    }), 201

@app.route('/api/delegations/<delegation_id>', methods=['GET'])
@handle_errors
def get_delegation(delegation_id):
    """Get delegation details."""
    delegation = storage_manager.get_delegation(delegation_id)
    if not delegation:
        return jsonify({"error": "Delegation not found"}), 404
    
    return jsonify(delegation.to_dict())

@app.route('/api/delegations/<delegation_id>/approve', methods=['PUT'])
@handle_errors
def approve_delegation(delegation_id):
    """Approve a delegation request."""
    try:
        delegation_token = storage_manager.approve_delegation(delegation_id)
        delegation = storage_manager.get_delegation(delegation_id)
        
        return jsonify({
            "message": "Delegation approved successfully",
            "delegation": delegation.to_dict(),
            "delegation_token": delegation_token
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/delegations/<delegation_id>/deny', methods=['PUT'])
@handle_errors
def deny_delegation(delegation_id):
    """Deny a delegation request."""
    if not storage_manager.deny_delegation(delegation_id):
        return jsonify({"error": "Delegation not found"}), 404
    
    delegation = storage_manager.get_delegation(delegation_id)
    
    return jsonify({
        "message": "Delegation denied successfully",
        "delegation": delegation.to_dict()
    })

@app.route('/api/delegations/<delegation_id>', methods=['DELETE'])
@handle_errors
def revoke_delegation(delegation_id):
    """Revoke a delegation."""
    if not storage_manager.revoke_delegation(delegation_id):
        return jsonify({"error": "Delegation not found"}), 404
    
    return jsonify({"message": "Delegation revoked successfully"})

# ============================================================================
# TOKEN MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/tokens/active', methods=['GET'])
@handle_errors
def list_active_tokens():
    """List active tokens."""
    active_tokens = storage_manager.get_active_tokens()
    
    token_dicts = []
    for token_info in active_tokens:
        token_dicts.append({
            "token": token_info.token[:20] + "...",  # Truncated for security
            "type": token_info.token_type,
            "subject": token_info.subject,
            "expires_at": token_info.expires_at,
            "issued_at": token_info.issued_at,
            "scopes": token_info.scopes,
            "time_to_expiry_seconds": token_info.time_to_expiry_seconds
        })
    
    return jsonify({
        "active_tokens": token_dicts,
        "total": len(token_dicts),
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/tokens/introspect', methods=['POST'])
@validate_json(['token'])
@handle_errors
def introspect_token():
    """Detailed token analysis."""
    token = g.json_data['token']
    
    token_info = storage_manager.introspect_token(token)
    
    return jsonify({
        "token_info": token_info.to_dict()
    })

@app.route('/api/tokens/revoke', methods=['POST'])
@validate_json(['token'])
@handle_errors
def revoke_token():
    """Revoke a specific token."""
    token = g.json_data['token']
    storage_manager.revoke_token(token)
    
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
        demo_agent = storage_manager.get_agent(demo_agent_id)
        
        if not demo_agent:
            demo_agent = storage_manager.create_agent({
                'id': demo_agent_id,
                'name': "Demo Agent",
                'description': "Agent for demonstration purposes",
                'scopes': ["read:data", "write:data"]
            })
        
        # Step 2: Create delegation
        delegation = storage_manager.create_delegation({
            'agent_id': demo_agent_id,
            'user_id': "alice",
            'scopes': ["read:data"]
        })
        
        # Step 3: Auto-approve delegation
        delegation_token = storage_manager.approve_delegation(delegation.id)
        
        # Step 4: Generate access token from delegation
        delegation = storage_manager.get_delegation(delegation.id)
        access_token = delegation.generate_access_token()
        storage_manager.add_active_token(access_token)
        
        return jsonify({
            "demo_result": {
                "step": "complete",
                "delegation_token": delegation_token,
                "access_token": access_token,
                "delegation_id": delegation.id,
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
    stats = storage_manager.get_system_stats()
    
    return jsonify({
        "status": "healthy",
        "service": "api-server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": stats.to_dict()
    })

@app.route('/api/logs', methods=['GET'])
@handle_errors
def get_logs():
    """Get recent system activity logs."""
    limit = min(int(request.args.get('limit', 50)), 100)
    activities = storage_manager.get_activities(limit)
    logs = [activity.to_dict() for activity in activities]
    
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
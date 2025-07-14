# === File: auth_server.py ===
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import json
import os
import requests
from urllib.parse import urlencode
import hashlib
import base64
from config import config
from logging_config import get_logger
from storage_manager import storage_manager
from data_models import Agent, AgentStatus

app = Flask(__name__)

# Configure CORS
cors_origins = config.cors_origins if config.cors_origins else ["http://localhost:3000", "http://localhost:7000"]
CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize logger
logger = get_logger('auth_server')

# Use configuration values
JWT_SECRET = config.jwt_secret
KEYCLOAK_URL = config.keycloak_url
KEYCLOAK_REALM = config.keycloak_realm
KEYCLOAK_CLIENT_ID = config.keycloak_client_id
KEYCLOAK_CLIENT_SECRET = config.keycloak_client_secret
REDIRECT_URI = config.redirect_uri


@app.route('/register', methods=['POST'])
def register():
    """Register a new agent with enhanced validation."""
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid JSON data',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        client_id = data.get('client_id')
        name = data.get('name')
        
        if not client_id or not name:
            return jsonify({
                'error': 'Missing required fields',
                'required_fields': ['client_id', 'name'],
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Check if agent already exists
        if storage_manager.get_agent(client_id):
            return jsonify({
                'error': 'Agent already exists',
                'client_id': client_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 409

        # Create agent using storage manager
        agent_data = {
            'id': client_id,
            'name': name,
            'description': data.get('description', ''),
            'scopes': data.get('scopes', []),
            'status': AgentStatus.ACTIVE.value
        }
        
        agent = storage_manager.create_agent(agent_data)
        
        logger.info(f"Agent registered: {client_id}")
        return jsonify({
            'status': 'registered',
            'client_id': client_id,
            'agent': agent.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'error': 'Validation error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    except Exception as e:
        logger.error(f"Error in register endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/register_user', methods=['POST'])
def register_user():
    """Register a new user with enhanced validation."""
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid JSON data',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'error': 'Missing required fields',
                'required_fields': ['username', 'password'],
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Check if user already exists using storage manager
        if storage_manager.get_user(username):
            return jsonify({
                'error': 'User already exists',
                'username': username,
                'timestamp': datetime.utcnow().isoformat()
            }), 409
        
        # Create user using storage manager
        if not storage_manager.create_user(username, password):
            return jsonify({
                'error': 'Failed to create user',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
        
        logger.info(f"User registered: {username}")
        return jsonify({
            'status': 'registered',
            'username': username,
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error in register_user endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/authorize')
def authorize():
    client_id = request.args.get('client_id')
    scope = request.args.get('scope', '')
    code_challenge = request.args.get('code_challenge')
    code_challenge_method = request.args.get('code_challenge_method', 'plain')

    # Check if agent exists using storage manager
    if not storage_manager.get_agent(client_id):
        return "Agent not registered", 403

    if KEYCLOAK_URL:
        state = f"{client_id}|{scope}"
        query = urlencode({
            "client_id": KEYCLOAK_CLIENT_ID,
            "response_type": "code",
            "scope": "openid profile",
            "redirect_uri": REDIRECT_URI,
            "state": state,
        })
        return redirect(f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth?{query}")

    user = request.args.get('user')
    if not storage_manager.get_user(user):
        return "User not found", 403

    delegation = {
        "iss": config.auth_server_url,
        "sub": client_id,
        "delegator": user,
        "scope": scope.split(),
        "exp": datetime.utcnow() + timedelta(minutes=config.delegation_token_expiry),
        "iat": datetime.utcnow(),
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method
    }
    delegation_token = jwt.encode(delegation, JWT_SECRET, algorithm="HS256")
    return jsonify({"delegation_token": delegation_token})

@app.route('/callback')
def callback():
    if not KEYCLOAK_URL:
        return "Keycloak not configured", 404

    code = request.args.get('code')
    state = request.args.get('state', '')
    if not code or not state:
        return "Invalid request", 400

    if '|' in state:
        client_id, scope = state.split('|', 1)
    else:
        client_id, scope = state, ''

    # Check if agent exists using storage manager
    if not storage_manager.get_agent(client_id):
        return "Agent not registered", 403

    token_res = requests.post(
        f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": KEYCLOAK_CLIENT_ID,
            "client_secret": KEYCLOAK_CLIENT_SECRET,
        },
    )
    token_res.raise_for_status()
    id_token = token_res.json().get("id_token")
    id_claims = jwt.decode(id_token, options={"verify_signature": False})

    delegation = {
        "iss": config.auth_server_url,
        "sub": client_id,
        "delegator": id_claims["sub"],
        "scope": scope.split(),
        "exp": datetime.utcnow() + timedelta(minutes=config.delegation_token_expiry),
        "iat": datetime.utcnow(),
    }
    delegation_token = jwt.encode(delegation, JWT_SECRET, algorithm="HS256")
    return jsonify({"delegation_token": delegation_token})

@app.route('/token', methods=['POST'])
def token():
    token_str = request.form.get('delegation_token')
    try:
        delegation = jwt.decode(token_str, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "Delegation token expired", 403
    except jwt.InvalidTokenError:
        return "Invalid delegation token", 403

    # Check if token is revoked
    if storage_manager.is_token_revoked(token_str):
        return "Delegation token revoked", 403

    challenge = delegation.get("code_challenge")
    challenge_method = delegation.get("code_challenge_method", "plain")
    code_verifier = request.form.get("code_verifier")
    if challenge and not code_verifier:
        return "Missing code verifier", 403
    if challenge and code_verifier:
        if challenge_method == "S256":
            digest = hashlib.sha256(code_verifier.encode()).digest()
            encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
            if encoded != challenge:
                return "Invalid code verifier", 403
        else:
            if code_verifier != challenge:
                return "Invalid code verifier", 403

    # Get current active token count for JTI
    active_tokens = storage_manager.get_active_tokens()
    access_claim = {
        "iss": config.auth_server_url,
        "sub": delegation['delegator'],
        "actor": delegation['sub'],
        "scope": delegation['scope'],
        "exp": datetime.utcnow() + timedelta(minutes=config.access_token_expiry),
        "iat": datetime.utcnow(),
        "jti": f"token-{len(active_tokens)+1}"
    }
    access_token = jwt.encode(access_claim, JWT_SECRET, algorithm="HS256")
    
    # Add token to storage manager
    storage_manager.add_active_token(access_token)
    
    return jsonify({"access_token": access_token, "token_type": "Bearer"})

@app.route('/revoke', methods=['POST'])
def revoke():
    token = request.form.get('token')
    storage_manager.revoke_token(token)
    return jsonify({"status": "revoked"})

@app.route('/introspect', methods=['POST'])
def introspect():
    token = request.form.get('token')
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if storage_manager.is_token_revoked(token):
            return jsonify({"active": False})
        return jsonify({"active": True, **decoded})
    except jwt.InvalidTokenError:
        return jsonify({"active": False})

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "authorization-server",
        "version": "1.0.0",
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
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.utcnow().isoformat()
    }), 500

def main():
    """Main entry point for the authorization server."""
    from config import config
    from logging_config import get_logger
    
    logger = get_logger('auth_server')
    logger.info(f"Starting Authorization Server on port {config.auth_server_port}")
    
    app.run(
        host=config.auth_server_host,
        port=config.auth_server_port,
        debug=False
    )

if __name__ == '__main__':
    main()

# === File: resource_server.py ===
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime
import requests
from config import config
from logging_config import get_logger

app = Flask(__name__)

# Configure CORS
cors_origins = config.cors_origins if config.cors_origins else ["http://localhost:3000", "http://localhost:7000"]
CORS(app, origins=cors_origins, supports_credentials=True)

# Initialize logger
logger = get_logger('resource_server')

INTROSPECT_URL = f"{config.auth_server_url}/introspect"

@app.route('/data')
def data():
    """Get protected data with enhanced validation."""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({
                "error": "Missing or invalid Authorization header",
                "message": "Authorization header must be in format 'Bearer <token>'",
                "timestamp": datetime.utcnow().isoformat()
            }), 401
        
        token = auth.split()[1]
        
        # Introspect token
        try:
            r = requests.post(INTROSPECT_URL, data={"token": token}, timeout=5)
            r.raise_for_status()
            result = r.json()
        except requests.RequestException as e:
            logger.error(f"Token introspection failed: {str(e)}")
            return jsonify({
                "error": "Token validation failed",
                "message": "Unable to validate token with authorization server",
                "timestamp": datetime.utcnow().isoformat()
            }), 503

        if not result.get("active"):
            return jsonify({
                "error": "Invalid token",
                "message": "Token is invalid, expired, or revoked",
                "timestamp": datetime.utcnow().isoformat()
            }), 403

        # Return protected data
        return jsonify({
            "message": "Access granted to protected resource",
            "data": {
                "user": result['sub'],
                "agent": result['actor'],
                "scope": result['scope'],
                "timestamp": datetime.utcnow().isoformat(),
                "resource": "sample_data",
                "content": "This is protected data accessible via delegation"
            }
        })
        
    except Exception as e:
        logger.error(f"Error in data endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "resource-server",
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
    """Main entry point for the resource server."""
    from config import config
    from logging_config import get_logger
    
    logger = get_logger('resource_server')
    logger.info(f"Starting Resource Server on port {config.resource_server_port}")
    
    app.run(
        host=config.resource_server_host,
        port=config.resource_server_port,
        debug=False
    )

if __name__ == '__main__':
    main()

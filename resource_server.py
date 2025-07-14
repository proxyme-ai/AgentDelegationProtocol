# === File: resource_server.py ===
from flask import Flask, request, jsonify
import jwt
from datetime import datetime
import requests

app = Flask(__name__)
INTROSPECT_URL = "http://localhost:5000/introspect"

@app.route('/data')
def data():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return "Missing Authorization header", 401
    token = auth.split()[1]

    r = requests.post(INTROSPECT_URL, data={"token": token})
    result = r.json()

    if not result.get("active"):
        return "Token invalid or revoked", 403

    return jsonify({
        "user": result['sub'],
        "agent": result['actor'],
        "scope": result['scope']
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    from datetime import datetime
    return jsonify({
        "status": "healthy",
        "service": "resource-server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })

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

# === File: auth_server.py ===
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import jwt
import json
import os

app = Flask(__name__)
JWT_SECRET = 'jwt-signing-secret'
AGENTS_FILE = os.environ.get("AGENTS_FILE", "agents.json")


def load_agents():
    if os.path.exists(AGENTS_FILE):
        with open(AGENTS_FILE) as f:
            return json.load(f)
    return {}


def save_agents(data):
    with open(AGENTS_FILE, "w") as f:
        json.dump(data, f)


AGENTS = load_agents()
USERS = {"alice": "password123"}
ACTIVE_TOKENS = []
REVOKED_TOKENS = set()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True, silent=True) or {}
    client_id = data.get('client_id')
    name = data.get('name')
    if not client_id or not name:
        return jsonify({'error': 'missing client_id or name'}), 400
    if client_id in AGENTS:
        return jsonify({'error': 'client exists'}), 400

    AGENTS[client_id] = {'name': name}
    save_agents(AGENTS)
    return jsonify({'status': 'registered'}), 201

@app.route('/authorize')
def authorize():
    user = request.args.get('user')
    client_id = request.args.get('client_id')
    scope = request.args.get('scope', '')

    if user not in USERS:
        return "User not found", 403
    if client_id not in AGENTS:
        return "Agent not registered", 403

    delegation = {
        "iss": "http://localhost:5000",
        "sub": client_id,
        "delegator": user,
        "scope": scope.split(),
        "exp": datetime.utcnow() + timedelta(minutes=10),
        "iat": datetime.utcnow()
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

    access_claim = {
        "iss": "http://localhost:5000",
        "sub": delegation['delegator'],
        "actor": delegation['sub'],
        "scope": delegation['scope'],
        "exp": datetime.utcnow() + timedelta(minutes=5),
        "iat": datetime.utcnow(),
        "jti": f"token-{len(ACTIVE_TOKENS)+1}"
    }
    access_token = jwt.encode(access_claim, JWT_SECRET, algorithm="HS256")
    ACTIVE_TOKENS.append(access_token)
    return jsonify({"access_token": access_token, "token_type": "Bearer"})

@app.route('/revoke', methods=['POST'])
def revoke():
    token = request.form.get('token')
    REVOKED_TOKENS.add(token)
    return jsonify({"status": "revoked"})

@app.route('/introspect', methods=['POST'])
def introspect():
    token = request.form.get('token')
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if token in REVOKED_TOKENS:
            return jsonify({"active": False})
        return jsonify({"active": True, **decoded})
    except jwt.InvalidTokenError:
        return jsonify({"active": False})

if __name__ == '__main__':
    app.run(port=5000)

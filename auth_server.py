# === File: auth_server.py ===
from flask import Flask, request, jsonify, redirect
from datetime import datetime, timedelta
import jwt
import json
import os
import requests
from urllib.parse import urlencode
import hashlib
import base64

app = Flask(__name__)
JWT_SECRET = 'jwt-signing-secret'
AGENTS_FILE = os.environ.get("AGENTS_FILE", "agents.json")
KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:5000/callback")

DEFAULT_AGENT = {"agent-client-id": {"name": "CalendarAgent"}}


def load_agents():
    if os.path.exists(AGENTS_FILE):
        with open(AGENTS_FILE) as f:
            return json.load(f)
    # initialize file with default agent if missing
    with open(AGENTS_FILE, "w") as f:
        json.dump(DEFAULT_AGENT, f)
    return DEFAULT_AGENT.copy()


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
    client_id = request.args.get('client_id')
    scope = request.args.get('scope', '')
    code_challenge = request.args.get('code_challenge')
    code_challenge_method = request.args.get('code_challenge_method', 'plain')

    if client_id not in AGENTS:
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
    if user not in USERS:
        return "User not found", 403

    delegation = {
        "iss": "http://localhost:5000",
        "sub": client_id,
        "delegator": user,
        "scope": scope.split(),
        "exp": datetime.utcnow() + timedelta(minutes=10),
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

    if client_id not in AGENTS:
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
        "iss": "http://localhost:5000",
        "sub": client_id,
        "delegator": id_claims["sub"],
        "scope": scope.split(),
        "exp": datetime.utcnow() + timedelta(minutes=10),
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

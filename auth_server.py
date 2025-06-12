# === File: auth_server.py ===
import os
import secrets
from urllib.parse import urlencode

import requests
from flask import Flask, request, jsonify, redirect
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
JWT_SECRET = 'jwt-signing-secret'
AGENTS = {"agent-client-id": {"name": "CalendarAgent"}}
USERS = {"alice": "password123"}
ACTIVE_TOKENS = []
REVOKED_TOKENS = set()

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "test-client")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET", "secret")
REDIRECT_URI = "http://localhost:5000/callback"

PENDING_AUTH = {}
ID_TOKENS = {}

@app.route('/authorize')
def authorize():
    client_id = request.args.get('client_id')
    scope = request.args.get('scope', '')

    if client_id not in AGENTS:
        return "Agent not registered", 403

    state = secrets.token_urlsafe(16)
    PENDING_AUTH[state] = {
        "client_id": client_id,
        "scope": scope,
    }

    query = urlencode({
        "client_id": KEYCLOAK_CLIENT_ID,
        "response_type": "code",
        "scope": "openid",
        "redirect_uri": REDIRECT_URI,
        "state": state,
    })
    return redirect(
        f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth?{query}"
    )


@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code or state not in PENDING_AUTH:
        return "Invalid callback", 400

    pending = PENDING_AUTH.pop(state)
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
    if not id_token:
        return "No id token", 400

    claims = jwt.decode(id_token, options={"verify_signature": False})
    ID_TOKENS[claims["sub"]] = id_token

    delegation = {
        "iss": "http://localhost:5000",
        "sub": pending["client_id"],
        "delegator": claims["sub"],
        "scope": pending["scope"].split(),
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

    if delegation["delegator"] not in ID_TOKENS:
        return "User not authenticated", 403

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

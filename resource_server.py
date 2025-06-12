# === File: resource_server.py ===
from flask import Flask, request, jsonify
import jwt
from jwt import algorithms
from datetime import datetime
import requests
import json
import time

app = Flask(__name__)
INTROSPECT_URL = "http://localhost:5000/introspect"
DPOP_JTIS = set()

@app.route('/data')
def data():
    auth = request.headers.get("Authorization")
    dpop = request.headers.get("DPoP")
    if not auth or not auth.startswith("Bearer "):
        return "Missing Authorization header", 401
    if not dpop:
        return "Missing DPoP header", 401

    token = auth.split()[1]

    # Validate DPoP proof
    try:
        header = jwt.get_unverified_header(dpop)
        jwk = header.get("jwk")
        key = algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        payload = jwt.decode(dpop, key=key, algorithms=["RS256"])
    except Exception:
        return "Invalid DPoP proof", 401

    if payload.get("htm") != request.method:
        return "DPoP htm mismatch", 401
    if payload.get("htu") != request.base_url:
        return "DPoP htu mismatch", 401
    if abs(time.time() - payload.get("iat", 0)) > 300:
        return "DPoP iat expired", 401
    jti = payload.get("jti")
    if jti in DPOP_JTIS:
        return "DPoP replay", 401
    DPOP_JTIS.add(jti)

    r = requests.post(INTROSPECT_URL, data={"token": token})
    result = r.json()

    if not result.get("active"):
        return "Token invalid or revoked", 403

    return jsonify({
        "user": result['sub'],
        "agent": result['actor'],
        "scope": result['scope']
    })

if __name__ == '__main__':
    app.run(port=6000)

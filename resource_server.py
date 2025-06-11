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

if __name__ == '__main__':
    app.run(port=6000)

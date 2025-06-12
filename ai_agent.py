# === File: ai_agent.py ===
import requests
import secrets
import hashlib
import base64
import time
import uuid
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jwt import algorithms
import jwt

# PKCE setup
code_verifier = secrets.token_urlsafe(32)
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip("=")

print("=== STEP 1: Requesting Delegation Token with PKCE ===")
res = requests.get(
    "http://localhost:5000/authorize",
    params={
        "user": "alice",
        "client_id": "agent-client-id",
        "scope": "read:data write:data",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    },
)
delegation_token = res.json()["delegation_token"]
print("Delegation Token Received\n")

print("=== STEP 2: Exchanging for Access Token ===")
res = requests.post(
    "http://localhost:5000/token",
    data={"delegation_token": delegation_token, "code_verifier": code_verifier},
)
access_token = res.json()["access_token"]
print("Access Token Received\n")

print("=== STEP 3: Accessing Protected Resource with DPoP ===")

# Generate ephemeral key for DPoP
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_jwk = json.loads(algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))

def create_dpop_proof(url, method):
    payload = {
        "htu": url,
        "htm": method,
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"jwk": public_jwk, "typ": "dpop+jwt"},
    )

proof = create_dpop_proof("http://localhost:6000/data", "GET")
headers = {
    "Authorization": f"Bearer {access_token}",
    "DPoP": proof,
}
res = requests.get("http://localhost:6000/data", headers=headers)
print("Response:", res.json())

# Uncomment to test revocation:
# print("\n=== OPTIONAL: Revoking Token ===")
# res = requests.post("http://localhost:5000/revoke", data={"token": access_token})
# print(res.json())

# === How to Run ===
# Terminal 1: python auth_server.py
# Terminal 2: python resource_server.py
# Terminal 3: python ai_agent.py

# Optional:
# - Call /revoke to revoke access tokens.
# - /introspect is used internally by the Resource Server.
# - Extend to support refresh tokens or purpose binding.

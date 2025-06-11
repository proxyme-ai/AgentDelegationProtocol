# === File: ai_agent.py ===
import requests

print("=== STEP 1: Requesting Delegation Token ===")
res = requests.get("http://localhost:5000/authorize", params={
    "user": "alice",
    "client_id": "agent-client-id",
    "scope": "read:data write:data"
})
delegation_token = res.json()["delegation_token"]
print("Delegation Token Received\n")

print("=== STEP 2: Exchanging for Access Token ===")
res = requests.post("http://localhost:5000/token", data={
    "delegation_token": delegation_token
})
access_token = res.json()["access_token"]
print("Access Token Received\n")

print("=== STEP 3: Accessing Protected Resource ===")
headers = {"Authorization": f"Bearer {access_token}"}
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

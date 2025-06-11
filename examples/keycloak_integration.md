# Keycloak Integration Example

This guide shows how to adapt the Agent Delegation Protocol to use a Keycloak server for authentication. Keycloak handles the user login while your authorization server issues the delegation and access tokens expected by the resource server.

## Flow Overview
1. **User Authentication with Keycloak** – Redirect the user to Keycloak's login endpoint.
2. **Receive Authorization Code** – Keycloak sends the user back with an authorization code.
3. **Exchange Code for ID Token** – The auth server talks to Keycloak's token endpoint to obtain an ID token.
4. **Issue Delegation Token** – The auth server converts the Keycloak identity into a delegation token for the agent.
5. **Token Exchange** – The agent exchanges the delegation token for an access token just like in the base protocol.

## Authorization Server Changes
Below is a simplified extension of `auth_server.py` for Keycloak. Replace the placeholders with your Keycloak realm, client ID, and secret.

```python
# keycloak_auth_server.py
import os
import requests
from flask import Flask, request, redirect, jsonify
from urllib.parse import urlencode
from datetime import datetime, timedelta
import jwt

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL")  # e.g. http://localhost:8080
REALM = os.environ.get("KEYCLOAK_REALM", "master")
CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID")
CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"

app = Flask(__name__)
JWT_SECRET = "jwt-signing-secret"
```

```python
@app.route('/authorize')
def authorize():
    # Redirect the user to Keycloak for login
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid profile",
        "redirect_uri": REDIRECT_URI,
        "state": request.args.get('client_id'),
    })
    return redirect(f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth?{query}")
```

```python
@app.route('/callback')
def callback():
    # Keycloak returns an authorization code
    code = request.args['code']
    state = request.args['state']  # the agent client_id

    # Exchange the code for tokens
    token_res = requests.post(
        f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    token_res.raise_for_status()
    id_token = token_res.json()["id_token"]
    id_claims = jwt.decode(id_token, options={"verify_signature": False})

    # Issue delegation token for the agent
    delegation = {
        "iss": "http://localhost:5000",
        "sub": state,
        "delegator": id_claims['sub'],
        "scope": ["example:scope"],
        "exp": datetime.utcnow() + timedelta(minutes=10),
        "iat": datetime.utcnow(),
    }
    delegation_token = jwt.encode(delegation, JWT_SECRET, algorithm="HS256")
    return jsonify({"delegation_token": delegation_token})
```

Reuse the `/token`, `/revoke`, and `/introspect` endpoints from the existing `auth_server.py`.

## Running the Example
1. Install dependencies:
   ```bash
   pip install Flask PyJWT requests
   ```
2. Set your Keycloak environment variables:
   ```bash
   export KEYCLOAK_URL=http://localhost:8080
   export KEYCLOAK_REALM=myrealm
   export KEYCLOAK_CLIENT_ID=<client_id>
   export KEYCLOAK_CLIENT_SECRET=<client_secret>
   ```
3. Run the modified authorization server:
   ```bash
   python keycloak_auth_server.py
   ```
4. Start `resource_server.py` normally and use an agent like `ai_agent.py` to test the flow.

## GitHub Actions Deployment
The repository includes a workflow at `.github/workflows/keycloak.yml` that spins up a Keycloak container during CI. It waits for Keycloak to start and performs a simple smoke test by fetching the realm configuration.

This workflow demonstrates how you might automate integration tests against a running Keycloak server.


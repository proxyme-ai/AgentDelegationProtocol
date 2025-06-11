# Okta Integration Example

This example demonstrates how to adapt the Agent Delegation Protocol to use Okta as the identity provider. The idea is to let Okta handle user authentication and consent, while our local authorization server issues the delegation and access tokens expected by the resource server.

## Flow Overview
1. **User Authentication with Okta** – Redirect the user to Okta's authorization endpoint.
2. **Receive Authorization Code** – Okta redirects back with an authorization code.
3. **Exchange Code for ID Token** – The auth server contacts Okta's token endpoint and obtains an ID token and access token.
4. **Issue Delegation Token** – The auth server wraps the Okta identity into a delegation token for the agent.
5. **Token Exchange** – The agent exchanges the delegation token for an access token as usual.

## Authorization Server Changes
Below is a simplified example of extending `auth_server.py` to integrate with Okta. Replace the placeholders with your Okta domain, client ID, and client secret.

```python
# okta_auth_server.py
import os
import requests
from flask import Flask, request, redirect, jsonify
from urllib.parse import urlencode
from datetime import datetime, timedelta
import jwt

OKTA_DOMAIN = os.environ.get("OKTA_DOMAIN")  # e.g. https://dev-123456.okta.com
CLIENT_ID = os.environ.get("OKTA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("OKTA_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"

app = Flask(__name__)
JWT_SECRET = "jwt-signing-secret"
```

```python
@app.route('/authorize')
def authorize():
    # Step 1: redirect user to Okta for login and consent
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid profile",
        "redirect_uri": REDIRECT_URI,
        "state": request.args.get('client_id'),
    })
    return redirect(f"{OKTA_DOMAIN}/oauth2/default/v1/authorize?{query}")
```

```python
@app.route('/callback')
def callback():
    # Step 2: Okta returns an authorization code
    code = request.args['code']
    state = request.args['state']  # contains the agent client_id

    # Step 3: exchange code for tokens
    token_res = requests.post(
        f"{OKTA_DOMAIN}/oauth2/default/v1/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    token_res.raise_for_status()
    id_token = token_res.json()["id_token"]
    id_claims = jwt.decode(id_token, options={"verify_signature": False})

    # Step 4: issue delegation token for the agent
    delegation = {
        "iss": "http://localhost:5000",
        "sub": state,  # agent client_id from `state`
        "delegator": id_claims['sub'],
        "scope": ["example:scope"],
        "exp": datetime.utcnow() + timedelta(minutes=10),
        "iat": datetime.utcnow(),
    }
    delegation_token = jwt.encode(delegation, JWT_SECRET, algorithm="HS256")
    return jsonify({"delegation_token": delegation_token})
```

The remaining `/token`, `/revoke`, and `/introspect` endpoints can be reused from the existing `auth_server.py`.

## Running the Example
1. Install dependencies:
   ```bash
   pip install Flask PyJWT requests
   ```
2. Set your Okta environment variables:
   ```bash
   export OKTA_DOMAIN=https://dev-123456.okta.com
   export OKTA_CLIENT_ID=<client_id>
   export OKTA_CLIENT_SECRET=<client_secret>
   ```
3. Run the modified authorization server:
   ```bash
   python okta_auth_server.py
   ```
4. Start `resource_server.py` normally and use an agent similar to `ai_agent.py` to test the flow.

This example focuses on the integration points with Okta. In a real deployment you would also handle error cases, secure the secret values, and validate the ID token's signature using Okta's public keys.

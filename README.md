# Agent Delegation Protocol - Python Implementation

This repository implements a complete prototype of the **Agent Delegation Protocol** inspired by the paper _"Authenticated Delegation and Authorized AI Agents"_.

It demonstrates how to securely delegate authority from a human user to an AI agent using standard OAuth2-like patterns, JWT tokens, and Python-based microservices.

## 🧩 Components

- **Authorization Server (`auth_server.py`)**
  - Issues signed delegation tokens to AI agents on behalf of users.
  - Exposes token exchange and revocation endpoints.

- **Resource Server (`resource_server.py`)**
  - Validates access tokens and enforces scope- and identity-based access.

- **AI Agent (`ai_agent.py`)**
  - Simulates a delegated agent requesting access and consuming a protected resource.

## 🔧 Prerequisites

- Python 3.8+

Install required packages:
```bash
pip install Flask PyJWT requests
```

## 🚀 Running the System

Start each service in its own terminal:

### 1. Authorization Server
```bash
python auth_server.py
```

### 2. Resource Server
```bash
python resource_server.py
```

### 3. AI Agent (Client)
```bash
python ai_agent.py
```

## ✅ Expected Flow

- The AI agent requests a **delegation token** for a user (`alice`).
- It exchanges the delegation token for a signed **access token**.
- It then uses the access token to call a protected endpoint on the Resource Server.

## 🔒 Security Features

- Delegation token includes `user`, `agent`, `scope`, and `exp` (expiry).
- Access token includes both `sub` (user) and `actor` (agent).
- Token introspection and revocation endpoints included.

## 🔁 Revocation
To revoke an access token:
```bash
curl -X POST -d "token=<access_token>" http://localhost:5000/revoke
```
Subsequent attempts to use the token will be rejected.

## 📂 File Structure
```
.
├── auth_server.py         # Authorization + Delegation Token Issuer
├── resource_server.py     # Validates tokens and protects resources
├── ai_agent.py            # Client agent simulation
├── README.md              # This file
```

## 🧪 Extensions & TODO
- [ ] Add refresh token support
- [ ] Add UI for user consent
- [ ] Integrate PKCE & Proof-of-Possession (DPoP)

## 📚 Reference
- [Authenticated Delegation and Authorized AI Agents (arXiv)](https://arxiv.org/abs/2501.09674)
- [OAuth 2.0 Token Exchange (RFC 8693)](https://tools.ietf.org/html/rfc8693)

---
© 2025 – MIT License

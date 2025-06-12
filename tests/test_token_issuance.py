import jwt
import requests
import responses
import auth_server

JWT_SECRET = auth_server.JWT_SECRET
BASE_URL = 'http://localhost:5000'

def _mock_idp(rsps, sub="alice"):
    id_token = jwt.encode({"sub": sub}, "id-secret", algorithm="HS256")
    url = (
        f"{auth_server.KEYCLOAK_URL}/realms/{auth_server.KEYCLOAK_REALM}/protocol/openid-connect/token"
    )
    rsps.add(rsps.POST, url, json={"id_token": id_token})
    return id_token


@responses.activate
def test_authorize_returns_delegation_token():
    _mock_idp(responses)
    responses.add_passthru(BASE_URL)
    resp = requests.get(
        f"{BASE_URL}/authorize",
        params={"client_id": "agent-client-id", "scope": "read:data write:data"},
        allow_redirects=False,
    )
    assert resp.status_code == 302
    state = resp.headers["Location"].split("state=")[1]

    resp = requests.get(
        f"{BASE_URL}/callback", params={"code": "fake", "state": state}
    )
    assert resp.status_code == 200
    token = resp.json()["delegation_token"]
    decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert decoded["sub"] == "agent-client-id"
    assert decoded["delegator"] == "alice"


@responses.activate
def test_token_exchange_returns_access_token():
    _mock_idp(responses)
    responses.add_passthru(BASE_URL)
    r = requests.get(
        f"{BASE_URL}/authorize",
        params={"client_id": "agent-client-id", "scope": "read:data"},
        allow_redirects=False,
    )
    state = r.headers["Location"].split("state=")[1]
    r = requests.get(f"{BASE_URL}/callback", params={"code": "fake", "state": state})
    delegation_token = r.json()["delegation_token"]

    r = requests.post(f"{BASE_URL}/token", data={"delegation_token": delegation_token})
    assert r.status_code == 200
    access_token = r.json()["access_token"]
    decoded = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
    assert decoded["sub"] == "alice"
    assert decoded["actor"] == "agent-client-id"

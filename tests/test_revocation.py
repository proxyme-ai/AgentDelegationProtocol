import requests
import responses
import jwt
import auth_server

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

def _mock_idp(rsps):
    id_token = jwt.encode({"sub": "alice"}, "id-secret", algorithm="HS256")
    url = f"{auth_server.KEYCLOAK_URL}/realms/{auth_server.KEYCLOAK_REALM}/protocol/openid-connect/token"
    rsps.add(rsps.POST, url, json={"id_token": id_token})


def _get_access_token():
    with responses.RequestsMock() as rsps:
        _mock_idp(rsps)
        rsps.add_passthru(BASE_AUTH)
        rsps.add_passthru(BASE_RS)
        r = requests.get(
            f"{BASE_AUTH}/authorize",
            params={"client_id": "agent-client-id", "scope": "read:data"},
            allow_redirects=False,
        )
        state = r.headers["Location"].split("state=")[1]
        r = requests.get(f"{BASE_AUTH}/callback", params={"code": "fake", "state": state})
        delegation = r.json()["delegation_token"]

        r = requests.post(f"{BASE_AUTH}/token", data={"delegation_token": delegation})
        return r.json()["access_token"]

def test_revoked_token_rejected():
    token = _get_access_token()
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200

    r = requests.post(f'{BASE_AUTH}/revoke', data={'token': token})
    assert r.status_code == 200

    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 403

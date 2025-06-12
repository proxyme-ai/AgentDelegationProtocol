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
    return id_token


@responses.activate
def test_full_delegation_flow():
    _mock_idp(responses)
    responses.add_passthru(BASE_AUTH)
    responses.add_passthru(BASE_RS)
    r = requests.get(
        f"{BASE_AUTH}/authorize",
        params={"client_id": "agent-client-id", "scope": "read:data"},
        allow_redirects=False,
    )
    assert r.status_code == 302
    state = r.headers["Location"].split("state=")[1]

    r = requests.get(f"{BASE_AUTH}/callback", params={"code": "fake", "state": state})
    assert r.status_code == 200
    delegation = r.json()["delegation_token"]

    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation})
    assert r.status_code == 200
    access_token = r.json()['access_token']

    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body['user'] == 'alice'
    assert body['agent'] == 'agent-client-id'

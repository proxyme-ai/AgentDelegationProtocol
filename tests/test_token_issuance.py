import jwt
import requests
import auth_server
from tests.utils import generate_pkce_pair

JWT_SECRET = auth_server.JWT_SECRET
BASE_URL = 'http://localhost:5000'

def test_authorize_returns_delegation_token():
    verifier, challenge = generate_pkce_pair()
    resp = requests.get(
        f'{BASE_URL}/authorize',
        params={
            'user': 'alice',
            'client_id': 'agent-client-id',
            'scope': 'read:data write:data',
            'code_challenge': challenge,
            'code_challenge_method': 'S256'
        }
    )
    assert resp.status_code == 200
    token = resp.json()['delegation_token']
    decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    assert decoded['sub'] == 'agent-client-id'
    assert decoded['delegator'] == 'alice'


def test_token_exchange_returns_access_token():
    # obtain delegation token first
    verifier, challenge = generate_pkce_pair()
    r = requests.get(
        f'{BASE_URL}/authorize',
        params={
            'user': 'alice',
            'client_id': 'agent-client-id',
            'scope': 'read:data',
            'code_challenge': challenge,
            'code_challenge_method': 'S256'
        }
    )
    delegation_token = r.json()['delegation_token']

    r = requests.post(
        f'{BASE_URL}/token',
        data={'delegation_token': delegation_token, 'code_verifier': verifier}
    )
    assert r.status_code == 200
    access_token = r.json()['access_token']
    decoded = jwt.decode(access_token, JWT_SECRET, algorithms=['HS256'])
    assert decoded['sub'] == 'alice'
    assert decoded['actor'] == 'agent-client-id'

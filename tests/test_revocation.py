import requests
from tests.utils import generate_pkce_pair

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

def _get_access_token():
    verifier, challenge = generate_pkce_pair()
    r = requests.get(
        f'{BASE_AUTH}/authorize',
        params={
            'user': 'alice',
            'client_id': 'agent-client-id',
            'scope': 'read:data',
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
        },
    )
    delegation = r.json()['delegation_token']
    r = requests.post(
        f'{BASE_AUTH}/token',
        data={'delegation_token': delegation, 'code_verifier': verifier},
    )
    return r.json()['access_token']

def test_revoked_token_rejected(dpop_key):
    token = _get_access_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'DPoP': dpop_key.proof(f'{BASE_RS}/data', 'GET')
    }
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200

    r = requests.post(f'{BASE_AUTH}/revoke', data={'token': token})
    assert r.status_code == 200

    headers['DPoP'] = dpop_key.proof(f'{BASE_RS}/data', 'GET')
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 403

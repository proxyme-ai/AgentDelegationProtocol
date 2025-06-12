import requests
from tests.utils import generate_pkce_pair

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'


def test_invalid_code_verifier():
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
    token = r.json()['delegation_token']
    # send wrong verifier
    r = requests.post(
        f'{BASE_AUTH}/token',
        data={'delegation_token': token, 'code_verifier': 'wrong'}
    )
    assert r.status_code == 403


def test_missing_dpop_header(dpop_key):
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
    token = r.json()['delegation_token']
    r = requests.post(
        f'{BASE_AUTH}/token',
        data={'delegation_token': token, 'code_verifier': verifier}
    )
    access = r.json()['access_token']
    headers = {'Authorization': f'Bearer {access}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 401


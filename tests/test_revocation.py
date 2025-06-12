import requests

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

def _get_access_token():
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    delegation = r.json()['delegation_token']
    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation})
    return r.json()['access_token']

def test_revoked_token_rejected():
    token = _get_access_token()
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200

    r = requests.post(f'{BASE_AUTH}/revoke', data={'token': token})
    assert r.status_code == 200

    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 403

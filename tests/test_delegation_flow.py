import requests

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

def test_full_delegation_flow():
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    assert r.status_code == 200
    delegation = r.json()['delegation_token']

    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation})
    assert r.status_code == 200
    access_token = r.json()['access_token']

    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body['user'] == 'alice'
    assert body['agent'] == 'agent-client-id'

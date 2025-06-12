import time
import requests

BASE_AUTH = 'http://localhost:5000'
BASE_RESOURCE = 'http://localhost:6000'

def wait_for(url, timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = requests.get(url)
            if r.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def test_delegation_flow():
    assert wait_for(f"{BASE_AUTH}/authorize")

    r = requests.get(f"{BASE_AUTH}/authorize", params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    assert r.status_code == 200
    delegation = r.json()['delegation_token']

    r = requests.post(f"{BASE_AUTH}/token", data={'delegation_token': delegation})
    assert r.status_code == 200
    token = r.json()['access_token']

    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f"{BASE_RESOURCE}/data", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data['user'] == 'alice'
    assert data['agent'] == 'agent-client-id'

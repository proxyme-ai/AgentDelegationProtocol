import requests

BASE_URL = 'http://localhost:5000'


def test_register_new_client():
    resp = requests.post(f'{BASE_URL}/register', json={
        'client_id': 'test-agent',
        'name': 'TestAgent'
    })
    assert resp.status_code == 201

    # Newly registered agent should be authorized
    r = requests.get(f'{BASE_URL}/authorize', params={
        'user': 'alice',
        'client_id': 'test-agent',
        'scope': 'read:data'
    })
    assert r.status_code == 200


def test_register_duplicate_client_fails():
    resp = requests.post(f'{BASE_URL}/register', json={
        'client_id': 'agent-client-id',
        'name': 'CalendarAgent'
    })
    assert resp.status_code == 400


def test_authorize_unregistered_client_fails():
    r = requests.get(f'{BASE_URL}/authorize', params={
        'user': 'alice',
        'client_id': 'unknown-agent',
        'scope': 'read:data'
    })
    assert r.status_code == 403

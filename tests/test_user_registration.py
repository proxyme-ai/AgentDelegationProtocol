import requests

BASE_URL = 'http://localhost:5000'


def test_register_new_user():
    resp = requests.post(f'{BASE_URL}/register_user', json={
        'username': 'bob',
        'password': 'secret'
    })
    assert resp.status_code == 201

    r = requests.get(f'{BASE_URL}/authorize', params={
        'user': 'bob',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    assert r.status_code == 200


def test_register_duplicate_user_fails():
    resp = requests.post(f'{BASE_URL}/register_user', json={
        'username': 'alice',
        'password': 'password123'
    })
    assert resp.status_code == 400

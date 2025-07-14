import requests
import jwt
import time
from datetime import datetime, timedelta
import auth_server

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'
JWT_SECRET = auth_server.JWT_SECRET

def test_expired_delegation_token():
    """Test that expired delegation tokens are rejected"""
    # Create an expired delegation token
    expired_delegation = {
        "iss": "http://localhost:5000",
        "sub": "agent-client-id",
        "delegator": "alice",
        "scope": ["read:data"],
        "exp": datetime.utcnow() - timedelta(minutes=1),  # Expired
        "iat": datetime.utcnow() - timedelta(minutes=2),
    }
    expired_token = jwt.encode(expired_delegation, JWT_SECRET, algorithm="HS256")
    
    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': expired_token})
    assert r.status_code == 403
    assert "expired" in r.text.lower()

def test_invalid_delegation_token():
    """Test that invalid delegation tokens are rejected"""
    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': 'invalid-token'})
    assert r.status_code == 403
    assert "invalid" in r.text.lower()

def test_token_revocation():
    """Test token revocation functionality"""
    # Get valid tokens
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    delegation_token = r.json()['delegation_token']
    
    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation_token})
    access_token = r.json()['access_token']
    
    # Verify token works
    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200
    
    # Revoke token
    r = requests.post(f'{BASE_AUTH}/revoke', data={'token': access_token})
    assert r.status_code == 200
    
    # Verify token no longer works
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 403

def test_scope_enforcement():
    """Test that scope is properly enforced"""
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data write:data'
    })
    delegation_token = r.json()['delegation_token']
    
    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation_token})
    access_token = r.json()['access_token']
    
    # Verify scope is included in response
    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert 'read:data' in data['scope']
    assert 'write:data' in data['scope']

def test_unauthorized_agent():
    """Test that unregistered agents are rejected"""
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'unregistered-agent',
        'scope': 'read:data'
    })
    assert r.status_code == 403

def test_unauthorized_user():
    """Test that unregistered users are rejected"""
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'unknown-user',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    assert r.status_code == 403

def test_missing_authorization_header():
    """Test that requests without authorization header are rejected"""
    r = requests.get(f'{BASE_RS}/data')
    assert r.status_code == 401

def test_malformed_authorization_header():
    """Test that malformed authorization headers are rejected"""
    headers = {'Authorization': 'InvalidFormat token'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 401
import requests
import hashlib
import base64
import secrets

BASE_AUTH = 'http://localhost:5000'

def test_pkce_s256_flow():
    """Test PKCE with S256 code challenge method"""
    # Generate code verifier and challenge
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    # Get delegation token with PKCE
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    })
    assert r.status_code == 200
    delegation_token = r.json()['delegation_token']
    
    # Exchange with correct verifier
    r = requests.post(f'{BASE_AUTH}/token', data={
        'delegation_token': delegation_token,
        'code_verifier': code_verifier
    })
    assert r.status_code == 200
    assert 'access_token' in r.json()

def test_pkce_s256_wrong_verifier():
    """Test PKCE with wrong code verifier"""
    # Generate code verifier and challenge
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    # Get delegation token with PKCE
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    })
    delegation_token = r.json()['delegation_token']
    
    # Exchange with wrong verifier
    wrong_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    r = requests.post(f'{BASE_AUTH}/token', data={
        'delegation_token': delegation_token,
        'code_verifier': wrong_verifier
    })
    assert r.status_code == 403
    assert "invalid" in r.text.lower()

def test_pkce_plain_flow():
    """Test PKCE with plain code challenge method"""
    code_verifier = "test-verifier-123"
    
    # Get delegation token with plain PKCE
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data',
        'code_challenge': code_verifier,
        'code_challenge_method': 'plain'
    })
    delegation_token = r.json()['delegation_token']
    
    # Exchange with correct verifier
    r = requests.post(f'{BASE_AUTH}/token', data={
        'delegation_token': delegation_token,
        'code_verifier': code_verifier
    })
    assert r.status_code == 200
    assert 'access_token' in r.json()
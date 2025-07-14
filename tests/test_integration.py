import requests
import threading
import time
import subprocess
import sys
import os

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

def test_end_to_end_flow():
    """Test complete end-to-end delegation flow"""
    # Step 1: Register a new agent
    agent_data = {
        'client_id': 'test-integration-agent',
        'name': 'Integration Test Agent'
    }
    r = requests.post(f'{BASE_AUTH}/register', json=agent_data)
    assert r.status_code == 201
    
    # Step 2: Register a new user
    user_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    r = requests.post(f'{BASE_AUTH}/register_user', json=user_data)
    assert r.status_code == 201
    
    # Step 3: Get delegation token
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'testuser',
        'client_id': 'test-integration-agent',
        'scope': 'read:data write:data'
    })
    assert r.status_code == 200
    delegation_token = r.json()['delegation_token']
    
    # Step 4: Exchange for access token
    r = requests.post(f'{BASE_AUTH}/token', data={
        'delegation_token': delegation_token
    })
    assert r.status_code == 200
    access_token = r.json()['access_token']
    
    # Step 5: Access protected resource
    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data['user'] == 'testuser'
    assert data['agent'] == 'test-integration-agent'
    assert 'read:data' in data['scope']
    assert 'write:data' in data['scope']
    
    # Step 6: Test token introspection
    r = requests.post(f'{BASE_AUTH}/introspect', data={'token': access_token})
    assert r.status_code == 200
    introspect_data = r.json()
    assert introspect_data['active'] is True
    assert introspect_data['sub'] == 'testuser'
    assert introspect_data['actor'] == 'test-integration-agent'
    
    # Step 7: Revoke token
    r = requests.post(f'{BASE_AUTH}/revoke', data={'token': access_token})
    assert r.status_code == 200
    
    # Step 8: Verify token is revoked
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 403

def test_multiple_concurrent_agents():
    """Test multiple agents accessing resources concurrently"""
    agents = []
    tokens = []
    
    # Register multiple agents
    for i in range(3):
        agent_data = {
            'client_id': f'concurrent-agent-{i}',
            'name': f'Concurrent Agent {i}'
        }
        r = requests.post(f'{BASE_AUTH}/register', json=agent_data)
        assert r.status_code == 201
        agents.append(f'concurrent-agent-{i}')
    
    # Get tokens for all agents
    for agent_id in agents:
        r = requests.get(f'{BASE_AUTH}/authorize', params={
            'user': 'alice',
            'client_id': agent_id,
            'scope': 'read:data'
        })
        delegation_token = r.json()['delegation_token']
        
        r = requests.post(f'{BASE_AUTH}/token', data={
            'delegation_token': delegation_token
        })
        access_token = r.json()['access_token']
        tokens.append(access_token)
    
    # Test concurrent access
    def access_resource(token, results, index):
        headers = {'Authorization': f'Bearer {token}'}
        r = requests.get(f'{BASE_RS}/data', headers=headers)
        results[index] = r.status_code == 200
    
    results = [False] * len(tokens)
    threads = []
    
    for i, token in enumerate(tokens):
        thread = threading.Thread(target=access_resource, args=(token, results, i))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # All requests should succeed
    assert all(results)

def test_scope_limitation():
    """Test that agents can only access resources within their scope"""
    # This test would be more meaningful with multiple resource endpoints
    # For now, we test that the scope is properly returned
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data'  # Limited scope
    })
    delegation_token = r.json()['delegation_token']
    
    r = requests.post(f'{BASE_AUTH}/token', data={
        'delegation_token': delegation_token
    })
    access_token = r.json()['access_token']
    
    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(f'{BASE_RS}/data', headers=headers)
    assert r.status_code == 200
    data = r.json()
    
    # Should only have read access, not write
    assert 'read:data' in data['scope']
    assert 'write:data' not in data['scope']
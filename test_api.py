#!/usr/bin/env python3
"""
Test script for the enhanced API endpoints.
Tests all the new functionality added to the backend.
"""

import requests
import json
import time
from config import config

# Server URLs
AUTH_URL = config.auth_server_url
RESOURCE_URL = config.resource_server_url
API_URL = f"http://localhost:{config.frontend_port}"

def test_health_endpoints():
    """Test health endpoints for all servers."""
    print("Testing health endpoints...")
    
    try:
        # Test auth server health
        response = requests.get(f"{AUTH_URL}/health", timeout=5)
        print(f"Auth server health: {response.status_code} - {response.json()}")
        
        # Test resource server health
        response = requests.get(f"{RESOURCE_URL}/health", timeout=5)
        print(f"Resource server health: {response.status_code} - {response.json()}")
        
        # Test API server health
        response = requests.get(f"{API_URL}/api/status", timeout=5)
        print(f"API server status: {response.status_code} - {response.json()}")
        
    except requests.RequestException as e:
        print(f"Health check failed: {str(e)}")
        return False
    
    return True

def test_agent_management():
    """Test agent management endpoints."""
    print("\nTesting agent management...")
    
    try:
        # Create a test agent
        agent_data = {
            "name": "Test Agent",
            "description": "Agent for testing purposes",
            "scopes": ["read:data", "write:data"]
        }
        
        response = requests.post(f"{API_URL}/api/agents", json=agent_data)
        print(f"Create agent: {response.status_code} - {response.json()}")
        
        if response.status_code == 201:
            agent_id = response.json()['agent']['id']
            
            # List agents
            response = requests.get(f"{API_URL}/api/agents")
            print(f"List agents: {response.status_code} - Found {len(response.json()['agents'])} agents")
            
            # Get specific agent
            response = requests.get(f"{API_URL}/api/agents/{agent_id}")
            print(f"Get agent: {response.status_code} - {response.json()['name']}")
            
            # Update agent
            update_data = {"description": "Updated test agent"}
            response = requests.put(f"{API_URL}/api/agents/{agent_id}", json=update_data)
            print(f"Update agent: {response.status_code}")
            
            return agent_id
        
    except requests.RequestException as e:
        print(f"Agent management test failed: {str(e)}")
        return None

def test_delegation_management(agent_id):
    """Test delegation management endpoints."""
    print("\nTesting delegation management...")
    
    try:
        # Create a delegation
        delegation_data = {
            "agent_id": agent_id,
            "user_id": "alice",
            "scopes": ["read:data"]
        }
        
        response = requests.post(f"{API_URL}/api/delegations", json=delegation_data)
        print(f"Create delegation: {response.status_code} - {response.json()}")
        
        if response.status_code == 201:
            delegation_id = response.json()['delegation']['id']
            
            # List delegations
            response = requests.get(f"{API_URL}/api/delegations")
            print(f"List delegations: {response.status_code} - Found {len(response.json()['delegations'])} delegations")
            
            # Approve delegation
            response = requests.put(f"{API_URL}/api/delegations/{delegation_id}/approve")
            print(f"Approve delegation: {response.status_code}")
            
            return delegation_id
        
    except requests.RequestException as e:
        print(f"Delegation management test failed: {str(e)}")
        return None

def test_token_management():
    """Test token management endpoints."""
    print("\nTesting token management...")
    
    try:
        # List active tokens
        response = requests.get(f"{API_URL}/api/tokens/active")
        print(f"List active tokens: {response.status_code} - Found {len(response.json()['active_tokens'])} tokens")
        
    except requests.RequestException as e:
        print(f"Token management test failed: {str(e)}")

def test_demo_flow():
    """Test the demo flow endpoint."""
    print("\nTesting demo flow...")
    
    try:
        response = requests.post(f"{API_URL}/api/demo/run")
        print(f"Demo flow: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Demo completed - Delegation ID: {result['demo_result']['delegation_id']}")
            return True
        
    except requests.RequestException as e:
        print(f"Demo flow test failed: {str(e)}")
        return False

def test_simulation():
    """Test simulation endpoints."""
    print("\nTesting simulation...")
    
    try:
        # List scenarios
        response = requests.get(f"{API_URL}/api/simulate/scenarios")
        print(f"List scenarios: {response.status_code} - Found {len(response.json()['scenarios'])} scenarios")
        
        # Run happy path simulation
        response = requests.post(f"{API_URL}/api/simulate/happy_path")
        print(f"Happy path simulation: {response.status_code}")
        
    except requests.RequestException as e:
        print(f"Simulation test failed: {str(e)}")

def main():
    """Run all tests."""
    print("Starting API tests...")
    print("=" * 50)
    
    # Wait for servers to be ready
    print("Waiting for servers to start...")
    time.sleep(3)
    
    # Test health endpoints first
    if not test_health_endpoints():
        print("Health checks failed. Make sure all servers are running.")
        return
    
    # Test agent management
    agent_id = test_agent_management()
    if not agent_id:
        print("Agent management tests failed.")
        return
    
    # Test delegation management
    delegation_id = test_delegation_management(agent_id)
    
    # Test token management
    test_token_management()
    
    # Test demo flow
    test_demo_flow()
    
    # Test simulation
    test_simulation()
    
    print("\n" + "=" * 50)
    print("API tests completed!")

if __name__ == '__main__':
    main()
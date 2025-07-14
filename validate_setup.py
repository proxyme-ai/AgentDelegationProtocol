#!/usr/bin/env python3
"""
Validation script to ensure the backend setup is working correctly.
Tests imports, configuration, and basic functionality.
"""

import sys
import json
from datetime import datetime

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    
    try:
        from config import config
        print("✓ Config module imported successfully")
        
        from logging_config import get_logger
        print("✓ Logging config imported successfully")
        
        from auth_server import app as auth_app
        print("✓ Auth server imported successfully")
        
        from resource_server import app as resource_app
        print("✓ Resource server imported successfully")
        
        from api_server import app as api_app
        print("✓ API server imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {str(e)}")
        return False

def test_configuration():
    """Test configuration values."""
    print("\nTesting configuration...")
    
    try:
        from config import config
        
        print(f"✓ JWT Secret length: {len(config.jwt_secret)} characters")
        print(f"✓ Auth server: {config.auth_server_url}")
        print(f"✓ Resource server: {config.resource_server_url}")
        print(f"✓ API server port: {config.frontend_port}")
        print(f"✓ Access token expiry: {config.access_token_expiry} minutes")
        print(f"✓ Delegation token expiry: {config.delegation_token_expiry} minutes")
        
        if len(config.jwt_secret) < 32:
            print("⚠ Warning: JWT secret should be at least 32 characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        return False

def test_data_files():
    """Test data file access."""
    print("\nTesting data files...")
    
    try:
        from config import config
        import os
        
        # Check if files exist
        agents_exists = os.path.exists(config.agents_file)
        users_exists = os.path.exists(config.users_file)
        
        print(f"✓ Agents file ({config.agents_file}): {'exists' if agents_exists else 'will be created'}")
        print(f"✓ Users file ({config.users_file}): {'exists' if users_exists else 'will be created'}")
        
        # Test loading data
        if agents_exists:
            with open(config.agents_file) as f:
                agents = json.load(f)
                print(f"✓ Loaded {len(agents)} agents")
        
        if users_exists:
            with open(config.users_file) as f:
                users = json.load(f)
                print(f"✓ Loaded {len(users)} users")
        
        return True
        
    except Exception as e:
        print(f"✗ Data file test failed: {str(e)}")
        return False

def test_api_server_functionality():
    """Test basic API server functionality."""
    print("\nTesting API server functionality...")
    
    try:
        from api_server import AGENTS, Agent
        
        # Test creating an agent
        test_agent = Agent(
            id="test-agent",
            name="Test Agent",
            description="Test agent for validation"
        )
        
        print(f"✓ Agent creation works: {test_agent.name}")
        print(f"✓ Agent created at: {test_agent.created_at}")
        print(f"✓ Agent status: {test_agent.status}")
        
        return True
        
    except Exception as e:
        print(f"✗ API server functionality test failed: {str(e)}")
        return False

def test_jwt_functionality():
    """Test JWT token creation and validation."""
    print("\nTesting JWT functionality...")
    
    try:
        import jwt
        from config import config
        from datetime import datetime, timedelta
        
        # Create a test token
        test_claims = {
            "iss": config.auth_server_url,
            "sub": "test-user",
            "exp": datetime.utcnow() + timedelta(minutes=5),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(test_claims, config.jwt_secret, algorithm=config.jwt_algorithm)
        print("✓ JWT token creation works")
        
        # Decode the token
        decoded = jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algorithm])
        print(f"✓ JWT token validation works: {decoded['sub']}")
        
        return True
        
    except Exception as e:
        print(f"✗ JWT functionality test failed: {str(e)}")
        return False

def main():
    """Run all validation tests."""
    print("Agent Delegation Protocol - Backend Validation")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_data_files,
        test_api_server_functionality,
        test_jwt_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Backend setup is working correctly.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start servers: python run_servers.py")
        print("3. Test API endpoints: python test_api.py")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
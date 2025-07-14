import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

def test_token_generation_performance():
    """Test token generation performance under load"""
    def generate_token():
        start_time = time.time()
        r = requests.get(f'{BASE_AUTH}/authorize', params={
            'user': 'alice',
            'client_id': 'agent-client-id',
            'scope': 'read:data'
        })
        if r.status_code == 200:
            delegation_token = r.json()['delegation_token']
            r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation_token})
            if r.status_code == 200:
                return time.time() - start_time
        return None
    
    # Test with multiple concurrent requests
    num_requests = 50
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(generate_token) for _ in range(num_requests)]
        response_times = []
        
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                response_times.append(result)
    
    # Analyze performance
    assert len(response_times) >= num_requests * 0.9  # At least 90% success rate
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    
    # Performance assertions (adjust based on your requirements)
    assert avg_time < 1.0, f"Average response time too high: {avg_time:.3f}s"
    assert max_time < 2.0, f"Maximum response time too high: {max_time:.3f}s"
    
    print(f"Performance metrics:")
    print(f"  Requests: {len(response_times)}/{num_requests}")
    print(f"  Average time: {avg_time:.3f}s")
    print(f"  Max time: {max_time:.3f}s")
    print(f"  Min time: {min(response_times):.3f}s")

def test_resource_access_performance():
    """Test resource access performance"""
    # Get a valid token first
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    delegation_token = r.json()['delegation_token']
    
    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation_token})
    access_token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    
    def access_resource():
        start_time = time.time()
        r = requests.get(f'{BASE_RS}/data', headers=headers)
        if r.status_code == 200:
            return time.time() - start_time
        return None
    
    # Test concurrent resource access
    num_requests = 100
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(access_resource) for _ in range(num_requests)]
        response_times = []
        
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                response_times.append(result)
    
    # Analyze performance
    assert len(response_times) >= num_requests * 0.95  # At least 95% success rate
    avg_time = statistics.mean(response_times)
    
    # Resource access should be very fast
    assert avg_time < 0.1, f"Average resource access time too high: {avg_time:.3f}s"
    
    print(f"Resource access performance:")
    print(f"  Requests: {len(response_times)}/{num_requests}")
    print(f"  Average time: {avg_time:.3f}s")

def test_token_introspection_performance():
    """Test token introspection performance"""
    # Get a valid token
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    delegation_token = r.json()['delegation_token']
    
    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation_token})
    access_token = r.json()['access_token']
    
    def introspect_token():
        start_time = time.time()
        r = requests.post(f'{BASE_AUTH}/introspect', data={'token': access_token})
        if r.status_code == 200:
            return time.time() - start_time
        return None
    
    # Test introspection performance
    num_requests = 50
    response_times = []
    
    for _ in range(num_requests):
        result = introspect_token()
        if result is not None:
            response_times.append(result)
    
    avg_time = statistics.mean(response_times)
    assert avg_time < 0.05, f"Token introspection too slow: {avg_time:.3f}s"
    
    print(f"Token introspection performance:")
    print(f"  Average time: {avg_time:.3f}s")

def test_memory_usage():
    """Basic memory usage test"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Generate many tokens to test memory usage
    tokens = []
    for i in range(100):
        r = requests.get(f'{BASE_AUTH}/authorize', params={
            'user': 'alice',
            'client_id': 'agent-client-id',
            'scope': 'read:data'
        })
        if r.status_code == 200:
            delegation_token = r.json()['delegation_token']
            r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation_token})
            if r.status_code == 200:
                tokens.append(r.json()['access_token'])
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f"Memory usage:")
    print(f"  Initial: {initial_memory:.1f} MB")
    print(f"  Final: {final_memory:.1f} MB")
    print(f"  Increase: {memory_increase:.1f} MB")
    
    # Memory increase should be reasonable
    assert memory_increase < 50, f"Memory usage too high: {memory_increase:.1f} MB"
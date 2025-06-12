import requests
import demo_frontend
from tests.utils import start_server


def test_frontend_demo():
    server = start_server(demo_frontend.app, port=7000)
    resp = requests.get('http://localhost:7000/')
    flow = requests.get('http://localhost:7000/flow')
    server.shutdown()
    assert resp.status_code == 200
    assert 'Delegation Protocol Demo' in resp.text
    assert flow.status_code == 200
    assert 'alice' in flow.text

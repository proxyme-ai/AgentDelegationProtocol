import requests
import demo_frontend
from tests.utils import start_server


def test_frontend_demo():
    server = start_server(demo_frontend.app, port=7000)
    resp = requests.get('http://localhost:7000/')
    run = requests.get('http://localhost:7000/run')
    server.shutdown()
    assert resp.status_code == 200
    assert 'Start Demo' in resp.text
    assert run.status_code == 200
    assert run.json()['data']['user'] == 'alice'

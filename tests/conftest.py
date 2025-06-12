import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
import auth_server
import resource_server
from tests.utils import start_server

@pytest.fixture(scope='session', autouse=True)
def servers():
    # start auth and resource servers for tests
    auth_srv = start_server(auth_server.app, port=5000)
    res_srv = start_server(resource_server.app, port=6000)
    yield
    res_srv.shutdown()
    auth_srv.shutdown()

@pytest.fixture(autouse=True)
def reset_state():
    auth_server.ACTIVE_TOKENS.clear()
    auth_server.REVOKED_TOKENS.clear()

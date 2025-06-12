import os
import sys
import json
import tempfile

# Create a temporary agents file and set the environment variable BEFORE
# importing the auth_server module so that it loads the correct file.
temp_agents_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
json.dump({"agent-client-id": {"name": "CalendarAgent"}}, temp_agents_file)
temp_agents_file.close()
os.environ["AGENTS_FILE"] = temp_agents_file.name

# Temporary users file so tests can register and authenticate users
temp_users_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
json.dump({"alice": "password123"}, temp_users_file)
temp_users_file.close()
os.environ["USERS_FILE"] = temp_users_file.name

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
    os.remove(temp_agents_file.name)
    os.remove(temp_users_file.name)

@pytest.fixture(autouse=True)
def reset_state():
    auth_server.ACTIVE_TOKENS.clear()
    auth_server.REVOKED_TOKENS.clear()
    # reload agents from persistent file to ensure isolation
    auth_server.AGENTS = auth_server.load_agents()
    auth_server.USERS = auth_server.load_users()

import os

# Flag controlling whether Keycloak is used for user authentication
USE_KEYCLOAK = os.environ.get("USE_KEYCLOAK", "false").lower() == "true"

KEYCLOAK_URL = os.environ.get("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "test-client")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET", "secret")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:5000/callback")

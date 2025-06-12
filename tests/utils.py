import threading
import time
from werkzeug.serving import make_server
import secrets
import hashlib
import base64
import json
import uuid
import jwt
from jwt import algorithms
from cryptography.hazmat.primitives.asymmetric import rsa

class ServerThread(threading.Thread):
    def __init__(self, app, host='localhost', port=0):
        super().__init__()
        self.server = make_server(host, port, app)
        self.port = self.server.server_port
        self.daemon = True

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
        self.join()

def start_server(app, port):
    server = ServerThread(app, port=port)
    server.start()
    # Wait briefly for server to start
    time.sleep(0.2)
    return server


def generate_pkce_pair():
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")
    return verifier, challenge


class DPoPKey:
    def __init__(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_jwk = json.loads(algorithms.RSAAlgorithm.to_jwk(self.private_key.public_key()))

    def proof(self, url, method="GET"):
        payload = {
            "htu": url,
            "htm": method,
            "iat": int(time.time()),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(
            payload,
            self.private_key,
            algorithm="RS256",
            headers={"jwk": self.public_jwk, "typ": "dpop+jwt"},
        )

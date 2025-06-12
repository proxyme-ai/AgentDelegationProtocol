import threading
import time
from werkzeug.serving import make_server

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

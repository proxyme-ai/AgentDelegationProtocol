from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

TEMPLATE = """<!doctype html>
<html lang='en'>
  <head>
    <meta charset='utf-8'/>
    <title>Delegation Protocol Demo</title>
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'>
  </head>
  <body class='container py-4'>
    <h1 class='mb-4'>Delegation Protocol Demo</h1>
    <button id='start' class='btn btn-primary mb-3'>Start Demo</button>
    <pre id='log' class='bg-light p-3'></pre>
    <script>
      function runDemo() {
        fetch('/run')
          .then(r => r.json())
          .then(data => {
            document.getElementById('log').textContent = JSON.stringify(data, null, 2);
          });
      }
      document.getElementById('start').addEventListener('click', runDemo);
    </script>
  </body>
</html>"""

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

@app.route('/')
def demo():
    return render_template_string(TEMPLATE)


@app.route('/run')
def run_flow():
    r = requests.get(f"{BASE_AUTH}/authorize", params={
        "user": "alice",
        "client_id": "agent-client-id",
        "scope": "read:data",
    })
    r.raise_for_status()
    delegation = r.json()["delegation_token"]

    r = requests.post(f"{BASE_AUTH}/token", data={"delegation_token": delegation})
    r.raise_for_status()
    access = r.json()["access_token"]

    r = requests.get(f"{BASE_RS}/data", headers={"Authorization": f"Bearer {access}"})
    r.raise_for_status()
    body = r.json()

    return jsonify({"delegation": delegation, "access": access, "data": body})

if __name__ == '__main__':
    app.run(port=7000)

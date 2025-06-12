from flask import Flask, render_template_string
import requests
import json

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
    <h2 class='h5'>Step 1: Delegation Token</h2>
    <pre class='bg-light p-3'>{{ delegation }}</pre>
    <h2 class='h5'>Step 2: Access Token</h2>
    <pre class='bg-light p-3'>{{ access }}</pre>
    <h2 class='h5'>Step 3: Resource Response</h2>
    <pre class='bg-light p-3'>{{ data }}</pre>
  </body>
</html>"""

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

@app.route('/')
def demo():
    r = requests.get(f'{BASE_AUTH}/authorize', params={
        'user': 'alice',
        'client_id': 'agent-client-id',
        'scope': 'read:data'
    })
    r.raise_for_status()
    delegation = r.json()['delegation_token']

    r = requests.post(f'{BASE_AUTH}/token', data={'delegation_token': delegation})
    r.raise_for_status()
    access = r.json()['access_token']

    r = requests.get(f'{BASE_RS}/data', headers={'Authorization': f'Bearer {access}'})
    r.raise_for_status()
    data = json.dumps(r.json(), indent=2)

    return render_template_string(TEMPLATE, delegation=delegation, access=access, data=data)

if __name__ == '__main__':
    app.run(port=7000)

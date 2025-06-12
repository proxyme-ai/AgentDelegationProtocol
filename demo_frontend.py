from flask import Flask, render_template_string, Response
import requests
import json

app = Flask(__name__)

TEMPLATE = """<!doctype html>
<html lang='en'>
  <head>
    <meta charset='utf-8'/>
    <title>Delegation Protocol Demo</title>
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'>
    <script src='https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js'></script>
  </head>
  <body class='container py-4'>
    <h1 class='mb-4'>Delegation Protocol Demo</h1>
    <div id='diagram'></div>
    <pre id='log' class='bg-light p-3 mt-3'></pre>
    <script>
      mermaid.initialize({startOnLoad:false});
      let diagram = '';
      const container = document.getElementById('diagram');
      const log = document.getElementById('log');
      const evt = new EventSource('/flow');
      evt.addEventListener('line', e => {
        diagram += e.data + '\n';
        container.innerHTML = '<div class="mermaid">'+diagram+'</div>';
        mermaid.init(undefined, container);
      });
      evt.addEventListener('result', e => {
        log.textContent += e.data + '\n';
      });
    </script>
  </body>
</html>"""

BASE_AUTH = 'http://localhost:5000'
BASE_RS = 'http://localhost:6000'

@app.route('/')
def demo():
    return render_template_string(TEMPLATE)


@app.route('/flow')
def flow():
    def generate():
        yield 'event: line\n'
        yield 'data: sequenceDiagram\\n    participant Browser\\n    participant AS\\n    participant RS\n\n'

        r = requests.get(f"{BASE_AUTH}/authorize", params={
            "user": "alice",
            "client_id": "agent-client-id",
            "scope": "read:data",
        })
        r.raise_for_status()
        delegation = r.json()["delegation_token"]
        yield 'event: line\n'
        yield 'data: Browser->>AS: /authorize\n\n'
        yield 'event: result\n'
        yield f"data: {json.dumps({'delegation': delegation})}\n\n"

        r = requests.post(f"{BASE_AUTH}/token", data={"delegation_token": delegation})
        r.raise_for_status()
        access = r.json()["access_token"]
        yield 'event: line\n'
        yield 'data: Browser->>AS: /token\n\n'
        yield 'event: result\n'
        yield f"data: {json.dumps({'access': access})}\n\n"

        r = requests.get(f"{BASE_RS}/data", headers={"Authorization": f"Bearer {access}"})
        r.raise_for_status()
        body = r.json()
        yield 'event: line\n'
        yield 'data: Browser->>RS: /data\n\n'
        yield 'event: result\n'
        yield f"data: {json.dumps(body)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=7000)

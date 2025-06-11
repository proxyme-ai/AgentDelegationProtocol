"""LangChain agent example integrating the delegation protocol with an EspoCRM API."""
from langchain.agents import Tool, initialize_agent
from langchain.llms import OpenAI
import requests

AUTH_URL = "http://localhost:5000"
RESOURCE_URL = "http://localhost:6000/data"
ESPOCRM_BASE = "https://your-espocrm.example/api/v1"  # Replace with your EspoCRM URL


def fetch_access_token(scope: str = "crm:read") -> str:
    """Obtain an access token via the delegation flow."""
    res = requests.get(
        f"{AUTH_URL}/authorize",
        params={"user": "alice", "client_id": "agent-client-id", "scope": scope},
    )
    res.raise_for_status()
    delegation_token = res.json()["delegation_token"]

    res = requests.post(f"{AUTH_URL}/token", data={"delegation_token": delegation_token})
    res.raise_for_status()
    return res.json()["access_token"]


def query_espocrm(endpoint: str) -> dict:
    """Call an EspoCRM endpoint using a delegated access token."""
    token = fetch_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "EspoCRM-Api-Key": "<espocrm_api_key>",  # TODO: replace with your key
    }
    resp = requests.get(f"{ESPOCRM_BASE}/{endpoint}", headers=headers)
    resp.raise_for_status()
    return resp.json()


espocrm_tool = Tool(
    name="EspoCRM lookup",
    func=lambda text: query_espocrm(text),
    description="Access EspoCRM with delegated authority",
)


llm = OpenAI(temperature=0)
agent = initialize_agent([espocrm_tool], llm=llm, agent="zero-shot-react-description")

if __name__ == "__main__":
    print(agent.run("lookup Accounts/1234"))

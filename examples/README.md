# LangChain + EspoCRM Example

This directory contains `langchain_espo_agent.py`, an example showing how to wrap the delegation flow from this repository into a LangChain agent that queries an EspoCRM API.

## Requirements

- Python 3.8+
- Packages from `requirements.txt`
- `langchain` and `openai`
- Access to an EspoCRM instance and API key

## Running the Example

1. Install dependencies:

```bash
pip install -r ../requirements.txt
pip install langchain openai
```

2. Start the Authorization and Resource servers in separate terminals:

```bash
python ../auth_server.py
python ../resource_server.py
```

3. Set your OpenAI API key (required by LangChain's default LLM):

```bash
export OPENAI_API_KEY=<your-openai-key>
```

4. Set your EspoCRM connection details (URL and API key) as environment variables:

```bash
export ESPOCRM_BASE=https://your-espocrm.example/api/v1
export ESPOCRM_API_KEY=<your-espocrm-key>
```

5. Run the agent:

```bash
python langchain_espo_agent.py
```

The script requests a delegation token, exchanges it for an access token, and then calls the specified EspoCRM endpoint using that token.

#!/bin/bash
set -e

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

# Start servers in background
python auth_server.py &
AUTH_PID=$!
python resource_server.py &
RS_PID=$!

# Ensure servers are terminated on exit
cleanup() {
    kill $AUTH_PID $RS_PID
    deactivate
}
trap cleanup EXIT

# Give servers time to start
sleep 1

# Run the demo agent
python ai_agent.py


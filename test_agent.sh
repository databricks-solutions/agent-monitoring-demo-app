#!/bin/bash

set -e

# Source .env and .env.local if they exist
if [ -f ".env" ]; then
  echo "Loading .env"
  export $(grep -v '^#' .env | xargs)
fi
if [ -f ".env.local" ]; then
  echo "Loading .env.local"
  export $(grep -v '^#' .env.local | xargs)
fi

# Run the Python test script
uv run python test_agent.py
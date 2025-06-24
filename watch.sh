#!/bin/bash

set -e


# source .env and .env.local if they exist
if [ -f ".env" ]; then
  echo "Loading .env"
  export $(grep -v '^#' .env | xargs)
fi
if [ -f ".env.local" ]; then
  echo "Loading .env.local"
  export $(grep -v '^#' .env.local | xargs)
fi

if [ ! -z "$DATABRICKS_CONFIG_PROFILE" ]; then
  databricks auth login --profile $DATABRICKS_CONFIG_PROFILE
else
  databricks auth login
fi

uv run python -m scripts.make_fastapi_client

pushd client && BROWSER=none bun run dev | cat && popd &
pid[2]=$!

uv run uvicorn server.app:app --reload  --reload-dir server &
pid[1]=$!

uv run watchmedo auto-restart \
  --patterns="*.py" \
  --debounce-interval=1 \
  --no-restart-on-command-exit \
  --recursive \
  --directory=server \
  uv -- run python -m scripts.make_fastapi_client &
pid[0]=$!

sleep 2 && open "http://localhost:8000"

# When control+c is pressed, kill all process ids.
trap "pkill -P $$;  exit 1" INT
wait

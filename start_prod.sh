set -e

uv run python -m scripts.make_fastapi_client

pushd client && BROWSER=none npm run build && popd

FASTAPI_ENV=production uv run uvicorn server.app:app

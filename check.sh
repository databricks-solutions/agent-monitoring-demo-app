#!/bin/bash

set -e

echo "Running TypeScript and lint checks..."
echo "====================================="

# Check Python code with ruff
echo "Checking Python files with ruff..."
uv run ruff check .

# Check TypeScript in client directory
echo "Checking TypeScript files..."
cd client
npx tsc --noEmit --project .
cd ..

echo "✅ All checks passed!"
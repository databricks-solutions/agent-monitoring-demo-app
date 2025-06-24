#!/usr/bin/env python3
"""Test script for the Databricks agent."""

import json
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup (required for this script structure)
from server.agents.databricks_assistant import databricks_agent  # noqa: E402
from server.tracing import setup_mlflow_tracing  # noqa: E402


def main():
  """Test the Databricks agent with a sample message."""
  print('Setting up MLflow tracing...')
  setup_mlflow_tracing()
  print('MLflow tracing configured.')
  print()

  print('Testing Databricks agent...')
  print('=' * 50)

  # Test message
  test_messages = [{'role': 'user', 'content': 'How do I create a cluster in Databricks?'}]

  print('Sending message:')
  print(json.dumps(test_messages, indent=2))
  print()
  print('Agent response:')
  print('=' * 30)

  try:
    response = databricks_agent(test_messages)
    print(json.dumps(response, indent=2))

    # Also show just the content for easier reading
    if response and 'choices' in response and response['choices']:
      content = response['choices'][0]['message']['content']
      print()
      print('Response content only:')
      print('=' * 40)
      print(content)

    # Show trace information
    import mlflow

    trace_id = mlflow.get_last_active_trace_id()
    if trace_id:
      print()
      print(f'MLflow trace ID: {trace_id}')
      print('Trace logged to MLflow experiment.')

  except Exception as e:
    print(f'Error: {e}')
    import traceback

    traceback.print_exc()
    sys.exit(1)


if __name__ == '__main__':
  main()

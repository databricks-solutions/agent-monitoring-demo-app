"""Calls a model serving endpoint."""

import logging
import os
from typing import Any, Dict, List

import mlflow
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv(dotenv_path='.env.local')

logger = logging.getLogger(__name__)


# Initialize the OpenAI client lazily to handle deployment environments
def get_client():
  """Get or create the OpenAI client with Databricks configuration.
  
  In production Databricks Apps, we need to use OAuth authentication.
  The OpenAI client doesn't directly support OAuth, so we use the 
  Databricks SDK to get the host and create a proper client.
  """
  from databricks.sdk import WorkspaceClient
  
  # Try to get a workspace client (handles auth automatically)
  try:
    w = WorkspaceClient()
    # Get the host from the workspace client config
    databricks_host = w.config.host
    
    # For model serving endpoints in Databricks Apps, we can use
    # a special token that the SDK provides
    databricks_token = w.config.token
    
    if not databricks_token:
      # In OAuth scenarios, we need to get an access token
      # The SDK handles this automatically
      auth = w.config.authenticate()
      databricks_token = auth.get('access_token', 'no-token-required')
    
    # Remove https:// prefix if present since we're adding it
    if databricks_host.startswith('https://'):
      databricks_host = databricks_host[8:]
    
    return OpenAI(
      api_key=databricks_token,
      base_url=f'https://{databricks_host}/serving-endpoints',
    )
  except Exception:
    # Fallback to environment variables for local development
    databricks_token = os.getenv('DATABRICKS_TOKEN')
    databricks_host = os.getenv('DATABRICKS_HOST')
    
    if not databricks_token:
      raise ValueError('Unable to authenticate with Databricks')
    if not databricks_host:
      raise ValueError('Unable to determine Databricks host')
    
    # Remove https:// prefix if present since we're adding it
    if databricks_host.startswith('https://'):
      databricks_host = databricks_host[8:]
    
    return OpenAI(
      api_key=databricks_token,
      base_url=f'https://{databricks_host}/serving-endpoints',
    )


@mlflow.trace(span_type='LLM')
def model_serving_endpoint(
  endpoint_name: str, messages: List[ChatCompletionMessageParam]
) -> Dict[str, Any]:
  """Calls a model serving endpoint using OpenAI client."""
  # Create request preview
  user_messages = [msg for msg in messages if hasattr(msg, 'get') and msg.get('role') == 'user']
  if user_messages:
    last_content = user_messages[-1].get('content', '')
    if isinstance(last_content, str):
      request_preview = last_content
    else:
      request_preview = str(last_content) if last_content else 'No user message'
  else:
    request_preview = 'No user message'

  # Use OpenAI chat completions API with the specified endpoint
  client = get_client()
  response = client.chat.completions.create(
    model=endpoint_name, messages=messages, max_tokens=1000, temperature=0.1
  )

  # Convert OpenAI response to the expected format
  formatted_response = {
    'choices': [
      {
        'message': {
          'role': response.choices[0].message.role,
          'content': response.choices[0].message.content,
        },
        'index': response.choices[0].index,
        'finish_reason': response.choices[0].finish_reason,
      }
    ],
    'usage': {
      'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
      'completion_tokens': response.usage.completion_tokens if response.usage else 0,
      'total_tokens': response.usage.total_tokens if response.usage else 0,
    },
    'model': response.model,
    'id': response.id,
    'object': 'chat.completion',
    'created': response.created,
  }

  # Create response preview
  try:
    response_preview = response.choices[0].message.content or ''
  except (AttributeError, IndexError):
    response_preview = str(formatted_response)

  # Update current trace with better previews
  try:
    mlflow.update_current_trace(request_preview=request_preview, response_preview=response_preview)
  except Exception as e:
    logger.warning(f'Could not update trace previews: {e}')

  return formatted_response

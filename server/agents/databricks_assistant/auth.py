"""Authentication utilities for Databricks SDK."""

import os

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env.local')


def get_workspace_client() -> WorkspaceClient:
  """Initialize Databricks WorkspaceClient with proper authentication.
  
  Supports both development (token-based) and production (OAuth) authentication.
  In production Databricks Apps, uses DATABRICKS_CLIENT_ID and DATABRICKS_CLIENT_SECRET.
  In development, uses DATABRICKS_HOST and DATABRICKS_TOKEN.
  """
  # Check for OAuth client credentials (production in Databricks Apps)
  client_id = os.getenv('DATABRICKS_CLIENT_ID')
  client_secret = os.getenv('DATABRICKS_CLIENT_SECRET')
  
  if client_id and client_secret:
    # Production: Use OAuth client credentials
    # Let the SDK handle the authentication automatically
    return WorkspaceClient()
  
  # Development: Use token-based authentication
  databricks_host = os.getenv('DATABRICKS_HOST')
  databricks_token = os.getenv('DATABRICKS_TOKEN')

  if databricks_token and databricks_host:
    # Remove https:// prefix if present
    if databricks_host.startswith('https://'):
      databricks_host = databricks_host[8:]
    return WorkspaceClient(host=databricks_host, token=databricks_token)
  
  # Fallback: Let the SDK try to authenticate using its default chain
  # This works in Databricks Apps with proper environment setup
  return WorkspaceClient()
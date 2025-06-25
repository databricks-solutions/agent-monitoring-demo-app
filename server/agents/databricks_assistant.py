"""A LangChain agent with Databricks catalog exploration tools."""

import logging
import os
from typing import Any, Dict, List

import mlflow
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool, Tool
from langchain_community.chat_models import ChatDatabricks
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field

load_dotenv(dotenv_path='.env.local')

logger = logging.getLogger(__name__)


class SchemaInput(BaseModel):
  """Input for listing schemas."""

  catalog_name: str = Field(description='Name of the catalog to list schemas from')


class TableInput(BaseModel):
  """Input for listing tables."""

  catalog_name: str = Field(description='Name of the catalog')
  schema_name: str = Field(description='Name of the schema')


class VolumeInput(BaseModel):
  """Input for listing volumes."""

  catalog_name: str = Field(description='Name of the catalog')
  schema_name: str = Field(description='Name of the schema')


def get_workspace_client() -> WorkspaceClient:
  """Initialize Databricks WorkspaceClient."""
  databricks_host = os.getenv('DATABRICKS_HOST')
  databricks_token = os.getenv('DATABRICKS_TOKEN')

  if not databricks_token:
    raise ValueError('DATABRICKS_TOKEN environment variable is required')
  if not databricks_host:
    raise ValueError('DATABRICKS_HOST environment variable is required')

  # Remove https:// prefix if present
  if databricks_host.startswith('https://'):
    databricks_host = databricks_host[8:]

  return WorkspaceClient(host=databricks_host, token=databricks_token)


def list_catalogs(query: str = '') -> str:
  """List all available catalogs in the workspace."""
  try:
    w = get_workspace_client()
    catalogs = w.catalogs.list()
    catalog_names = [cat.name for cat in catalogs if cat.name]
    if catalog_names:
      return f'Available catalogs: {", ".join(catalog_names)}'
    else:
      return 'No catalogs found in the workspace.'
  except Exception as e:
    return f'Error listing catalogs: {str(e)}'


def list_schemas(args: SchemaInput) -> str:
  """List all schemas in a specific catalog."""
  try:
    w = get_workspace_client()
    schemas = w.schemas.list(catalog_name=args.catalog_name)
    schema_names = [schema.name for schema in schemas if schema.name]
    if schema_names:
      return f"Schemas in catalog '{args.catalog_name}': {', '.join(schema_names)}"
    else:
      return f"No schemas found in catalog '{args.catalog_name}'."
  except Exception as e:
    return f"Error listing schemas in catalog '{args.catalog_name}': {str(e)}"


def list_tables(args: TableInput) -> str:
  """List all tables in a specific schema."""
  try:
    w = get_workspace_client()
    tables = w.tables.list(catalog_name=args.catalog_name, schema_name=args.schema_name)
    table_info = []
    for table in tables:
      if table.name:
        table_type = table.table_type if hasattr(table, 'table_type') else 'TABLE'
        table_info.append(f'{table.name} ({table_type})')

    if table_info:
      return f'Tables in {args.catalog_name}.{args.schema_name}: {", ".join(table_info)}'
    else:
      return f'No tables found in {args.catalog_name}.{args.schema_name}.'
  except Exception as e:
    return f'Error listing tables in {args.catalog_name}.{args.schema_name}: {str(e)}'


def list_volumes(args: VolumeInput) -> str:
  """List all volumes in a specific schema."""
  try:
    w = get_workspace_client()
    volumes = w.volumes.list(catalog_name=args.catalog_name, schema_name=args.schema_name)
    volume_names = [vol.name for vol in volumes if vol.name]
    if volume_names:
      return f'Volumes in {args.catalog_name}.{args.schema_name}: {", ".join(volume_names)}'
    else:
      return f'No volumes found in {args.catalog_name}.{args.schema_name}.'
  except Exception as e:
    return f'Error listing volumes in {args.catalog_name}.{args.schema_name}: {str(e)}'


def create_catalog_tools():
  """Create LangChain tools for catalog operations."""
  return [
    Tool(
      func=list_catalogs,
      name='list_catalogs',
      description='List all available catalogs in the Databricks workspace',
    ),
    StructuredTool.from_function(
      func=list_schemas,
      name='list_schemas',
      description='List all schemas in a specific catalog',
      args_schema=SchemaInput,
    ),
    StructuredTool.from_function(
      func=list_tables,
      name='list_tables',
      description=(
        'List all tables in a specific schema. Requires both catalog_name and schema_name.'
      ),
      args_schema=TableInput,
    ),
    StructuredTool.from_function(
      func=list_volumes,
      name='list_volumes',
      description=(
        'List all volumes in a specific schema. Requires both catalog_name and schema_name.'
      ),
      args_schema=VolumeInput,
    ),
  ]


# Create the prompt template for tool-calling agent
SYSTEM_PROMPT = (
  'You are a helpful assistant that answers questions about Databricks, '
  'with special capabilities to explore the Databricks catalog structure.\n\n'
  'You have access to tools that allow you to:\n'
  '- List all catalogs in the workspace\n'
  '- List schemas in a specific catalog\n'
  '- List tables in a specific schema\n'
  '- List volumes in a specific schema\n\n'
  'Use these tools to answer questions about the data organization and structure in Databricks.'
)


# Enable MLflow autologging for LangChain
mlflow.langchain.autolog()


@mlflow.trace(span_type='LLM')
def databricks_agent(messages: List[ChatCompletionMessageParam]) -> Dict[str, Any]:
  """A LangChain agent that can explore Databricks catalogs and answer questions."""
  # Extract the last user message
  user_messages = [msg for msg in messages if hasattr(msg, 'get') and msg.get('role') == 'user']
  if user_messages:
    last_content = user_messages[-1].get('content', '')
    if isinstance(last_content, str):
      user_query = last_content
    else:
      user_query = str(last_content) if last_content else 'No user message'
  else:
    user_query = 'No user message'

  try:
    # Initialize the ChatDatabricks LLM
    llm = ChatDatabricks(
      endpoint='databricks-claude-sonnet-4',
      max_tokens=1000,
      temperature=0.1,
    )

    # Create catalog tools
    tools = create_catalog_tools()

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages(
      [
        ('system', SYSTEM_PROMPT),
        ('human', '{input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad'),
      ]
    )

    # Create the tool-calling agent
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

    # Create the agent executor
    agent_executor = AgentExecutor(
      agent=agent, tools=tools, verbose=True, max_iterations=5, handle_parsing_errors=True
    )

    # Execute the agent
    result = agent_executor.invoke({'input': user_query})

    # Extract the final answer
    final_answer = result.get('output', 'I could not generate a response.')

    # Format response to match expected structure
    formatted_response = {
      'choices': [
        {
          'message': {
            'role': 'assistant',
            'content': final_answer,
          },
          'index': 0,
          'finish_reason': 'stop',
        }
      ],
      'usage': {
        'prompt_tokens': 0,  # Would need token counting for accuracy
        'completion_tokens': 0,
        'total_tokens': 0,
      },
      'model': 'databricks-claude-sonnet-4',
      'id': 'langchain-agent-response',
      'object': 'chat.completion',
      'created': 0,
    }

    # Update trace with previews
    try:
      mlflow.update_current_trace(request_preview=user_query, response_preview=final_answer)
    except Exception as e:
      logger.warning(f'Could not update trace previews: {e}')

    return formatted_response

  except Exception as e:
    logger.error(f'Error in databricks_agent: {str(e)}')
    # Return error response in expected format
    error_message = f'I encountered an error: {str(e)}'
    return {
      'choices': [
        {
          'message': {
            'role': 'assistant',
            'content': error_message,
          },
          'index': 0,
          'finish_reason': 'stop',
        }
      ],
      'usage': {
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'total_tokens': 0,
      },
      'model': 'databricks-claude-sonnet-4',
      'id': 'error-response',
      'object': 'chat.completion',
      'created': 0,
    }

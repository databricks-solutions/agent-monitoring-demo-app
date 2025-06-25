"""Databricks catalog exploration tools for LangChain agent."""

import logging
from typing import List

from langchain.tools import StructuredTool, Tool
from pydantic import BaseModel, Field

from .auth import get_workspace_client

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


def list_schemas(catalog_name: str) -> str:
  """List all schemas in a specific catalog."""
  try:
    w = get_workspace_client()
    schemas = w.schemas.list(catalog_name=catalog_name)
    schema_names = [schema.name for schema in schemas if schema.name]
    if schema_names:
      return f'Schemas in catalog "{catalog_name}": {", ".join(schema_names)}'
    else:
      return f'No schemas found in catalog "{catalog_name}".'
  except Exception as e:
    return f'Error listing schemas in catalog "{catalog_name}": {str(e)}'


def list_tables(catalog_name: str, schema_name: str) -> str:
  """List all tables in a specific schema."""
  try:
    w = get_workspace_client()
    tables = w.tables.list(catalog_name=catalog_name, schema_name=schema_name)
    table_info = []
    for table in tables:
      if table.name:
        table_type = getattr(table, 'table_type', 'TABLE')
        table_info.append(f'{table.name} ({table_type})')

    if table_info:
      return f'Tables in {catalog_name}.{schema_name}: {", ".join(table_info)}'
    else:
      return f'No tables found in {catalog_name}.{schema_name}.'
  except Exception as e:
    return f'Error listing tables in {catalog_name}.{schema_name}: {str(e)}'


def list_volumes(catalog_name: str, schema_name: str) -> str:
  """List all volumes in a specific schema."""
  try:
    w = get_workspace_client()
    volumes = w.volumes.list(catalog_name=catalog_name, schema_name=schema_name)
    volume_names = [vol.name for vol in volumes if vol.name]
    if volume_names:
      return f'Volumes in {catalog_name}.{schema_name}: {", ".join(volume_names)}'
    else:
      return f'No volumes found in {catalog_name}.{schema_name}.'
  except Exception as e:
    return f'Error listing volumes in {catalog_name}.{schema_name}: {str(e)}'


def create_catalog_tools() -> List[Tool]:
  """Create and return the list of catalog exploration tools."""
  return [
    Tool(
      name='list_catalogs',
      func=list_catalogs,
      description='List all available catalogs in the Databricks workspace.',
    ),
    StructuredTool.from_function(
      func=list_schemas,
      name='list_schemas',
      description='List all schemas in a specific catalog. Requires the catalog name as input.',
      args_schema=SchemaInput,
    ),
    StructuredTool.from_function(
      func=list_tables,
      name='list_tables',
      description='List all tables in a specific schema. Requires catalog and schema names.',
      args_schema=TableInput,
    ),
    StructuredTool.from_function(
      func=list_volumes,
      name='list_volumes',
      description='List all volumes in a specific schema. Requires catalog and schema names.',
      args_schema=VolumeInput,
    ),
  ]

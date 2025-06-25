"""LangChain agent with Databricks catalog exploration tools."""

import logging
from typing import Any, Dict, List

import mlflow
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatDatabricks
from openai.types.chat import ChatCompletionMessageParam

from .tools import create_catalog_tools

logger = logging.getLogger(__name__)

# Agent prompt
SYSTEM_PROMPT = """You are a helpful Databricks assistant that can explore Unity Catalog.

You have access to tools that let you:
- List all catalogs in the workspace
- List schemas within a specific catalog
- List tables within a specific schema
- List volumes within a specific schema

Use these tools to help users understand their data structure and find the information they need.
When listing items, present them in a clear, organized format.

Always be helpful and provide context about what you find. If a user asks about data,
start by exploring the catalog structure to understand what's available."""


def format_messages_for_langchain(
  messages: List[ChatCompletionMessageParam],
) -> List[Dict[str, Any]]:
  """Convert OpenAI message format to LangChain format."""
  formatted_messages = []
  for msg in messages:
    role = msg.get('role', 'user')
    content = msg.get('content', '')

    # Map OpenAI roles to LangChain roles
    if role == 'system':
      # System messages are handled by the prompt template
      continue
    elif role == 'assistant':
      formatted_messages.append({'role': 'assistant', 'content': content})
    else:  # user or any other role
      formatted_messages.append({'role': 'human', 'content': content})

  return formatted_messages


@mlflow.trace(span_type='LLM')
def databricks_agent(messages: List[ChatCompletionMessageParam]) -> Dict[str, Any]:
  """A LangChain agent that can explore Databricks catalogs and answer questions."""
  # Initialize the LLM
  llm = ChatDatabricks(
    endpoint='databricks-claude-sonnet-4',
    max_tokens=1000,
    temperature=0.1,
  )

  # Create the prompt template
  prompt = ChatPromptTemplate.from_messages(
    [
      ('system', SYSTEM_PROMPT),
      MessagesPlaceholder(variable_name='messages'),
      MessagesPlaceholder(variable_name='agent_scratchpad'),
    ]
  )

  # Create tools
  tools = create_catalog_tools()

  # Create the agent
  agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
  )

  # Create the agent executor
  agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
  )

  # Format messages for LangChain
  formatted_messages = format_messages_for_langchain(messages)

  # Get the last user message as the input
  user_messages = [msg for msg in messages if msg.get('role') == 'user']
  if not user_messages:
    return {
      'response': {
        'choices': [
          {'message': {'role': 'assistant', 'content': 'Please provide a question or request.'}}
        ]
      }
    }

  last_user_message = user_messages[-1].get('content', '')

  # Run the agent
  try:
    result = agent_executor.invoke(
      {
        'messages': formatted_messages,
        'input': last_user_message,
      }
    )

    # Format the response to match OpenAI's format
    return {
      'response': {
        'choices': [
          {
            'message': {
              'role': 'assistant',
              'content': result.get('output', 'I encountered an error processing your request.'),
            }
          }
        ]
      }
    }
  except Exception as e:
    logger.error(f'Error in agent execution: {str(e)}')
    return {
      'response': {
        'choices': [
          {'message': {'role': 'assistant', 'content': f'I encountered an error: {str(e)}'}}
        ]
      }
    }

"""MLFlow tracing utils."""

import os
from typing import Optional

import mlflow
from mlflow import tracing

# Set the mlflow tracking URI to databricks.
# NOTE: You can also use the environment variable MLFLOW_TRACKING_URI to set the tracking URI.
mlflow.set_tracking_uri('databricks')

MLFLOW_EXPERIMENT_ID = os.environ.get('MLFLOW_EXPERIMENT_ID', None)
mlflow.set_experiment(experiment_id=MLFLOW_EXPERIMENT_ID)
tracing.set_destination(tracing.destination.Databricks(experiment_id=MLFLOW_EXPERIMENT_ID))

IS_DESTINATION_ONLINE = True


def setup_mlflow_tracing():
  """Sets up MLflow tracing."""
  # Set the mlflow tracking URI to databricks.
  mlflow.set_tracking_uri('databricks')

  MLFLOW_EXPERIMENT_ID = os.environ.get('MLFLOW_EXPERIMENT_ID', None)
  mlflow.set_experiment(experiment_id=MLFLOW_EXPERIMENT_ID)
  
  # Enable LangChain autologging
  # This automatically logs:
  # - LLM calls with prompts and completions
  # - Tool invocations with inputs and outputs
  # - Agent executor runs with full conversation history
  # - Retriever queries and results (if using RAG)
  mlflow.langchain.autolog(
    log_input_examples=True,
    log_model_signatures=True,
    log_models=False,  # We don't need to log models, just traces
    log_datasets=False,
    log_inputs_outputs=True,
    disable=False,
    exclusive=False,
    disable_for_unsupported_versions=False,
    silent=False
  )


def get_mlflow_experiment_id() -> Optional[str]:
  """Gets the current mlflow experiment id."""
  return MLFLOW_EXPERIMENT_ID

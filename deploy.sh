# Deploy the Lakehouse App.
# For configuration options see README.md and .env.local.

set -e

# Load environment variables from .env.local if it exists.
if [ -f .env.local ]
then
  set -a
  source .env.local
  set +a
fi

# If LHA_SOURCE_CODE_PATH is not set throw an error.
if [ -z "$LHA_SOURCE_CODE_PATH" ]
then
  echo "LHA_SOURCE_CODE_PATH is not set. Please set to the /Workspace/Users/{username}/{lha-name} in .env.local."
  exit 1
fi

if [ -z "$DATABRICKS_APP_NAME" ]
then
  echo "DATABRICKS_APP_NAME is not set. Please set to the name of the app in .env.local."
  exit 1
fi

if [ -z "$DATABRICKS_CONFIG_PROFILE" ]
then
  DATABRICKS_CONFIG_PROFILE="DEFAULT"
fi

# Authenticate with Databricks CLI using the host from environment
if [ -n "$DATABRICKS_HOST" ]
then
  echo "Authenticating with Databricks at $DATABRICKS_HOST..."
  databricks auth login --host "$DATABRICKS_HOST"
fi

mkdir -p client/build

# Generate requirements.txt from pyproject.toml preserving version ranges
uv run python scripts/generate_semver_requirements.py

# Update app.yaml with MLFLOW_EXPERIMENT_ID from .env.local
if [ -n "$MLFLOW_EXPERIMENT_ID" ]; then
  echo "🔧 Setting MLFLOW_EXPERIMENT_ID to $MLFLOW_EXPERIMENT_ID in app.yaml..."
  sed -i.bak "s/value: 'your-experiment-id'/value: '$MLFLOW_EXPERIMENT_ID'/" app.yaml
  rm -f app.yaml.bak
else
  echo "⚠️  MLFLOW_EXPERIMENT_ID not found in environment"
fi

# Build fastapi client.
uv run python -m scripts.make_fastapi_client

# Build javascript.
pushd client && BROWSER=none npm run build && popd

databricks sync . "$LHA_SOURCE_CODE_PATH" \
  --profile "$DATABRICKS_CONFIG_PROFILE"

databricks apps deploy $DATABRICKS_APP_NAME \
  --source-code-path "$LHA_SOURCE_CODE_PATH"\
  --profile "$DATABRICKS_CONFIG_PROFILE"

echo ""
echo "🎉 Deployment completed!"
echo ""

# Get app status and URL
echo "📊 Checking app status..."
APP_STATUS=$(databricks apps list --profile "$DATABRICKS_CONFIG_PROFILE" | grep "$DATABRICKS_APP_NAME" || echo "")

if [ -n "$APP_STATUS" ]; then
  echo "✅ App found in Databricks Apps list"
  echo "$APP_STATUS"
  echo ""
  
  # Wait a moment for app to start up
  echo "⏳ Waiting for app to start up..."
  sleep 10
  
  # Attempt to get app URL and test health endpoint
  echo "🔍 Testing app health..."
  
  # Note: You'll need to replace this with your actual app URL pattern
  # This is a placeholder that would need to be customized based on your Databricks setup
  echo "📋 Post-deployment checklist:"
  echo ""
  echo "🔗 App Access:"
  echo "  • Navigate to Compute → Apps in your Databricks workspace"
  echo "  • Click on '$DATABRICKS_APP_NAME' to access your app"
  echo "  • Test the chat interface to verify agent functionality"
  echo ""
  echo "📊 Monitoring Setup:"
  echo "  • App Logs: Click 'Logs' tab in your app overview"
  echo "  • Direct Log Access: Add /logz to your app URL"
  echo "  • Health Check: Add /api/health to your app URL"
  echo "  • MLflow Traces: Check experiment ID $MLFLOW_EXPERIMENT_ID"
  echo ""
  echo "🧪 Verification Steps:"
  echo "  1. Send a test message in the chat interface"
  echo "  2. Verify logs appear in the Logs tab"
  echo "  3. Check MLflow experiment for new traces"
  echo "  4. Test thumbs up/down feedback functionality"
  echo ""
  echo "🚨 Troubleshooting:"
  echo "  • If app won't start: Check Environment tab for errors"
  echo "  • If no logs: Verify app writes to stdout/stderr"
  echo "  • If MLflow issues: Check MLFLOW_EXPERIMENT_ID in Environment"
  echo ""
else
  echo "⚠️  App not found in apps list - deployment may have failed"
  echo ""
  echo "🔧 Debugging steps:"
  echo "  1. Run: databricks apps list --profile $DATABRICKS_CONFIG_PROFILE"
  echo "  2. Check your .env.local file for correct DATABRICKS_APP_NAME"
  echo "  3. Verify workspace permissions for app deployment"
  echo "  4. Check app.yaml configuration file"
fi

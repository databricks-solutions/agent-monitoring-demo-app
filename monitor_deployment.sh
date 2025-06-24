#!/bin/bash

# Monitor deployment status and health of Databricks App
# This script provides ongoing monitoring capabilities after deployment

set -e

# Load environment variables from .env.local if it exists
if [ -f .env.local ]; then
  set -a
  source .env.local
  set +a
fi

if [ -z "$DATABRICKS_APP_NAME" ]; then
  echo "DATABRICKS_APP_NAME is not set. Please set it in .env.local."
  exit 1
fi

if [ -z "$DATABRICKS_CONFIG_PROFILE" ]; then
  DATABRICKS_CONFIG_PROFILE="DEFAULT"
fi

echo "🔍 Monitoring Databricks App: $DATABRICKS_APP_NAME"
echo "=================================================="

# Check if app exists
echo "📋 Checking app status..."
APP_LIST=$(databricks apps list --profile "$DATABRICKS_CONFIG_PROFILE" 2>/dev/null || echo "")

if echo "$APP_LIST" | grep -q "$DATABRICKS_APP_NAME"; then
  echo "✅ App '$DATABRICKS_APP_NAME' is deployed"
  
  # Show app details
  echo ""
  echo "📊 App Details:"
  echo "$APP_LIST" | grep "$DATABRICKS_APP_NAME"
  
  echo ""
  echo "🔗 Access Options:"
  echo "  • Databricks Workspace: Compute → Apps → $DATABRICKS_APP_NAME"
  echo "  • Direct App URL: [Your app URL from Databricks]"
  echo "  • Health Check: [Your app URL]/api/health"
  echo "  • Logs: [Your app URL]/logz"
  
  echo ""
  echo "📈 Monitoring Commands:"
  echo "  • Watch logs: tail -f [log location] (if available locally)"
  echo "  • Check health: curl [your-app-url]/api/health"
  echo "  • MLflow traces: Visit experiment $MLFLOW_EXPERIMENT_ID"
  
  echo ""
  echo "🧪 Test Commands:"
  echo "  • Local agent test: ./test_agent.sh"
  echo "  • Health check: curl -f [your-app-url]/api/health"
  
else
  echo "❌ App '$DATABRICKS_APP_NAME' not found"
  echo ""
  echo "Available apps:"
  if [ -n "$APP_LIST" ]; then
    echo "$APP_LIST"
  else
    echo "  No apps found or permission denied"
  fi
  
  echo ""
  echo "🔧 Troubleshooting:"
  echo "  • Verify app name in .env.local"
  echo "  • Check workspace permissions"
  echo "  • Run ./deploy.sh to deploy the app"
fi

echo ""
echo "📚 Documentation:"
echo "  • Databricks Apps: https://docs.databricks.com/aws/en/dev-tools/databricks-apps/"
echo "  • MLflow Tracing: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/concepts/log-assessment"
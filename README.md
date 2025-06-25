# Lakehouse Apps + AI Agents Template

A complete template for building and deploying AI agents with **Databricks Lakehouse Apps**. This repo demonstrates best practices for agent development with **MLflow 3.0 monitoring**, **traced function observability**, and a modern chat interface.

🎯 **Perfect for getting started with:**
- **Databricks Agent development** with production monitoring
- **MLflow 3.0 tracing** and experiment tracking
- **Lakehouse Apps deployment** with a beautiful UI
- **Modern development workflow** with hot reload and automated scripts

✨ **What makes this template special:**
- **Ready-to-deploy agent** with chat interface in under 5 minutes
- **Professional dev setup** with automated scripts for development and deployment  
- **Production-ready observability** with MLflow tracing and monitoring
- **Optimized dependencies** - lean production builds with conflict-free package management
- **Claude memory ready** - includes [CLAUDE.md](./CLAUDE.md) for AI-assisted development with full project context

<img width="1723" alt="image" src="https://github.com/user-attachments/assets/14aa98ad-33fa-4270-9479-48894dc6f69f" />

The Agent being served:

**databricks_assistant.py** is a LangChain tool-calling agent that can explore and query your Databricks Unity Catalog structure. The agent includes the following tools:

- **list_catalogs**: Lists all available catalogs in the workspace
- **list_schemas**: Lists all schemas in a specific catalog  
- **list_tables**: Lists all tables in a specific schema
- **list_volumes**: Lists all volumes in a specific schema

```python
@mlflow.trace(span_type='LLM')
def databricks_agent(messages):
  """A LangChain agent that can explore Databricks catalogs and answer questions."""
  # Initialize ChatDatabricks LLM
  llm = ChatDatabricks(
    endpoint='databricks-claude-sonnet-4',
    max_tokens=1000,
    temperature=0.1,
  )
  
  # Create catalog exploration tools
  tools = create_catalog_tools()  # list_catalogs, list_schemas, list_tables, list_volumes
  
  # Create tool-calling agent with custom prompt
  agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
  
  # Execute agent with AgentExecutor for tool orchestration
  agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
  result = agent_executor.invoke({'input': user_query})
  
  return formatted_response  # Formatted for UI compatibility
```

The agent uses the Databricks SDK (`WorkspaceClient`) to interact with Unity Catalog, providing dynamic exploration of your data assets. The UI renders markdown responses with proper formatting for lists, code blocks, and emphasis.

## Tech Stack

**🖥️ Frontend (Port 3000)**
- **[React](https://react.dev/)** + **[TypeScript](https://www.typescriptlang.org/)** for the UI framework
- **[Vite](https://vitejs.dev/)** for fast development and hot module replacement
- **[shadcn/ui](https://ui.shadcn.com/)** for beautiful, accessible components built on Radix UI
- **[Tailwind CSS](https://tailwindcss.com/)** for styling
- **[Bun](https://bun.sh/)** as the package manager and dev server
- **[react-markdown](https://github.com/remarkjs/react-markdown)** + **[remark-gfm](https://github.com/remarkjs/remark-gfm)** for rendering agent markdown responses

**⚙️ Backend (Port 8000)**
- **[FastAPI](https://fastapi.tiangolo.com/)** for the Python API server with auto-docs
- **[uvicorn](https://www.uvicorn.org/)** with hot reload for development
- **[LangChain](https://python.langchain.com/)** for building the tool-calling agent with AgentExecutor
- **[Databricks SDK](https://databricks-sdk-py.readthedocs.io/)** for Unity Catalog operations
- **[OpenAI Python SDK](https://github.com/openai/openai-python)** for Databricks model serving endpoints

**📊 Observability & Deployment**
- **[MLflow](https://mlflow.org/)** for experiment tracking and [agent monitoring/evaluation](https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/)
- **[Lakehouse Apps](https://www.databricks.com/product/databricks-apps)** for production deployment

**🔧 Development Tools**
- **Fast edit-refresh cycle**: `./watch.sh` runs both servers with hot reload
- **Frontend proxy**: In dev mode, port 8000 proxies non-API requests to port 3000
- **Auto-reloading**: Backend reloads on Python changes, frontend on React/CSS changes

### Adding UI Components

The template uses **shadcn/ui** for consistent, accessible components:

```bash
# Add a new component (run from project root)
bunx --bun shadcn@latest add button
bunx --bun shadcn@latest add dialog
bunx --bun shadcn@latest add form

# Browse available components
bunx --bun shadcn@latest add
```

Components are installed to `client/src/components/ui/` and use the canonical "@/" import pattern:

```tsx
import { Button } from "@/components/ui/button"
import { Dialog } from "@/components/ui/dialog"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

function MyComponent() {
  return (
    <Card>
      <CardHeader>My Card</CardHeader>
      <CardContent>
        <Button variant="outline">Click me</Button>
      </CardContent>
    </Card>
  )
}
```

**Styling approach:**
- shadcn/ui components use **CSS variables** for theming (see `client/src/index.css`)
- **Tailwind classes** for custom styling and layout
- **Responsive design** built-in with Tailwind's breakpoint system


## Quick Start

Get the template running in 3 commands:

```bash
git clone <this-repo>
./setup.sh                 # Interactive environment setup
./watch.sh                 # Start development server
```

🎉 **Open http://localhost:8000** - You'll have a working chat interface with Databricks agent!

**What you get:**
- 🤖 Chat interface with AI agent responses (~5-10s response time)
- 📊 MLflow experiment tracking with trace IDs
- 🔥 Hot reload for both frontend and backend changes
- 🧪 Built-in testing and formatting tools

## Project Structure

```
├── server/                 # FastAPI backend
│   ├── agents/            # Agent implementations
│   │   ├── databricks_assistant.py  # Main agent (customize this!)
│   │   └── model_serving.py         # Direct model endpoint calls
│   ├── app.py             # FastAPI routes and setup
│   └── tracing.py         # MLflow integration
├── client/                # React frontend
│   ├── src/components/    # UI components (shadcn/ui based)
│   ├── src/queries/       # API client and React Query hooks
│   └── build/             # Production build output
├── scripts/               # Build and utility scripts
├── *.sh                   # Development automation scripts
└── .env.local            # Environment configuration (create with ./setup.sh)
```

## Customization Guide

**To adapt this template for your use case:**

1. **Change the agent behavior** - Edit `server/agents/databricks_assistant.py`:
   - Modify the `SYSTEM_PROMPT` for your domain
   - Swap the model endpoint (currently Claude Sonnet 4)
   - Add custom logic, retrieval, or tools

2. **Update branding** - Modify `client/src/App.tsx`:
   - Change app title, colors, and styling
   - Add your organization's UI components

3. **Add new endpoints** - Extend `server/app.py`:
   - Follow the existing `/api/agent` pattern
   - Use MLflow tracing for observability

4. **Environment variables** - Update `.env.local`:
   - Point to your Databricks workspace
   - Configure your model serving endpoints
   - Set up your MLflow experiment

# Deploy

## Prerequisites

Make sure you've created a Custom Lakehouse App and you've set the `DATABRICKS_APP_NAME` to the name of the lakehouse app with environment flags above.

## Deploy to LHA

```bash
./deploy.sh
```

**✨ Smart deployment verification**: When using Claude Code, simply ask to "deploy" and it will:
- Run the deployment script automatically
- Verify deployment success by checking app status 
- Scan logs for errors and provide troubleshooting steps
- Report back with monitoring and access information

Note: you may have to upgrade the databricks CLI for the above command to work.

## Development

### Prerequisites

```
brew install uv bun
```

### Environment setup

Run the interactive setup script to create your `.env.local` file:

```bash
./setup.sh
```

Or manually create an `.env.local` file with the following variables:

```
DATABRICKS_HOST="e2-dogfood.staging.cloud.databricks.com"
DATABRICKS_TOKEN="..."
DATABRICKS_CONFIG_PROFILE="..."

# Your LHA name here:
DATABRICKS_APP_NAME="nikhil-chatbot-fastapi"

# The agents monitoring destination. See external trace logging SDK for configuration of this param. If not defined, will not monitor the traces in mlflow.
DATABRICKS_AGENTS_MONITORING_DESTINATION="rag.external_agent_monitoring.nikhil_chatbot_fastapi"

# The source code path is only necessary for local dev:
LHA_SOURCE_CODE_PATH="/Workspace/Users/nikhil.thorat@databricks.com/nikhil-chatbot-fastapi"
```

### Development scripts

**Setup and configuration:**
- `./setup.sh` - Interactive setup to create `.env.local` file
- `./fix.sh` - Format all code (ruff for Python, prettier for TypeScript)
- `./check.sh` - Run code quality checks

**Development and testing:**
- `./watch.sh` - Run fast-edit refresh python + typescript locally
- `./start_prod.sh` - Run the production server locally  
- `./test_agent.sh` - Test agent directly without starting full web app

## Claude Code Integration

🤖 **This repository is Claude memory ready!** 

This project includes comprehensive configuration for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) to accelerate your development workflow. The [CLAUDE.md](./CLAUDE.md) file contains detailed project instructions, conventions, and context that Claude Code uses to understand your codebase and assist effectively.

**What makes this Claude-ready:**
- **Project memory**: [CLAUDE.md](./CLAUDE.md) provides Claude with deep context about the codebase structure, development patterns, and best practices
- **Smart commands**: Claude understands common tasks like "deploy", "test agent", and "fix" without detailed explanations
- **Contextual awareness**: Claude knows about the tech stack, file organization, and project-specific conventions
- **Automated workflows**: Claude can handle complex tasks like deployment verification and dependency conflict resolution

**Key Claude commands:**
- "setup" - Run the interactive environment setup script
- "deploy" - Deploy the application and verify success automatically  
- "fix" - Format all code according to project style guidelines
- "test agent" - Test the agent directly without starting the full web application
- "start server" - Run the development server in a screen session
- "kill server" - Stop the development server

Claude Code understands the project structure and can help with development tasks while following the established patterns and conventions. When you work with Claude on this project, it already knows your tooling, dependencies, and workflows!

## Troubleshooting

### Common Issues

**❌ "Profile error" when running `./watch.sh`**
- **Solution**: The script handles optional `DATABRICKS_CONFIG_PROFILE` - if not set, it uses default auth
- **Check**: Ensure your `.env.local` has valid `DATABRICKS_HOST` and `DATABRICKS_TOKEN`

**❌ Port 8000 already in use**
- **Check**: `lsof -i :8000` to see what's using the port
- **Solution**: Kill the process or change `UVICORN_PORT` in your environment

**❌ Frontend not loading/502 errors**
- **Check**: Both uvicorn (backend) and bun (frontend) processes are running
- **Solution**: Run `./watch.sh` again - it starts both servers

**❌ Agent responses are slow (>30s)**
- **Expected**: 5-10s response time is normal for LLM calls
- **Check**: Your `DATABRICKS_HOST` network connectivity
- **Monitor**: Use the MLflow experiment link to see trace details

**❌ MLflow tracing not working**
- **Check**: `MLFLOW_EXPERIMENT_ID` is set in `.env.local`
- **Verify**: Visit the tracing experiment URL from `/api/tracing_experiment`

### Development Tips

- **Hot reload issues**: If changes aren't picked up, restart `./watch.sh`
- **Screen session stuck**: Use `screen -list` and `screen -X -S lha-dev quit` to force-kill
- **API testing**: Use the built-in curl commands from [CLAUDE.md](./CLAUDE.md)
- **Debug mode**: Add `print()` statements in Python code - they'll show in the uvicorn output

## Contributing to Template

Found a bug or want to improve the template? 

1. **Test your changes** with `./test_agent.sh` and `./fix.sh`
2. **Update documentation** if you add new features
3. **Follow the development patterns** established in [CLAUDE.md](./CLAUDE.md)

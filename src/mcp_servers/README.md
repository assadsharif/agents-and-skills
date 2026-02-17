# MCP Servers

**Model Context Protocol (MCP) Server Implementations** - Python-based MCP servers for specialized integrations and capabilities.

## Overview

This directory contains 32 MCP server implementations that extend Claude Code with specialized capabilities. MCP servers provide standardized interfaces for:

- External service integrations (APIs, databases, cloud services)
- File system operations
- Development tools and workflows
- Data processing and analysis

## What is MCP?

**Model Context Protocol (MCP)** is a standard protocol that allows AI assistants like Claude to interact with external tools and services in a structured, safe way.

**Key Concepts:**
- **Server:** Python process that implements MCP protocol
- **Tool:** Function exposed by server (e.g., `search-docs`, `query-database`)
- **Resource:** Data source provided by server (e.g., files, API endpoints)
- **Prompt:** Reusable prompt templates from server

## Directory Structure

```
src/mcp_servers/
├── __init__.py                 # Package initialization
├── README.md                   # This file
├── <server_name>_mcp.py        # Individual MCP server implementations
└── requirements.txt            # Python dependencies for MCP servers
```

## Available MCP Servers (32 Total)

### Development & Testing

| Server | File | Purpose |
|--------|------|---------|
| **TDD** | `tdd_mcp.py` | Test-driven development workflow automation |
| **Pytest** | `pytest_mcp.py` | Pytest test runner and reporting |
| **Coverage** | `coverage_mcp.py` | Code coverage analysis and reporting |
| **Lint** | `lint_mcp.py` | Code linting with ruff/black/mypy |

### Data & Databases

| Server | File | Purpose |
|--------|------|---------|
| **PostgreSQL** | `postgres_mcp.py` | PostgreSQL database operations |
| **SQLite** | `sqlite_mcp.py` | SQLite database operations |
| **MongoDB** | `mongodb_mcp.py` | MongoDB document database operations |
| **Redis** | `redis_mcp.py` | Redis caching and pub/sub |
| **Pandas** | `pandas_mcp.py` | DataFrame operations and analysis |

### Cloud & Infrastructure

| Server | File | Purpose |
|--------|------|---------|
| **AWS** | `aws_mcp.py` | AWS service integrations (S3, EC2, Lambda) |
| **Docker** | `docker_mcp.py` | Docker container management |
| **Kubernetes** | `k8s_mcp.py` | Kubernetes cluster operations |
| **Terraform** | `terraform_mcp.py` | Infrastructure as code operations |

### APIs & Web Services

| Server | File | Purpose |
|--------|------|---------|
| **FastAPI** | `fastapi_mcp.py` | FastAPI endpoint testing and docs |
| **HTTP** | `http_mcp.py` | Generic HTTP client with auth |
| **GraphQL** | `graphql_mcp.py` | GraphQL query and mutation execution |
| **WebSocket** | `websocket_mcp.py` | WebSocket client operations |

### File & Document Processing

| Server | File | Purpose |
|--------|------|---------|
| **PDF** | `pdf_mcp.py` | PDF reading, writing, manipulation |
| **Excel** | `excel_mcp.py` | Excel spreadsheet operations |
| **CSV** | `csv_mcp.py` | CSV file parsing and generation |
| **JSON** | `json_mcp.py` | JSON validation, transformation, query |
| **YAML** | `yaml_mcp.py` | YAML parsing and generation |

### Git & Version Control

| Server | File | Purpose |
|--------|------|---------|
| **Git** | `git_mcp.py` | Git operations (commit, branch, merge) |
| **GitHub** | `github_mcp.py` | GitHub API integration (PRs, issues) |
| **GitLab** | `gitlab_mcp.py` | GitLab API integration |

### AI & ML

| Server | File | Purpose |
|--------|------|---------|
| **OpenAI** | `openai_mcp.py` | OpenAI API integration |
| **Embeddings** | `embeddings_mcp.py` | Text embedding generation |
| **Vector Store** | `vectorstore_mcp.py` | Vector similarity search |

### Utilities

| Server | File | Purpose |
|--------|------|---------|
| **Filesystem** | `filesystem_mcp.py` | Safe file operations with sandboxing |
| **Environment** | `env_mcp.py` | Environment variable management |
| **Process** | `process_mcp.py` | System process management |
| **Time** | `time_mcp.py` | Time/date operations and scheduling |

*(Note: Exact server inventory may vary. Run `ls -1 src/mcp_servers/*.py | wc -l` to confirm current count.)*

---

## Installation

### Prerequisites

- Python 3.10+
- Virtual environment recommended

### Setup

```bash
# From repository root
cd src/mcp_servers

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import mcp; print('MCP SDK installed')"
```

---

## Usage

### Configuring MCP Servers in Claude Code

MCP servers are configured in `.claude/mcp/` directory:

**Example Configuration** (`.claude/mcp/postgres/mcp.json`):

```json
{
  "name": "postgres",
  "version": "1.0.0",
  "command": "python",
  "args": [
    "src/mcp_servers/postgres_mcp.py"
  ],
  "env": {
    "DATABASE_URL": "postgresql://user:pass@localhost:5432/dbname"
  }
}
```

### Running MCP Server Standalone

For development/testing:

```bash
# Run server directly
python src/mcp_servers/postgres_mcp.py

# With debug logging
DEBUG=1 python src/mcp_servers/postgres_mcp.py
```

### Using MCP Servers from Claude Code

Once configured, servers are automatically available:

```
User: "Query the users table in PostgreSQL"
Claude: Uses postgres MCP server → executes query → returns results

User: "Run pytest with coverage"
Claude: Uses pytest + coverage MCP servers → runs tests → reports
```

---

## Creating New MCP Servers

### 1. Choose Template

Start with the MCP SDK template:

```python
# src/mcp_servers/myserver_mcp.py
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("myserver")

@app.list_tools()
async def list_tools():
    return [
        {
            "name": "my_tool",
            "description": "What this tool does",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                },
                "required": ["param1"]
            }
        }
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "my_tool":
        result = do_work(arguments["param1"])
        return {"content": [{"type": "text", "text": result}]}

async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Implement Tools

Each tool should:
- Have clear name and description
- Define JSON schema for inputs
- Validate inputs rigorously
- Handle errors gracefully
- Return structured output

### 3. Add Configuration

Create MCP config in `.claude/mcp/<server-name>/mcp.json`:

```json
{
  "name": "myserver",
  "version": "1.0.0",
  "command": "python",
  "args": ["src/mcp_servers/myserver_mcp.py"],
  "env": {
    "API_KEY": "your-api-key"
  }
}
```

### 4. Test Locally

```bash
# Run server
python src/mcp_servers/myserver_mcp.py

# In Claude Code, test with:
# "Use myserver to <do something>"
```

### 5. Document

Add entry to this README with:
- Server name and file
- Purpose and use cases
- Configuration requirements
- Example usage

---

## Best Practices

### Security

- ✅ **Never hardcode secrets** - Use environment variables
- ✅ **Validate all inputs** - Prevent injection attacks
- ✅ **Sandbox file operations** - Restrict to safe directories
- ✅ **Rate limit API calls** - Prevent abuse
- ❌ **Don't trust user input** - Always sanitize and validate

### Error Handling

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        result = risky_operation(arguments)
        return {"content": [{"type": "text", "text": result}]}
    except ValidationError as e:
        return {"content": [{"type": "text", "text": f"Invalid input: {e}"}], "isError": True}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
```

### Performance

- Use `async/await` for I/O operations
- Implement connection pooling for databases
- Cache expensive computations
- Stream large results instead of loading in memory

### Documentation

Each MCP server should have:

```python
"""
MCP Server: MyServer

Purpose: Brief description of what this server does

Tools:
- my_tool: What it does and when to use it

Environment Variables:
- API_KEY: Required API key for service
- ENDPOINT: Optional custom endpoint (default: https://api.example.com)

Example Usage:
    User: "Use myserver to fetch data"
    Claude: Calls my_tool → returns formatted results
"""
```

---

## Troubleshooting

### Server Not Found

**Problem:** Claude says "No MCP server named X"
**Solution:**
1. Check `.claude/mcp/<server-name>/mcp.json` exists
2. Verify `command` and `args` are correct
3. Restart Claude Code

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'mcp'`
**Solution:**
```bash
pip install -r src/mcp_servers/requirements.txt
```

### Server Crashes on Startup

**Problem:** Server exits immediately
**Solution:**
1. Run manually: `python src/mcp_servers/server_mcp.py`
2. Check for syntax errors or missing dependencies
3. Enable debug logging: `DEBUG=1 python src/mcp_servers/server_mcp.py`

### Tool Not Executing

**Problem:** Tool listed but doesn't execute
**Solution:**
1. Check tool name matches exactly
2. Verify input schema matches arguments
3. Check for errors in `call_tool()` implementation

---

## Contributing

### Adding New Server

1. **Identify need** - What capability is missing?
2. **Check existing servers** - Can existing server be extended?
3. **Create server file** - Use template above
4. **Write tests** - Validate tool behavior
5. **Add configuration** - Create MCP config JSON
6. **Document** - Update this README
7. **Commit** - Follow git workflow

### Updating Existing Server

1. **Maintain compatibility** - Don't break existing tools
2. **Version appropriately** - Bump version in mcp.json
3. **Update docs** - Document new tools/changes
4. **Test thoroughly** - Ensure backward compatibility

---

## Dependencies

Common dependencies for MCP servers:

```
# Core MCP SDK
mcp>=1.0.0

# Common libraries
aiohttp>=3.9.0         # Async HTTP client
asyncio-mqtt>=0.16.0   # MQTT client
pydantic>=2.0.0        # Data validation
python-dotenv>=1.0.0   # .env file support

# Database drivers
psycopg2-binary>=2.9.0  # PostgreSQL
pymongo>=4.0.0          # MongoDB
redis>=5.0.0            # Redis

# Cloud SDKs
boto3>=1.28.0          # AWS
google-cloud>=0.34.0   # GCP
azure-core>=1.28.0     # Azure

# File processing
pandas>=2.0.0          # DataFrames
openpyxl>=3.1.0        # Excel
PyPDF2>=3.0.0          # PDF
```

**Install all:**
```bash
pip install -r src/mcp_servers/requirements.txt
```

---

## Official Resources

- **MCP Documentation:** https://modelcontextprotocol.io/
- **MCP SDK (Python):** https://github.com/modelcontextprotocol/python-sdk
- **Example Servers:** https://github.com/modelcontextprotocol/servers
- **Claude Code MCP Guide:** https://docs.anthropic.com/claude/docs/mcp

---

## See Also

- [MCP Builder Skill](../../.claude/skills/mcp-builder/SKILL.md) - Guide for creating MCP servers
- [MCP SDK Skill](../../.claude/skills/mcp-sdk/SKILL.md) - Using MCP SDK
- [Project README](../../README.md) - Overall toolkit documentation
- [CLAUDE.md](../../CLAUDE.md) - Runtime development guidelines

---

**Maintained by:** SDD Toolkit Team
**Last Updated:** 2026-02-18
**MCP SDK Version:** 1.0+

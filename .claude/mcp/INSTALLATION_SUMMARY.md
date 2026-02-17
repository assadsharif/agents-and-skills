# MCP Servers Installation Summary

**Status:** Ready for use

## What's Included

- **31 MCP servers** in `src/mcp_servers/`
- **Configuration** in `.mcp.json` (project root)
- All servers use relative paths - portable across machines

## Quick Setup

1. Ensure Python 3.11+ is installed
2. Install dependencies: `pip install mcp fastmcp pydantic`
3. Run `claude mcp list` to verify servers are detected

## Using in Other Projects

To use these MCP servers in another project:

1. Copy `src/mcp_servers/` to your project
2. Copy or merge `.mcp.json` entries into your project's `.mcp.json`
3. Install required Python packages

## Server Categories

- **Backend:** FastAPI, Django, SQLModel, Neon DB
- **Frontend:** Next.js, Frontend Design, Theme Factory, ChatKit
- **DevOps:** Docker, Helm, kubectl, Minikube, K8s Deployment
- **Testing:** TDD, Webapp Testing, Quality Enforcer
- **AI:** OpenAI Agents, Prompt Engineer
- **Documents:** PDF, PPTX, Web Content, Web Artifacts
- **Data:** Pandas
- **Social:** LinkedIn, Meta, Twitter/X
- **Utilities:** Token Warden, Venv Manager, Interview, Xero

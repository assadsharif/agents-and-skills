# MCP Servers

This repository includes 31 custom MCP (Model Context Protocol) servers located in `src/mcp_servers/`.

## Server Categories

### Backend & API
| Server | Purpose |
|--------|---------|
| `fastapi_backend_mcp` | FastAPI backend scaffolding and best practices |
| `django_mcp` | Django web framework patterns and scaffolding |
| `sqlmodel_orm_mcp` | SQLModel ORM patterns and database modeling |
| `neon_db_mcp` | Neon serverless PostgreSQL operations |

### Frontend & UI
| Server | Purpose |
|--------|---------|
| `nextjs_app_router_mcp` | Next.js App Router patterns and components |
| `frontend_design_mcp` | Frontend design system and UI patterns |
| `theme_factory_mcp` | Theme generation and design tokens |
| `openai_chatkit_mcp` | OpenAI ChatKit UI components |

### DevOps & Infrastructure
| Server | Purpose |
|--------|---------|
| `docker_containerization_mcp` | Docker containerization and Dockerfile generation |
| `helm_packaging_mcp` | Helm chart packaging for Kubernetes |
| `kubectl_ai_mcp` | Kubernetes kubectl AI-assisted operations |
| `minikube_cluster_mcp` | Minikube local cluster management |
| `k8s_deployment_mcp` | Kubernetes deployment manifests and strategies |
| `kagent_analysis_mcp` | Kubernetes agent analysis tools |

### Testing & Quality
| Server | Purpose |
|--------|---------|
| `tdd_mcp` | Test-Driven Development guidance and test generation |
| `webapp_testing_mcp` | Web application testing strategies |
| `quality_enforcer_mcp` | Code quality enforcement and review |

### AI & Agents
| Server | Purpose |
|--------|---------|
| `openai_agents_mcp` | OpenAI Agents SDK integration |
| `prompt_engineer_mcp` | Prompt engineering patterns and optimization |

### Documents & Content
| Server | Purpose |
|--------|---------|
| `pdf_mcp` | PDF generation and manipulation |
| `pptx_mcp` | PowerPoint presentation generation |
| `web_content_fetch_mcp` | Web content fetching and extraction |
| `web_artifacts_mcp` | Web artifact generation and management |

### Data & Analytics
| Server | Purpose |
|--------|---------|
| `pandas_mcp` | Pandas data analysis and manipulation |

### Social & Integration
| Server | Purpose |
|--------|---------|
| `linkedin_mcp` | LinkedIn integration |
| `meta_social_mcp` | Meta social platform integration |
| `twitter_mcp` | Twitter/X platform integration |
| `xero_accounting_mcp` | Xero accounting integration |

### Utilities
| Server | Purpose |
|--------|---------|
| `token_warden_mcp` | Token management and security |
| `venv_manager_mcp` | Python virtual environment management |
| `interview_mcp` | Technical interview preparation |

## Usage

All servers are configured in the project root `.mcp.json`. When using Claude Code in this project, servers are automatically available.

### Check Status
```bash
claude mcp list
```

### Add a New Server
1. Create `src/mcp_servers/your_server_mcp.py`
2. Add entry to `.mcp.json`
3. Restart Claude Code

## Requirements

- Python 3.11+
- `mcp` or `fastmcp` package installed
- Server-specific dependencies (check individual server files)

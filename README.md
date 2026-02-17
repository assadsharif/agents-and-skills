# SDD Toolkit

**Spec-Driven Development (SDD) Toolkit** — A comprehensive system for feature-driven development with Claude Code, including 31 MCP servers, 16 autonomous agents, 52+ skills, and templates/scripts for structured workflows.

## Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd agents-and-skills

# 2. Set up Python virtual environment
source .venv/bin/activate

# 3. Install dependencies (already set up)
pip install -r requirements.txt

# 4. Start using SDD workflows
# See .claude/agents/README.md for agent usage
```

## What's Included

### Core Components

- **16 Autonomous Agents** (`.claude/agents/`) - Specialized agents for SDD workflow stages
- **52+ Skills** (`.claude/skills/`) - Reusable capabilities for common development tasks
- **31 MCP Servers** (`src/mcp_servers/`) - Python-based MCP servers for specialized integrations
- **SDD Templates** (`.specify/templates/`) - Spec, plan, tasks, ADR, and PHR templates
- **Bash Scripts** (`.specify/scripts/bash/`) - Automation for PHR, ADR, and feature workflows
- **Constitution** (`.specify/memory/constitution.md`) - Project principles and quality gates

### SDD Workflow

The toolkit follows a structured development workflow:

1. **Specify** (`/sp.specify`) - Create feature specifications
2. **Plan** (`/sp.plan`) - Generate technical implementation plans
3. **Tasks** (`/sp.tasks`) - Break plans into ordered, testable tasks
4. **Implement** (`/sp.implement`) - Execute tasks with TDD
5. **Review** (`/sp.git.commit_pr`) - Commit and create pull requests

Supporting workflows:
- `/sp.clarify` - Clarify underspecified requirements
- `/sp.analyze` - Validate cross-artifact consistency
- `/sp.adr` - Document architectural decisions
- `/sp.phr` - Record prompt history for learning

## Project Structure

```
.
├── .claude/
│   ├── agents/          # Autonomous agents (sdd-*, github-workflow, etc.)
│   ├── skills/          # Reusable skills (TDD, mcp-builder, frontend-design, etc.)
│   └── mcp/             # MCP integration configs
├── .specify/
│   ├── memory/          # Constitution and project memory
│   ├── templates/       # Feature artifact templates
│   └── scripts/bash/    # Automation scripts
├── history/
│   ├── prompts/         # Prompt History Records (PHRs)
│   └── adr/             # Architecture Decision Records
├── specs/               # Feature specifications (organized by feature)
├── src/
│   └── mcp_servers/     # 31 MCP server implementations
├── CLAUDE.md            # Claude Code runtime instructions
├── requirements.txt     # Core Python dependencies
└── README.md            # This file
```

## Key Agents

### SDD Core Workflow Agents

- **sdd-specify** - Feature specification creation from natural language
- **sdd-plan** - Technical planning and architecture design
- **sdd-tasks** - Task generation with dependency ordering
- **sdd-implement** - Implementation execution with TDD
- **sdd-git-commit-pr** - Git workflows and PR creation

### Supporting Agents

- **sdd-clarify** - Requirement clarification through targeted questions
- **sdd-analyze** - Cross-artifact consistency and quality validation
- **sdd-adr** - Architecture Decision Record creation
- **sdd-phr** - Prompt History Record creation for learning
- **sdd-constitution** - Project constitution management
- **sdd-checklist** - Custom validation checklist generation
- **sdd-reverse-engineer** - Extract specs from existing code
- **sdd-taskstoissues** - Convert tasks to GitHub issues

Full agent documentation: [`.claude/agents/README.md`](.claude/agents/README.md)

## MCP Servers

31 specialized MCP servers covering:

- **Backend**: FastAPI, Django, SQLModel ORM, Neon DB
- **Frontend**: Next.js, Docusaurus, Frontend Design, Theme Factory
- **DevOps**: Docker, Kubernetes, Helm, Minikube, kubectl-ai
- **Testing**: TDD, Webapp Testing, Quality Enforcer
- **AI/ML**: OpenAI Agents SDK, OpenAI ChatKit, Prompt Engineer
- **Development**: Web Content Fetch, PDF, PPTX, Pandas
- **Social**: LinkedIn, Twitter, Meta Social
- **Other**: Venv Manager, Token Warden, Interview Prep, Xero Accounting

Configuration: [`.mcp.json`](.mcp.json)

## Constitution

The project follows strict development principles defined in `.specify/memory/constitution.md`:

1. **Spec-Driven Development** - All features start with approved specs
2. **Test-First (TDD)** - Mandatory red-green-refactor cycle
3. **Smallest Viable Diff** - Minimum necessary changes only
4. **Traceability** - All work linked through artifacts (PHRs, ADRs)
5. **Security by Default** - No hardcoded secrets, validate at boundaries
6. **Simplicity (YAGNI)** - No premature abstraction or complexity

## Usage Examples

### Create a New Feature

```bash
# 1. Create specification
/sp.specify "Add user authentication with OAuth2"

# 2. Generate implementation plan
/sp.plan

# 3. Generate tasks
/sp.tasks

# 4. Execute implementation
/sp.implement

# 5. Commit and create PR
/sp.git.commit_pr "Complete user authentication"
```

### Review and Analyze

```bash
# Validate cross-artifact consistency
/sp.analyze

# Create architectural decision record
/sp.adr "jwt-vs-session-authentication"

# Generate custom security checklist
/sp.checklist "Create security validation checklist"
```

## Dependencies

Core dependencies (installed in `.venv/`):

```
mcp>=1.0.0              # FastMCP framework
pydantic>=2.0.0         # Data validation
httpx>=0.27.0           # Async HTTP client
pyyaml>=6.0.0           # YAML parsing
anthropic>=0.40.0       # Anthropic API client
```

## Contributing

When creating new components:

1. **Agents**: Follow structure in existing agents, include comprehensive AGENT.md
2. **Skills**: Use `/skill-creator` or `/skill-creator-pro` for consistent structure
3. **MCP Servers**: Follow FastMCP patterns, include tool documentation
4. **Templates**: Maintain YAML frontmatter, use consistent placeholders

## License

[Add your license here]

## Support

- [Open an issue](https://github.com/your-org/your-repo/issues)
- See `.claude/agents/README.md` for detailed agent documentation
- Check `CLAUDE.md` for runtime development guidelines

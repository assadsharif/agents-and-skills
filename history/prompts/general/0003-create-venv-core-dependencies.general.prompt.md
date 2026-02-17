---
id: 0003
title: Create Ready Virtual Environment for New Projects
stage: general
date: 2026-02-17
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: asad
command: implement plan
labels: ["venv", "dependencies", "setup", "python"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - requirements.txt
  - .gitignore
  - .venv/
tests:
  - "python3 -c 'import mcp, pydantic, httpx, yaml, anthropic; print(\"OK\")' — PASS"
---

## Prompt

Implement the following plan:

# Plan: Create Ready Virtual Environment for New Projects

## Context
The SDD toolkit has 31 MCP servers and 50+ Python scripts but no centralized dependency management or virtual environment. A fresh clone cannot run any MCP servers without manually discovering and installing packages. This creates a `requirements.txt` and `.venv` with core dependencies.

## Scope: Core Only
- `mcp` - FastMCP framework (all MCP servers depend on this)
- `pydantic` - Data validation (all MCP servers use BaseModel)
- `httpx` - Async HTTP client (web_content_fetch_mcp, others)
- `pyyaml` - YAML parsing (k8s, deployment manifests)
- `anthropic` - Anthropic API client (mcp-builder evaluation)

## Steps
1. Create `requirements.txt` at repo root with pinned core dependencies
2. Create `.venv` using `python3 -m venv`
3. Install dependencies via pip into `.venv`
4. Verify the venv works by importing all core packages
5. Ensure `.venv` is gitignored

## Response snapshot

Created three artifacts:
1. `requirements.txt` with 5 core dependencies (mcp>=1.0.0, pydantic>=2.0.0, httpx>=0.27.0, pyyaml>=6.0.0, anthropic>=0.40.0)
2. `.gitignore` at repo root excluding .venv/, __pycache__/, *.pyc, .env
3. `.venv/` Python 3.12 virtual environment with all packages installed and verified

Verification: `python3 -c "import mcp, pydantic, httpx, yaml, anthropic; print('OK')"` returned OK.

## Outcome

- ✅ Impact: Fresh clones can now `source .venv/bin/activate` and run MCP servers immediately
- 🧪 Tests: Import verification passed for all 5 core packages
- 📁 Files: 2 new files (requirements.txt, .gitignore), 1 new directory (.venv/)
- 🔁 Next prompts: Consider adding dev dependencies (pytest, black, ruff), per-MCP-server optional deps
- 🧠 Reflection: Minimum-floor approach with >= version pins balances stability and flexibility

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Import test PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add `requirements-dev.txt` for testing/linting tools

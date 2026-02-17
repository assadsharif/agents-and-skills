---
id: "0001"
title: SDD Toolkit Reuse Readiness Analysis
stage: general
date: 2026-02-17
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: Asad Sharif
command: /sp.analyze
labels: ["analysis", "quality", "reuse-readiness", "toolkit", "audit"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/phr-template.prompt.md
  - .specify/templates/spec-template.md
  - .specify/templates/plan-template.md
  - .specify/templates/tasks-template.md
  - .specify/templates/adr-template.md
  - .specify/templates/agent-file-template.md
  - .specify/templates/checklist-template.md
  - .specify/scripts/bash/common.sh
  - .specify/scripts/bash/create-phr.sh
  - .specify/scripts/bash/create-adr.sh
  - .specify/scripts/bash/create-new-feature.sh
  - .specify/scripts/bash/check-prerequisites.sh
  - .specify/scripts/bash/setup-plan.sh
  - .specify/scripts/bash/update-agent-context.sh
  - .claude/agents/rag-orchestration/AGENT.md
  - .claude/agents/sdd-specify/AGENT.md
  - .claude/agents/sdd-constitution/AGENT.md
  - .claude/agents/sdd-git-commit-pr/AGENT.md
  - .claude/settings.local.json
  - .mcp.json
  - CLAUDE.md
tests: []
---

## Prompt

check everything is up to date and well optimized before using to new project or in another project

## Response snapshot

Performed comprehensive analysis across 8 areas: templates, constitution, scripts, agents, skills, directory structure, CLAUDE.md, and settings. Generated a 20-finding structured report with severity ratings, locations, issues, and recommendations.

Key findings:
- CRITICAL: constitution.md is entirely unfilled raw template
- CRITICAL: history/prompts/, history/adr/, specs/ directories missing
- CRITICAL: .mcp.json uses relative paths for 32 MCP servers
- HIGH: rag-orchestration agent references 2 missing skills (rag-chatbot, signup-personalization)
- HIGH: 10 fte-* skills are domain-specific to one product, not generic SDD
- MEDIUM: Placeholder style inconsistency ({{double-brace}} vs [bracket]) across templates
- MEDIUM: sdd-git-commit-pr hardcodes "Claude Sonnet 4.5" in 6 places
- LOW: TDD-Skill uses wrong casing convention, PHR template has emojis, misc typos

Also created history/prompts/general/ directory as part of remediation.

## Outcome

- Impact: 20 findings across 8 areas; toolkit is usable but needs 6 actions before first use in a new project
- Tests: no tests run (analysis task)
- Files: history/prompts/general/ directory created; no other files modified
- Next prompts: Fix constitution, fix directory bootstrap, remove/fix rag-orchestration references, add root README.md
- Reflection: The scripts are the strongest part of the toolkit - fully portable. The constitution being entirely unfilled is the most critical gap since all plan checks reference it.

## Evaluation notes (flywheel)

- Failure modes observed: none - all file reads succeeded
- Graders run and results (PASS/FAIL): n/a (analysis task, no code changed)
- Prompt variant (if applicable): initial analysis
- Next experiment: add a bootstrap `make init` or setup script that creates required directories and validates constitution is filled

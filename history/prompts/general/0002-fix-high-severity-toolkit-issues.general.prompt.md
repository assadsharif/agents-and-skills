---
id: "0002"
title: Fix High Severity Toolkit Issues
stage: general
date: 2026-02-17
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: asad
command: /sp.analyze (follow-up fix)
labels: ["fix", "high-severity", "rag-orchestration", "chatkit", "fte-skills"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/rag-orchestration/AGENT.md (deleted)
  - .claude/agents/README.md
  - .claude/agents/mcp/chatkit/README.md
  - .claude/mcp/chatkit/README.md
  - .claude/mcp/better-auth/README.md
  - .claude/agents/mcp/better-auth/README.md
  - .claude/skills-examples/README.md (created)
  - .claude/skills/fte-* (moved to .claude/skills-examples/)
tests: []
---

## Prompt

fix the remaining high severity issues

## Response snapshot

Fixed all 3 HIGH severity issues from the analysis report:

H1: Removed project-specific `rag-orchestration` agent entirely (AGENT.md deleted, reference removed from agents README). It was extracted from a specific project's `specs/001-rag-chatbot/` and referenced non-existent `rag-chatbot` skill.

H2: Cleaned dead skill references across 4 files (chatkit README x2, better-auth README x2). Removed all links to non-existent paths: `.claude/skills/rag-chatbot/`, `.claude/skills/signup-personalization/`, `.claude/skills/chatkit-widget/patterns.md`, `.claude/agents/rag-orchestration/`.

H3: Moved all 10 `fte-*` domain-specific skills from `.claude/skills/` to `.claude/skills-examples/` with a README explaining they are reference implementations for an "AI Employee" product, not core SDD toolkit components.

## Outcome

- Impact: 3 HIGH issues resolved; toolkit now has zero project-specific artifacts in core paths
- Tests: none (documentation/structure changes only)
- Files: 1 directory deleted, 4 files edited, 10 skill directories relocated, 1 README created
- Next prompts: Fix medium severity issues (placeholder standardization, error messages, model version hardcoding)
- Reflection: WSL cross-filesystem `mv` fails with permission denied; use `cp -r` + `rm -rf` pattern instead

## Evaluation notes (flywheel)

- Failure modes observed: `mv` across WSL filesystems fails; fallback to cp+rm worked
- Graders run and results (PASS/FAIL): n/a (structural changes, no code)
- Prompt variant (if applicable): initial
- Next experiment: verify remaining dangling references with grep after all fixes complete

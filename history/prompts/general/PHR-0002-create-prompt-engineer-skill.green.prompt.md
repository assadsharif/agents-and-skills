---
id: PHR-0002
title: Create Prompt Engineer Skill
stage: green
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: asad
command: user-request
labels: [prompt-engineering, skill, mcp-server, green]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/prompt-engineer/SKILL.md
  - .claude/skills/prompt-engineer/references/techniques.md
  - .claude/skills/prompt-engineer/references/anti-patterns.md
  - .claude/skills/prompt-engineer/references/model-config.md
  - .claude/skills/prompt-engineer/references/templates.md
  - /mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0/src/mcp_servers/prompt_engineer_mcp.py
  - .mcp.json
tests:
  - MCP server loads successfully with 7 tools
  - Skill validation: 90.4/100 (PASS - production rating)
  - All reference files created and well-structured
---

## Prompt

Create a skill named prompt engineer read this docs https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, use of C:\Users\HomePC\Desktop\CODE\Backend API project\.claude\skills\skill-creator-pro if needed use sub skills in it with markdown format as well, and also validate using of C:\Users\HomePC\Desktop\CODE\Backend API project\.claude\skills\skill-validator and also create MCP server using of C:\Users\HomePC\Desktop\CODE\Backend API project\.claude\skills\mcp-builder and C:\Users\HomePC\Desktop\CODE\Backend API project\.claude\skills\mcp-code-execution and C:\Users\HomePC\Desktop\CODE\Backend API project\.claude\skills\mcp-sdk and C:\Users\HomePC\Desktop\CODE\Backend API project\.claude\skills\memory-mcp, and if needed plugin this skill in Agent.

## Response snapshot

Created the complete prompt-engineer skill with 6 files:

**SKILL.md** (163 lines): Main skill file with frontmatter, 5-step workflow (Understand Goal, Select Techniques, Draft Prompt, Validate, Deliver), model-specific notes for Opus 4.6/Sonnet 4.5/Haiku 4.5, quick reference table, and anti-pattern checklist.

**references/techniques.md**: 19 techniques from Claude's official best practices — explicit instructions, context motivation, XML tags, tool usage, parallel calling, autonomy balance, hallucination prevention, state tracking, over-engineering prevention, format control, research, subagent orchestration, anti-overthinking, model identity, verbosity control, file creation control.

**references/anti-patterns.md**: 15 anti-patterns with detection, severity, and fixes — vague instructions, over-prompting, 'think' sensitivity, prefill dependency, negative-only instructions, missing context, aggressive tool language, hard-coded solutions, injection vulnerability.

**references/model-config.md**: API configuration guide — model IDs, thinking modes (enabled/adaptive), budget guidelines, reasoning effort, temperature, max tokens, streaming, tool use config, 4 configuration recipes.

**references/templates.md**: 13 composable prompt templates — general agent, code agent, research agent, accuracy-critical, prose output, JSON output, long-horizon tasks, autonomy balance, parallel tools, minimalism, anti-overthinking, error handling, security-aware, plus composition guide.

**MCP Server** (prompt_engineer_mcp.py): FastMCP server with 7 tools — prompt_analyze, prompt_optimize, prompt_generate_template, prompt_validate, prompt_diagnose_issues, prompt_recommend_config, prompt_generate_system. Registered in .mcp.json.

## Outcome

- Impact: Full prompt engineering skill created — Claude can now craft, analyze, optimize, and debug prompts using official best practices
- Tests: MCP server loads with 7 tools; Skill validation scored 90.4/100 (PASS)
- Files: 7 files created/modified
- Next prompts: Test skill with /prompt-engineer command, verify MCP tools work end-to-end
- Reflection: Skill-creator-pro pattern worked well for structuring the skill; reference files keep SKILL.md concise

## Evaluation notes (flywheel)

- Failure modes observed: None — clean creation
- Graders run and results (PASS/FAIL): Skill validation PASS (90.4/100), MCP import PASS (7/7 tools)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add source URLs to Anthropic documentation for verification

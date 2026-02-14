---
id: PHR-0003
title: Create Pandas Skill
stage: green
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: asad
command: user-request
labels: [pandas, skill, mcp-server, data-analysis, green]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/pandas/SKILL.md
  - .claude/skills/pandas/references/core-operations.md
  - .claude/skills/pandas/references/data-cleaning.md
  - .claude/skills/pandas/references/aggregation.md
  - .claude/skills/pandas/references/io-guide.md
  - .claude/skills/pandas/references/performance.md
  - /mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0/src/mcp_servers/pandas_mcp.py
  - .mcp.json
tests:
  - MCP server loads successfully with 8 tools (no warnings)
  - Skill validation: 78/100 (PASS - Good rating)
  - All reference files created and well-structured
---

## Prompt

Create a skill named pandas, read this https://pandas.pydata.org/docs/ use of skill-creator-pro and also validate using skill-validator, and also create MCP server using mcp-builder, mcp-code-execution, mcp-sdk, and memory-mcp, and if needed plugin this skill in Agent.

## Response snapshot

Created the complete pandas skill with 7 files:

**SKILL.md** (129 lines): Main skill file with 5-step workflow (Understand Data, Choose Operation, Generate Code, Validate, Optimize), quick reference table of common patterns, Must Avoid anti-patterns, performance tips, and reference file table.

**references/core-operations.md**: DataFrame/Series creation, .loc/.iloc indexing, boolean indexing, query(), where/mask, setting values, sorting, column operations, sampling, duplicates, key gotchas.

**references/data-cleaning.md**: Missing data (detection, dropping, filling, replacing), type conversion (numeric, datetime, nullable types), string operations (case, whitespace, substring, replace, split), data quality checks, common cleaning pipeline pattern.

**references/aggregation.md**: GroupBy (named aggregation, transform, filter), merge/join (all join types, merge_asof), pivot tables, reshaping (melt, stack/unstack, explode, crosstab), window functions (rolling, expanding, ewm, shift).

**references/io-guide.md**: Format overview (CSV, Excel, JSON, Parquet, SQL, Feather, Pickle, HTML, Clipboard), detailed read/write parameters for each format, remote/compressed file support, best practices.

**references/performance.md**: Vectorization patterns, memory optimization (categorical, downcasting, nullable types), efficient patterns (build-then-concat, pipe, query, eval), anti-patterns (iterrows, chained indexing, inplace, object dtype), benchmarking, when to use alternatives.

**MCP Server** (pandas_mcp.py): FastMCP server with 8 tools — pandas_generate_read, pandas_generate_transform, pandas_generate_aggregate, pandas_generate_merge, pandas_generate_io, pandas_detect_antipatterns, pandas_optimize_code, pandas_generate_pipeline. Registered in .mcp.json.

## Outcome

- Impact: Full pandas data manipulation skill — Claude can generate, analyze, and optimize pandas code
- Tests: MCP server loads with 8 tools; Skill validation scored 78/100 (PASS)
- Files: 8 files created/modified
- Next prompts: Test skill with /pandas command, consider adding clarification questions per validator recommendations
- Reflection: Comprehensive reference files make the skill immediately practical for data analysis tasks

## Evaluation notes (flywheel)

- Failure modes observed: BaseModel field name "validate" shadowed parent attribute — renamed to merge_validate
- Graders run and results (PASS/FAIL): Skill validation PASS (78/100), MCP import PASS (8/8 tools, 0 warnings)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add structured clarification questions section to improve interaction score

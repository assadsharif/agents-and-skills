# Skills Examples

This directory contains **domain-specific skill examples** that are not part of the core SDD toolkit. They demonstrate how to build specialized skills for a particular product or workflow.

## FTE (Full-Time Employee AI) Skills

These 10 skills were built for a specific "AI Employee" product that manages tasks through an Obsidian vault. They are included as reference implementations, not as reusable toolkit components.

| Skill | Purpose |
|-------|---------|
| `fte-vault-init` | Initialize Obsidian vault with canonical folder layout |
| `fte-vault-status` | Display task counts and vault health |
| `fte-vault-validate` | Validate vault structure and state transitions |
| `fte-task-triage` | Classify and route inbox tasks |
| `fte-approval-review` | Present pending approvals for decision |
| `fte-briefing-generate` | Generate CEO briefings from vault data |
| `fte-health-check` | Run system-wide health diagnostics |
| `fte-orchestrator-status` | Show orchestrator liveness and metrics |
| `fte-security-scan` | Scan vault for secrets and sensitive data |
| `fte-watcher-status` | Display watcher health (Gmail, WhatsApp, etc.) |

## Using These as Templates

To create your own domain-specific skills, use these as structural references and the `/skill-creator` or `/skill-creator-pro` skills for guided creation.

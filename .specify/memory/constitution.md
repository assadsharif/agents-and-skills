# SDD Toolkit Constitution

## Core Principles

### I. Spec-Driven Development
Every feature MUST begin with a specification (`spec.md`) before any code is written. Specifications define requirements, acceptance criteria, and scope boundaries. No implementation work proceeds without an approved spec.

### II. Test-First (NON-NEGOTIABLE)
TDD is mandatory for all implementation work. Tests written first, approved by user, confirmed to fail (red), then implementation to pass (green), then refactor. Red-Green-Refactor cycle strictly enforced.

### III. Smallest Viable Diff
Every change MUST be the minimum necessary to satisfy the requirement. No speculative features, no unrelated refactoring, no premature abstractions. Three similar lines of code is better than a premature helper.

### IV. Traceability
All work MUST be traceable: specs link to plans, plans link to tasks, tasks link to commits, and Prompt History Records (PHRs) capture every significant interaction. Architecture Decision Records (ADRs) document significant decisions.

### V. Security by Default
Never hardcode secrets or tokens; use environment variables and `.env` files. Validate at system boundaries. Follow OWASP top 10 guidelines. Secrets files (`.env`, credentials) MUST be gitignored.

### VI. Simplicity (YAGNI)
Start simple. Do not design for hypothetical future requirements. Only add complexity when current requirements demand it. Prefer explicit over clever. Prefer readable over compact.

## Quality Gates

- All specs MUST have measurable acceptance criteria
- All plans MUST reference the spec they implement
- All tasks MUST be independently testable
- All code changes MUST pass existing tests before merge
- All PRs MUST reference the originating task or spec
- Constitution violations are CRITICAL and block implementation

## Development Workflow

1. **Specify** (`/sp.specify`): Create feature spec from natural language
2. **Plan** (`/sp.plan`): Generate architecture and implementation plan
3. **Tasks** (`/sp.tasks`): Break plan into ordered, testable tasks
4. **Implement** (`/sp.implement`): Execute tasks with TDD
5. **Review** (`/sp.git.commit_pr`): Commit and create PR

Each stage validates against the previous. Skipping stages requires explicit user consent.

## Governance

- This constitution supersedes all other development practices within its scope
- Amendments require explicit documentation and user approval
- All PRs and reviews MUST verify compliance with these principles
- Complexity MUST be justified against the Simplicity principle
- See `CLAUDE.md` for runtime development guidance

**Version**: 1.0.0 | **Ratified**: 2026-02-17 | **Last Amended**: 2026-02-17

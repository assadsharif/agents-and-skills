---
id: PHR-0004
title: Create Django Skill
stage: green
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: asad
command: user-request
labels: [django, skill, mcp-server, web-framework, green]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/django/SKILL.md
  - .claude/skills/django/references/models-orm.md
  - .claude/skills/django/references/views.md
  - .claude/skills/django/references/urls-routing.md
  - .claude/skills/django/references/forms-admin.md
  - .claude/skills/django/references/settings-deployment.md
  - /mnt/c/Users/HomePC/Desktop/CODE/Personal AI Employee Hackathon 0/src/mcp_servers/django_mcp.py
  - .mcp.json
tests:
  - MCP server loads successfully with 8 tools (no warnings)
  - Skill validation: 88.8/100 (PASS - Production rating)
  - All reference files created and well-structured
---

## Prompt

Create a skill named Django, read this https://docs.djangoproject.com/en/6.0/ use of skill-creator-pro and also validate using skill-validator, and also create MCP server using mcp-builder, mcp-code-execution, mcp-sdk, and memory-mcp, and if needed plugin this skill in Agent.

## Response snapshot

Created the complete Django 6.0 skill with 8 files:

**SKILL.md** (117 lines): Main skill file with 5-step workflow (Understand Requirements, Choose Pattern, Generate Code, Validate, Optimize), quick reference table of Django CLI commands, Must Avoid anti-patterns, performance tips, and reference file table.

**references/models-orm.md**: Model definition, field types (16 types), field options, relationships (ForeignKey, ManyToMany with through, OneToOne), QuerySet API (CRUD, lookups, F/Q expressions, aggregation), custom managers, model inheritance (abstract, multi-table, proxy), migrations and data migrations.

**references/views.md**: Function-based views (GET/POST, JSON, decorators), class-based views (View, TemplateView), generic CRUD views (ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, RedirectView), mixins (LoginRequired, PermissionRequired, UserPassesTest, custom), async views, error handlers, response types.

**references/urls-routing.md**: Basic URL configuration, path converters (str, int, slug, uuid, path), custom converters, re_path, includes with namespaces, reverse URL resolution (Python, templates), REST-style patterns, API versioning, static/media files.

**references/forms-admin.md**: Basic forms, ModelForm with widgets/labels/validation, form usage in views/templates, field types table, formsets (basic, model, inline), admin registration (ModelAdmin, list_display, filters, search, fieldsets, inlines, actions, custom methods), custom validators.

**references/settings-deployment.md**: Split settings pattern (base/dev/prod), database configuration (SQLite, PostgreSQL, MySQL, dj-database-url), custom middleware, security checklist, WSGI/ASGI, Gunicorn deployment, Docker deployment, management commands, testing.

**MCP Server** (django_mcp.py): FastMCP server with 8 tools — django_generate_model, django_generate_view, django_generate_urls, django_generate_form, django_generate_admin, django_generate_settings, django_detect_antipatterns, django_generate_test. Registered in .mcp.json.

## Outcome

- Impact: Full Django 6.0 web framework skill — Claude can generate models, views, URLs, forms, admin, settings, and detect anti-patterns
- Tests: MCP server loads with 8 tools (0 warnings); Skill validation scored 88.8/100 (PASS)
- Files: 8 files created/modified
- Next prompts: Test skill with Django project, consider adding clarification questions per validator recommendations
- Reflection: Comprehensive reference files covering all major Django components; high validation score indicates production-quality skill

## Evaluation notes (flywheel)

- Failure modes observed: FastMCP() rejected version parameter; non-raw string escape sequences in regex patterns
- Graders run and results (PASS/FAIL): Skill validation PASS (88.8/100), MCP import PASS (8/8 tools, 0 warnings)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add pre-generation clarification questions to improve Interaction category score

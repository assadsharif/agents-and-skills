---
name: django
description: >
  Expert Django 6.0 web framework guidance. Generate models, views, URLs, forms,
  admin, templates, middleware, and deployment configurations. Triggers on:
  django, model, queryset, view, cbv, fbv, urlpattern, orm, migration, admin,
  middleware, template, form, serializer, settings, deployment, wsgi, asgi
---

# Django 6.0 Skill

Generate production-grade Django code following official best practices.

## Workflow

### Step 1: Understand Requirements

Identify what the user needs:
- **Models/ORM**: Data modeling, relationships, queries, migrations
- **Views**: Function-based (FBV) or class-based (CBV), API responses
- **URLs**: Routing, converters, namespaces, includes
- **Forms**: Validation, ModelForm, formsets, widgets
- **Admin**: ModelAdmin, customization, inlines, actions
- **Auth**: Users, permissions, groups, decorators
- **Config**: Settings, middleware, deployment, ASGI/WSGI

### Step 2: Choose Pattern

| Need | Pattern | When |
|------|---------|------|
| CRUD pages | Generic CBVs (ListView, DetailView, CreateView, UpdateView, DeleteView) | Standard model operations |
| Custom logic | Function-based views | Complex workflows, non-standard responses |
| API endpoints | JsonResponse + FBV or DRF | REST API without templates |
| Data modeling | Models + Managers + QuerySets | Database schema design |
| Background tasks | Celery + Django | Async processing |
| Real-time | Django Channels | WebSockets, SSE |
| Full-text search | SearchVector + SearchQuery | PostgreSQL text search |

### Step 3: Generate Code

Apply Django conventions:
- Fat models, thin views (business logic in models/managers)
- Use `get_object_or_404()` not manual try/except
- Prefer `reverse()` and named URLs over hardcoded paths
- Use class-based views for standard CRUD, FBVs for custom logic
- Always validate with forms/serializers at boundaries

### Step 4: Validate

Check against Django best practices:
- [ ] Models have `__str__()` and `Meta` class
- [ ] Views handle GET/POST correctly
- [ ] URLs use `path()` with typed converters
- [ ] Forms validate all user input
- [ ] Settings split: base, dev, production
- [ ] No raw SQL unless absolutely necessary
- [ ] Migrations are forward-compatible
- [ ] Admin registered for all models

### Step 5: Optimize

Apply performance patterns:
- `select_related()` for FK, `prefetch_related()` for M2M
- `only()` / `defer()` for partial field loading
- Database indexes on filtered/ordered fields
- `QuerySet.iterator()` for large result sets
- Cache with `@cache_page` or low-level cache API
- `bulk_create()` / `bulk_update()` for batch operations

## Quick Reference

| Task | Code |
|------|------|
| New project | `django-admin startproject mysite` |
| New app | `python manage.py startapp myapp` |
| Run server | `python manage.py runserver` |
| Make migrations | `python manage.py makemigrations` |
| Apply migrations | `python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Shell | `python manage.py shell` |
| Collect static | `python manage.py collectstatic` |
| Run tests | `python manage.py test` |
| Check deployment | `python manage.py check --deploy` |

## Must Avoid

- **N+1 queries**: Always use `select_related()` / `prefetch_related()`
- **Logic in views**: Move business logic to models or services
- **Hardcoded URLs**: Use `reverse()` and `{% url %}` tag
- **Raw user input in queries**: Use ORM or parameterized queries
- **`settings.py` for secrets**: Use environment variables
- **`DEBUG=True` in production**: Split settings by environment
- **Ignoring migrations**: Always create and apply migrations
- **`objects.all()` in templates**: Query in views, pass via context

## Performance Tips

| Tip | Impact |
|-----|--------|
| `select_related` / `prefetch_related` | Eliminates N+1 queries |
| Database indexes | 10-100x faster filtered queries |
| `only()` / `defer()` | Reduces memory for large models |
| `iterator()` | Streams large querysets |
| `bulk_create` / `bulk_update` | Batch DB operations |
| Template fragment caching | Reduces template rendering time |
| `@cache_page` decorator | Full page caching |

## Reference Files

| File | Content |
|------|---------|
| [models-orm.md](references/models-orm.md) | Models, fields, relationships, querysets, managers |
| [views.md](references/views.md) | FBVs, CBVs, generic views, mixins, async views |
| [urls-routing.md](references/urls-routing.md) | URL patterns, converters, namespaces, includes |
| [forms-admin.md](references/forms-admin.md) | Forms, ModelForm, formsets, admin customization |
| [settings-deployment.md](references/settings-deployment.md) | Settings, middleware, security, ASGI/WSGI, deployment |

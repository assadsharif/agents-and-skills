"""Django MCP Server — Generate Django code patterns and detect anti-patterns."""

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

mcp = FastMCP("django_mcp")

# ── Constants ──────────────────────────────────────────────────────────────

FIELD_TYPES = {
    "string": "CharField(max_length=255)",
    "text": "TextField()",
    "integer": "IntegerField()",
    "float": "FloatField()",
    "decimal": "DecimalField(max_digits=10, decimal_places=2)",
    "boolean": "BooleanField(default=False)",
    "date": "DateField()",
    "datetime": "DateTimeField()",
    "email": "EmailField()",
    "url": "URLField()",
    "slug": "SlugField(unique=True)",
    "uuid": "UUIDField(default=uuid.uuid4, editable=False)",
    "file": "FileField(upload_to='uploads/')",
    "image": "ImageField(upload_to='images/')",
    "json": "JSONField(default=dict, blank=True)",
    "ip": "GenericIPAddressField()",
    "money": "DecimalField(max_digits=12, decimal_places=2)",
}

RELATIONSHIP_TYPES = {
    "fk": "ForeignKey",
    "m2m": "ManyToManyField",
    "o2o": "OneToOneField",
}

ON_DELETE_OPTIONS = ["CASCADE", "PROTECT", "SET_NULL", "SET_DEFAULT", "DO_NOTHING"]

VIEW_TYPES = {
    "list": "ListView",
    "detail": "DetailView",
    "create": "CreateView",
    "update": "UpdateView",
    "delete": "DeleteView",
    "form": "FormView",
    "template": "TemplateView",
    "redirect": "RedirectView",
}

ANTI_PATTERNS = [
    {
        "name": "N+1 queries",
        "indicators": [r"\.all\(\)", r"for .* in .*\.objects", r"for .* in .*queryset"],
        "severity": "high",
        "fix": "Use select_related() for FK/O2O, prefetch_related() for M2M/reverse FK",
    },
    {
        "name": "Logic in views",
        "indicators": [r"def (get|post)\(.*\):.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n"],
        "severity": "medium",
        "fix": "Move business logic to model methods, managers, or service layer",
    },
    {
        "name": "Hardcoded URLs",
        "indicators": [r'href="/', r"redirect\([\"']/", r'action="/', r"HttpResponseRedirect\([\"']/"],
        "severity": "medium",
        "fix": "Use reverse() in Python, {% url %} in templates",
    },
    {
        "name": "Missing CSRF",
        "indicators": [r"@csrf_exempt", r"csrf_exempt"],
        "severity": "high",
        "fix": "Remove @csrf_exempt; use {% csrf_token %} in forms",
    },
    {
        "name": "DEBUG in production",
        "indicators": [r"DEBUG\s*=\s*True(?!.*dev|.*local|.*test)"],
        "severity": "critical",
        "fix": "Set DEBUG=False in production; use environment variable",
    },
    {
        "name": "Secret key exposed",
        "indicators": [r"SECRET_KEY\s*=\s*[\"'][^{]"],
        "severity": "critical",
        "fix": "Use os.environ['DJANGO_SECRET_KEY'] or django-environ",
    },
    {
        "name": "Raw SQL injection risk",
        "indicators": [r"\.raw\(.*%s", r"\.extra\(", r"cursor\.execute\(.*format\(", r"cursor\.execute\(.*%"],
        "severity": "critical",
        "fix": "Use ORM queries or parameterized raw SQL with %s placeholders",
    },
    {
        "name": "Missing model __str__",
        "indicators": [r"class \w+\(models\.Model\)(?![\s\S]*def __str__)"],
        "severity": "low",
        "fix": "Add __str__() method to all models for admin/debug readability",
    },
    {
        "name": "No Meta ordering",
        "indicators": [r"class \w+\(models\.Model\)(?![\s\S]*class Meta)"],
        "severity": "low",
        "fix": "Add Meta class with ordering, verbose_name, indexes",
    },
    {
        "name": "objects.all() in template context",
        "indicators": [r"\.objects\.all\(\).*context", r"context\[.*\]\s*=.*\.objects\.all\(\)"],
        "severity": "medium",
        "fix": "Filter and limit querysets in views; avoid passing .all() to templates",
    },
]

MIDDLEWARE_ORDER = [
    "SecurityMiddleware",
    "WhiteNoiseMiddleware",
    "SessionMiddleware",
    "CorsMiddleware",
    "CommonMiddleware",
    "CsrfViewMiddleware",
    "AuthenticationMiddleware",
    "MessageMiddleware",
    "XFrameOptionsMiddleware",
]


# ── Input Models ───────────────────────────────────────────────────────────

class GenerateModelInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(description="Model name in PascalCase (e.g. 'Article', 'UserProfile')")
    fields: list[str] = Field(
        description="List of 'field_name:type' pairs (e.g. ['title:string', 'body:text', 'published:boolean']). Types: string, text, integer, float, decimal, boolean, date, datetime, email, url, slug, uuid, file, image, json, money"
    )
    relationships: list[str] = Field(
        default=[],
        description="List of 'field_name:type:target' (e.g. ['author:fk:User', 'tags:m2m:Tag', 'profile:o2o:Profile'])",
    )
    timestamps: bool = Field(default=True, description="Add created_at/updated_at fields")
    abstract: bool = Field(default=False, description="Make abstract base model")
    app_name: str = Field(default="myapp", description="Django app name for imports")


class GenerateViewInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    model_name: str = Field(description="Model name this view operates on (e.g. 'Article')")
    view_type: str = Field(description="View type: list, detail, create, update, delete, form, template, redirect")
    app_name: str = Field(default="myapp", description="Django app name")
    require_login: bool = Field(default=False, description="Require authentication")
    fields: list[str] = Field(default=[], description="Form fields for create/update views")
    template_name: Optional[str] = Field(default=None, description="Custom template name")
    paginate_by: Optional[int] = Field(default=None, description="Pagination count for list views")


class GenerateURLsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    app_name: str = Field(description="Django app name (used as namespace)")
    model_name: str = Field(description="Model name for CRUD URL patterns")
    lookup_field: str = Field(default="pk", description="URL lookup field: pk, slug, uuid")
    include_api: bool = Field(default=False, description="Include JSON API endpoints")


class GenerateFormInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    model_name: str = Field(description="Model name for ModelForm")
    fields: list[str] = Field(description="Form fields to include")
    app_name: str = Field(default="myapp", description="Django app name")
    widgets: list[str] = Field(
        default=[],
        description="Custom widgets as 'field:widget' (e.g. ['body:Textarea', 'tags:CheckboxSelectMultiple'])",
    )
    custom_validation: list[str] = Field(
        default=[],
        description="Fields needing custom clean methods (e.g. ['title', 'email'])",
    )


class GenerateAdminInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    model_name: str = Field(description="Model name to register in admin")
    list_display: list[str] = Field(description="Fields to show in list view")
    list_filter: list[str] = Field(default=[], description="Fields for sidebar filters")
    search_fields: list[str] = Field(default=[], description="Fields for search box")
    app_name: str = Field(default="myapp", description="Django app name")
    inlines: list[str] = Field(default=[], description="Related models to show inline (e.g. ['Comment'])")
    prepopulated: list[str] = Field(
        default=[],
        description="Prepopulated fields as 'target:source' (e.g. ['slug:title'])",
    )


class GenerateSettingsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    project_name: str = Field(description="Django project name")
    environment: str = Field(default="production", description="Target: development, production, test")
    database: str = Field(default="postgresql", description="Database: sqlite, postgresql, mysql")
    extras: list[str] = Field(
        default=[],
        description="Extra features: cors, redis, celery, whitenoise, debug_toolbar, sentry, email",
    )


class DetectAntiPatternsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    code: str = Field(description="Django code to analyze for anti-patterns")
    context: str = Field(default="general", description="Context: model, view, settings, template, url")


class GenerateTestInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    model_name: str = Field(description="Model to generate tests for")
    test_type: str = Field(default="all", description="Test type: model, view, form, api, all")
    app_name: str = Field(default="myapp", description="Django app name")
    endpoints: list[str] = Field(
        default=[],
        description="URL names to test (e.g. ['article-list', 'article-detail'])",
    )


# ── Pure helpers ───────────────────────────────────────────────────────────

def _build_model_code(inp: GenerateModelInput) -> str:
    lines = [
        "import uuid",
        "from django.db import models",
        "from django.urls import reverse",
        "",
        "",
    ]

    base = "models.Model"
    meta_abstract = ""
    if inp.abstract:
        meta_abstract = "        abstract = True\n"

    lines.append(f"class {inp.name}({base}):")

    # Fields
    for field_def in inp.fields:
        parts = field_def.split(":")
        if len(parts) != 2:
            continue
        name, ftype = parts[0].strip(), parts[1].strip().lower()
        django_field = FIELD_TYPES.get(ftype, f'CharField(max_length=255)  # Unknown type: {ftype}')
        lines.append(f"    {name} = models.{django_field}")

    # Relationships
    for rel_def in inp.relationships:
        parts = rel_def.split(":")
        if len(parts) != 3:
            continue
        name, rtype, target = parts[0].strip(), parts[1].strip().lower(), parts[2].strip()
        rel_class = RELATIONSHIP_TYPES.get(rtype, "ForeignKey")
        if rtype == "fk":
            lines.append(f'    {name} = models.{rel_class}("{target}", on_delete=models.CASCADE, related_name="{inp.name.lower()}s")')
        elif rtype == "o2o":
            lines.append(f'    {name} = models.{rel_class}("{target}", on_delete=models.CASCADE, related_name="{inp.name.lower()}")')
        elif rtype == "m2m":
            lines.append(f'    {name} = models.{rel_class}("{target}", blank=True, related_name="{inp.name.lower()}s")')

    # Timestamps
    if inp.timestamps:
        lines.append("    created_at = models.DateTimeField(auto_now_add=True)")
        lines.append("    updated_at = models.DateTimeField(auto_now=True)")

    # Meta
    lines.append("")
    lines.append("    class Meta:")
    if meta_abstract:
        lines.append("        abstract = True")
    lines.append('        ordering = ["-created_at"]' if inp.timestamps else '        ordering = ["pk"]')
    lines.append(f'        verbose_name_plural = "{inp.name.lower()}s"')

    # __str__
    first_char_field = None
    for field_def in inp.fields:
        parts = field_def.split(":")
        if len(parts) == 2 and parts[1].strip().lower() in ("string", "text", "email", "slug"):
            first_char_field = parts[0].strip()
            break
    str_field = first_char_field or "pk"
    lines.append("")
    lines.append("    def __str__(self):")
    lines.append(f"        return str(self.{str_field})")

    # get_absolute_url
    lines.append("")
    lines.append("    def get_absolute_url(self):")
    slug_field = None
    for field_def in inp.fields:
        parts = field_def.split(":")
        if len(parts) == 2 and parts[1].strip().lower() == "slug":
            slug_field = parts[0].strip()
            break
    if slug_field:
        lines.append(f'        return reverse("{inp.name.lower()}-detail", kwargs={{"{slug_field}": self.{slug_field}}})')
    else:
        lines.append(f'        return reverse("{inp.name.lower()}-detail", kwargs={{"pk": self.pk}})')

    return "\n".join(lines)


def _build_view_code(inp: GenerateViewInput) -> str:
    vtype = inp.view_type.lower()
    cbv_class = VIEW_TYPES.get(vtype)
    if not cbv_class:
        return f"# Unknown view type: {vtype}. Available: {', '.join(VIEW_TYPES.keys())}"

    imports = ["from django.views.generic import " + cbv_class]
    if inp.require_login:
        imports.append("from django.contrib.auth.mixins import LoginRequiredMixin")
    imports.append(f"from .models import {inp.model_name}")

    if vtype in ("create", "update", "delete"):
        imports.append("from django.urls import reverse_lazy")

    lines = imports + ["", ""]

    model_lower = inp.model_name.lower()
    template = inp.template_name or f"{inp.app_name}/{model_lower}_{vtype}.html"
    if vtype == "delete":
        template = inp.template_name or f"{inp.app_name}/{model_lower}_confirm_delete.html"

    mixins = "LoginRequiredMixin, " if inp.require_login else ""
    class_name = f"{inp.model_name}{cbv_class}"

    lines.append(f"class {class_name}({mixins}{cbv_class}):")
    lines.append(f"    model = {inp.model_name}")
    lines.append(f'    template_name = "{template}"')

    if vtype == "list":
        lines.append(f'    context_object_name = "{model_lower}s"')
        if inp.paginate_by:
            lines.append(f"    paginate_by = {inp.paginate_by}")

    if vtype == "detail":
        lines.append(f'    context_object_name = "{model_lower}"')

    if vtype in ("create", "update") and inp.fields:
        lines.append(f"    fields = {inp.fields}")

    if vtype == "delete":
        lines.append(f'    success_url = reverse_lazy("{model_lower}-list")')

    if vtype == "create":
        lines.append("")
        lines.append("    def form_valid(self, form):")
        lines.append("        form.instance.author = self.request.user")
        lines.append("        return super().form_valid(form)")

    return "\n".join(lines)


def _build_urls_code(inp: GenerateURLsInput) -> str:
    model_lower = inp.model_name.lower()
    lookup = inp.lookup_field

    converter = "int:pk"
    if lookup == "slug":
        converter = "slug:slug"
    elif lookup == "uuid":
        converter = "uuid:uuid"

    lines = [
        "from django.urls import path",
        "from . import views",
        "",
        f'app_name = "{inp.app_name}"',
        "",
        "urlpatterns = [",
        f'    path("", views.{inp.model_name}ListView.as_view(), name="{model_lower}-list"),',
        f'    path("create/", views.{inp.model_name}CreateView.as_view(), name="{model_lower}-create"),',
        f'    path("<{converter}>/", views.{inp.model_name}DetailView.as_view(), name="{model_lower}-detail"),',
        f'    path("<{converter}>/edit/", views.{inp.model_name}UpdateView.as_view(), name="{model_lower}-update"),',
        f'    path("<{converter}>/delete/", views.{inp.model_name}DeleteView.as_view(), name="{model_lower}-delete"),',
    ]

    if inp.include_api:
        lines.append(f'    path("api/", views.api_{model_lower}_list, name="api-{model_lower}-list"),')
        lines.append(f'    path("api/<{converter}>/", views.api_{model_lower}_detail, name="api-{model_lower}-detail"),')

    lines.append("]")
    return "\n".join(lines)


def _detect_issues(code: str, context: str) -> list[dict]:
    import re

    issues = []
    for pattern in ANTI_PATTERNS:
        for indicator in pattern["indicators"]:
            try:
                if re.search(indicator, code, re.MULTILINE | re.DOTALL):
                    issues.append({
                        "name": pattern["name"],
                        "severity": pattern["severity"],
                        "fix": pattern["fix"],
                    })
                    break
            except re.error:
                continue
    return issues


# ── Tools ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def django_generate_model(inp: GenerateModelInput) -> str:
    """Generate a Django model with fields, relationships, Meta, and methods."""
    code = _build_model_code(inp)
    return json.dumps({
        "code": code,
        "file": f"{inp.app_name}/models.py",
        "notes": [
            "Run: python manage.py makemigrations && python manage.py migrate",
            "Register in admin.py for admin interface",
        ],
    })


@mcp.tool()
async def django_generate_view(inp: GenerateViewInput) -> str:
    """Generate a Django class-based view (ListView, DetailView, CreateView, etc.)."""
    code = _build_view_code(inp)
    return json.dumps({
        "code": code,
        "file": f"{inp.app_name}/views.py",
        "template": f"{inp.app_name}/templates/{inp.app_name}/{inp.model_name.lower()}_{inp.view_type}.html",
    })


@mcp.tool()
async def django_generate_urls(inp: GenerateURLsInput) -> str:
    """Generate Django URL patterns with CRUD routes for a model."""
    code = _build_urls_code(inp)
    return json.dumps({
        "code": code,
        "file": f"{inp.app_name}/urls.py",
        "notes": [
            f'Add to root urls.py: path("{inp.app_name}/", include("{inp.app_name}.urls"))',
        ],
    })


@mcp.tool()
async def django_generate_form(inp: GenerateFormInput) -> str:
    """Generate a Django ModelForm with custom widgets and validation."""
    lines = [
        "from django import forms",
        f"from .models import {inp.model_name}",
        "",
        "",
        f"class {inp.model_name}Form(forms.ModelForm):",
        "    class Meta:",
        f"        model = {inp.model_name}",
        f"        fields = {inp.fields}",
    ]

    if inp.widgets:
        lines.append("        widgets = {")
        for w in inp.widgets:
            parts = w.split(":")
            if len(parts) == 2:
                lines.append(f'            "{parts[0].strip()}": forms.{parts[1].strip()}(),')
        lines.append("        }")

    for field in inp.custom_validation:
        lines.extend([
            "",
            f"    def clean_{field}(self):",
            f'        value = self.cleaned_data["{field}"]',
            f"        # Add custom validation for {field}",
            f"        return value",
        ])

    return json.dumps({
        "code": "\n".join(lines),
        "file": f"{inp.app_name}/forms.py",
    })


@mcp.tool()
async def django_generate_admin(inp: GenerateAdminInput) -> str:
    """Generate Django admin configuration with list display, filters, search, and inlines."""
    lines = [
        "from django.contrib import admin",
        f"from .models import {inp.model_name}",
    ]

    if inp.inlines:
        for inline in inp.inlines:
            lines.append(f"from .models import {inline}")

    lines.append("")

    # Inlines
    for inline in inp.inlines:
        lines.extend([
            "",
            f"class {inline}Inline(admin.TabularInline):",
            f"    model = {inline}",
            "    extra = 0",
        ])

    lines.extend([
        "",
        f"@admin.register({inp.model_name})",
        f"class {inp.model_name}Admin(admin.ModelAdmin):",
        f"    list_display = {inp.list_display}",
    ])

    if inp.list_filter:
        lines.append(f"    list_filter = {inp.list_filter}")
    if inp.search_fields:
        lines.append(f"    search_fields = {inp.search_fields}")

    for pp in inp.prepopulated:
        parts = pp.split(":")
        if len(parts) == 2:
            lines.append(f'    prepopulated_fields = {{"{parts[0].strip()}": ("{parts[1].strip()}",)}}')

    if inp.inlines:
        inline_names = [f"{i}Inline" for i in inp.inlines]
        lines.append(f"    inlines = [{', '.join(inline_names)}]")

    return json.dumps({
        "code": "\n".join(lines),
        "file": f"{inp.app_name}/admin.py",
    })


@mcp.tool()
async def django_generate_settings(inp: GenerateSettingsInput) -> str:
    """Generate Django settings for development, production, or test environments."""
    env = inp.environment.lower()
    lines = ['"""Django settings for ' + inp.project_name + f' ({env})."""', ""]
    lines.append("import os")
    lines.append("from pathlib import Path")
    lines.append("")
    lines.append("BASE_DIR = Path(__file__).resolve().parent.parent")
    lines.append("")

    if env == "development":
        lines.append("DEBUG = True")
        lines.append('ALLOWED_HOSTS = ["localhost", "127.0.0.1"]')
        lines.append("SECRET_KEY = 'dev-secret-key-change-in-production'")
    else:
        lines.append("DEBUG = False")
        lines.append('ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")')
        lines.append('SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]')

    lines.append("")
    lines.append("INSTALLED_APPS = [")
    lines.append('    "django.contrib.admin",')
    lines.append('    "django.contrib.auth",')
    lines.append('    "django.contrib.contenttypes",')
    lines.append('    "django.contrib.sessions",')
    lines.append('    "django.contrib.messages",')
    lines.append('    "django.contrib.staticfiles",')

    if "cors" in inp.extras:
        lines.append('    "corsheaders",')
    if "celery" in inp.extras:
        lines.append('    "django_celery_beat",')
    if "debug_toolbar" in inp.extras and env == "development":
        lines.append('    "debug_toolbar",')

    lines.append("]")
    lines.append("")

    # Database
    lines.append("DATABASES = {")
    lines.append('    "default": {')
    if inp.database == "sqlite" or env == "development":
        lines.append('        "ENGINE": "django.db.backends.sqlite3",')
        lines.append('        "NAME": BASE_DIR / "db.sqlite3",')
    elif inp.database == "postgresql":
        lines.append('        "ENGINE": "django.db.backends.postgresql",')
        lines.append('        "NAME": os.environ.get("DB_NAME", "' + inp.project_name + '"),')
        lines.append('        "USER": os.environ.get("DB_USER", "postgres"),')
        lines.append('        "PASSWORD": os.environ.get("DB_PASSWORD", ""),')
        lines.append('        "HOST": os.environ.get("DB_HOST", "localhost"),')
        lines.append('        "PORT": os.environ.get("DB_PORT", "5432"),')
    elif inp.database == "mysql":
        lines.append('        "ENGINE": "django.db.backends.mysql",')
        lines.append('        "NAME": os.environ.get("DB_NAME", "' + inp.project_name + '"),')
        lines.append('        "USER": os.environ.get("DB_USER", "root"),')
        lines.append('        "PASSWORD": os.environ.get("DB_PASSWORD", ""),')
        lines.append('        "HOST": os.environ.get("DB_HOST", "localhost"),')
        lines.append('        "PORT": os.environ.get("DB_PORT", "3306"),')
    lines.append("    }")
    lines.append("}")

    # Security for production
    if env == "production":
        lines.extend([
            "",
            "# Security",
            "SECURE_SSL_REDIRECT = True",
            "SECURE_HSTS_SECONDS = 31536000",
            "SECURE_HSTS_INCLUDE_SUBDOMAINS = True",
            "SESSION_COOKIE_SECURE = True",
            "CSRF_COOKIE_SECURE = True",
        ])

    if "redis" in inp.extras:
        lines.extend([
            "",
            "# Cache (Redis)",
            "CACHES = {",
            '    "default": {',
            '        "BACKEND": "django.core.cache.backends.redis.RedisCache",',
            '        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),',
            "    }",
            "}",
        ])

    return json.dumps({
        "code": "\n".join(lines),
        "file": f"{inp.project_name}/settings/{env}.py",
        "notes": [
            f"Set DJANGO_SETTINGS_MODULE={inp.project_name}.settings.{env}",
        ],
    })


@mcp.tool()
async def django_detect_antipatterns(inp: DetectAntiPatternsInput) -> str:
    """Detect Django anti-patterns and security issues in code."""
    issues = _detect_issues(inp.code, inp.context)

    summary = {
        "total_issues": len(issues),
        "critical": sum(1 for i in issues if i["severity"] == "critical"),
        "high": sum(1 for i in issues if i["severity"] == "high"),
        "medium": sum(1 for i in issues if i["severity"] == "medium"),
        "low": sum(1 for i in issues if i["severity"] == "low"),
    }

    return json.dumps({
        "issues": issues,
        "summary": summary,
        "clean": len(issues) == 0,
    })


@mcp.tool()
async def django_generate_test(inp: GenerateTestInput) -> str:
    """Generate Django test cases for models, views, forms, or API endpoints."""
    model_lower = inp.model_name.lower()
    lines = [
        "from django.test import TestCase, Client",
        "from django.urls import reverse",
        "from django.contrib.auth import get_user_model",
        f"from .models import {inp.model_name}",
        "",
        "User = get_user_model()",
        "",
        "",
    ]

    if inp.test_type in ("model", "all"):
        lines.extend([
            f"class {inp.model_name}ModelTests(TestCase):",
            "    @classmethod",
            "    def setUpTestData(cls):",
            '        cls.user = User.objects.create_user("testuser", password="testpass123")',
            f'        cls.{model_lower} = {inp.model_name}.objects.create(',
            f'            # Add required fields here',
            "        )",
            "",
            f"    def test_{model_lower}_str(self):",
            f'        self.assertIsNotNone(str(self.{model_lower}))',
            "",
            f"    def test_{model_lower}_get_absolute_url(self):",
            f"        url = self.{model_lower}.get_absolute_url()",
            '        self.assertIsNotNone(url)',
            "",
            "",
        ])

    if inp.test_type in ("view", "all"):
        lines.extend([
            f"class {inp.model_name}ViewTests(TestCase):",
            "    @classmethod",
            "    def setUpTestData(cls):",
            '        cls.user = User.objects.create_user("testuser", password="testpass123")',
            f'        cls.{model_lower} = {inp.model_name}.objects.create(',
            f'            # Add required fields here',
            "        )",
            "",
            f"    def test_{model_lower}_list_view(self):",
            f'        response = self.client.get(reverse("{model_lower}-list"))',
            "        self.assertEqual(response.status_code, 200)",
            "",
            f"    def test_{model_lower}_detail_view(self):",
            f'        response = self.client.get(self.{model_lower}.get_absolute_url())',
            "        self.assertEqual(response.status_code, 200)",
            "",
        ])

        for endpoint in inp.endpoints:
            safe_name = endpoint.replace("-", "_")
            lines.extend([
                f"    def test_{safe_name}_status_code(self):",
                f'        response = self.client.get(reverse("{endpoint}"))',
                "        self.assertEqual(response.status_code, 200)",
                "",
            ])

    return json.dumps({
        "code": "\n".join(lines),
        "file": f"{inp.app_name}/tests.py",
        "notes": [
            f"Run: python manage.py test {inp.app_name}",
            "Fill in required model fields in setUpTestData",
        ],
    })


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")

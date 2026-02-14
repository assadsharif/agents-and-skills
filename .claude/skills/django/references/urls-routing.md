# URL Routing

URL patterns, path converters, namespaces, includes, and reverse resolution.

---

## Basic URL Configuration

```python
# project/urls.py (root URLconf)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("blog.urls")),
    path("api/", include("api.urls", namespace="api")),
    path("", include("pages.urls")),
]

# blog/urls.py (app URLconf)
from django.urls import path
from . import views

app_name = "blog"  # Required for namespacing

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="article-list"),
    path("<slug:slug>/", views.ArticleDetailView.as_view(), name="article-detail"),
    path("create/", views.ArticleCreateView.as_view(), name="article-create"),
    path("<slug:slug>/edit/", views.ArticleUpdateView.as_view(), name="article-update"),
    path("<slug:slug>/delete/", views.ArticleDeleteView.as_view(), name="article-delete"),
]
```

---

## Path Converters

| Converter | Matches | Example |
|-----------|---------|---------|
| `str` | Any non-empty string excluding `/` (default) | `<str:name>` or `<name>` |
| `int` | Zero or positive integer | `<int:pk>` |
| `slug` | ASCII letters, numbers, hyphens, underscores | `<slug:slug>` |
| `uuid` | UUID format | `<uuid:id>` |
| `path` | Any non-empty string including `/` | `<path:filepath>` |

```python
urlpatterns = [
    path("articles/<int:pk>/", views.article_detail, name="article-detail"),
    path("articles/<slug:slug>/", views.article_by_slug, name="article-by-slug"),
    path("users/<uuid:user_id>/", views.user_profile, name="user-profile"),
    path("files/<path:filepath>/", views.serve_file, name="serve-file"),
]
```

### Custom Path Converter

```python
# converters.py
class FourDigitYearConverter:
    regex = r"[0-9]{4}"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return f"{value:04d}"

# urls.py
from django.urls import register_converter
from . import converters

register_converter(converters.FourDigitYearConverter, "yyyy")

urlpatterns = [
    path("archive/<yyyy:year>/", views.archive_year, name="archive-year"),
]
```

---

## URL Patterns with re_path

```python
from django.urls import re_path

urlpatterns = [
    re_path(r"^articles/(?P<year>[0-9]{4})/$", views.year_archive),
    re_path(r"^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$", views.month_archive),
]
```

---

## Including Other URLconfs

```python
from django.urls import path, include

# Basic include
path("blog/", include("blog.urls")),

# With namespace
path("api/v1/", include("api.urls", namespace="api-v1")),
path("api/v2/", include("api_v2.urls", namespace="api-v2")),

# Inline patterns
extra_patterns = [
    path("reports/", views.reports, name="reports"),
    path("stats/", views.stats, name="stats"),
]
path("dashboard/", include(extra_patterns)),
```

---

## Reverse URL Resolution

### In Python Code

```python
from django.urls import reverse

# Basic reverse
url = reverse("article-list")                          # /blog/
url = reverse("article-detail", kwargs={"slug": "hello"})  # /blog/hello/
url = reverse("article-detail", args=["hello"])        # Same

# With namespace
url = reverse("blog:article-detail", kwargs={"slug": "hello"})
url = reverse("api:user-detail", kwargs={"pk": 1})

# In views — redirect
from django.shortcuts import redirect
return redirect("article-detail", slug=article.slug)

# In models — get_absolute_url
class Article(models.Model):
    def get_absolute_url(self):
        return reverse("blog:article-detail", kwargs={"slug": self.slug})
```

### In Templates

```html
<!-- Basic -->
<a href="{% url 'article-list' %}">All Articles</a>

<!-- With arguments -->
<a href="{% url 'article-detail' slug=article.slug %}">{{ article.title }}</a>

<!-- With namespace -->
<a href="{% url 'blog:article-detail' slug=article.slug %}">{{ article.title }}</a>

<!-- In forms -->
<form action="{% url 'article-create' %}" method="post">
```

---

## Namespaces

### Application Namespace

```python
# blog/urls.py
app_name = "blog"  # Application namespace

urlpatterns = [
    path("", views.index, name="index"),
]
```

### Instance Namespace

```python
# project/urls.py
path("blog/", include("blog.urls")),                         # Default instance
path("author-blog/", include("blog.urls", namespace="author")),  # Named instance
```

---

## Common URL Patterns

### REST-Style Resource URLs

```python
app_name = "articles"

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="list"),
    path("create/", views.ArticleCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ArticleDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.ArticleUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.ArticleDeleteView.as_view(), name="delete"),
]
```

### API Versioning

```python
urlpatterns = [
    path("api/v1/", include("api.v1.urls", namespace="api-v1")),
    path("api/v2/", include("api.v2.urls", namespace="api-v2")),
]
```

### Static and Media Files (Development Only)

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

# Models & ORM

Django ORM: models, fields, relationships, querysets, managers, and migrations.

---

## Model Definition

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="articles")
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField("Tag", blank=True, related_name="articles")
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["-created_at", "published"]),
        ]
        verbose_name_plural = "articles"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("article-detail", kwargs={"slug": self.slug})
```

---

## Field Types

### Common Fields

| Field | Usage |
|-------|-------|
| `CharField(max_length=N)` | Short text (required max_length) |
| `TextField()` | Long text (no max_length) |
| `IntegerField()` | Integers |
| `FloatField()` | Floating point |
| `DecimalField(max_digits, decimal_places)` | Precise decimals (money) |
| `BooleanField(default=False)` | True/False |
| `DateField()` | Date only |
| `DateTimeField()` | Date + time |
| `EmailField()` | Email with validation |
| `URLField()` | URL with validation |
| `SlugField()` | URL-safe string |
| `UUIDField()` | UUID |
| `FileField(upload_to="path/")` | File upload |
| `ImageField(upload_to="path/")` | Image upload (requires Pillow) |
| `JSONField()` | JSON data (PostgreSQL native, SQLite 3.9+) |

### Field Options

```python
# Common options (apply to most fields)
field = models.CharField(
    max_length=100,
    null=True,          # Allow NULL in DB (avoid for string fields)
    blank=True,         # Allow empty in forms
    default="value",    # Default value
    unique=True,        # Unique constraint
    db_index=True,      # Database index
    choices=[("D", "Draft"), ("P", "Published")],  # Choices
    help_text="Description for admin/forms",
    verbose_name="Custom Label",
    validators=[MinLengthValidator(3)],
    editable=False,     # Exclude from forms
)
```

### Auto Fields

```python
created_at = models.DateTimeField(auto_now_add=True)  # Set on create only
updated_at = models.DateTimeField(auto_now=True)       # Set on every save
```

---

## Relationships

### ForeignKey (Many-to-One)

```python
class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,      # Delete comments when article deleted
        related_name="comments",       # article.comments.all()
    )

# on_delete options:
# CASCADE      — Delete related objects
# PROTECT      — Prevent deletion (raises ProtectedError)
# SET_NULL     — Set to NULL (requires null=True)
# SET_DEFAULT  — Set to default value
# SET(func)    — Set to return value of func
# DO_NOTHING   — Do nothing (may break referential integrity)
```

### ManyToManyField

```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Article(models.Model):
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")

# Usage:
article.tags.add(tag1, tag2)
article.tags.remove(tag1)
article.tags.set([tag1, tag2, tag3])
article.tags.clear()
article.tags.all()
tag.articles.all()  # Reverse relation
```

### ManyToMany with Through Model

```python
class Membership(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["person", "group"]

class Group(models.Model):
    members = models.ManyToManyField("Person", through=Membership, related_name="groups")
```

### OneToOneField

```python
class Profile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)

# Usage:
user.profile        # Forward
profile.user        # Reverse
```

---

## QuerySet API

### Creating

```python
# Single object
article = Article.objects.create(title="Hello", body="World", author=user)

# Or two-step
article = Article(title="Hello", body="World", author=user)
article.save()

# Bulk create (efficient for many objects)
Article.objects.bulk_create([
    Article(title="A", body="...", author=user),
    Article(title="B", body="...", author=user),
])

# Get or create
obj, created = Article.objects.get_or_create(slug="hello", defaults={"title": "Hello", "author": user})

# Update or create
obj, created = Article.objects.update_or_create(slug="hello", defaults={"title": "Updated"})
```

### Retrieving

```python
# Single object
article = Article.objects.get(pk=1)           # Raises DoesNotExist if not found
article = Article.objects.get(slug="hello")   # Raises MultipleObjectsReturned if >1

# QuerySets (lazy — not evaluated until iterated)
Article.objects.all()
Article.objects.filter(published=True)
Article.objects.exclude(published=False)
Article.objects.filter(published=True).exclude(category=None)

# Chaining (each returns new QuerySet)
Article.objects.filter(published=True).order_by("-created_at")[:10]
```

### Field Lookups

```python
# Exact (default)
Article.objects.filter(title="Hello")         # WHERE title = 'Hello'
Article.objects.filter(title__exact="Hello")  # Same

# Comparison
Article.objects.filter(id__gt=5)              # > 5
Article.objects.filter(id__gte=5)             # >= 5
Article.objects.filter(id__lt=5)              # < 5
Article.objects.filter(id__lte=5)             # <= 5

# String lookups
Article.objects.filter(title__contains="hello")      # LIKE '%hello%'
Article.objects.filter(title__icontains="hello")     # Case-insensitive
Article.objects.filter(title__startswith="Hello")
Article.objects.filter(title__endswith="world")

# In / Range
Article.objects.filter(id__in=[1, 2, 3])
Article.objects.filter(created_at__range=(start, end))

# Null / Empty
Article.objects.filter(category__isnull=True)

# Date parts
Article.objects.filter(created_at__year=2026)
Article.objects.filter(created_at__month=2)
Article.objects.filter(created_at__date=date.today())

# Related field lookups (double underscore spans relations)
Article.objects.filter(author__username="john")
Article.objects.filter(category__name__icontains="tech")
```

### F and Q Expressions

```python
from django.db.models import F, Q

# F expressions — reference model fields
Article.objects.filter(updated_at__gt=F("created_at"))
Article.objects.update(views=F("views") + 1)  # Atomic increment

# Q objects — complex queries with OR / NOT
Article.objects.filter(Q(published=True) | Q(author=user))
Article.objects.filter(Q(title__icontains="django") & ~Q(category=None))

# Combining
Article.objects.filter(
    Q(published=True) | Q(author=user),
    created_at__year=2026,  # AND with Q
)
```

### Aggregation & Annotation

```python
from django.db.models import Count, Sum, Avg, Max, Min

# Aggregate (returns dict)
Article.objects.aggregate(total=Count("id"), avg_views=Avg("views"))
# {'total': 42, 'avg_views': 156.3}

# Annotate (adds field to each object)
categories = Category.objects.annotate(article_count=Count("articles"))
for cat in categories:
    print(cat.name, cat.article_count)

# Group by (annotate + values)
Article.objects.values("category__name").annotate(count=Count("id")).order_by("-count")
```

### Updating & Deleting

```python
# Update (efficient — single SQL query)
Article.objects.filter(published=False).update(published=True)

# Bulk update
articles = Article.objects.filter(author=user)
for a in articles:
    a.published = True
Article.objects.bulk_update(articles, ["published"])

# Delete
Article.objects.filter(created_at__lt=cutoff).delete()
article.delete()  # Single object
```

### Performance Optimization

```python
# select_related — JOIN for ForeignKey/OneToOne (single query)
articles = Article.objects.select_related("author", "category").all()

# prefetch_related — separate query for ManyToMany/reverse FK
articles = Article.objects.prefetch_related("tags", "comments").all()

# Partial field loading
Article.objects.only("title", "slug")   # Load only these fields
Article.objects.defer("body")           # Load all except these

# Exists check (more efficient than count)
if Article.objects.filter(slug="hello").exists():
    ...

# Count
total = Article.objects.filter(published=True).count()

# Values / values_list (return dicts / tuples instead of objects)
Article.objects.values("title", "author__username")
Article.objects.values_list("title", flat=True)  # Flat list

# Iterator for large querysets
for article in Article.objects.all().iterator(chunk_size=1000):
    process(article)
```

---

## Custom Managers

```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True)

class Article(models.Model):
    # ...
    objects = models.Manager()          # Default manager
    published = PublishedManager()      # Custom manager

# Usage:
Article.published.all()                # Only published articles
Article.published.filter(author=user)  # Chain further
```

---

## Model Inheritance

### Abstract Base Class (no DB table)

```python
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Article(TimestampMixin):
    title = models.CharField(max_length=200)
    # Inherits created_at and updated_at
```

### Multi-Table Inheritance (separate tables with JOIN)

```python
class Place(models.Model):
    name = models.CharField(max_length=50)

class Restaurant(Place):
    serves_pizza = models.BooleanField(default=False)
    # Gets implicit OneToOneField to Place
```

### Proxy Models (same table, different behavior)

```python
class OrderedArticle(Article):
    class Meta:
        proxy = True
        ordering = ["title"]
```

---

## Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations
python manage.py makemigrations myapp  # Specific app

# Apply migrations
python manage.py migrate
python manage.py migrate myapp 0003   # Migrate to specific version

# Show migration status
python manage.py showmigrations

# Generate SQL (without applying)
python manage.py sqlmigrate myapp 0001

# Rollback
python manage.py migrate myapp 0002   # Roll back to migration 0002
python manage.py migrate myapp zero   # Roll back all
```

### Data Migrations

```python
from django.db import migrations

def populate_slugs(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    for article in Article.objects.filter(slug=""):
        article.slug = slugify(article.title)
        article.save()

class Migration(migrations.Migration):
    dependencies = [("blog", "0002_add_slug")]
    operations = [migrations.RunPython(populate_slugs, migrations.RunPython.noop)]
```

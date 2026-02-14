# Forms & Admin

Django forms, ModelForm, formsets, validation, widgets, and admin customization.

---

## Forms

### Basic Form

```python
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    category = forms.ChoiceField(choices=[
        ("general", "General"),
        ("support", "Support"),
        ("feedback", "Feedback"),
    ])

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email.endswith("@spam.com"):
            raise forms.ValidationError("Invalid email domain.")
        return email

    def clean(self):
        cleaned = super().clean()
        # Cross-field validation
        if cleaned.get("category") == "support" and len(cleaned.get("message", "")) < 20:
            raise forms.ValidationError("Support messages must be at least 20 characters.")
        return cleaned
```

### ModelForm

```python
from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body", "category", "tags"]  # Explicit fields
        # Or: exclude = ["author", "published"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 10, "class": "rich-editor"}),
            "tags": forms.CheckboxSelectMultiple(),
        }
        labels = {"body": "Content"}
        help_texts = {"title": "Enter a descriptive title"}
        error_messages = {
            "title": {"max_length": "Title is too long (max 200 chars)."},
        }

    def clean_title(self):
        title = self.cleaned_data["title"]
        if Article.objects.filter(title=title).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An article with this title already exists.")
        return title
```

### Using Forms in Views

```python
# FBV
def create_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()  # Save ManyToMany fields
            return redirect(article)
    else:
        form = ArticleForm()
    return render(request, "blog/article_form.html", {"form": form})

# Update
def update_article(request, slug):
    article = get_object_or_404(Article, slug=slug, author=request.user)
    form = ArticleForm(request.POST or None, instance=article)
    if form.is_valid():
        form.save()
        return redirect(article)
    return render(request, "blog/article_form.html", {"form": form})
```

### Form Template

```html
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}

    <!-- Render all fields -->
    {{ form.as_p }}

    <!-- Or render individually -->
    {% for field in form %}
    <div class="field {% if field.errors %}error{% endif %}">
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {{ field }}
        {% for error in field.errors %}
        <span class="error">{{ error }}</span>
        {% endfor %}
        {% if field.help_text %}
        <small>{{ field.help_text }}</small>
        {% endif %}
    </div>
    {% endfor %}

    <!-- Non-field errors -->
    {% if form.non_field_errors %}
    <div class="errors">
        {% for error in form.non_field_errors %}
        <p>{{ error }}</p>
        {% endfor %}
    </div>
    {% endif %}

    <button type="submit">Submit</button>
</form>
```

---

## Field Types

| Form Field | HTML Widget | Model Field |
|------------|-------------|-------------|
| `CharField` | `<input type="text">` | `CharField` |
| `EmailField` | `<input type="email">` | `EmailField` |
| `IntegerField` | `<input type="number">` | `IntegerField` |
| `FloatField` | `<input type="number">` | `FloatField` |
| `DecimalField` | `<input type="number">` | `DecimalField` |
| `BooleanField` | `<input type="checkbox">` | `BooleanField` |
| `DateField` | `<input type="date">` | `DateField` |
| `DateTimeField` | `<input type="datetime-local">` | `DateTimeField` |
| `ChoiceField` | `<select>` | Field with `choices` |
| `FileField` | `<input type="file">` | `FileField` |
| `ImageField` | `<input type="file">` | `ImageField` |
| `SlugField` | `<input type="text">` | `SlugField` |

---

## Formsets

```python
from django.forms import formset_factory, modelformset_factory, inlineformset_factory

# Basic formset
ContactFormSet = formset_factory(ContactForm, extra=3)

# Model formset
ArticleFormSet = modelformset_factory(Article, fields=["title", "published"], extra=0)

# Inline formset (parent-child)
CommentFormSet = inlineformset_factory(
    Article, Comment,
    fields=["body"],
    extra=2,
    can_delete=True,
)

# Usage in view
def manage_comments(request, slug):
    article = get_object_or_404(Article, slug=slug)
    formset = CommentFormSet(request.POST or None, instance=article)
    if formset.is_valid():
        formset.save()
        return redirect(article)
    return render(request, "blog/comments.html", {"formset": formset})
```

---

## Admin

### Basic Registration

```python
from django.contrib import admin
from .models import Article, Category, Tag

# Simple registration
admin.site.register(Tag)

# With ModelAdmin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "published", "created_at"]
    list_filter = ["published", "category", "created_at"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    list_editable = ["published"]
    list_per_page = 25
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["author"]         # For large FK tables
    autocomplete_fields = ["category"]  # With search_fields on CategoryAdmin
    filter_horizontal = ["tags"]        # For ManyToMany

    fieldsets = (
        (None, {"fields": ("title", "slug", "body")}),
        ("Publishing", {"fields": ("author", "published", "category", "tags")}),
        ("Metadata", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )
```

### Inline Admin

```python
class CommentInline(admin.TabularInline):  # or StackedInline
    model = Comment
    extra = 0
    readonly_fields = ["created_at"]

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
```

### Custom Admin Actions

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    actions = ["publish_selected", "unpublish_selected"]

    @admin.action(description="Publish selected articles")
    def publish_selected(self, request, queryset):
        count = queryset.update(published=True)
        self.message_user(request, f"{count} articles published.")

    @admin.action(description="Unpublish selected articles")
    def unpublish_selected(self, request, queryset):
        queryset.update(published=False)
```

### Custom Admin Methods

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "word_count", "is_long"]

    @admin.display(description="Word Count", ordering="body")
    def word_count(self, obj):
        return len(obj.body.split())

    @admin.display(boolean=True, description="Long Article")
    def is_long(self, obj):
        return len(obj.body.split()) > 500
```

### Admin Site Customization

```python
# admin.py or apps.py
admin.site.site_header = "My Blog Admin"
admin.site.site_title = "Blog Admin Portal"
admin.site.index_title = "Dashboard"
```

---

## Custom Validators

```python
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError

# Built-in validators (use on model or form fields)
rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
phone = models.CharField(validators=[RegexValidator(r"^\+?1?\d{9,15}$")])

# Custom validator function
def validate_no_profanity(value):
    banned = ["spam", "scam"]
    if any(word in value.lower() for word in banned):
        raise ValidationError("Content contains prohibited words.")

class Article(models.Model):
    title = models.CharField(max_length=200, validators=[validate_no_profanity])
```

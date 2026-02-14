# Views

Function-based views, class-based views, generic views, mixins, and async views.

---

## Function-Based Views (FBVs)

### Basic Pattern

```python
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

def article_list(request):
    articles = Article.objects.filter(published=True)
    return render(request, "blog/article_list.html", {"articles": articles})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, published=True)
    return render(request, "blog/article_detail.html", {"article": article})
```

### Handling GET and POST

```python
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect("article-detail", slug=article.slug)
    else:
        form = ArticleForm()
    return render(request, "blog/article_form.html", {"form": form})
```

### JSON Responses (API)

```python
def api_articles(request):
    articles = Article.objects.filter(published=True).values("id", "title", "slug")
    return JsonResponse(list(articles), safe=False)

def api_article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    data = {"id": article.id, "title": article.title, "body": article.body}
    return JsonResponse(data)
```

### View Decorators

```python
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

@login_required
@require_http_methods(["GET", "POST"])
def my_view(request):
    ...

@permission_required("blog.add_article", raise_exception=True)
def create_article(request):
    ...

@cache_page(60 * 15)  # Cache for 15 minutes
def article_list(request):
    ...
```

---

## Class-Based Views (CBVs)

### Base View

```python
from django.views import View

class ArticleView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("GET response")

    def post(self, request, *args, **kwargs):
        return HttpResponse("POST response")

# urls.py
path("articles/", ArticleView.as_view(), name="articles")
```

### TemplateView

```python
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured"] = Article.objects.filter(featured=True)[:5]
        return context
```

---

## Generic CRUD Views

### ListView

```python
from django.views.generic import ListView

class ArticleListView(ListView):
    model = Article
    template_name = "blog/article_list.html"  # Default: article_list.html
    context_object_name = "articles"           # Default: object_list
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset().filter(published=True)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q)
        return qs
```

### DetailView

```python
from django.views.generic import DetailView

class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"        # Default
    slug_url_kwarg = "slug"    # Default

    def get_queryset(self):
        return super().get_queryset().select_related("author", "category")
```

### CreateView

```python
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    fields = ["title", "body", "category", "tags"]
    template_name = "blog/article_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("article-detail", kwargs={"slug": self.object.slug})
```

### UpdateView

```python
from django.views.generic import UpdateView

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    fields = ["title", "body", "category", "tags"]
    template_name = "blog/article_form.html"

    def get_queryset(self):
        # Only allow editing own articles
        return super().get_queryset().filter(author=self.request.user)
```

### DeleteView

```python
from django.views.generic import DeleteView
from django.urls import reverse_lazy

class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = "blog/article_confirm_delete.html"
    success_url = reverse_lazy("article-list")

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)
```

### FormView

```python
from django.views.generic import FormView

class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact-success")

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)
```

### RedirectView

```python
from django.views.generic import RedirectView

class OldArticleRedirect(RedirectView):
    permanent = True
    pattern_name = "article-detail"

    def get_redirect_url(self, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs["pk"])
        return reverse("article-detail", kwargs={"slug": article.slug})
```

---

## Common Mixins

```python
from django.contrib.auth.mixins import (
    LoginRequiredMixin,          # Requires authenticated user
    PermissionRequiredMixin,     # Requires specific permission
    UserPassesTestMixin,         # Custom test function
)

class AdminOnlyView(UserPassesTestMixin, ListView):
    model = Article

    def test_func(self):
        return self.request.user.is_staff

class ManageArticleView(PermissionRequiredMixin, UpdateView):
    model = Article
    permission_required = "blog.change_article"
```

### Custom Mixins

```python
class OwnerRequiredMixin:
    """Only allow object owner to access."""
    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

class ArticleUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Article
    fields = ["title", "body"]
```

---

## Async Views

```python
# Function-based async view
async def async_article_list(request):
    articles = [a async for a in Article.objects.filter(published=True)]
    return JsonResponse([{"title": a.title} for a in articles], safe=False)

# Class-based async view
class AsyncArticleView(View):
    async def get(self, request):
        articles = [a async for a in Article.objects.all()]
        return JsonResponse({"count": len(articles)})
```

---

## Error Handlers

```python
# In main urls.py
handler400 = "myapp.views.bad_request"
handler403 = "myapp.views.permission_denied"
handler404 = "myapp.views.page_not_found"
handler500 = "myapp.views.server_error"

# views.py
def page_not_found(request, exception):
    return render(request, "errors/404.html", status=404)

def server_error(request):
    return render(request, "errors/500.html", status=500)
```

---

## Response Types

```python
from django.http import (
    HttpResponse,              # Basic response
    JsonResponse,              # JSON (auto-serializes dict)
    HttpResponseRedirect,      # 302 redirect
    HttpResponsePermanentRedirect,  # 301 redirect
    HttpResponseNotFound,      # 404
    HttpResponseForbidden,     # 403
    StreamingHttpResponse,     # Streaming content
    FileResponse,              # File download
)

# File download
from django.http import FileResponse
def download_file(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    return FileResponse(doc.file.open(), as_attachment=True, filename=doc.name)

# Streaming response
def stream_csv(request):
    def generate():
        yield "id,name\n"
        for item in Item.objects.iterator():
            yield f"{item.id},{item.name}\n"
    response = StreamingHttpResponse(generate(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="export.csv"'
    return response
```

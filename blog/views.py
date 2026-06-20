"""
blog view'lari (02-System-Design 3-bo'lim).

BlogListView — pagination + ixtiyoriy kategoriya filtri.
BlogDetailView — bitta maqola (slug-based).
"""
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import BlogCategory, BlogPost


class BlogListView(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        qs = BlogPost.published.select_related("category")
        self.active_category = None
        slug = self.kwargs.get("slug")
        if slug:
            self.active_category = get_object_or_404(BlogCategory, slug=slug)
            qs = qs.filter(category=self.active_category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = BlogCategory.objects.all()
        ctx["active_category"] = self.active_category
        return ctx


class BlogDetailView(DetailView):
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.published.select_related("category")

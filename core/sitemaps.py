"""
SEO sitemap'lari (02-System-Design 3-bo'lim: /sitemap.xml).
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import BlogPost

from .models import Project


class StaticViewSitemap(Sitemap):
    """Statik sahifalar (home, projects, blog ro'yxati)."""

    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return ["core:home", "core:project_list", "blog:post_list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return Project.published.all()

    def lastmod(self, obj):
        return obj.created_at


class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return BlogPost.published.all()

    def lastmod(self, obj):
        return obj.published_at or obj.created_at


sitemaps = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "blog": BlogSitemap,
}

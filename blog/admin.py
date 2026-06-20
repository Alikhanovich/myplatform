"""
blog admin (02-System-Design 4-bo'lim).
"""
from django.contrib import admin

from .models import BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "published_at", "order")
    list_editable = ("status", "order")
    list_filter = ("status", "category")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    autocomplete_fields = ("category",)

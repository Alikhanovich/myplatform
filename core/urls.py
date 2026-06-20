from django.urls import path

from . import views
from . import views_api

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("contact/", views.ContactView.as_view(), name="contact"),

    # ── Custom Admin Panel ──────────────────────────────────────────────
    path("admin-panel/login/", views_api.admin_login_view, name="admin_login"),
    path("admin-panel/logout/", views_api.admin_logout_view, name="admin_logout"),
    path("admin-panel/", views_api.admin_panel_view, name="admin_panel"),

    # API endpoints (faqat login + staff/superuser)
    path("admin-panel/api/data/", views_api.api_data, name="api_data"),
    path("admin-panel/api/profile/save/", views_api.api_profile_save, name="api_profile_save"),
    path("admin-panel/api/profile/social/", views_api.api_social_save, name="api_social_save"),
    path("admin-panel/api/stats/save/", views_api.api_stats_save, name="api_stats_save"),
    path("admin-panel/api/skills/save/", views_api.api_skills_save, name="api_skills_save"),
    path("admin-panel/api/experience/save/", views_api.api_experience_save, name="api_experience_save"),
    path("admin-panel/api/projects/toggle/", views_api.api_project_toggle, name="api_project_toggle"),
    path("admin-panel/api/projects/save/", views_api.api_project_save, name="api_project_save"),
    path("admin-panel/api/projects/delete/", views_api.api_project_delete, name="api_project_delete"),
    path("admin-panel/api/blog/toggle/", views_api.api_blog_toggle, name="api_blog_toggle"),
    path("admin-panel/api/blog/save/", views_api.api_blog_save, name="api_blog_save"),
    path("admin-panel/api/blog/delete/", views_api.api_blog_delete, name="api_blog_delete"),
]


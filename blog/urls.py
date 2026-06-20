from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.BlogListView.as_view(), name="post_list"),
    # Kategoriya filtri — slug bilan adashmasligi uchun 'category/' prefiksi oldinda.
    path("category/<slug:slug>/", views.BlogListView.as_view(), name="post_list_by_category"),
    path("<slug:slug>/", views.BlogDetailView.as_view(), name="post_detail"),
]

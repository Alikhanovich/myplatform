"""
Root URL konfiguratsiyasi (02-System-Design 3-bo'lim).

  /                       -> core (home, projects, contact)
  /blog/                  -> blog
  /<ADMIN_URL>            -> Django admin (default: /studio-panel/)
  /sitemap.xml            -> SEO
  /robots.txt            -> SEO
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import sitemaps as sitemaps_dict
from core.views import robots_txt

urlpatterns = [
    # Admin noyob prefiksda (xavfsizlik).
    path(settings.ADMIN_URL, admin.site.urls),

    # SEO
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps_dict},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", robots_txt, name="robots"),

    # Ilovalar
    path("blog/", include("blog.urls")),
    path("", include("core.urls")),
]

# Maxsus xato sahifalari (templates/404.html, 500.html).
handler404 = "core.views.handler404"
handler500 = "core.views.handler500"

# DEV'da media fayllarni Django bersin (PROD'da Cloudinary/WhiteNoise).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

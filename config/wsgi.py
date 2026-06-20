"""WSGI konfiguratsiyasi (Gunicorn / Vercel shu nuqtadan ilovani yuklaydi)."""
import os

from django.core.wsgi import get_wsgi_application

# Settings tanlash tartibi:
#   1) DJANGO_SETTINGS_MODULE env aniq berilgan bo'lsa — o'sha (Render: prod).
#   2) Vercel'da (VERCEL=1 avtomatik) — serverless prod sozlamalari.
#   3) Aks holda — lokal dev.
# Vercel bir nechta system env beradi (VERCEL, VERCEL_ENV, VERCEL_URL) —
# qaysi biri bo'lsa ham serverless prod sozlamalarini tanlaymiz.
_on_vercel = any(os.environ.get(k) for k in ("VERCEL", "VERCEL_ENV", "VERCEL_URL"))
if _on_vercel:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.vercel")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = get_wsgi_application()

# Vercel @vercel/python WSGI ilovani `app` nomi orqali ham qidiradi.
app = application

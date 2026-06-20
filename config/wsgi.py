"""WSGI konfiguratsiyasi (Gunicorn shu nuqtadan ilovani yuklaydi)."""
import os

from django.core.wsgi import get_wsgi_application

# Prod'da render.yaml / build.sh DJANGO_SETTINGS_MODULE=config.settings.prod beradi.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

application = get_wsgi_application()

"""WSGI konfiguratsiyasi (Gunicorn / Vercel shu nuqtadan ilovani yuklaydi)."""
import os

from django.core.wsgi import get_wsgi_application

# Bu fayl WSGI kirish nuqtasi (Vercel / gunicorn). Sukut bo'yicha serverless
# prod sozlamalarini (vercel.py) ishlatamiz — Vercel'ning system env'lari
# (VERCEL) ba'zan runtime'da ochiq bo'lmaydi, shuning uchun aniqlashga tayanmaymiz.
#   • Render: render.yaml DJANGO_SETTINGS_MODULE=config.settings.prod beradi (env setdefault'ni ustun qiladi).
#   • Lokal: `python manage.py runserver` -> manage.py dev'ni ishlatadi (bu faylga tegmaydi).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.vercel")

application = get_wsgi_application()

# Vercel @vercel/python WSGI ilovani `app` nomi orqali ham qidiradi.
app = application

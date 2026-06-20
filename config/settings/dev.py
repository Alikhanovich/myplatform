"""
Lokal development sozlamalari.

DEBUG=True, SQLite, email konsolga. Hech qanday tashqi servis talab qilmaydi.
Ishga tushirish:  python manage.py runserver
"""
from decouple import Csv, config

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,0.0.0.0,testserver",
    cast=Csv(),
) + VERCEL_ALLOWED_HOSTS  # noqa: F405 (base'dan keladi)

# Dev'da email haqiqatan yuborilmaydi — terminalga bosiladi.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Dev'da media lokal diskdan beriladi (base STORAGES default = FileSystemStorage).
# DB esa base'dagi SQLite.

# Ixtiyoriy: brauzerda Django Debug Toolbar kerak bo'lsa shu yerga qo'shiladi.

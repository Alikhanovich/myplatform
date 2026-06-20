"""
Lokal development sozlamalari.

DEBUG=True, SQLite.
Agar .env'da EMAIL_BACKEND=smtp bo'lsa haqiqiy Gmail orqali yuboriladi,
aks holda xabarlar konsolga chiqariladi.
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

# Email backend: .env'dan o'qiladi.
# SMTP:    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# Konsol:  EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend (standart)
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# Gmail SMTP sozlamalari (.env'da to'ldirilgan bo'lsa ishlatiladi)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# Dev'da media lokal diskdan beriladi (base STORAGES default = FileSystemStorage).
# DB esa base'dagi SQLite.

# Ixtiyoriy: brauzerda Django Debug Toolbar kerak bo'lsa shu yerga qo'shiladi.

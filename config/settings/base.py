"""
Umumiy (base) sozlamalar — dev va prod o'rtasida bo'lishiladi.

dev.py va prod.py shu fayldan `from .base import *` bilan meros oladi va
faqat o'z muhitiga xos sozlamalarni qayta yozadi (DEBUG, DB, security...).

Secret/muhit qiymatlari python-decouple orqali env'dan o'qiladi —
kod ichida hech qanday maxfiy qiymat saqlanmaydi.
"""
from pathlib import Path

from decouple import Csv, config

# config/settings/base.py -> config/settings -> config -> <project root>
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --------------------------------------------------------------------------
# Asosiy xavfsizlik
# --------------------------------------------------------------------------
# base'da dev uchun fallback bor; prod.py uni env'dan MAJBURIY oladi.
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-dev-only-change-me-in-production",
)

# Sukut bo'yicha xavfsiz tomon — dev.py True qiladi.
DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# --------------------------------------------------------------------------
# Vercel deployment hostlari
# --------------------------------------------------------------------------
# `.vercel.app` — barcha *.vercel.app (preview + production) subdomenlarni qamraydi.
# VERCEL_URL — Vercel har deployga avtomatik beradigan joriy URL (env orqali).
# CUSTOM_HOSTS — ulangan maxsus domen(lar).
# Bu ro'yxat dev.py / prod.py'da ALLOWED_HOSTS'ga qo'shiladi (ular uni qayta yozadi).
VERCEL_ALLOWED_HOSTS = [".vercel.app"]
_vercel_url = config("VERCEL_URL", default="")
if _vercel_url:
    VERCEL_ALLOWED_HOSTS.append(_vercel_url)
VERCEL_ALLOWED_HOSTS += config(
    "CUSTOM_HOSTS",
    default="3006-3009.uz,www.3006-3009.uz",
    cast=Csv(),
)

ALLOWED_HOSTS += VERCEL_ALLOWED_HOSTS

# Form/admin POST'lari HTTPS domenlardan ishlashi uchun (Django 4+ majburiy qiladi).
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default=(
        "https://*.vercel.app,"
        "https://3006-3009.uz,https://www.3006-3009.uz"
    ),
    cast=Csv(),
)

# --------------------------------------------------------------------------
# Ilovalar
# --------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

LOCAL_APPS = [
    "core",
    "blog",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

# --------------------------------------------------------------------------
# Middleware
# --------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise — statik fayllarni Django jarayonidan beradi (Security'dan keyin).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# --------------------------------------------------------------------------
# Template'lar
# --------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Profil + ijtimoiy havolalarni har sahifaga (nav/footer) beradi.
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --------------------------------------------------------------------------
# Ma'lumotlar bazasi — base'da SQLite (dev). prod.py Postgres'ga almashtiradi.
# --------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --------------------------------------------------------------------------
# Parol validatorlari
# --------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Til / vaqt
# --------------------------------------------------------------------------
# Field nomlari inglizcha/suffiksiz — keyin django-modeltranslation qo'shilsa
# buzilmaydi (02-System-Design 7-bo'lim).
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Statik fayllar (WhiteNoise) va media
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Django 5 STORAGES API. prod.py "default" (media) ni Cloudinary'ga almashtiradi.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --------------------------------------------------------------------------
# Admin
# --------------------------------------------------------------------------
# Xavfsizlik: /admin emas, noyob prefiks (01-Arxitektura 4-bo'lim).
ADMIN_URL = config("ADMIN_URL", default="studio-panel/")

# --------------------------------------------------------------------------
# Email (contact form)
# --------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="portfolio@example.com")
CONTACT_RECIPIENT_EMAIL = config("CONTACT_RECIPIENT_EMAIL", default="you@example.com")

# --------------------------------------------------------------------------
# Boshqalar
# --------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Render kabi reverse-proxy ortida to'g'ri sxema (http/https) aniqlash.
USE_X_FORWARDED_HOST = True

"""
Production sozlamalari (Render.com).

- DEBUG=False, SECRET_KEY/ALLOWED_HOSTS env'dan MAJBURIY.
- PostgreSQL (DATABASE_URL).
- Cloudinary media storage (ephemeral diskdan himoya).
- HTTPS / security headerlari (01-Arxitektura 4-bo'lim).

Faollashtirish: DJANGO_SETTINGS_MODULE=config.settings.prod
"""
import dj_database_url
from decouple import Csv, config

from .base import *  # noqa: F401,F403

DEBUG = False

# Prod'da bularni MAJBURAN env'dan olamiz (default yo'q -> noto'g'ri deploy darrov bilinadi).
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# --------------------------------------------------------------------------
# Ma'lumotlar bazasi — Render managed PostgreSQL (DATABASE_URL)
# --------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# --------------------------------------------------------------------------
# Media — Cloudinary (persistent, CDN, avtomatik optimallashtirish)
# --------------------------------------------------------------------------
INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]  # noqa: F405

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": config("CLOUDINARY_API_KEY"),
    "API_SECRET": config("CLOUDINARY_API_SECRET"),
}

# Media uchun "default" storage'ni Cloudinary'ga almashtiramiz; static esa WhiteNoise.
STORAGES["default"] = {  # noqa: F405
    "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
}

# --------------------------------------------------------------------------
# Xavfsizlik (01-Arxitektura 4-bo'lim jadvali)
# --------------------------------------------------------------------------
# Render TLS'ni proxy orqali beradi — sxemani to'g'ri aniqlash uchun.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS — 1 yil, subdomenlar bilan, preload tayyor.
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# --------------------------------------------------------------------------
# Email — haqiqiy SMTP (contact form)
# --------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# --------------------------------------------------------------------------
# Logging — xatolar Render konsoliga chiqsin
# --------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

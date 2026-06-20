"""
Vercel (serverless) production sozlamalari.

- DEBUG=False (env bilan boshqariladi).
- PostgreSQL (Neon) — DATABASE_URL env orqali (barqaror, serverless'ga mos).
- WhiteNoise statik fayllarni runtime'da FINDERS orqali beradi — collectstatic
  shart emas, shuning uchun Vercel build oddiy bo'ladi.
- Media: filesystem (Vercel'da vaqtinchalik). Portfolio kontenti DB'dan keladi;
  rasm yuklash kerak bo'lsa keyin Cloudinary qo'shiladi (prod.py'dagi kabi).

Vercel `VERCEL=1` env'ni avtomatik beradi va config/wsgi.py shu modulni tanlaydi —
DJANGO_SETTINGS_MODULE'ni qo'lda qo'yish shart emas.

Vercel → Settings → Environment Variables'ga qo'shiladigan kerakli qiymatlar:
    SECRET_KEY      (majburiy — xavfsiz tasodifiy qiymat)
    DATABASE_URL    (majburiy — Neon Postgres connection string)
Ixtiyoriy: DEBUG, ALLOWED_HOSTS, CUSTOM_HOSTS, CSRF_TRUSTED_ORIGINS
"""
import dj_database_url
from decouple import config

from .base import *  # noqa: F401,F403

# Xavfsiz tomon: sukut bo'yicha False. Debug kerak bo'lsa Vercel'da DEBUG=1 qo'ying.
DEBUG = config("DEBUG", default=False, cast=bool)

# Prod SECRET_KEY env'dan; base'dagi dev qiymati fallback (lekin Vercel'da o'rnating).
SECRET_KEY = config("SECRET_KEY", default=SECRET_KEY)  # noqa: F405

# --------------------------------------------------------------------------
# Ma'lumotlar bazasi — PostgreSQL (Vercel Postgres / Neon)
# --------------------------------------------------------------------------
# Vercel'ning o'rnatilgan Postgres (Storage) integratsiyasi `DATABASE_URL` va
# `POSTGRES_URL` ni avtomatik qo'shadi — ikkalasini ham qo'llab-quvvatlaymiz.
# conn_max_age=0: serverless + connection pooler uchun xavfsiz (har so'rovda yopiladi).
# Vercel Postgres integratsiyasi prefix bilan (STORAGE_...) yoki prefixsiz nom
# berishi mumkin — keng tarqalgan barcha nomlarni tekshiramiz.
_db_url = (
    config("DATABASE_URL", default="")
    or config("POSTGRES_URL", default="")
    or config("STORAGE_DATABASE_URL", default="")
    or config("STORAGE_POSTGRES_URL", default="")
    or config("STORAGE_URL", default="")
)
DATABASES = {
    "default": dj_database_url.parse(
        _db_url,
        conn_max_age=0,
        ssl_require=True,
    )
}

# --------------------------------------------------------------------------
# Statik fayllar — WhiteNoise, collectstatic'siz (runtime finders)
# --------------------------------------------------------------------------
# Manifest storage collectstatic talab qiladi; serverless read-only FS'da
# finders bilan to'g'ridan-to'g'ri manbadan beramiz.
WHITENOISE_USE_FINDERS = True
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}

# --------------------------------------------------------------------------
# Xavfsizlik — Vercel proksisi ortida HTTPS
# --------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# --------------------------------------------------------------------------
# Logging — xatolar Vercel konsoliga (Runtime Logs) chiqsin
# --------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

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
# Catch-all: agar nom kutilmagan prefix bilan bo'lsa, env ichidagi har qanday
# postgres ulanish manzilini topamiz (Vercel integratsiyasi nomi har xil bo'lishi mumkin).
if not _db_url:
    import os as _os

    for _v in _os.environ.values():
        if isinstance(_v, str) and _v.startswith(("postgres://", "postgresql://")):
            _db_url = _v
            break
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
# Email — haqiqiy SMTP (contact form "yozib qoldiring")
# --------------------------------------------------------------------------
# base.py SMTP host/parolni bermaydi (faqat dev/prod beradi), shuning uchun
# Vercel'da bularni shu yerda o'rnatamiz — aks holda Django localhost:25 ga
# ulanmoqchi bo'lib xat yuborilmaydi.
# Gmail App Password kerak: Google Account → Security → App Passwords.
# Vercel → Settings → Environment Variables'ga qo'shing:
#     EMAIL_HOST_USER       (Gmail manzilingiz)
#     EMAIL_HOST_PASSWORD   (16 belgilik App Password)
#     DEFAULT_FROM_EMAIL    (odatda Gmail manzilingiz)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=10, cast=int)

# Xabar shu manzilga keladi (env bilan o'zgartirsa bo'ladi).
CONTACT_RECIPIENT_EMAIL = config(
    "CONTACT_RECIPIENT_EMAIL", default="Abboskhonilmnuri@gmail.com"
)
# from_email berilmasa, jo'natuvchi sifatida SMTP user ishlatiladi (Gmail talabi).
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER or "Abboskhonilmnuri@gmail.com")

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

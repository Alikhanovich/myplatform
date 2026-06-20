# Portfolio — Django

Shaxsiy portfolio sayt. **Django monolith** (public frontend + admin orqali
kontent boshqaruvi), 3D/motion esa **CDN orqali** (Three.js + GSAP), build
jarayonisiz. Arxitektura `docs/` papkasidagi 3 hujjatga asoslangan.

- **Backend:** Django 5 · PostgreSQL (prod) / SQLite (dev)
- **Static:** WhiteNoise · **Media:** Cloudinary (prod)
- **Frontend:** server-rendered template + vanilla JS (React'siz)
- **Deploy:** Render.com

---

## 1. Lokal ishga tushirish

> Talab: Python 3.12+

```bash
# 1) Virtual muhit
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 2) Paketlar
pip install -r requirements.txt

# 3) Muhit faylini tayyorlash
copy .env.example .env       # Windows
# cp .env.example .env       # macOS / Linux
#   -> .env ichida SECRET_KEY ni o'zgartiring (yangi kalit):
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4) Ma'lumotlar bazasi (SQLite) + boshlang'ich kontent
python manage.py migrate
python manage.py loaddata initial_data

# 5) Admin foydalanuvchi
python manage.py createsuperuser

# 6) Serverni ishga tushirish
python manage.py runserver
```

- Sayt:  http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/studio-panel/  (`ADMIN_URL` orqali sozlanadi)

Dev'da `DJANGO_SETTINGS_MODULE` sukut bo'yicha `config.settings.dev` (SQLite,
`DEBUG=True`, email konsolga chiqadi).

---

## 2. Loyiha tuzilishi

```
config/        # sozlamalar (settings/base·dev·prod), urls, wsgi/asgi
core/          # profil · ko'nikma · tajriba · loyihalar (+ sitemaps, context_processors)
blog/          # maqolalar
templates/     # base.html, partials/, core/, blog/, 404/500
static/        # css/main.css, js/hero3d.js, js/motion.js, img/
docs/          # arxitektura hujjatlari (01/02/03)
```

Batafsil: `docs/02-System-Design.md` (8-bo'lim).

---

## 3. Kontent qo'shish (admin)

`/studio-panel/` ga kiring va:

- **Sayt profili** — ism, shior, bio, email; inline'da ijtimoiy havolalar,
  hero ko'rsatkichlar, tajriba.
- **Loyihalar** — sarlavha yozsangiz slug avtomatik; inline'da texnologiyalar;
  `is_featured` bosh sahifaga chiqaradi, `is_published` saytda ko'rsatadi.
- **Blog** — sarlavha (slug avto) → excerpt → body → kategoriya → `status=Chop etilgan`.

Rasm yuklash: faqat `jpg/jpeg/png/webp`, maksimal 5 MB.

---

## 4. Render.com'ga deploy

### Variant A — Blueprint (`render.yaml`)
1. Kodingizni GitHub repozitoriyga yuklang.
2. Render → **New → Blueprint** → repo'ni tanlang. `render.yaml` web service +
   PostgreSQL'ni avtomatik yaratadi.
3. `sync: false` env'larni Render UI'da to'ldiring:
   - `ALLOWED_HOSTS` = `your-app.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` = `https://your-app.onrender.com`
   - `CLOUDINARY_CLOUD_NAME` · `CLOUDINARY_API_KEY` · `CLOUDINARY_API_SECRET`
   - `DEFAULT_FROM_EMAIL` · `CONTACT_RECIPIENT_EMAIL` · `EMAIL_HOST_USER` · `EMAIL_HOST_PASSWORD`
   - (`SECRET_KEY` avtomatik, `DATABASE_URL` bazadan ulanadi)
4. Deploy. Build: `pip install` → `collectstatic` → `migrate`.
5. Birinchi marta admin yaratish — Render **Shell**:
   ```bash
   python manage.py createsuperuser
   python manage.py loaddata initial_data   # ixtiyoriy: namuna kontent
   ```

### Variant B — qo'lda (Procfile)
Web Service yarating: **Build** `bash build.sh`, **Start**
`gunicorn config.wsgi:application`. Env'larni yuqoridagidek qo'ying va
`DJANGO_SETTINGS_MODULE=config.settings.prod` ni qo'shing.

---

## 5. Muhit o'zgaruvchilari

To'liq ro'yxat va izohlar: `.env.example`.

| O'zgaruvchi | Dev | Prod |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | `config.settings.prod` |
| `SECRET_KEY` | fallback bor | **majburiy** |
| `ALLOWED_HOSTS` | localhost | **majburiy** (domen) |
| `DATABASE_URL` | (SQLite) | **majburiy** (Postgres) |
| `CLOUDINARY_*` | — | media uchun |
| `EMAIL_*` | konsol | SMTP |

---

## Eslatma — mockup fayllari
`Portfolio.dc.html` va `support.js` faqat **dizayn/motion referensi** (React
asosidagi preview). Ular yakuniy loyihaga import qilinmagan — barcha vizual va
motion mantiqi `static/css/main.css`, `static/js/hero3d.js`, `static/js/motion.js`
ichida React'siz qayta yozilgan.

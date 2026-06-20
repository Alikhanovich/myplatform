"""
Custom Admin Panel API views.

Ushbu modul Admin.dc.html frontend uchun zarur bo'lgan barcha
backend API'larini ta'minlaydi.

Xavfsizlik: barcha view'lar login + is_staff/is_superuser tekshiruvidan o'tadi.
Tizimga kirmaganlar Django admin login sahifasiga yo'naltiriladi.
"""
import json
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from blog.models import BlogCategory, BlogPost
from core.models import (
    Experience,
    HeroStat,
    Project,
    ProjectTech,
    SkillCategory,
    Skill,
    SiteProfile,
    SocialLink,
)


def superuser_required(view_func):
    """
    Faqat login bo'lgan staff/superuser kirishi mumkin bo'lgan dekorator.
    Login kerak bo'lganda maxsus admin login sahifasiga (/admin-panel/login/) yo'naltiradi.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        admin_login = reverse("core:admin_login")
        if not request.user.is_authenticated:
            return redirect(f"{admin_login}?next={request.path}")
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect(admin_login)
        return view_func(request, *args, **kwargs)
    return wrapper


@ensure_csrf_cookie
def admin_login_view(request):
    """
    Maxsus admin login sahifasi (/admin-panel/login/).

    Muvaffaqiyatli kirgandan keyin /admin-panel/ ga (yoki ?next= ga) yo'naltiradi.
    Faqat staff/superuser kira oladi.
    """
    panel_url = reverse("core:admin_panel")
    # Allaqachon kirgan staff -> to'g'ridan-to'g'ri panelga
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect(panel_url)

    error = None
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    if request.method == "POST":
        username = request.POST.get("login", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            # Ochiq redirect'dan himoya: faqat shu saytning ichki URL'iga.
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect(panel_url)
        error = "Login yoki parol noto'g'ri, yoki sizda ruxsat yo'q."

    return render(request, "admin/login.html", {"error": error, "next": next_url})


def admin_logout_view(request):
    """Admin paneldan chiqish -> login sahifasiga."""
    logout(request)
    return redirect("core:admin_login")


@ensure_csrf_cookie
@superuser_required
def admin_panel_view(request):
    """Custom admin panel sahifasi. Admin.dc.html ni Django template sifatida yuklaydi."""
    return render(request, "admin/admin_panel.html")


# ──────────────────────────────────────────────────────────────────────────
# API: Ma'lumotlarni yuklash (GET)
# ──────────────────────────────────────────────────────────────────────────

@superuser_required
@require_GET
def api_data(request):
    """
    Barcha kontent ma'lumotlarini yagona JSON sifatida qaytaradi.
    Admin.dc.html componentDidMount ichida chaqiriladi.
    """
    profile = SiteProfile.objects.filter(is_active=True).first()

    # Profil
    profile_data = None
    social_links = []
    hero_stats = []
    experiences = []
    if profile:
        profile_data = {
            "id": profile.id,
            "full_name": profile.full_name,
            "role": profile.role,
            "tagline": profile.tagline,
            "bio": profile.bio,
            "email": profile.email,
            "location": profile.location,
            "is_active": profile.is_active,
            "avatar_url": profile.avatar.url if profile.avatar else "",
        }
        social_links = [
            {"id": sl.id, "platform": sl.platform, "url": sl.url, "icon_key": sl.icon_key, "order": sl.order}
            for sl in profile.social_links.all()
        ]
        hero_stats = [
            {"id": hs.id, "label": hs.label, "value": hs.value, "suffix": hs.suffix, "order": hs.order}
            for hs in profile.hero_stats.all()
        ]
        experiences = [
            {
                "id": xp.id,
                "role_title": xp.role_title,
                "organization": xp.organization,
                "period": xp.period,
                "description": xp.description,
                "is_current": xp.is_current,
                "order": xp.order,
            }
            for xp in profile.experiences.all()
        ]

    # Ko'nikmalar
    skill_categories = []
    for cat in SkillCategory.objects.prefetch_related("skills").all():
        skill_categories.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "order": cat.order,
            "skills": [
                {"id": s.id, "name": s.name, "level": s.level, "order": s.order}
                for s in cat.skills.all()
            ],
        })

    # Loyihalar
    projects = []
    for p in Project.objects.prefetch_related("technologies").order_by("order", "-created_at"):
        projects.append({
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "summary": p.summary,
            "description": p.description,
            "demo_url": p.demo_url,
            "repo_url": p.repo_url,
            "is_featured": p.is_featured,
            "is_published": p.is_published,
            "order": p.order,
            "date": p.created_at.strftime("%Y.%m") if p.created_at else "",
            "cover_url": p.cover_image.url if p.cover_image else "",
            "tech": [t.name for t in p.technologies.all()],
        })

    # Blog
    blog_posts = []
    for b in BlogPost.objects.select_related("category").order_by("-created_at"):
        blog_posts.append({
            "id": b.id,
            "title": b.title,
            "slug": b.slug,
            "excerpt": b.excerpt,
            "category": b.category.name if b.category else "",
            "category_id": b.category_id,
            "status": b.status,
            "date": b.published_at.strftime("%Y.%m") if b.published_at else "",
            "created": b.created_at.strftime("%Y.%m") if b.created_at else "",
            "order": b.order,
        })

    blog_categories = [
        {"id": bc.id, "name": bc.name, "slug": bc.slug}
        for bc in BlogCategory.objects.all()
    ]

    return JsonResponse({
        "profile": profile_data,
        "social_links": social_links,
        "hero_stats": hero_stats,
        "experiences": experiences,
        "skill_categories": skill_categories,
        "projects": projects,
        "blog": blog_posts,
        "blog_categories": blog_categories,
    })


# ──────────────────────────────────────────────────────────────────────────
# API: Profil saqlash (POST)
# ──────────────────────────────────────────────────────────────────────────

@csrf_exempt
@superuser_required
@require_POST
def api_profile_save(request):
    """Profil ma'lumotlarini saqlaydi (ism, lavozim, bio, email, location)."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    profile = SiteProfile.objects.filter(is_active=True).first()
    if not profile:
        profile = SiteProfile.objects.create(
            full_name=data.get("full_name", "Portfolio"),
            role=data.get("role", ""),
            tagline=data.get("tagline", ""),
            bio=data.get("bio", ""),
            email=data.get("email", ""),
        )

    profile.full_name = data.get("full_name", profile.full_name)
    profile.role = data.get("role", profile.role)
    profile.tagline = data.get("tagline", profile.tagline)
    profile.bio = data.get("bio", profile.bio)
    profile.email = data.get("email", profile.email)
    profile.location = data.get("location", profile.location)
    profile.save()
    return JsonResponse({"ok": True, "id": profile.id})


@csrf_exempt
@superuser_required
@require_POST
def api_social_save(request):
    """Ijtimoiy havolalarni saqlaydi (full replace)."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    profile = SiteProfile.objects.filter(is_active=True).first()
    if not profile:
        return JsonResponse({"ok": False, "error": "Profil topilmadi"}, status=404)

    links = data.get("links", [])
    # Mavjudlarini o'chir, yangisini qo'sh
    profile.social_links.all().delete()
    for lnk in links:
        SocialLink.objects.create(
            profile=profile,
            platform=lnk.get("platform", ""),
            url=lnk.get("url", ""),
            icon_key=lnk.get("icon_key", ""),
            order=lnk.get("order", 0),
        )
    return JsonResponse({"ok": True})


# ──────────────────────────────────────────────────────────────────────────
# API: Hero statlar
# ──────────────────────────────────────────────────────────────────────────

@csrf_exempt
@superuser_required
@require_POST
def api_stats_save(request):
    """Hero ko'rsatkichlarni saqlaydi (full replace)."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    profile = SiteProfile.objects.filter(is_active=True).first()
    if not profile:
        return JsonResponse({"ok": False, "error": "Profil topilmadi"}, status=404)

    stats = data.get("stats", [])
    profile.hero_stats.all().delete()
    for st in stats:
        HeroStat.objects.create(
            profile=profile,
            label=st.get("label", ""),
            value=st.get("value", ""),
            suffix=st.get("suffix", ""),
            order=st.get("order", 0),
        )
    return JsonResponse({"ok": True})


# ──────────────────────────────────────────────────────────────────────────
# API: Ko'nikmalar
# ──────────────────────────────────────────────────────────────────────────

@csrf_exempt
@superuser_required
@require_POST
def api_skills_save(request):
    """Ko'nikmalar kategoriyalari + ko'nikmalarni saqlaydi."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    categories = data.get("categories", [])
    SkillCategory.objects.all().delete()
    for cat in categories:
        sc = SkillCategory.objects.create(
            name=cat.get("name", ""),
            order=cat.get("order", 0),
        )
        for sk in cat.get("skills", []):
            Skill.objects.create(
                category=sc,
                name=sk.get("name", ""),
                level=int(sk.get("level", 50)),
                order=sk.get("order", 0),
            )
    return JsonResponse({"ok": True})


# ──────────────────────────────────────────────────────────────────────────
# API: Tajriba
# ──────────────────────────────────────────────────────────────────────────

@csrf_exempt
@superuser_required
@require_POST
def api_experience_save(request):
    """Tajriba yozuvlarini saqlaydi (full replace)."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    profile = SiteProfile.objects.filter(is_active=True).first()
    if not profile:
        return JsonResponse({"ok": False, "error": "Profil topilmadi"}, status=404)

    items = data.get("items", [])
    profile.experiences.all().delete()
    for item in items:
        Experience.objects.create(
            profile=profile,
            role_title=item.get("role_title", ""),
            organization=item.get("organization", ""),
            period=item.get("period", ""),
            description=item.get("description", ""),
            is_current=bool(item.get("is_current", False)),
            order=item.get("order", 0),
        )
    return JsonResponse({"ok": True})


# ──────────────────────────────────────────────────────────────────────────
# API: Loyihalar
# ──────────────────────────────────────────────────────────────────────────

@csrf_exempt
@superuser_required
@require_POST
def api_project_toggle(request):
    """Loyiha is_featured / is_published / order ni tezkor o'zgartiradi."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    try:
        p = Project.objects.get(id=data["id"])
    except Project.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Loyiha topilmadi"}, status=404)

    key = data.get("key")
    if key in ("is_featured", "is_published"):
        setattr(p, key, not getattr(p, key))
    elif key == "order":
        try:
            p.order = int(data.get("value", p.order))
        except (TypeError, ValueError):
            pass
    p.save()
    return JsonResponse({"ok": True, "is_featured": p.is_featured, "is_published": p.is_published, "order": p.order})


@csrf_exempt
@superuser_required
@require_POST
def api_project_save(request):
    """Loyiha yaratadi yoki tahrirlaydi. multipart/form-data qabul qiladi (rasm uchun)."""
    pid = request.POST.get("id") or None
    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"ok": False, "error": "Nomi majburiy"}, status=400)

    if pid:
        try:
            p = Project.objects.get(id=int(pid))
        except Project.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Loyiha topilmadi"}, status=404)
    else:
        p = Project()

    p.title = title
    p.summary = request.POST.get("summary", "")
    p.description = request.POST.get("description", "")
    p.demo_url = request.POST.get("demo_url", "")
    p.repo_url = request.POST.get("repo_url", "")
    p.is_featured = request.POST.get("is_featured") == "true"
    p.is_published = request.POST.get("is_published") == "true"
    try:
        p.order = int(request.POST.get("order", 0))
    except ValueError:
        p.order = 0

    if "cover" in request.FILES:
        p.cover_image = request.FILES["cover"]

    p.save()

    # Texnologiyalar (vergul bilan ajratilgan)
    tech_raw = request.POST.get("tech", "")
    p.technologies.all().delete()
    for i, name in enumerate(t.strip() for t in tech_raw.split(",") if t.strip()):
        ProjectTech.objects.create(project=p, name=name, order=i)

    return JsonResponse({"ok": True, "id": p.id, "slug": p.slug})


@csrf_exempt
@superuser_required
@require_POST
def api_project_delete(request):
    """Loyihani o'chiradi."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    try:
        Project.objects.get(id=data["id"]).delete()
    except Project.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Loyiha topilmadi"}, status=404)
    return JsonResponse({"ok": True})


# ──────────────────────────────────────────────────────────────────────────
# API: Blog
# ──────────────────────────────────────────────────────────────────────────

@csrf_exempt
@superuser_required
@require_POST
def api_blog_toggle(request):
    """Blog post status (published <-> draft) ni o'zgartiradi."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    try:
        b = BlogPost.objects.get(id=data["id"])
    except BlogPost.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Post topilmadi"}, status=404)

    if b.status == BlogPost.Status.PUBLISHED:
        b.status = BlogPost.Status.DRAFT
    else:
        b.status = BlogPost.Status.PUBLISHED
        if b.published_at is None:
            b.published_at = timezone.now()
    b.save()
    return JsonResponse({"ok": True, "status": b.status})


@csrf_exempt
@superuser_required
@require_POST
def api_blog_save(request):
    """Blog post yaratadi yoki tahrirlaydi. multipart/form-data qabul qiladi."""
    pid = request.POST.get("id") or None
    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"ok": False, "error": "Sarlavha majburiy"}, status=400)

    if pid:
        try:
            b = BlogPost.objects.get(id=int(pid))
        except BlogPost.DoesNotExist:
            return JsonResponse({"ok": False, "error": "Post topilmadi"}, status=404)
    else:
        b = BlogPost()

    b.title = title
    b.excerpt = request.POST.get("excerpt", "")
    b.body = request.POST.get("body", "")
    b.status = request.POST.get("status", BlogPost.Status.DRAFT)

    cat_id = request.POST.get("category_id")
    if cat_id:
        try:
            b.category_id = int(cat_id)
        except ValueError:
            b.category = None
    else:
        b.category = None

    if "cover" in request.FILES:
        b.cover_image = request.FILES["cover"]

    b.save()
    return JsonResponse({"ok": True, "id": b.id, "slug": b.slug})


@csrf_exempt
@superuser_required
@require_POST
def api_blog_delete(request):
    """Blog postni o'chiradi."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON parse xatosi"}, status=400)

    try:
        BlogPost.objects.get(id=data["id"]).delete()
    except BlogPost.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Post topilmadi"}, status=404)
    return JsonResponse({"ok": True})

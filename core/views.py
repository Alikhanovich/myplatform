"""
core view'lari (02-System-Design 3-bo'lim).

Generic class-based view'lar (TemplateView/ListView/DetailView) — kod kam,
pagination/slug-lookup bepul keladi.
"""
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView, View

from blog.models import BlogPost

from .forms import ContactForm
from .models import Experience, Project, SiteProfile, SkillCategory


class HomeView(TemplateView):
    """Bosh sahifa: hero + about + skills + featured loyihalar + blog preview + contact."""

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = SiteProfile.get_active()
        ctx["profile"] = profile
        ctx["hero_stats"] = profile.hero_stats.all() if profile else []
        ctx["experiences"] = profile.experiences.all() if profile else []
        ctx["skill_categories"] = (
            SkillCategory.objects.prefetch_related("skills").all()
        )
        ctx["featured_projects"] = (
            Project.published.filter(is_featured=True).prefetch_related("technologies")
        )
        ctx["latest_posts"] = BlogPost.published.select_related("category")[:3]
        # Contact forma (POST'dan kelgan xatolarni session orqali qayta ko'rsatish o'rniga
        # bu yerda toza forma beriladi; xatolar ContactView'da messages bilan ko'rsatiladi).
        ctx["contact_form"] = kwargs.get("contact_form") or ContactForm()
        return ctx


class ProjectListView(ListView):
    """Barcha chop etilgan loyihalar grid."""

    template_name = "core/project_list.html"
    context_object_name = "projects"
    paginate_by = 9

    def get_queryset(self):
        return Project.published.prefetch_related("technologies")


class ProjectDetailView(DetailView):
    """Bitta loyiha to'liq sahifasi (slug-based)."""

    template_name = "core/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.published.prefetch_related("technologies")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        # "Keyingi loyiha →" havolasi (tartib bo'yicha keyingisi, aylanma).
        qs = list(Project.published.all())
        if obj in qs and len(qs) > 1:
            idx = qs.index(obj)
            ctx["next_project"] = qs[(idx + 1) % len(qs)]
        return ctx


class ContactView(View):
    """Contact form yuborish (POST) — email + honeypot."""

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        redirect_url = reverse("core:home") + "#contact"

        if not form.is_valid():
            messages.error(
                request, "Xabar yuborilmadi — maydonlarni tekshirib qayta urinib ko'ring."
            )
            return redirect(redirect_url)

        data = form.cleaned_data
        subject = f"[Portfolio] Yangi xabar: {data['name']}"
        body = (
            f"Ism: {data['name']}\n"
            f"Email: {data['email']}\n\n"
            f"Xabar:\n{data['message']}\n"
        )
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_RECIPIENT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Rahmat! Xabaringiz yuborildi — tez orada javob beraman.")
        except Exception:
            messages.error(
                request, "Texnik nosozlik tufayli xabar yuborilmadi. Birozdan keyin urinib ko'ring."
            )
        return redirect(redirect_url)


# --------------------------------------------------------------------------
# robots.txt + xato sahifalari
# --------------------------------------------------------------------------
def robots_txt(request):
    """Oddiy robots.txt — sitemap havolasi bilan."""
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Disallow: /{settings.ADMIN_URL.rstrip('/')}/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def handler404(request, exception):
    from django.shortcuts import render

    return render(request, "404.html", status=404)


def handler500(request):
    from django.shortcuts import render

    return render(request, "500.html", status=500)

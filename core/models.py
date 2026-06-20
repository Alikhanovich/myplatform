"""
core modellari (02-System-Design ERD).

Profilning "shaxs" qismi: SiteProfile (singleton), SocialLink, HeroStat,
SkillCategory, Skill, Experience, Project, ProjectTech.

Matnli field nomlari inglizcha va suffiksiz (title, body, summary) —
keyin django-modeltranslation bilan kengaytirilganda buzilmaydi.
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .validators import UUIDImagePath, validate_image_extension, validate_image_size


# ==========================================================================
#  Profil (singleton) + bog'liq inline modellar
# ==========================================================================
class SiteProfile(models.Model):
    """
    Sayt egasi haqidagi yagona yozuv (singleton).

    Admin'da "add" bittadan keyin cheklanadi (admin.py: has_add_permission).
    """

    full_name = models.CharField("To'liq ism", max_length=120)
    role = models.CharField("Lavozim", max_length=120)
    tagline = models.CharField("Shior (hero)", max_length=200)
    bio = models.TextField("Bio / about")
    avatar = models.ImageField(
        "Avatar",
        upload_to=UUIDImagePath("profile"),
        blank=True,
        validators=[validate_image_extension, validate_image_size],
    )
    email = models.EmailField("Email")
    location = models.CharField("Manzil", max_length=120, blank=True)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Sayt profili"
        verbose_name_plural = "Sayt profili"

    def __str__(self):
        return self.full_name

    @classmethod
    def get_active(cls):
        """View'lar uchun: faol profilni qaytaradi (yoki None)."""
        return cls.objects.filter(is_active=True).first()


class SocialLink(models.Model):
    """Profilga tegishli ijtimoiy/aloqa havolasi (GitHub, Telegram, ...)."""

    profile = models.ForeignKey(
        SiteProfile, related_name="social_links", on_delete=models.CASCADE
    )
    platform = models.CharField("Platforma", max_length=60)
    url = models.URLField("Havola")
    icon_key = models.CharField(
        "Ikona kaliti",
        max_length=40,
        blank=True,
        help_text="Masalan: github, telegram, linkedin, email",
    )
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Ijtimoiy havola"
        verbose_name_plural = "Ijtimoiy havolalar"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.platform}"


class HeroStat(models.Model):
    """Hero bo'limidagi raqamli ko'rsatkich (12+ Loyiha, 3+ Yil...)."""

    profile = models.ForeignKey(
        SiteProfile, related_name="hero_stats", on_delete=models.CASCADE
    )
    label = models.CharField("Yorliq", max_length=60)
    value = models.CharField(
        "Qiymat",
        max_length=20,
        help_text="Raqam (masalan 12) bo'lsa animatsiya bilan sanaladi; matn (UZ) statik.",
    )
    suffix = models.CharField("Suffiks", max_length=10, blank=True, help_text="Masalan: +")
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Hero ko'rsatkich"
        verbose_name_plural = "Hero ko'rsatkichlar"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.value}{self.suffix} · {self.label}"


# ==========================================================================
#  Ko'nikmalar
# ==========================================================================
class SkillCategory(models.Model):
    """Ko'nikmalar guruhi (Backend, Mobil, Vositalar...)."""

    name = models.CharField("Nomi", max_length=60)
    slug = models.SlugField("Slug", max_length=70, unique=True, blank=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Ko'nikma kategoriyasi"
        verbose_name_plural = "Ko'nikma kategoriyalari"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Skill(models.Model):
    """Bitta ko'nikma + 0–100 kalibr darajasi."""

    category = models.ForeignKey(
        SkillCategory, related_name="skills", on_delete=models.CASCADE
    )
    name = models.CharField("Nomi", max_length=80)
    level = models.PositiveSmallIntegerField(
        "Daraja (0–100)",
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Ko'nikma"
        verbose_name_plural = "Ko'nikmalar"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.level})"


# ==========================================================================
#  Tajriba
# ==========================================================================
class Experience(models.Model):
    """Ish/tajriba yozuvi (timeline)."""

    profile = models.ForeignKey(
        SiteProfile, related_name="experiences", on_delete=models.CASCADE
    )
    role_title = models.CharField("Lavozim", max_length=120)
    organization = models.CharField("Tashkilot", max_length=120)
    period = models.CharField("Davr", max_length=60, help_text="Masalan: 2023 — HOZIR")
    description = models.TextField("Tavsif")
    is_current = models.BooleanField("Hozirgi", default=False)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Tajriba"
        verbose_name_plural = "Tajribalar"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.role_title} · {self.organization}"


# ==========================================================================
#  Loyihalar
# ==========================================================================
class PublishedProjectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Project(models.Model):
    """Portfolio loyihasi."""

    title = models.CharField("Sarlavha", max_length=140)
    slug = models.SlugField("Slug", max_length=160, unique=True, blank=True)
    summary = models.CharField("Qisqa tavsif", max_length=300)
    description = models.TextField("To'liq tavsif")
    cover_image = models.ImageField(
        "Muqova rasmi",
        upload_to=UUIDImagePath("projects"),
        blank=True,
        validators=[validate_image_extension, validate_image_size],
    )
    demo_url = models.URLField("Demo havola", blank=True)
    repo_url = models.URLField("Repozitoriy havola", blank=True)
    is_featured = models.BooleanField("Tanlangan (bosh sahifa)", default=False)
    is_published = models.BooleanField("Chop etilgan", default=True)
    created_at = models.DateField("Sana", default=timezone.now)
    order = models.PositiveIntegerField("Tartib", default=0)

    # ERD: Project }o--o| BlogPost (ixtiyoriy bog'liqlik).
    related_post = models.ForeignKey(
        "blog.BlogPost",
        verbose_name="Bog'liq maqola (ixtiyoriy)",
        related_name="related_projects",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    objects = models.Manager()
    published = PublishedProjectManager()

    class Meta:
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:project_detail", kwargs={"slug": self.slug})


class ProjectTech(models.Model):
    """Loyihada ishlatilgan texnologiya (inline)."""

    project = models.ForeignKey(
        Project, related_name="technologies", on_delete=models.CASCADE
    )
    name = models.CharField("Texnologiya", max_length=60)
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Texnologiya"
        verbose_name_plural = "Texnologiyalar"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

"""
blog modellari (02-System-Design ERD).

Maqolalar — alohida hayot tsikliga ega kontent oqimi (kategoriya, status, sana).
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from core.validators import UUIDImagePath, validate_image_extension, validate_image_size


class BlogCategory(models.Model):
    """Maqola kategoriyasi (Django, Flutter, SaaS...)."""

    name = models.CharField("Nomi", max_length=60)
    slug = models.SlugField("Slug", max_length=70, unique=True, blank=True)

    class Meta:
        verbose_name = "Blog kategoriyasi"
        verbose_name_plural = "Blog kategoriyalari"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_list_by_category", kwargs={"slug": self.slug})


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(status=BlogPost.Status.PUBLISHED, published_at__lte=timezone.now())
        )


class BlogPost(models.Model):
    """Bitta blog maqolasi."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        PUBLISHED = "published", "Chop etilgan"

    category = models.ForeignKey(
        BlogCategory,
        verbose_name="Kategoriya",
        related_name="posts",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    title = models.CharField("Sarlavha", max_length=180)
    slug = models.SlugField("Slug", max_length=200, unique=True, blank=True)
    excerpt = models.CharField("Qisqa matn (excerpt)", max_length=300)
    body = models.TextField("Matn")
    cover_image = models.ImageField(
        "Muqova rasmi",
        upload_to=UUIDImagePath("blog"),
        blank=True,
        validators=[validate_image_extension, validate_image_size],
    )
    status = models.CharField(
        "Holat",
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField("Chop etilgan sana", null=True, blank=True)
    created_at = models.DateTimeField("Yaratilgan", auto_now_add=True)
    order = models.PositiveIntegerField("Tartib", default=0)

    objects = models.Manager()
    published = PublishedPostManager()

    class Meta:
        verbose_name = "Blog maqolasi"
        verbose_name_plural = "Blog maqolalari"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Chop etilganda sana bo'sh bo'lsa — hozirgi vaqt.
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

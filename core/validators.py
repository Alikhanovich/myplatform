"""
Rasm yuklash validatorlari (01-Arxitektura 4-bo'lim, 02-System-Design 5-bo'lim).

- Faqat ruxsat etilgan formatlar: jpg / jpeg / png / webp
- Maksimal o'lcham: 5 MB
"""
import os

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible

# Migratsiyalarda seriyalanishi uchun modul darajasidagi instans.
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_SIZE = MAX_IMAGE_SIZE_MB * 1024 * 1024

validate_image_extension = FileExtensionValidator(
    allowed_extensions=ALLOWED_IMAGE_EXTENSIONS
)


@deconstructible
class ImageSizeValidator:
    """Yuklangan rasm hajmi cheklovdan oshmasligini tekshiradi."""

    def __init__(self, max_size=MAX_IMAGE_SIZE):
        self.max_size = max_size

    def __call__(self, file):
        if file and file.size and file.size > self.max_size:
            raise ValidationError(
                "Rasm hajmi juda katta (%(size).1f MB). "
                "Ruxsat etilgan maksimal: %(max)d MB."
                % {"size": file.size / (1024 * 1024), "max": self.max_size // (1024 * 1024)}
            )

    def __eq__(self, other):
        return isinstance(other, ImageSizeValidator) and self.max_size == other.max_size


validate_image_size = ImageSizeValidator()


@deconstructible
class UUIDImagePath:
    """
    upload_to callable: rasmni sana bo'yicha papkaga, UUID nomi bilan saqlaydi.

    Natija:  <subdir>/2026/06/<uuid32>.<ext>
    (02-System-Design: upload_to='projects/%Y/%m/' + UUID qayta nomlash)
    """

    def __init__(self, subdir):
        self.subdir = subdir

    def __call__(self, instance, filename):
        # Kechiktirilgan import — modul yuklanishini yengillashtiradi.
        import uuid

        from django.utils import timezone

        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        if ext == "jpeg":
            ext = "jpg"
        name = f"{uuid.uuid4().hex}.{ext}"
        return f"{self.subdir}/{timezone.now():%Y/%m}/{name}"

    def __eq__(self, other):
        return isinstance(other, UUIDImagePath) and self.subdir == other.subdir

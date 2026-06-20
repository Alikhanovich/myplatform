"""
core admin (02-System-Design 4-bo'lim).

Texnik bo'lmagan egasi uchun qulay kontent-boshqaruv paneli:
list_display / list_editable / list_filter / search / prepopulated / inline.
"""
from django.contrib import admin

from .models import (
    Experience,
    HeroStat,
    Project,
    ProjectTech,
    SiteProfile,
    Skill,
    SkillCategory,
    SocialLink,
)

# Admin sarlavhalari (/studio-panel/).
admin.site.site_header = "Portfolio Studio"
admin.site.site_title = "Portfolio Studio"
admin.site.index_title = "Kontent boshqaruvi"


# ==========================================================================
#  SiteProfile (singleton) + inline'lar
# ==========================================================================
class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1


class HeroStatInline(admin.TabularInline):
    model = HeroStat
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "is_active")
    list_editable = ("is_active",)
    inlines = [SocialLinkInline, HeroStatInline, ExperienceInline]

    def has_add_permission(self, request):
        # Singleton — bitta profil mavjud bo'lsa "add" cheklanadi.
        if SiteProfile.objects.exists():
            return False
        return super().has_add_permission(request)


# ==========================================================================
#  Ko'nikmalar
# ==========================================================================
class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SkillInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "level", "order")
    list_editable = ("level", "order")
    list_filter = ("category",)
    search_fields = ("name",)


# ==========================================================================
#  Tajriba
# ==========================================================================
@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("role_title", "organization", "period", "is_current", "order")
    list_editable = ("is_current", "order")
    ordering = ("order",)


# ==========================================================================
#  Loyihalar
# ==========================================================================
class ProjectTechInline(admin.TabularInline):
    model = ProjectTech
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "is_published", "order", "created_at")
    list_editable = ("is_featured", "is_published", "order")
    list_filter = ("is_featured", "is_published")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    inlines = [ProjectTechInline]
    autocomplete_fields = ("related_post",)

"""
Global template konteksti — har sahifaga profil + ijtimoiy havolalar beradi
(nav va footer shularga tayanadi). Profil bo'lmasa ham xavfsiz (None) ishlaydi.
"""
from .models import SiteProfile


def site_context(request):
    profile = SiteProfile.get_active()
    social_links = profile.social_links.all() if profile else []
    return {
        "site_profile": profile,
        "site_social_links": social_links,
    }

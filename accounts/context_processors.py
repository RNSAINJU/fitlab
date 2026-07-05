from django.conf import settings

from accounts.models import SiteConfiguration
from accounts.theme import resolve_theme


def social_auth(request):
    return {
        "SOCIAL_AUTH_GOOGLE_ENABLED": settings.SOCIAL_AUTH_GOOGLE_ENABLED,
        "SOCIAL_AUTH_APPLE_ENABLED": settings.SOCIAL_AUTH_APPLE_ENABLED,
    }


def site_branding(request):
    return {"site_config": SiteConfiguration.load()}


def theme(request):
    active = resolve_theme(request)
    return {
        "theme": active,
        "theme_is_light": active == "light",
    }

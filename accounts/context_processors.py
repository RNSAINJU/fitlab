from django.conf import settings


def social_auth(request):
    return {
        "SOCIAL_AUTH_GOOGLE_ENABLED": settings.SOCIAL_AUTH_GOOGLE_ENABLED,
        "SOCIAL_AUTH_APPLE_ENABLED": settings.SOCIAL_AUTH_APPLE_ENABLED,
    }

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import include, path


def oauth_provider_disabled(request, provider):
    messages.info(request, f"{provider.title()} sign-in is not configured.")
    return redirect("accounts:login")


urlpatterns = [
    path("django-admin/", admin.site.urls),
]

if not settings.SOCIAL_AUTH_GOOGLE_ENABLED:
    urlpatterns.append(
        path(
            "oauth/google/login/",
            lambda request: oauth_provider_disabled(request, "google"),
            name="google_login",
        )
    )
    urlpatterns.append(
        path(
            "oauth/google/login/callback/",
            lambda request: oauth_provider_disabled(request, "google"),
        )
    )
if not settings.SOCIAL_AUTH_APPLE_ENABLED:
    urlpatterns.append(
        path(
            "oauth/apple/login/",
            lambda request: oauth_provider_disabled(request, "apple"),
            name="apple_login",
        )
    )
    urlpatterns.append(
        path(
            "oauth/apple/login/callback/",
            lambda request: oauth_provider_disabled(request, "apple"),
        )
    )

urlpatterns += [
    path("oauth/", include("allauth.urls")),
    path("", include("accounts.urls")),
    path("activity/", include("activity.urls")),
    path("rewards/", include("rewards.urls")),
    path("referrals/", include("referrals.urls")),
    path("admin-portal/", include("admin_portal.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

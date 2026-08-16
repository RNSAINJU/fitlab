from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from accounts.sitemaps import StaticViewSitemap

sitemaps = {"static": StaticViewSitemap}

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("oauth/", include("allauth.urls")),
    path("", include("accounts.urls")),
    path("activity/", include("activity.urls")),
    path("rewards/", include("rewards.urls")),
    path("referrals/", include("referrals.urls")),
    path("admin-portal/", include("admin_portal.urls")),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

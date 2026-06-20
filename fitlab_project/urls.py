from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("activity/", include("activity.urls")),
    path("rewards/", include("rewards.urls")),
    path("referrals/", include("referrals.urls")),
    path("admin-portal/", include("admin_portal.urls")),
]

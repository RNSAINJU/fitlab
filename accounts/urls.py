from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register", views.register, name="register_short"),
    path("accounts/login/", views.FitlabLoginView.as_view(), name="login"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/profile/edit/", views.edit_profile, name="profile_edit"),
    path("accounts/profile/", views.profile, name="profile"),
    path("accounts/pending/", views.pending_approval, name="pending"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/theme/", views.set_theme, name="set_theme"),
    path("connection-lost/", views.connection_lost, name="connection_lost"),
]

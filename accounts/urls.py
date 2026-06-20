from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("accounts/login/", views.FitlabLoginView.as_view(), name="login"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/pending/", views.pending_approval, name="pending"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("connection-lost/", views.connection_lost, name="connection_lost"),
]

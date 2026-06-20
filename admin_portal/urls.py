from django.urls import path

from . import views

app_name = "admin_portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("customers/", views.customer_directory, name="customer_directory"),
    path("approvals/", views.registration_approvals, name="registration_approvals"),
    path("ledger/", views.points_ledger, name="points_ledger"),
]

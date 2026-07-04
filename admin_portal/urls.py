from django.urls import path

from . import views

app_name = "admin_portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("customers/", views.customer_directory, name="customer_directory"),
    path("customers/export/", views.customer_export, name="customer_export"),
    path("customers/import/", views.customer_import, name="customer_import"),
    path("approvals/", views.registration_approvals, name="registration_approvals"),
    path("rewards/", views.rewards_list, name="rewards_list"),
    path("rewards/create/", views.reward_create, name="reward_create"),
    path("roles/", views.role_management, name="role_management"),
    path("ledger/", views.points_ledger, name="points_ledger"),
    path("point-rules/", views.point_rules, name="point_rules"),
]

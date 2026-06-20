from django.urls import path

from . import views

app_name = "rewards"

urlpatterns = [
    path("", views.marketplace, name="marketplace"),
    path("<int:reward_id>/redeem/", views.redeem, name="redeem"),
]

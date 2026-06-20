from django.urls import path

from . import views

app_name = "activity"

urlpatterns = [
    path("", views.feed, name="feed"),
]

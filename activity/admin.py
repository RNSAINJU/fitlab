from django.contrib import admin

from .models import ActivityEvent


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "title", "created_at")
    list_filter = ("event_type",)

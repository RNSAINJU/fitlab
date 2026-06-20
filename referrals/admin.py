from django.contrib import admin

from .models import ReferralRecord


@admin.register(ReferralRecord)
class ReferralRecordAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referee", "bonus_awarded", "bonus_points", "created_at")

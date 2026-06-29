from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "phone", "approval_status", "is_staff", "date_joined")
    list_filter = ("approval_status", "is_staff", "is_superuser")
    search_fields = ("username", "email", "phone", "referral_code")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("The Fitlab", {"fields": ("phone", "approval_status", "referral_code", "referred_by")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("The Fitlab", {"fields": ("phone", "approval_status", "referral_code")}),
    )

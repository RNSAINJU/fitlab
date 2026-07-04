from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "member_id", "phone", "approval_status", "is_staff", "date_joined")
    list_filter = ("approval_status", "is_staff", "is_superuser")
    search_fields = ("username", "email", "phone", "member_id", "referral_code")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("The Fitlab", {"fields": ("member_id", "phone", "address", "date_of_birth", "gender", "profile_photo", "approval_status", "referral_code", "referred_by")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("The Fitlab", {"fields": ("phone", "date_of_birth", "gender", "profile_photo", "approval_status", "referral_code")}),
    )

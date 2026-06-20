from django.contrib import admin

from .models import RedemptionRequest, Reward


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("title", "points_cost", "is_active", "stock")


@admin.register(RedemptionRequest)
class RedemptionRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "reward", "points_cost", "status", "created_at")
    list_filter = ("status",)

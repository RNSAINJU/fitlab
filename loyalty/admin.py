from django.contrib import admin

from .models import PointRule, PointTransaction


@admin.register(PointRule)
class PointRuleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "points_amount", "trigger", "rule_kind", "is_active", "is_system", "updated_at")
    list_filter = ("is_active", "is_system", "trigger", "rule_kind")
    search_fields = ("title", "slug", "description")


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "transaction_type", "rule", "description", "created_at")
    list_filter = ("transaction_type",)
    search_fields = ("user__email", "user__username", "description")

from django.contrib import admin

from .models import PointTransaction


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "transaction_type", "description", "created_at")
    list_filter = ("transaction_type",)
    search_fields = ("user__email", "user__username", "description")

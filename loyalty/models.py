from django.conf import settings
from django.db import models


class PointTransaction(models.Model):
    class TransactionType(models.TextChoices):
        EARN = "earn", "Earn"
        REDEEM = "redeem", "Redeem"
        ADJUST = "adjust", "Adjust"
        REFERRAL = "referral", "Referral bonus"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="point_transactions")
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    description = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_point_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"{self.user} {sign}{self.amount} ({self.transaction_type})"

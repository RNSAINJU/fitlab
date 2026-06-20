from django.conf import settings
from django.db import models


class ReferralRecord(models.Model):
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_records",
    )
    referee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="referral_record",
    )
    bonus_awarded = models.BooleanField(default=False)
    bonus_points = models.PositiveIntegerField(default=0)
    awarded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer} → {self.referee}"

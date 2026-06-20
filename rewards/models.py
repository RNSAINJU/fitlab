from django.conf import settings
from django.db import models


class Reward(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    points_cost = models.PositiveIntegerField()
    image_emoji = models.CharField(max_length=8, default="🎁")
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["points_cost"]

    def __str__(self):
        return self.title

    @property
    def in_stock(self):
        return self.stock is None or self.stock > 0


class RedemptionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="redemptions")
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name="redemptions")
    points_cost = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_note = models.CharField(max_length=255, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_redemptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} → {self.reward} ({self.status})"

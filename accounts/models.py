import secrets
import string

from django.contrib.auth.models import AbstractUser
from django.db import models


def generate_referral_code():
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


class User(AbstractUser):
    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    phone = models.CharField(max_length=20, blank=True)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    referral_code = models.CharField(max_length=12, unique=True, default=generate_referral_code)
    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals",
    )

    @property
    def is_approved(self):
        return self.approval_status == self.ApprovalStatus.APPROVED

    @property
    def display_name(self):
        full = self.get_full_name().strip()
        return full or self.username

    def __str__(self):
        return self.email or self.username

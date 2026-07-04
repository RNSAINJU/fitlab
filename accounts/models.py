import secrets
import string

from django.contrib.auth.models import AbstractUser
from django.db import models


def generate_referral_code():
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


def profile_photo_path(instance, filename):
    return f"profile_photos/user_{instance.pk}/{filename}"


def site_logo_path(instance, filename):
    return f"site/logo_{filename}"


class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=120, default="The Fitlab")
    logo = models.ImageField(upload_to=site_logo_path, blank=True)

    class Meta:
        verbose_name = "Site configuration"
        verbose_name_plural = "Site configuration"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        from django.contrib.sites.models import Site

        Site.objects.filter(pk=1).update(name=self.site_name)

    def delete(self, *args, **kwargs):
        raise RuntimeError("Site configuration cannot be deleted.")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"site_name": "The Fitlab"})
        return obj

    @property
    def admin_title(self):
        return f"{self.site_name} Admin"


class User(AbstractUser):
    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        PREFER_NOT = "prefer_not", "Prefer not to say"

    phone = models.CharField(max_length=20, blank=True)
    member_id = models.CharField(max_length=32, blank=True, null=True, unique=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
    )
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True)
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

    @property
    def profile_initial(self):
        if self.first_name:
            return self.first_name[0].upper()
        if self.email:
            return self.email[0].upper()
        return "F"

    def __str__(self):
        return self.email or self.username

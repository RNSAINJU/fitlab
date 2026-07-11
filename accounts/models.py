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


def home_hero_image_path(instance, filename):
    return f"home/hero/{filename}"


def home_hero_video_path(instance, filename):
    return f"home/hero/{filename}"


def home_section_image_path(instance, filename):
    return f"home/sections/{filename}"


def home_powerlifter_path(instance, filename):
    return f"home/powerlifters/{filename}"


def home_trainer_path(instance, filename):
    return f"home/trainers/{filename}"


def home_gallery_path(instance, filename):
    return f"home/gallery/{filename}"


def home_client_path(instance, filename):
    return f"home/clients/{filename}"


def home_pricing_bg_path(instance, filename):
    return f"home/pricing/{filename}"


def home_pricing_banner_path(instance, filename):
    return f"home/pricing/banner_{filename}"


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


class HomePageSettings(models.Model):
    class HeroMediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    hero_headline = models.CharField(max_length=200, default="Recruit Yourself")
    hero_subtext = models.CharField(
        max_length=240,
        blank=True,
        default="Join the elite lab where data meets dedication.",
    )
    hero_cta_text = models.CharField(max_length=80, default="Enquire Now")
    hero_image = models.ImageField(upload_to=home_hero_image_path, blank=True)
    hero_video = models.FileField(upload_to=home_hero_video_path, blank=True)
    hero_media_type = models.CharField(
        max_length=10,
        choices=HeroMediaType.choices,
        default=HeroMediaType.IMAGE,
    )
    hero_image_url = models.URLField(
        blank=True,
        help_text="Used when no hero image is uploaded.",
    )

    powerlifters_title = models.CharField(max_length=120, default="Powerlifters")
    powerlifters_watermark = models.CharField(max_length=80, default="Iconic")

    welcome_tagline = models.CharField(max_length=200, default="A Private Gym in Kathmandu")
    welcome_paragraph_1 = models.TextField(blank=True)
    welcome_paragraph_2 = models.TextField(blank=True)
    welcome_paragraph_3 = models.TextField(blank=True)

    trainers_title = models.CharField(max_length=120, default="Meet the Trainers")
    training_title = models.CharField(max_length=120, default="Training")
    training_intro = models.TextField(blank=True)

    schedule_image = models.ImageField(upload_to=home_section_image_path, blank=True)
    schedule_image_url = models.URLField(blank=True)

    rates_title = models.CharField(max_length=120, default="Pricing")
    pricing_image = models.ImageField(upload_to=home_pricing_banner_path, blank=True)
    pricing_image_url = models.URLField(blank=True)
    pricing_image_alt = models.CharField(max_length=160, blank=True, default="Gym pricing")
    gallery_title = models.CharField(max_length=120, default="Training Gallery")
    gallery_watermark = models.CharField(max_length=80, default="Gallery")
    testimonials_title = models.CharField(max_length=160, default="What People Say About Us")

    clients_title = models.CharField(max_length=120, default="Our Clients")
    clients_intro = models.TextField(blank=True)

    footer_blurb = models.TextField(blank=True)
    footer_cta = models.CharField(max_length=120, default="Join us today!")
    contact_address = models.TextField(blank=True, default="Kathmandu, Nepal")
    contact_email = models.EmailField(blank=True, default="info@thefitlab.com.np")
    map_location = models.CharField(
        max_length=255,
        blank=True,
        default="The Fit Lab Gym, Bhaktapur, Nepal",
        help_text="Address or place name used for the Find Us map.",
    )
    map_embed_url = models.URLField(
        blank=True,
        default="https://maps.google.com/maps?q=Kathmandu%2C%20Nepal&z=13&output=embed",
    )

    class Meta:
        verbose_name = "Home page settings"
        verbose_name_plural = "Home page settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RuntimeError("Home page settings cannot be deleted.")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def hero_background_url(self):
        if self.hero_image:
            return self.hero_image.url
        return self.hero_image_url or (
            "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1920&q=80"
        )

    def schedule_photo_url(self):
        if self.schedule_image:
            return self.schedule_image.url
        return self.schedule_image_url or (
            "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&q=80"
        )

    def pricing_photo_url(self):
        if self.pricing_image:
            return self.pricing_image.url
        return self.pricing_image_url or ""

    def map_iframe_src(self):
        from urllib.parse import quote

        location = (self.map_location or "").strip()
        embed = (self.map_embed_url or "").strip()

        def is_embed_url(url):
            return bool(url) and ("/maps/embed" in url or "output=embed" in url)

        if is_embed_url(embed):
            return embed

        if location.startswith("http"):
            if is_embed_url(location):
                return location
            return ""

        if location:
            return (
                f"https://www.google.com/maps?q={quote(location)}"
                "&z=15&output=embed"
            )

        return ""


class HomePowerlifter(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to=home_powerlifter_path, blank=True)
    image_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.name

    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ""


class HomeTrainer(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to=home_trainer_path, blank=True)
    image_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.name

    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ""


class HomeTrainingService(models.Model):
    title = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.title


class HomeScheduleSlot(models.Model):
    title = models.CharField(max_length=160)
    time_info = models.CharField(max_length=200)
    days_info = models.CharField(max_length=120, default="Sunday – Friday")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.title


class HomePricingPlan(models.Model):
    title = models.CharField(max_length=120)
    feature_1 = models.CharField(max_length=200, blank=True)
    feature_2 = models.CharField(max_length=200, blank=True)
    feature_3 = models.CharField(max_length=200, blank=True)
    background_image = models.ImageField(upload_to=home_pricing_bg_path, blank=True)
    background_image_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.title

    def background_url(self):
        if self.background_image:
            return self.background_image.url
        return self.background_image_url or (
            "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80"
        )

    def features(self):
        return [f for f in (self.feature_1, self.feature_2, self.feature_3) if f]


class HomePricingTier(models.Model):
    plan = models.ForeignKey(HomePricingPlan, on_delete=models.CASCADE, related_name="tiers")
    price_label = models.CharField(max_length=200)
    sessions_label = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.price_label


class HomeGalleryImage(models.Model):
    image = models.ImageField(upload_to=home_gallery_path, blank=True)
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ""


class HomeTestimonial(models.Model):
    quote = models.TextField()
    author = models.CharField(max_length=120)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.author


class HomeClientSpotlight(models.Model):
    class Row(models.IntegerChoices):
        ROW_1 = 1, "Row 1"
        ROW_2 = 2, "Row 2"

    caption = models.CharField(max_length=200)
    image = models.ImageField(upload_to=home_client_path, blank=True)
    image_url = models.URLField(blank=True)
    row = models.PositiveSmallIntegerField(choices=Row.choices, default=Row.ROW_1)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["row", "sort_order", "pk"]

    def __str__(self):
        return self.caption

    def display_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url or ""


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
    theme_preference = models.CharField(
        max_length=10,
        choices=[("dark", "Dark"), ("light", "Light")],
        default="light",
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

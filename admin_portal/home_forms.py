from django import forms

from accounts.images import optimize_home_image
from accounts.models import (
    HomeClientSpotlight,
    HomeGalleryImage,
    HomePageSettings,
    HomePowerlifter,
    HomePricingPlan,
    HomePricingTier,
    HomeScheduleSlot,
    HomeTestimonial,
    HomeTrainer,
    HomeTrainingService,
)


def _apply_admin_input_widgets(form):
    """Apply consistent admin-input styling to Django form widgets."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            continue
        if isinstance(widget, forms.RadioSelect):
            continue
        existing = widget.attrs.get("class", "")
        if isinstance(widget, forms.FileInput):
            widget.attrs["class"] = f"{existing} admin-input admin-input--file".strip()
        elif isinstance(widget, forms.Textarea):
            widget.attrs["class"] = f"{existing} admin-input".strip()
        else:
            widget.attrs["class"] = f"{existing} admin-input".strip()


class AdminStyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_admin_input_widgets(self)


def _clean_home_image(field_name, uploaded_file):
    if not uploaded_file or not hasattr(uploaded_file, "read"):
        return uploaded_file
    try:
        return optimize_home_image(uploaded_file, field_name)
    except ValueError as exc:
        raise forms.ValidationError(str(exc)) from exc


class HomeHeroForm(AdminStyledModelForm):
    remove_hero_image = forms.BooleanField(required=False, label="Remove hero image")
    remove_hero_video = forms.BooleanField(required=False, label="Remove hero video")

    class Meta:
        model = HomePageSettings
        fields = [
            "hero_headline",
            "hero_subtext",
            "hero_cta_text",
            "hero_media_type",
            "hero_image",
            "hero_video",
            "hero_image_url",
        ]

    def clean_hero_image(self):
        return _clean_home_image("hero_image", self.cleaned_data.get("hero_image"))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_hero_image") and instance.hero_image:
            instance.hero_image.delete(save=False)
            instance.hero_image = None
        if self.cleaned_data.get("remove_hero_video") and instance.hero_video:
            instance.hero_video.delete(save=False)
            instance.hero_video = None
        if commit:
            instance.save()
        return instance


class HomePowerliftersSectionForm(AdminStyledModelForm):
    class Meta:
        model = HomePageSettings
        fields = ["powerlifters_title", "powerlifters_watermark"]


class HomeWelcomeForm(AdminStyledModelForm):
    class Meta:
        model = HomePageSettings
        fields = [
            "welcome_tagline",
            "welcome_paragraph_1",
            "welcome_paragraph_2",
            "welcome_paragraph_3",
            "trainers_title",
        ]
        widgets = {
            "welcome_paragraph_1": forms.Textarea(attrs={"rows": 4}),
            "welcome_paragraph_2": forms.Textarea(attrs={"rows": 4}),
            "welcome_paragraph_3": forms.Textarea(attrs={"rows": 4}),
        }


class HomeTrainingForm(AdminStyledModelForm):
    class Meta:
        model = HomePageSettings
        fields = ["training_title", "training_intro"]
        widgets = {"training_intro": forms.Textarea(attrs={"rows": 5})}


class HomeScheduleSectionForm(AdminStyledModelForm):
    remove_schedule_image = forms.BooleanField(required=False, label="Remove schedule photo")

    class Meta:
        model = HomePageSettings
        fields = ["schedule_image", "schedule_image_url"]

    def clean_schedule_image(self):
        return _clean_home_image("schedule_image", self.cleaned_data.get("schedule_image"))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_schedule_image") and instance.schedule_image:
            instance.schedule_image.delete(save=False)
            instance.schedule_image = None
        if commit:
            instance.save()
        return instance


class HomePricingImageForm(AdminStyledModelForm):
    remove_pricing_image = forms.BooleanField(required=False, label="Remove pricing image")

    class Meta:
        model = HomePageSettings
        fields = ["rates_title", "pricing_image", "pricing_image_url", "pricing_image_alt"]

    def clean_pricing_image(self):
        return _clean_home_image("pricing_image", self.cleaned_data.get("pricing_image"))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_pricing_image") and instance.pricing_image:
            instance.pricing_image.delete(save=False)
            instance.pricing_image = None
        if commit:
            instance.save()
        return instance


class HomeSectionsForm(AdminStyledModelForm):
    class Meta:
        model = HomePageSettings
        fields = [
            "rates_title",
            "gallery_title",
            "gallery_watermark",
            "testimonials_title",
            "clients_title",
            "clients_intro",
        ]
        widgets = {"clients_intro": forms.Textarea(attrs={"rows": 4})}


class HomeFooterForm(AdminStyledModelForm):
    class Meta:
        model = HomePageSettings
        fields = [
            "footer_blurb",
            "footer_cta",
            "contact_address",
            "contact_email",
            "map_location",
        ]
        widgets = {
            "footer_blurb": forms.Textarea(attrs={"rows": 3}),
            "contact_address": forms.Textarea(attrs={"rows": 2}),
        }


class HomePowerlifterForm(AdminStyledModelForm):
    remove_image = forms.BooleanField(required=False, label="Remove photo")

    class Meta:
        model = HomePowerlifter
        fields = ["name", "image", "image_url", "sort_order", "is_active"]

    def clean_image(self):
        return _clean_home_image("powerlifter_image", self.cleaned_data.get("image"))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_image") and instance.image:
            instance.image.delete(save=False)
            instance.image = None
        if commit:
            instance.save()
        return instance


class HomeTrainerForm(AdminStyledModelForm):
    remove_image = forms.BooleanField(required=False, label="Remove photo")

    class Meta:
        model = HomeTrainer
        fields = ["name", "image", "image_url", "sort_order", "is_active"]

    def clean_image(self):
        return _clean_home_image("trainer_image", self.cleaned_data.get("image"))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_image") and instance.image:
            instance.image.delete(save=False)
            instance.image = None
        if commit:
            instance.save()
        return instance


class HomeTrainingServiceForm(AdminStyledModelForm):
    class Meta:
        model = HomeTrainingService
        fields = ["title", "sort_order", "is_active"]


class HomeScheduleSlotForm(AdminStyledModelForm):
    class Meta:
        model = HomeScheduleSlot
        fields = ["title", "time_info", "days_info", "sort_order", "is_active"]


class HomePricingPlanForm(AdminStyledModelForm):
    remove_background = forms.BooleanField(required=False, label="Remove background image")

    class Meta:
        model = HomePricingPlan
        fields = [
            "title",
            "feature_1",
            "feature_2",
            "feature_3",
            "background_image",
            "background_image_url",
            "sort_order",
            "is_active",
        ]

    def clean_background_image(self):
        return _clean_home_image("pricing_bg", self.cleaned_data.get("background_image"))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_background") and instance.background_image:
            instance.background_image.delete(save=False)
            instance.background_image = None
        if commit:
            instance.save()
        return instance


class HomePricingTierForm(AdminStyledModelForm):
    class Meta:
        model = HomePricingTier
        fields = ["plan", "price_label", "sessions_label", "sort_order"]


class HomeGalleryImageForm(AdminStyledModelForm):
    remove_image = forms.BooleanField(required=False, label="Remove photo")

    class Meta:
        model = HomeGalleryImage
        fields = ["image", "image_url", "alt_text", "sort_order", "is_active"]

    def clean_image(self):
        return _clean_home_image("gallery_image", self.cleaned_data.get("image"))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_image") and instance.image:
            instance.image.delete(save=False)
            instance.image = None
        if commit:
            instance.save()
        return instance


class HomeTestimonialForm(AdminStyledModelForm):
    class Meta:
        model = HomeTestimonial
        fields = ["quote", "author", "sort_order", "is_active"]
        widgets = {"quote": forms.Textarea(attrs={"rows": 3})}


class HomeClientSpotlightForm(AdminStyledModelForm):
    remove_image = forms.BooleanField(required=False, label="Remove photo")

    class Meta:
        model = HomeClientSpotlight
        fields = ["caption", "image", "image_url", "row", "sort_order", "is_active"]

    def clean_image(self):
        return _clean_home_image("client_image", self.cleaned_data.get("image"))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_image") and instance.image:
            instance.image.delete(save=False)
            instance.image = None
        if commit:
            instance.save()
        return instance

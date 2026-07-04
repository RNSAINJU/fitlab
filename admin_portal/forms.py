from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from accounts.images import optimize_site_logo
from accounts.models import SiteConfiguration
from loyalty.models import PointRule, PointRuleKind, PointRuleTrigger

User = get_user_model()

WIPE_CONFIRM_PHRASE = "DELETE ALL DATA"


class SiteSettingsForm(forms.ModelForm):
    remove_logo = forms.BooleanField(required=False, label="Remove current logo")

    class Meta:
        model = SiteConfiguration
        fields = ["site_name", "logo"]
        widgets = {
            "site_name": forms.TextInput(attrs={"placeholder": "e.g. The Fitlab"}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        if not logo or not hasattr(logo, "read"):
            return logo
        try:
            return optimize_site_logo(logo)
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_logo") and instance.logo:
            instance.logo.delete(save=False)
            instance.logo = None
        if commit:
            instance.save()
        return instance


class WipeAllDataForm(forms.Form):
    confirm_phrase = forms.CharField(
        label=f'Type "{WIPE_CONFIRM_PHRASE}" to confirm',
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": WIPE_CONFIRM_PHRASE}),
    )

    def clean_confirm_phrase(self):
        phrase = self.cleaned_data["confirm_phrase"]
        if phrase != WIPE_CONFIRM_PHRASE:
            raise forms.ValidationError(f'You must type exactly: {WIPE_CONFIRM_PHRASE}')
        return phrase


class PromoteAdminForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=False).order_by("email"),
        label="Customer account",
        empty_label="Select a user to promote",
    )

    def clean_user(self):
        user = self.cleaned_data["user"]
        if user.is_staff:
            raise forms.ValidationError("This user already has admin access.")
        return user


class CreateAdminForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="Full name")
    username = forms.CharField(max_length=150, label="Username")
    email = forms.EmailField(label="Email address")
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        min_length=8,
    )
    is_superuser = forms.BooleanField(
        required=False,
        label="Full superuser access (can manage other admins)",
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self):
        name = self.cleaned_data["full_name"].strip()
        parts = name.split(None, 1)
        user = User(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"].lower(),
            first_name=parts[0],
            last_name=parts[1] if len(parts) > 1 else "",
            is_staff=True,
            is_superuser=self.cleaned_data.get("is_superuser", False),
            approval_status=User.ApprovalStatus.APPROVED,
        )
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class DistributePointsForm(forms.Form):
    rule = forms.ModelChoiceField(
        queryset=PointRule.objects.none(),
        label="Activity rule",
        empty_label="Select a gym activity rule",
    )
    customers = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        label="Customers",
        widget=forms.SelectMultiple(attrs={"size": 8}),
    )
    custom_points = forms.IntegerField(
        required=False,
        min_value=1,
        label="Custom points (optional)",
        widget=forms.NumberInput(attrs={"placeholder": "Leave blank to use rule default"}),
    )
    note = forms.CharField(
        required=False,
        max_length=200,
        label="Note (optional)",
        widget=forms.TextInput(attrs={"placeholder": "e.g. HIIT class, morning check-in"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rule"].queryset = PointRule.objects.filter(
            is_active=True,
            trigger=PointRuleTrigger.MANUAL,
            rule_kind=PointRuleKind.FIXED,
        ).order_by("title")
        self.fields["customers"].queryset = User.objects.filter(
            is_staff=False,
            approval_status=User.ApprovalStatus.APPROVED,
        ).order_by("email")
        gym_rule = PointRule.objects.filter(slug="gym_activity", is_active=True).first()
        if gym_rule:
            self.fields["rule"].initial = gym_rule.pk

    def clean_customers(self):
        customers = self.cleaned_data["customers"]
        if not customers:
            raise forms.ValidationError("Select at least one customer.")
        return customers


class PaymentPointsForm(forms.Form):
    customer = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Customer",
        empty_label="Select a customer",
    )
    amount_spent = forms.IntegerField(
        min_value=1,
        label="Amount spent",
        widget=forms.NumberInput(attrs={"placeholder": "e.g. 2500"}),
    )
    note = forms.CharField(
        required=False,
        max_length=200,
        label="Note (optional)",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Monthly membership renewal"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = User.objects.filter(
            is_staff=False,
            approval_status=User.ApprovalStatus.APPROVED,
        ).order_by("email")

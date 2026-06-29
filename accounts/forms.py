import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator

User = get_user_model()

INPUT_LOGIN = {"class": "auth-input", "placeholder": "athlete@fitlab.com"}
INPUT_REG = {"class": "auth-input auth-input--dark"}
INPUT_PROFILE = {"class": "profile-input"}
SELECT_PROFILE = {"class": "profile-input profile-input--select"}
FILE_PROFILE = {"class": "profile-input profile-input--file"}


def normalize_phone(value):
    return re.sub(r"\D", "", value or "")


class RegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="Full name",
        widget=forms.TextInput(attrs={**INPUT_REG, "placeholder": "John Doe"}),
    )
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={**INPUT_REG, "placeholder": "athlete42", "autocomplete": "username"}),
    )
    email = forms.EmailField(
        required=True,
        label="Email address",
        widget=forms.EmailInput(attrs={**INPUT_REG, "placeholder": "recruit@fitlab.com"}),
    )
    phone = forms.CharField(
        label="Mobile number",
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                **INPUT_REG,
                "placeholder": "+977 98XXXXXXXX",
                "autocomplete": "tel",
                "inputmode": "tel",
            }
        ),
    )
    password = forms.CharField(
        label="Security key",
        widget=forms.PasswordInput(attrs={**INPUT_REG, "placeholder": "••••••••"}),
    )
    referral_code = forms.CharField(
        max_length=12,
        required=False,
        label="Referral code (optional)",
        widget=forms.TextInput(attrs={**INPUT_REG, "placeholder": "LAB-XXXX"}),
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label="I accept the Protocol Terms and acknowledge the intensity of the program.",
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        from django.contrib.auth.validators import UnicodeUsernameValidator

        username = self.cleaned_data["username"]
        UnicodeUsernameValidator()(username)
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            raise forms.ValidationError("Mobile number is required.")
        digits = normalize_phone(phone)
        if len(digits) < 7 or len(digits) > 15:
            raise forms.ValidationError("Enter a valid mobile number.")
        for existing in User.objects.exclude(phone="").values_list("phone", flat=True):
            if normalize_phone(existing) == digits:
                raise forms.ValidationError("An account with this mobile number already exists.")
        return digits

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self, commit=True):
        user = User()
        user.email = self.cleaned_data["email"].lower()
        user.username = self.cleaned_data["username"]
        user.phone = self.cleaned_data["phone"]
        name = self.cleaned_data["full_name"].strip()
        parts = name.split(None, 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ""
        user.approval_status = User.ApprovalStatus.PENDING
        user.set_password(self.cleaned_data["password"])

        referral = self.cleaned_data.get("referral_code", "").strip().upper()
        if referral:
            referrer = User.objects.filter(referral_code__iexact=referral).first()
            if referrer:
                user.referred_by = referrer

        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                **INPUT_LOGIN,
                "autofocus": True,
                "placeholder": "username or email",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                **INPUT_LOGIN,
                "placeholder": "••••••••",
                "id": "login-password",
                "autocomplete": "current-password",
            }
        ),
    )

    def clean(self):
        identifier = self.cleaned_data.get("username", "").strip()
        if identifier:
            user = User.objects.filter(username__iexact=identifier).first()
            if user is None:
                user = User.objects.filter(email__iexact=identifier).first()
            if user is not None:
                self.cleaned_data["username"] = user.get_username()
        return super().clean()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff and user.approval_status == User.ApprovalStatus.REJECTED:
            raise forms.ValidationError("Your account was not approved.", code="inactive")


class ProfileEditForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label="Full name",
        widget=forms.TextInput(attrs={**INPUT_PROFILE, "placeholder": "John Doe", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        required=True,
        label="Email address",
        widget=forms.EmailInput(attrs={**INPUT_PROFILE, "placeholder": "you@example.com", "autocomplete": "email"}),
    )
    phone = forms.CharField(
        label="Mobile number",
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                **INPUT_PROFILE,
                "placeholder": "+977 98XXXXXXXX",
                "autocomplete": "tel",
                "inputmode": "tel",
            }
        ),
    )
    date_of_birth = forms.DateField(
        required=False,
        label="Date of birth",
        widget=forms.DateInput(attrs={**INPUT_PROFILE, "type": "date"}),
    )
    gender = forms.ChoiceField(
        required=False,
        label="Gender",
        choices=[("", "Select gender")] + list(User.Gender.choices),
        widget=forms.Select(attrs=SELECT_PROFILE),
    )
    profile_photo = forms.ImageField(
        required=False,
        label="Profile photo",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
        widget=forms.FileInput(attrs={**FILE_PROFILE, "accept": "image/jpeg,image/png,image/webp"}),
    )
    remove_profile_photo = forms.BooleanField(
        required=False,
        label="Remove current photo",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["full_name"].initial = user.get_full_name().strip()
        self.fields["email"].initial = user.email
        self.fields["phone"].initial = user.phone
        self.fields["date_of_birth"].initial = user.date_of_birth
        self.fields["gender"].initial = user.gender
        if not user.profile_photo:
            self.fields["remove_profile_photo"].widget = forms.HiddenInput()

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            raise forms.ValidationError("Mobile number is required.")
        digits = normalize_phone(phone)
        if len(digits) < 7 or len(digits) > 15:
            raise forms.ValidationError("Enter a valid mobile number.")
        for existing_pk, existing_phone in User.objects.exclude(phone="").exclude(pk=self.user.pk).values_list(
            "pk", "phone"
        ):
            if normalize_phone(existing_phone) == digits:
                raise forms.ValidationError("An account with this mobile number already exists.")
        return phone

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Profile photo must be 5 MB or smaller.")
        return photo

    def save(self):
        user = self.user
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]

        name = self.cleaned_data["full_name"].strip()
        parts = name.split(None, 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ""

        user.date_of_birth = self.cleaned_data.get("date_of_birth")
        user.gender = self.cleaned_data.get("gender") or ""

        if self.cleaned_data.get("remove_profile_photo") and user.profile_photo:
            user.profile_photo.delete(save=False)
            user.profile_photo = None

        photo = self.cleaned_data.get("profile_photo")
        if photo:
            if user.profile_photo:
                user.profile_photo.delete(save=False)
            user.profile_photo = photo

        user.save()
        return user

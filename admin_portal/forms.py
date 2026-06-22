from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


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

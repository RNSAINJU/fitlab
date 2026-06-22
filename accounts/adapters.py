from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

from activity.services import log_activity

from .auth_helpers import get_post_login_url

User = get_user_model()


class FitlabAccountAdapter(DefaultAccountAdapter):
    """Email/password signup uses the custom register form, not allauth."""

    def is_open_for_signup(self, request):
        return False

    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated:
            return get_post_login_url(user)
        return super().get_login_redirect_url(request)


class FitlabSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        if not sociallogin.is_existing:
            return

        user = sociallogin.user
        if user.is_staff:
            return

        if user.approval_status == User.ApprovalStatus.REJECTED:
            messages.error(request, "Your account was not approved.")
            raise ImmediateHttpResponse(redirect(reverse("accounts:login")))

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = (data.get("email") or user.email or "").lower()
        if email:
            user.email = email
            user.username = email
        user.approval_status = User.ApprovalStatus.PENDING
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        referral = (request.session.pop("referral_code", "") or "").strip().upper()
        if referral and not user.referred_by_id:
            referrer = User.objects.filter(referral_code__iexact=referral).first()
            if referrer and referrer.pk != user.pk:
                user.referred_by = referrer
                user.save(update_fields=["referred_by"])

        if not user.is_staff and user.approval_status == User.ApprovalStatus.PENDING:
            provider = sociallogin.account.get_provider().name
            log_activity(
                user=user,
                event_type="signup",
                title="Registration submitted",
                description=f"Signed up with {provider}. Awaiting admin approval.",
            )
            messages.success(request, "Registration submitted. Awaiting admin approval.")

        return user

    def get_login_redirect_url(self, request):
        return FitlabAccountAdapter().get_login_redirect_url(request)

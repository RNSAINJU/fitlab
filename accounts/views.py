from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
import json

from activity.models import ActivityEvent
from loyalty.helpers import get_lifetime_earned, get_member_rank, get_membership_tier, get_tier_progress
from loyalty.services import get_balance
from rewards.models import RedemptionRequest

from .auth_helpers import get_post_login_url
from .forms import (
    LoginForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    ProfileEditForm,
    RegistrationForm,
)
from .theme import THEME_COOKIE, VALID_THEMES

DEFAULT_AUTH_BACKEND = "django.contrib.auth.backends.ModelBackend"


def _store_referral_code(request):
    referral = request.GET.get("ref") or request.POST.get("referral_code", "")
    referral = referral.strip().upper()
    if referral:
        request.session["referral_code"] = referral


class FitlabLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        _store_referral_code(request)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return get_post_login_url(self.request.user)

    def get_redirect_url(self):
        if self.request.user.is_authenticated:
            return get_post_login_url(self.request.user)
        return super().get_redirect_url()

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_staff and user.approval_status == user.ApprovalStatus.PENDING:
            login(self.request, user, backend=DEFAULT_AUTH_BACKEND)
            return redirect("accounts:pending")

        response = super().form_valid(form)
        if not user.is_staff and user.is_approved:
            from loyalty.rule_engine import try_award_daily_login_points

            try_award_daily_login_points(user)
        return response


class FitlabPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/password_reset_email.txt"
    subject_template_name = "accounts/password_reset_subject.txt"
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy("accounts:password_reset_done")


class FitlabPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class FitlabPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy("accounts:password_reset_complete")


class FitlabPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


def register(request):
    if request.user.is_authenticated:
        return redirect(get_post_login_url(request.user))

    _store_referral_code(request)

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration submitted. Awaiting admin approval.")
            login(request, user, backend=DEFAULT_AUTH_BACKEND)
            return redirect("accounts:pending")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def pending_approval(request):
    user = request.user
    if user.is_staff or user.approval_status == user.ApprovalStatus.APPROVED:
        return redirect(get_post_login_url(user))
    return render(request, "accounts/pending.html", {"user": user})


@login_required
def profile(request):
    user = request.user
    if user.is_staff:
        return redirect("admin_portal:dashboard")
    if user.approval_status != user.ApprovalStatus.APPROVED:
        return redirect("accounts:pending")

    balance = get_balance(user)
    tier_progress, tier_remaining = get_tier_progress(balance)
    latest_points_activity = (
        user.activity_events.filter(event_type="points", points_amount__gt=0).first()
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "balance": balance,
            "membership_tier": get_membership_tier(balance),
            "tier_progress": tier_progress,
            "tier_remaining": tier_remaining,
            "lifetime_earned": get_lifetime_earned(user),
            "member_rank": get_member_rank(user),
            "member_since_year": user.date_joined.year,
            "latest_points_activity": latest_points_activity,
            "pending_redemptions": RedemptionRequest.objects.filter(
                user=user, status=RedemptionRequest.Status.PENDING
            ).count(),
            "referral_count": user.referrals.filter(
                approval_status=user.ApprovalStatus.APPROVED
            ).count(),
            "workout_count": user.activity_events.filter(event_type="points").count(),
        },
    )


@login_required
def edit_profile(request):
    user = request.user
    if user.is_staff:
        return redirect("admin_portal:dashboard")
    if user.approval_status != user.ApprovalStatus.APPROVED:
        return redirect("accounts:pending")

    if request.method == "POST":
        form = ProfileEditForm(user, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileEditForm(user)

    return render(request, "accounts/profile_edit.html", {"form": form})


def home(request):
    if request.user.is_authenticated:
        return redirect(get_post_login_url(request.user))
    from accounts.home_content import get_home_page_context

    return render(request, "accounts/home.html", get_home_page_context())


@login_required
def dashboard(request):
    user = request.user
    if user.is_staff:
        return redirect("admin_portal:dashboard")
    if not user.is_staff and user.approval_status != user.ApprovalStatus.APPROVED:
        return redirect("accounts:pending")

    recent_activity = ActivityEvent.objects.filter(user=user).exclude(
        event_type="points",
        description__startswith="Redeemed:",
    )[:5]
    pending_redemptions = RedemptionRequest.objects.filter(
        user=user, status=RedemptionRequest.Status.PENDING
    ).count()

    balance = get_balance(user)
    tier_progress, tier_remaining = get_tier_progress(balance)

    return render(
        request,
        "accounts/dashboard.html",
        {
            "balance": balance,
            "membership_tier": get_membership_tier(balance),
            "tier_progress": tier_progress,
            "tier_remaining": tier_remaining,
            "lifetime_earned": get_lifetime_earned(user),
            "recent_activity": recent_activity,
            "pending_redemptions": pending_redemptions,
            "referral_count": user.referrals.filter(
                approval_status=user.ApprovalStatus.APPROVED
            ).count(),
            "workout_count": user.activity_events.filter(event_type="points").count(),
        },
    )


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:home")


def connection_lost(request):
    return render(request, "accounts/connection_lost.html")


@require_POST
def set_theme(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid payload"}, status=400)

    theme = payload.get("theme", "")
    if theme not in VALID_THEMES:
        return JsonResponse({"error": "invalid theme"}, status=400)

    if request.user.is_authenticated:
        request.user.theme_preference = theme
        request.user.save(update_fields=["theme_preference"])

    response = JsonResponse({"theme": theme})
    response.set_cookie(THEME_COOKIE, theme, max_age=31536000, samesite="Lax")
    return response

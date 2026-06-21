from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from activity.models import ActivityEvent
from loyalty.helpers import get_lifetime_earned, get_membership_tier, get_tier_progress
from loyalty.services import get_balance
from rewards.models import RedemptionRequest

from .forms import LoginForm, RegistrationForm


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

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_staff and user.approval_status == user.ApprovalStatus.PENDING:
            login(self.request, user)
            return redirect("accounts:pending")
        return super().form_valid(form)


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    _store_referral_code(request)

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration submitted. Awaiting admin approval.")
            login(request, user)
            return redirect("accounts:pending")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def pending_approval(request):
    user = request.user
    if user.is_staff or user.approval_status == user.ApprovalStatus.APPROVED:
        return redirect("accounts:dashboard")
    return render(request, "accounts/pending.html", {"user": user})


@login_required
def dashboard(request):
    user = request.user
    if not user.is_staff and user.approval_status != user.ApprovalStatus.APPROVED:
        return redirect("accounts:pending")

    recent_activity = ActivityEvent.objects.filter(user=user)[:5]
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
    return redirect("accounts:login")


def connection_lost(request):
    return render(request, "accounts/connection_lost.html")

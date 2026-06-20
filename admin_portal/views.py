from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from activity.services import log_activity
from loyalty.models import PointTransaction
from loyalty.services import admin_adjust_points, deduct_points, get_balance
from rewards.models import RedemptionRequest

from .decorators import staff_required

User = get_user_model()


@staff_required
def dashboard(request):
    pending_users = User.objects.filter(approval_status=User.ApprovalStatus.PENDING).count()
    pending_redemptions = RedemptionRequest.objects.filter(status=RedemptionRequest.Status.PENDING).count()
    total_customers = User.objects.filter(is_staff=False).count()
    return render(
        request,
        "admin_portal/dashboard.html",
        {
            "pending_users": pending_users,
            "pending_redemptions": pending_redemptions,
            "total_customers": total_customers,
        },
    )


@staff_required
def customer_directory(request):
    q = request.GET.get("q", "").strip()
    customers = User.objects.filter(is_staff=False).order_by("-date_joined")
    if q:
        customers = customers.filter(
            models_q(q)
        )
    return render(
        request,
        "admin_portal/customer_directory.html",
        {"customers": customers, "q": q},
    )


def models_q(q):
    from django.db.models import Q

    return Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(phone__icontains=q)


@staff_required
def registration_approvals(request):
    pending = User.objects.filter(
        is_staff=False,
        approval_status=User.ApprovalStatus.PENDING,
    ).order_by("date_joined")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        user = get_object_or_404(User, pk=user_id, is_staff=False)

        if action == "approve":
            user.approval_status = User.ApprovalStatus.APPROVED
            user.save(update_fields=["approval_status"])
            messages.success(request, f"Approved {user.display_name}.")
        elif action == "reject":
            user.approval_status = User.ApprovalStatus.REJECTED
            user.save(update_fields=["approval_status"])
            log_activity(
                user=user,
                event_type="approval",
                title="Registration rejected",
                description="Your registration was not approved. Contact the gym for help.",
            )
            messages.info(request, f"Rejected {user.display_name}.")
        return redirect("admin_portal:registration_approvals")

    return render(request, "admin_portal/registration_approvals.html", {"pending_users": pending})


@staff_required
def points_ledger(request):
    transactions = PointTransaction.objects.select_related("user", "created_by")[:100]
    pending_redemptions = RedemptionRequest.objects.filter(
        status=RedemptionRequest.Status.PENDING
    ).select_related("user", "reward")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "adjust":
            user = get_object_or_404(User, pk=request.POST.get("user_id"))
            amount = int(request.POST.get("amount", "0"))
            note = request.POST.get("note", "Admin adjustment")
            admin_adjust_points(user, amount, note, request.user)
            messages.success(request, f"Adjusted {user.display_name} by {amount} TFL Points.")
            return redirect("admin_portal:points_ledger")

        if action == "approve_redemption":
            redemption = get_object_or_404(
                RedemptionRequest,
                pk=request.POST.get("redemption_id"),
                status=RedemptionRequest.Status.PENDING,
            )
            balance = get_balance(redemption.user)
            if balance < redemption.points_cost:
                messages.error(request, "User no longer has enough points.")
            else:
                deduct_points(
                    redemption.user,
                    redemption.points_cost,
                    f"Redeemed: {redemption.reward.title}",
                    created_by=request.user,
                )
                redemption.status = RedemptionRequest.Status.APPROVED
                redemption.reviewed_by = request.user
                redemption.reviewed_at = timezone.now()
                redemption.save()
                if redemption.reward.stock is not None:
                    redemption.reward.stock = max(0, redemption.reward.stock - 1)
                    redemption.reward.save(update_fields=["stock"])
                log_activity(
                    user=redemption.user,
                    event_type="redemption",
                    title=f"Redemption approved: {redemption.reward.title}",
                    description=f"{redemption.points_cost} TFL Points deducted.",
                )
                messages.success(request, "Redemption approved and points deducted.")
            return redirect("admin_portal:points_ledger")

        if action == "reject_redemption":
            redemption = get_object_or_404(
                RedemptionRequest,
                pk=request.POST.get("redemption_id"),
                status=RedemptionRequest.Status.PENDING,
            )
            redemption.status = RedemptionRequest.Status.REJECTED
            redemption.reviewed_by = request.user
            redemption.reviewed_at = timezone.now()
            redemption.admin_note = request.POST.get("admin_note", "")
            redemption.save()
            log_activity(
                user=redemption.user,
                event_type="redemption",
                title=f"Redemption rejected: {redemption.reward.title}",
                description=redemption.admin_note or "Your redemption request was not approved.",
            )
            messages.info(request, "Redemption rejected.")
            return redirect("admin_portal:points_ledger")

    customers = User.objects.filter(is_staff=False).order_by("email")
    return render(
        request,
        "admin_portal/points_ledger.html",
        {
            "transactions": transactions,
            "pending_redemptions": pending_redemptions,
            "customers": customers,
        },
    )

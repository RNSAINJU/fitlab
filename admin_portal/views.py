from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from django.db.models import Count, Sum

from accounts.models import SiteConfiguration
from .home_views import home_page_settings  # noqa: F401
from activity.services import log_activity
from loyalty.forms import CustomRuleForm, PointRuleForm, SystemRuleForm
from loyalty.helpers import get_membership_tier
from loyalty.models import PointRule, PointRuleKind, PointRuleTrigger, PointTransaction
from loyalty.rule_engine import award_rule_points, ensure_default_point_rules, get_point_rule, on_user_approved
from loyalty.services import admin_adjust_points, deduct_points, get_balance
from rewards.forms import RewardForm
from rewards.models import RedemptionRequest, Reward

from .customer_csv import export_customers_csv, import_customers_csv
from .decorators import staff_required, superuser_required
from .forms import (
    CreateAdminForm,
    DistributePointsForm,
    PaymentPointsForm,
    PromoteAdminForm,
    SiteSettingsForm,
    WipeAllDataForm,
)
from .site_services import wipe_all_application_data

User = get_user_model()


def _distribute_activity_points(request, form, redirect_name):
    if not form.is_valid():
        messages.error(request, form.errors.as_text())
        return redirect(redirect_name)

    rule = form.cleaned_data["rule"]
    customers = form.cleaned_data["customers"]
    note = form.cleaned_data["note"]
    custom_points = form.cleaned_data.get("custom_points")
    awarded = 0
    total_points = 0
    for customer in customers:
        tx = award_rule_points(
            customer,
            rule,
            request.user,
            note=note,
            custom_points=custom_points,
        )
        if tx:
            awarded += 1
            total_points += tx.amount
    messages.success(
        request,
        f"Awarded {total_points} TFL Points to {awarded} customer(s) via \"{rule.title}\".",
    )
    return redirect(redirect_name)


@staff_required
def dashboard(request):
    ensure_default_point_rules()
    pending_users = User.objects.filter(approval_status=User.ApprovalStatus.PENDING).count()
    pending_redemptions = RedemptionRequest.objects.filter(status=RedemptionRequest.Status.PENDING).count()
    total_customers = User.objects.filter(is_staff=False).count()
    total_points = PointTransaction.objects.filter(amount__gt=0).aggregate(total=Sum("amount"))["total"] or 0
    approved_members = User.objects.filter(is_staff=False, approval_status=User.ApprovalStatus.APPROVED).count()

    if request.method == "POST" and request.POST.get("action") == "distribute":
        return _distribute_activity_points(
            request,
            DistributePointsForm(request.POST),
            "admin_portal:dashboard",
        )

    return render(
        request,
        "admin_portal/dashboard.html",
        {
            "pending_users": pending_users,
            "pending_redemptions": pending_redemptions,
            "total_customers": total_customers,
            "total_points_issued": total_points,
            "approved_members": approved_members,
            "distribute_form": DistributePointsForm(),
            "gym_activity_rule": get_point_rule("gym_activity"),
        },
    )


@staff_required
def customer_directory(request):
    q = request.GET.get("q", "").strip()
    customers = User.objects.filter(is_staff=False).order_by("-date_joined")
    if q:
        customers = customers.filter(models_q(q))

    customer_rows = []
    for c in customers[:50]:
        balance = get_balance(c)
        customer_rows.append(
            {
                "user": c,
                "balance": balance,
                "tier": get_membership_tier(balance),
            }
        )

    total_points = PointTransaction.objects.filter(amount__gt=0).aggregate(total=Sum("amount"))["total"] or 0
    approved_count = User.objects.filter(is_staff=False, approval_status=User.ApprovalStatus.APPROVED).count()

    return render(
        request,
        "admin_portal/customer_directory.html",
        {
            "customers": customer_rows,
            "q": q,
            "total_customers": User.objects.filter(is_staff=False).count(),
            "total_points_issued": total_points,
            "approved_members": approved_count,
        },
    )


@staff_required
def customer_export(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="thefitlab-customers.csv"'
    export_customers_csv(response)
    return response


@staff_required
def customer_import(request):
    if request.method != "POST":
        return redirect("admin_portal:customer_directory")

    csv_file = request.FILES.get("csv_file")
    if not csv_file:
        messages.error(request, "Please choose a CSV file to import.")
        return redirect("admin_portal:customer_directory")

    if not csv_file.name.lower().endswith(".csv"):
        messages.error(request, "Upload a .csv file.")
        return redirect("admin_portal:customer_directory")

    created, updated, errors = import_customers_csv(csv_file)
    if created or updated:
        messages.success(
            request,
            f"Import complete: {created} created, {updated} updated.",
        )
    if errors:
        preview = "; ".join(errors[:5])
        suffix = f" (+{len(errors) - 5} more)" if len(errors) > 5 else ""
        messages.warning(request, f"{len(errors)} row(s) skipped: {preview}{suffix}")
    elif not created and not updated:
        messages.info(request, "No customer rows were found in the CSV.")

    return redirect("admin_portal:customer_directory")


def models_q(q):
    from django.db.models import Q

    return (
        Q(email__icontains=q)
        | Q(first_name__icontains=q)
        | Q(last_name__icontains=q)
        | Q(phone__icontains=q)
        | Q(member_id__icontains=q)
    )


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
            on_user_approved(user)
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

    return render(
        request,
        "admin_portal/registration_approvals.html",
        {"pending_users": pending, "pending_count": pending.count()},
    )


@staff_required
def rewards_list(request):
    rewards = Reward.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")
        reward = get_object_or_404(Reward, pk=request.POST.get("reward_id"))

        if action == "toggle_active":
            reward.is_active = not reward.is_active
            reward.save(update_fields=["is_active"])
            state = "activated" if reward.is_active else "deactivated"
            messages.success(request, f'Reward "{reward.title}" {state}.')
        elif action == "delete":
            title = reward.title
            reward.delete()
            messages.success(request, f'Reward "{title}" deleted.')

        return redirect("admin_portal:rewards_list")

    return render(
        request,
        "admin_portal/rewards_list.html",
        {
            "rewards": rewards,
            "active_count": rewards.filter(is_active=True).count(),
        },
    )


@staff_required
def reward_create(request):
    if request.method == "POST":
        form = RewardForm(request.POST)
        if form.is_valid():
            reward = form.save()
            messages.success(request, f'Reward "{reward.title}" created for {reward.points_cost} TFL Points.')
            return redirect("admin_portal:rewards_list")
    else:
        form = RewardForm(initial={"is_active": True, "image_emoji": "🎁"})

    return render(
        request,
        "admin_portal/reward_create.html",
        {"form": form},
    )


@superuser_required
def role_management(request):
    admins = User.objects.filter(is_staff=True).order_by("-is_superuser", "email")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "promote":
            form = PromoteAdminForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data["user"]
                user.is_staff = True
                user.approval_status = User.ApprovalStatus.APPROVED
                user.save(update_fields=["is_staff", "approval_status"])
                messages.success(request, f"{user.display_name} now has admin access.")
            else:
                messages.error(request, form.errors.as_text())
            return redirect("admin_portal:role_management")

        if action == "create":
            form = CreateAdminForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, f"Admin account created for {user.email}.")
            else:
                messages.error(request, form.errors.as_text())
            return redirect("admin_portal:role_management")

        if action == "revoke":
            target = get_object_or_404(User, pk=request.POST.get("user_id"), is_staff=True)
            if target.pk == request.user.pk:
                messages.error(request, "You cannot remove your own admin access.")
            elif User.objects.filter(is_staff=True).count() <= 1:
                messages.error(request, "At least one admin must remain.")
            else:
                target.is_staff = False
                target.is_superuser = False
                target.save(update_fields=["is_staff", "is_superuser"])
                messages.success(request, f"Admin access removed from {target.display_name}.")
            return redirect("admin_portal:role_management")

        if action == "toggle_superuser":
            target = get_object_or_404(User, pk=request.POST.get("user_id"), is_staff=True)
            if target.pk == request.user.pk and target.is_superuser:
                messages.error(request, "You cannot remove your own superuser access.")
            else:
                target.is_superuser = not target.is_superuser
                target.save(update_fields=["is_superuser"])
                role = "superuser" if target.is_superuser else "admin"
                messages.success(request, f"{target.display_name} is now a {role}.")
            return redirect("admin_portal:role_management")

    promote_form = PromoteAdminForm()
    create_form = CreateAdminForm()
    eligible_users = User.objects.filter(is_staff=False).count()

    return render(
        request,
        "admin_portal/role_management.html",
        {
            "admins": admins,
            "promote_form": promote_form,
            "create_form": create_form,
            "eligible_users": eligible_users,
        },
    )


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
                    log_activity_event=False,
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
                    points_amount=-redemption.points_cost,
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
    total_earned = PointTransaction.objects.filter(amount__gt=0).aggregate(total=Sum("amount"))["total"] or 0
    total_redemptions = RedemptionRequest.objects.filter(status=RedemptionRequest.Status.APPROVED).count()
    all_redemptions = RedemptionRequest.objects.count()
    redemption_rate = int((total_redemptions / all_redemptions) * 100) if all_redemptions else 0
    top_rewards = Reward.objects.filter(is_active=True).order_by("-points_cost")[:3]

    return render(
        request,
        "admin_portal/points_ledger.html",
        {
            "transactions": transactions,
            "pending_redemptions": pending_redemptions,
            "customers": customers,
            "total_earned": total_earned,
            "total_redemptions": total_redemptions,
            "redemption_rate": redemption_rate,
            "top_rewards": top_rewards,
        },
    )


@staff_required
def point_rules(request):
    ensure_default_point_rules()
    rules = PointRule.objects.annotate(award_count=Count("transactions"))

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_rule":
            form = PointRuleForm(request.POST)
            if form.is_valid():
                rule = form.save(commit=False)
                rule.trigger = PointRuleTrigger.MANUAL
                rule.rule_kind = PointRuleKind.FIXED
                rule.save()
                messages.success(request, f'Point rule "{rule.title}" created.')
            else:
                messages.error(request, form.errors.as_text())
            return redirect("admin_portal:point_rules")

        if action == "update_rule":
            rule = get_object_or_404(PointRule, pk=request.POST.get("rule_id"))
            post_data = request.POST.copy()
            if "is_active" not in post_data:
                post_data["is_active"] = False
            if rule.is_system:
                form = SystemRuleForm(post_data, instance=rule)
            else:
                form = CustomRuleForm(post_data, instance=rule)
            if form.is_valid():
                updated = form.save()
                messages.success(
                    request,
                    f'Updated "{updated.title}" — now awards {updated.points_amount} TFL Points.',
                )
            else:
                messages.error(request, form.errors.as_text())
            return redirect("admin_portal:point_rules")

        if action == "toggle_active":
            rule = get_object_or_404(PointRule, pk=request.POST.get("rule_id"))
            rule.is_active = not rule.is_active
            rule.save(update_fields=["is_active"])
            state = "activated" if rule.is_active else "deactivated"
            messages.success(request, f'Rule "{rule.title}" {state}.')
            return redirect("admin_portal:point_rules")

        if action == "delete":
            rule = get_object_or_404(PointRule, pk=request.POST.get("rule_id"), is_system=False)
            title = rule.title
            rule.delete()
            messages.success(request, f'Rule "{title}" deleted.')
            return redirect("admin_portal:point_rules")

        if action == "distribute":
            return _distribute_activity_points(
                request,
                DistributePointsForm(request.POST),
                "admin_portal:point_rules",
            )

        if action == "payment":
            form = PaymentPointsForm(request.POST)
            if form.is_valid():
                rule = get_point_rule("payment")
                if not rule:
                    messages.error(request, "Payment reward rule is not configured.")
                else:
                    customer = form.cleaned_data["customer"]
                    amount_spent = form.cleaned_data["amount_spent"]
                    note = form.cleaned_data["note"]
                    tx = award_rule_points(
                        customer,
                        rule,
                        request.user,
                        note=note,
                        amount_spent=amount_spent,
                    )
                    if tx:
                        messages.success(
                            request,
                            f"Awarded {tx.amount} TFL Points to {customer.display_name} "
                            f"for {amount_spent} spent.",
                        )
                    else:
                        messages.error(request, "Spend amount is too low to earn points.")
            else:
                messages.error(request, form.errors.as_text())
            return redirect("admin_portal:point_rules")

    rule_form = PointRuleForm(initial={"is_active": True, "icon_emoji": "🏆"})
    distribute_form = DistributePointsForm()
    payment_form = PaymentPointsForm()
    payment_rule = get_point_rule("payment")
    gym_activity_rule = get_point_rule("gym_activity")
    automatic_rules = rules.filter(
        is_system=True,
        trigger__in=[
            PointRuleTrigger.ON_APPROVAL,
            PointRuleTrigger.ON_DAILY_LOGIN,
            PointRuleTrigger.ON_REFERRAL,
        ],
    )
    recent_awards = (
        PointTransaction.objects.filter(transaction_type=PointTransaction.TransactionType.RULE)
        .select_related("user", "rule", "created_by")
        .order_by("-created_at")[:20]
    )
    active_rules = rules.filter(is_active=True).count()
    total_distributed = (
        PointTransaction.objects.filter(transaction_type=PointTransaction.TransactionType.RULE, amount__gt=0)
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )

    return render(
        request,
        "admin_portal/point_rules.html",
        {
            "rules": rules,
            "rule_form": rule_form,
            "distribute_form": distribute_form,
            "payment_form": payment_form,
            "payment_rule": payment_rule,
            "gym_activity_rule": gym_activity_rule,
            "automatic_rules": automatic_rules,
            "recent_awards": recent_awards,
            "active_rules": active_rules,
            "total_distributed": total_distributed,
        },
    )


@staff_required
def site_settings(request):
    config = SiteConfiguration.load()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "branding":
            form = SiteSettingsForm(request.POST, request.FILES, instance=config)
            if form.is_valid():
                form.save()
                messages.success(request, "Site name and logo updated.")
            else:
                messages.error(request, form.errors.as_text())
            return redirect("admin_portal:site_settings")

        if action == "wipe":
            if not request.user.is_superuser:
                messages.error(request, "Only superusers can delete all application data.")
                return redirect("admin_portal:site_settings")

            form = WipeAllDataForm(request.POST)
            if form.is_valid():
                stats = wipe_all_application_data()
                messages.success(
                    request,
                    "All customer and loyalty data was removed. "
                    f"Deleted {stats['customers_deleted']} customer account(s), "
                    f"{stats['transactions_deleted']} point transaction(s), "
                    f"{stats['rewards_deleted']} reward(s), and related records. "
                    "Admin accounts and site settings were kept.",
                )
            else:
                messages.error(request, form.errors.as_text())
            return redirect("admin_portal:site_settings")

    return render(
        request,
        "admin_portal/site_settings.html",
        {
            "settings_form": SiteSettingsForm(instance=config),
            "wipe_form": WipeAllDataForm(),
            "site_config": config,
        },
    )

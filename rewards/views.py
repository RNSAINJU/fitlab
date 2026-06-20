from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from activity.services import log_activity
from loyalty.services import get_balance

from .models import RedemptionRequest, Reward


@login_required
def marketplace(request):
    user = request.user
    if not user.is_approved and not user.is_staff:
        return redirect("accounts:pending")

    rewards = list(Reward.objects.filter(is_active=True))
    featured = max(rewards, key=lambda r: r.points_cost) if rewards else None
    grid_rewards = [r for r in rewards if r != featured] if featured else rewards
    my_redemptions = RedemptionRequest.objects.filter(user=user)[:10]
    balance = get_balance(user)

    return render(
        request,
        "rewards/marketplace.html",
        {
            "rewards": grid_rewards,
            "featured_reward": featured,
            "my_redemptions": my_redemptions,
            "balance": balance,
        },
    )


@login_required
def redeem(request, reward_id):
    user = request.user
    if not user.is_approved and not user.is_staff:
        return redirect("accounts:pending")

    reward = get_object_or_404(Reward, pk=reward_id, is_active=True)
    balance = get_balance(user)

    if request.method == "POST":
        if not reward.in_stock:
            messages.error(request, "This reward is out of stock.")
            return redirect("rewards:marketplace")
        if balance < reward.points_cost:
            messages.error(request, "Not enough TFL Points for this reward.")
            return redirect("rewards:marketplace")

        RedemptionRequest.objects.create(
            user=user,
            reward=reward,
            points_cost=reward.points_cost,
        )
        log_activity(
            user=user,
            event_type="redemption",
            title=f"Redemption requested: {reward.title}",
            description=f"{reward.points_cost} TFL Points — awaiting admin approval.",
        )
        messages.success(request, "Redemption submitted for admin approval.")
        return redirect("rewards:marketplace")

    return render(
        request,
        "rewards/redeem_confirm.html",
        {"reward": reward, "balance": balance},
    )

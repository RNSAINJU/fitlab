from collections import OrderedDict
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from loyalty.helpers import get_tier_progress
from loyalty.services import get_balance

from .models import ActivityEvent


def _group_key(dt):
    local = timezone.localtime(dt)
    today = timezone.localdate()
    event_date = local.date()
    if event_date == today:
        return "TOD", "Today"
    if event_date == today - timedelta(days=1):
        return "YST", "Yesterday"
    return local.strftime("%b %d").upper(), local.strftime("%B %d")


@login_required
def feed(request):
    user = request.user
    if not user.is_approved and not user.is_staff:
        return redirect("accounts:pending")

    events = ActivityEvent.objects.filter(user=user)
    balance = get_balance(user)
    _, tier_remaining = get_tier_progress(balance)
    monthly_goal = 1500
    monthly_progress = min(100, int((balance / monthly_goal) * 100)) if monthly_goal else 0

    grouped = OrderedDict()
    for event in events:
        code, label = _group_key(event.created_at)
        if code not in grouped:
            grouped[code] = {"label": label, "code": code, "events": []}
        grouped[code]["events"].append(event)

    return render(
        request,
        "activity/feed.html",
        {
            "grouped_events": grouped.values(),
            "balance": balance,
            "monthly_progress": monthly_progress,
        },
    )

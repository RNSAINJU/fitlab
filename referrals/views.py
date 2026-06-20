from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import ReferralRecord


@login_required
def referral_hub(request):
    user = request.user
    if not user.is_approved and not user.is_staff:
        return redirect("accounts:pending")

    referrals = user.referrals.all().order_by("-date_joined")
    records = ReferralRecord.objects.filter(referrer=user).select_related("referee")
    total_bonus = sum(r.bonus_points for r in records if r.bonus_awarded)

    approved_count = referrals.filter(approval_status=user.ApprovalStatus.APPROVED).count()
    next_rank_at = 15
    tier_progress = min(100, int((approved_count / next_rank_at) * 100)) if next_rank_at else 0
    recruits_until = max(0, next_rank_at - approved_count)

    return render(
        request,
        "referrals/hub.html",
        {
            "referral_code": user.referral_code,
            "referrals": referrals,
            "records": records,
            "total_bonus": total_bonus,
            "approved_count": approved_count,
            "pending_count": referrals.filter(approval_status=user.ApprovalStatus.PENDING).count(),
            "tier_name": "Lab Commander" if approved_count >= 10 else "Recruit Leader",
            "tier_progress": tier_progress,
            "recruits_until": recruits_until,
        },
    )

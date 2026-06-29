PLATINUM_TARGET = 3000
GOLD_TARGET = 1500


def get_membership_tier(balance):
    if balance >= PLATINUM_TARGET:
        return "Platinum Member"
    if balance >= GOLD_TARGET:
        return "Gold Member"
    return "Elite Member"


def get_tier_progress(balance):
    if balance >= PLATINUM_TARGET:
        return 100, 0
    progress = int(min(100, (balance / PLATINUM_TARGET) * 100))
    remaining = PLATINUM_TARGET - balance
    return progress, remaining


def get_lifetime_earned(user):
    return sum(
        tx.amount
        for tx in user.point_transactions.filter(amount__gt=0)
    )


def get_member_rank(user):
    from accounts.models import User
    from django.db.models import Q, Sum
    from django.db.models.functions import Coalesce

    from .services import get_balance

    balance = get_balance(user)
    ahead = (
        User.objects.filter(
            is_staff=False,
            approval_status=User.ApprovalStatus.APPROVED,
        )
        .annotate(balance=Coalesce(Sum("point_transactions__amount"), 0))
        .filter(
            Q(balance__gt=balance) | (Q(balance=balance) & Q(pk__lt=user.pk))
        )
        .count()
    )
    return ahead + 1

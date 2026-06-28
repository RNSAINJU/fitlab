from django.conf import settings

from activity.services import log_activity
from .models import PointTransaction


def get_balance(user):
    return sum(tx.amount for tx in user.point_transactions.all())


def award_points(
    user,
    amount,
    transaction_type,
    description,
    created_by=None,
    log_activity_event=True,
    rule=None,
):
    tx = PointTransaction.objects.create(
        user=user,
        amount=amount,
        transaction_type=transaction_type,
        description=description,
        created_by=created_by,
        rule=rule,
    )
    if log_activity_event:
        log_activity(
            user=user,
            event_type="points",
            title=f"{'+' if amount >= 0 else ''}{amount} TFL Points",
            description=description,
            points_amount=amount,
        )
    return tx


def deduct_points(user, amount, description, created_by=None, log_activity_event=True):
    return award_points(
        user=user,
        amount=-abs(amount),
        transaction_type=PointTransaction.TransactionType.REDEEM,
        description=description,
        created_by=created_by,
        log_activity_event=log_activity_event,
    )


def admin_adjust_points(user, amount, description, admin_user):
    tx_type = PointTransaction.TransactionType.ADJUST
    return award_points(user, amount, tx_type, description, created_by=admin_user)


def award_referral_bonus(referrer, referee):
    from .rule_engine import try_award_referral_points

    tx = try_award_referral_points(referrer, referee)
    if tx:
        return tx

    bonus = settings.REFERRAL_BONUS_POINTS
    return award_points(
        user=referrer,
        amount=bonus,
        transaction_type=PointTransaction.TransactionType.REFERRAL,
        description=f"Referral bonus for {referee.display_name}",
    )

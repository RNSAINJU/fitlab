from django.utils import timezone

from activity.services import log_activity
from loyalty.rule_engine import try_award_referral_points
from .models import ReferralRecord


def award_referrer_on_approval(referee):
    if not referee.referred_by_id:
        return None

    referrer = referee.referred_by
    record, _ = ReferralRecord.objects.get_or_create(
        referrer=referrer,
        referee=referee,
    )
    if record.bonus_awarded:
        return record

    tx = try_award_referral_points(referrer, referee)
    if not tx:
        return record

    record.bonus_awarded = True
    record.bonus_points = tx.amount
    record.awarded_at = timezone.now()
    record.save(update_fields=["bonus_awarded", "bonus_points", "awarded_at"])

    log_activity(
        user=referrer,
        event_type="referral",
        title="Referral bonus earned",
        description=f"You earned {tx.amount} TFL Points for referring {referee.display_name}.",
    )
    return record

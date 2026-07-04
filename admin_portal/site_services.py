from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import transaction

from activity.models import ActivityEvent
from loyalty.models import PointRule, PointTransaction
from loyalty.rule_engine import ensure_default_point_rules
from referrals.models import ReferralRecord
from rewards.models import RedemptionRequest, Reward

User = get_user_model()


def wipe_all_application_data():
    """Remove all customer and loyalty data while keeping staff accounts and site settings."""
    with transaction.atomic():
        redemptions_deleted, _ = RedemptionRequest.objects.all().delete()
        transactions_deleted, _ = PointTransaction.objects.all().delete()
        activity_deleted, _ = ActivityEvent.objects.all().delete()
        referrals_deleted, _ = ReferralRecord.objects.all().delete()
        rewards_deleted, _ = Reward.objects.all().delete()
        rules_deleted, _ = PointRule.objects.all().delete()
        customers_deleted, _ = User.objects.filter(is_staff=False).delete()

        User.objects.filter(is_staff=True).update(referred_by=None)
        Session.objects.all().delete()

        try:
            from axes.models import AccessAttempt, AccessLog

            AccessAttempt.objects.all().delete()
            AccessLog.objects.all().delete()
        except ImportError:
            pass

        ensure_default_point_rules()

    return {
        "customers_deleted": customers_deleted,
        "redemptions_deleted": redemptions_deleted,
        "transactions_deleted": transactions_deleted,
        "activity_deleted": activity_deleted,
        "referrals_deleted": referrals_deleted,
        "rewards_deleted": rewards_deleted,
        "rules_deleted": rules_deleted,
    }

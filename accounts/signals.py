from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User

SIGNUP_BONUS_DESCRIPTION = "Signup approval bonus"


@receiver(pre_save, sender=User)
def track_approval_change(sender, instance, **kwargs):
    if not instance.pk:
        instance._approval_just_granted = False
        return
    try:
        previous = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        instance._approval_just_granted = False
        return
    instance._approval_just_granted = (
        previous.approval_status != User.ApprovalStatus.APPROVED
        and instance.approval_status == User.ApprovalStatus.APPROVED
    )


@receiver(post_save, sender=User)
def award_approval_bonuses(sender, instance, **kwargs):
    if instance.is_staff or not getattr(instance, "_approval_just_granted", False):
        return

    from loyalty.models import PointTransaction
    from loyalty.services import award_points
    from referrals.services import award_referrer_on_approval

    signup_bonus = settings.SIGNUP_BONUS_POINTS
    if signup_bonus and not PointTransaction.objects.filter(
        user=instance,
        transaction_type=PointTransaction.TransactionType.EARN,
        description=SIGNUP_BONUS_DESCRIPTION,
    ).exists():
        award_points(
            user=instance,
            amount=signup_bonus,
            transaction_type=PointTransaction.TransactionType.EARN,
            description=SIGNUP_BONUS_DESCRIPTION,
        )

    award_referrer_on_approval(instance)

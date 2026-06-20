from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import User


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

from .models import ActivityEvent


def log_activity(user, event_type, title, description="", points_amount=None):
    return ActivityEvent.objects.create(
        user=user,
        event_type=event_type,
        title=title,
        description=description,
        points_amount=points_amount,
    )

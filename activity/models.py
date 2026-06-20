from django.conf import settings
from django.db import models


class ActivityEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_events")
    event_type = models.CharField(max_length=40)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}: {self.title}"

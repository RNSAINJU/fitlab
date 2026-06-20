from datetime import timedelta

from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag
def active_nav(request, app_name, url_name=""):
    match = request.resolver_match
    if not match:
        return ""
    if match.app_name == app_name and (not url_name or match.url_name == url_name):
        return "is-active"
    return ""


@register.filter
def points_from_title(title):
    if "+" in str(title) and "TFL" in str(title):
        return str(title).split("TFL")[0].strip()
    return ""


@register.filter
def timesince_short(dt):
    if not dt:
        return ""
    now = timezone.now()
    diff = now - dt
    if diff < timedelta(hours=1):
        return "Just now"
    if diff < timedelta(hours=24):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    if diff < timedelta(days=2):
        return "Yesterday"
    return f"{diff.days} days ago"

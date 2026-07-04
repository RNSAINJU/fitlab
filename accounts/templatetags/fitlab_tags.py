import re

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


@register.simple_tag
def in_settings_section(request):
    match = request.resolver_match
    if not match:
        return False
    return match.url_name in ("site_settings", "role_management", "home_page_settings")


@register.filter
def points_from_title(title):
    if "+" in str(title) and "TFL" in str(title):
        return str(title).split("TFL")[0].strip()
    return ""


@register.filter
def activity_display_title(event):
    if event.event_type == "redemption":
        return event.title
    if event.event_type == "points" and "TFL Points" in event.title:
        description = (event.description or "").strip()
        if description.startswith("Redeemed:"):
            reward = description.removeprefix("Redeemed:").strip()
            return f"Redemption approved: {reward}"
    return event.title


@register.filter
def activity_points(event):
    if getattr(event, "points_amount", None) is not None:
        amount = event.points_amount
        return f"{'+' if amount > 0 else ''}{amount}"

    if event.event_type == "redemption" and "approved" in event.title.lower():
        match = re.search(r"(\d+)\s*TFL Points deducted", event.description or "")
        if match:
            return f"-{match.group(1)}"

    title = str(event.title)
    match = re.search(r"([+-]?\d+)\s*TFL", title)
    if match:
        return match.group(1)
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

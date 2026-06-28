from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_staff:
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped


def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_staff:
            return redirect("accounts:dashboard")
        if not request.user.is_superuser:
            messages.error(request, "Only superusers can manage admin roles.")
            return redirect("admin_portal:dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped

from functools import wraps

from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("accounts:login")
        return view_func(request, *args, **kwargs)

    return _wrapped

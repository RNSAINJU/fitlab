from django.shortcuts import redirect
from django.urls import reverse


class ApprovalRequiredMiddleware:
    """Redirect unapproved users away from customer pages."""

    EXEMPT_PREFIXES = (
        "/static/",
        "/django-admin/",
        "/admin-portal/",
        "/oauth/",
        "/accounts/login",
        "/accounts/register",
        "/register",
        "/accounts/pending",
        "/accounts/logout",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        user = request.user

        if user.is_authenticated and not user.is_staff:
            if user.approval_status == user.ApprovalStatus.PENDING:
                if not any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
                    return redirect(reverse("accounts:pending"))
            elif user.approval_status == user.ApprovalStatus.REJECTED:
                if not any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
                    return redirect(reverse("accounts:pending"))

        return self.get_response(request)

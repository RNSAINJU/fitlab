from django.urls import reverse


def get_post_login_url(user):
    if user.is_staff:
        return reverse("admin_portal:dashboard")
    if user.approval_status == user.ApprovalStatus.PENDING:
        return reverse("accounts:pending")
    if user.approval_status == user.ApprovalStatus.REJECTED:
        return reverse("accounts:pending")
    return reverse("accounts:dashboard")

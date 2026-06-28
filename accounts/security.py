import os

from django.conf import settings

WEAK_PASSWORDS = frozenset({"admin123", "customer123", "password", "fitlab123"})


def get_admin_password_from_env():
    return os.environ.get("FITLAB_ADMIN_PASSWORD", "").strip()


def is_weak_password(password):
    if not password:
        return True
    if password in WEAK_PASSWORDS:
        return True
    return len(password) < 12


def production_security_enabled():
    return not settings.DEBUG

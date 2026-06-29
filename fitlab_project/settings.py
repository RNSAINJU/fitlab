import os
from pathlib import Path

from dotenv import load_dotenv

from accounts.oauth import build_socialaccount_providers, social_auth_enabled_flags

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-fitlab-dev-change-me-in-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "http://localhost,http://127.0.0.1",
    ).split(",")
    if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "axes",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.apple",
    "accounts",
    "loyalty",
    "rewards",
    "referrals",
    "activity",
    "admin_portal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "accounts.middleware.ApprovalRequiredMiddleware",
    "accounts.middleware.SecurityHeadersMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "fitlab_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "loyalty.context_processors.points_balance",
                "accounts.context_processors.social_auth",
            ],
        },
    },
]

WSGI_APPLICATION = "fitlab_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = "Lax"
    SECURE_REFERRER_POLICY = "same-origin"
    SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

    if os.environ.get("DJANGO_HTTPS", "0") == "1":
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True

    # Only force HTTP→HTTPS redirect when explicitly enabled (not when behind Cloudflare Flexible).
    if os.environ.get("FITLAB_SSL_REDIRECT", "0") == "1":
        SECURE_SSL_REDIRECT = True
        SECURE_HSTS_SECONDS = 31536000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

AXES_FAILURE_LIMIT = int(os.environ.get("AXES_FAILURE_LIMIT", "5"))
AXES_COOLOFF_TIME = float(os.environ.get("AXES_COOLOFF_TIME", "0.5"))
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ["ip_address", "username"]
AXES_LOCKOUT_TEMPLATE = None
AXES_ENABLE_ACCESS_FAILURE_LOG = True
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "X_FORWARDED_FOR",
    "REMOTE_ADDR",
]

AUTH_USER_MODEL = "accounts.User"

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_ADAPTER = "accounts.adapters.FitlabAccountAdapter"
SOCIALACCOUNT_ADAPTER = "accounts.adapters.FitlabSocialAccountAdapter"

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_UNIQUE_EMAIL = True

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_STORE_TOKENS = False

_social_providers = build_socialaccount_providers()
_social_flags = social_auth_enabled_flags(_social_providers)
SOCIALACCOUNT_PROVIDERS = _social_providers
SOCIAL_AUTH_GOOGLE_ENABLED = _social_flags["google"]
SOCIAL_AUTH_APPLE_ENABLED = _social_flags["apple"]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"

# Fitlab business defaults
REFERRAL_BONUS_POINTS = int(os.environ.get("REFERRAL_BONUS_POINTS", "5"))
SIGNUP_BONUS_POINTS = int(os.environ.get("SIGNUP_BONUS_POINTS", "10"))

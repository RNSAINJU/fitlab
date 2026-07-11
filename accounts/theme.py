THEME_COOKIE = "fitlab_theme"
THEME_STORAGE_KEY = "fitlab-theme"
VALID_THEMES = frozenset({"dark", "light"})

# Set to None to re-enable light/dark switching.
FORCED_THEME = "dark"


def resolve_theme(request):
    """Resolve active theme: forced theme, user preference, cookie, then light default."""
    if FORCED_THEME in VALID_THEMES:
        return FORCED_THEME

    if request.user.is_authenticated:
        pref = getattr(request.user, "theme_preference", "") or "light"
        if pref in VALID_THEMES:
            return pref

    cookie_theme = request.COOKIES.get(THEME_COOKIE, "")
    if cookie_theme in VALID_THEMES:
        return cookie_theme

    return "light"


def theme_toggle_enabled():
    return FORCED_THEME is None

THEME_COOKIE = "fitlab_theme"
THEME_STORAGE_KEY = "fitlab-theme"
VALID_THEMES = frozenset({"dark", "light"})


def resolve_theme(request):
    """Resolve active theme: user preference, cookie, then dark default."""
    if request.user.is_authenticated:
        pref = getattr(request.user, "theme_preference", "") or "dark"
        if pref in VALID_THEMES:
            return pref

    cookie_theme = request.COOKIES.get(THEME_COOKIE, "")
    if cookie_theme in VALID_THEMES:
        return cookie_theme

    return "dark"

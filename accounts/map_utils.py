import re
from urllib.parse import unquote, urlparse

import requests

_EMBED_MARKERS = ("/maps/embed", "output=embed")
_SHARE_HOSTS = ("maps.app.goo.gl", "goo.gl/maps", "google.com/maps", "maps.google.com")


def is_embed_url(value: str) -> bool:
    value = (value or "").strip()
    return bool(value) and any(marker in value for marker in _EMBED_MARKERS)


def is_share_url(value: str) -> bool:
    value = (value or "").strip().lower()
    if not value.startswith("http"):
        return False
    return any(host in value for host in _SHARE_HOSTS) and not is_embed_url(value)


def _coords_from_url(url: str) -> tuple[str, str] | None:
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if match:
        return match.group(1), match.group(2)
    return None


def _place_label_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = unquote(parsed.path)
    if "/maps/place/" in path:
        name = path.split("/maps/place/", 1)[1].split("/@", 1)[0]
        return name.replace("+", " ").strip()
    query = urlparse(url).query
    if "q=" in query:
        from urllib.parse import parse_qs

        q = parse_qs(query).get("q", [""])[0]
        return unquote(q).strip()
    return ""


def _embed_from_coords(lat: str, lng: str, zoom: int = 15) -> str:
    return f"https://www.google.com/maps?q={lat},{lng}&z={zoom}&output=embed"


def _embed_from_address(address: str, zoom: int = 15) -> str:
    from urllib.parse import quote

    return f"https://www.google.com/maps?q={quote(address)}&z={zoom}&output=embed"


def resolve_map_input(raw_value: str) -> tuple[str, str]:
    """
    Turn admin map input into (map_location label, map_embed_url).

    Accepts plain address, Google Maps embed URL, or share link.
    """
    value = (raw_value or "").strip()
    if not value:
        return "", ""

    if is_embed_url(value):
        label = _place_label_from_url(value) or "Gym location"
        return label, value

    if value.startswith("http"):
        final_url = value
        if is_share_url(value):
            try:
                response = requests.get(
                    value,
                    allow_redirects=True,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; FitlabBot/1.0)"},
                )
                final_url = response.url
            except requests.RequestException:
                return "", ""

        coords = _coords_from_url(final_url)
        label = _place_label_from_url(final_url) or "Gym location"
        if coords:
            return label, _embed_from_coords(*coords)
        if label:
            return label, _embed_from_address(label)
        return "", ""

    return value, _embed_from_address(value)

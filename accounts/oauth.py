import os


def _read_apple_private_key():
    key = os.environ.get("APPLE_PRIVATE_KEY", "").strip()
    if key:
        return key.replace("\\n", "\n")

    key_file = os.environ.get("APPLE_PRIVATE_KEY_FILE", "").strip()
    if key_file and os.path.isfile(key_file):
        with open(key_file, encoding="utf-8") as handle:
            return handle.read()

    return ""


def build_socialaccount_providers():
    providers = {}

    google_client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if google_client_id and google_client_secret:
        providers["google"] = {
            "APP": {
                "client_id": google_client_id,
                "secret": google_client_secret,
                "key": "",
            },
            "SCOPE": ["profile", "email"],
            "AUTH_PARAMS": {"access_type": "online"},
        }

    apple_client_id = os.environ.get("APPLE_CLIENT_ID", "").strip()
    apple_team_id = os.environ.get("APPLE_TEAM_ID", "").strip()
    apple_key_id = os.environ.get("APPLE_KEY_ID", "").strip()
    apple_private_key = _read_apple_private_key()
    if apple_client_id and apple_team_id and apple_key_id and apple_private_key:
        providers["apple"] = {
            "APP": {
                "client_id": apple_client_id,
                "secret": apple_key_id,
                "key": apple_team_id,
                "settings": {
                    "certificate_key": apple_private_key,
                },
            },
        }

    return providers


def social_auth_enabled_flags(providers):
    return {
        "google": "google" in providers,
        "apple": "apple" in providers,
    }

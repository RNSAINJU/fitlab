import os
from pathlib import Path


def build_database_config(base_dir: Path) -> dict:
    """Use PostgreSQL when POSTGRES_DB is set; otherwise SQLite for local dev."""
    if os.environ.get("FITLAB_USE_SQLITE", "").strip() == "1":
        return _sqlite_config(base_dir)

    postgres_db = os.environ.get("POSTGRES_DB", "").strip()
    if postgres_db:
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": postgres_db,
                "USER": os.environ.get("POSTGRES_USER", "fitlab"),
                "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
                "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
                "PORT": os.environ.get("POSTGRES_PORT", "5432"),
                "CONN_MAX_AGE": int(os.environ.get("POSTGRES_CONN_MAX_AGE", "60")),
                "OPTIONS": {
                    "connect_timeout": int(os.environ.get("POSTGRES_CONNECT_TIMEOUT", "10")),
                },
            }
        }

    return _sqlite_config(base_dir)


def _sqlite_config(base_dir: Path) -> dict:
    return {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": base_dir / "db.sqlite3",
        }
    }

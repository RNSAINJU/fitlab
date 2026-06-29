#!/usr/bin/env bash
# Migrate an existing Fitlab SQLite database to PostgreSQL.
# Run on the VPS as root after setup-postgres.sh:
#   cd /var/www/fitlab && sudo bash deploy/migrate-sqlite-to-postgres.sh
#
# Safe to re-run only before PostgreSQL has been populated; backs up SQLite first.

set -euo pipefail

APP_DIR="${FITLAB_APP_DIR:-/var/www/fitlab}"
cd "$APP_DIR"

if [ ! -f .env ]; then
  echo "Missing ${APP_DIR}/.env"
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

if [ -z "${POSTGRES_DB:-}" ]; then
  echo "POSTGRES_DB is not set in .env. Run deploy/setup-postgres.sh first."
  exit 1
fi

SQLITE_PATH="${APP_DIR}/db.sqlite3"
DUMP_PATH="${APP_DIR}/deploy/sqlite-export.json"
BACKUP_PATH="${APP_DIR}/deploy/db.sqlite3.backup-$(date +%Y%m%d%H%M%S)"

if [ ! -f "${SQLITE_PATH}" ]; then
  echo "No SQLite database at ${SQLITE_PATH}; running migrations on PostgreSQL only."
  .venv/bin/pip install -q -r requirements.txt
  .venv/bin/python manage.py migrate --noinput
  systemctl restart fitlab
  echo "PostgreSQL migrations complete."
  exit 0
fi

echo "==> Backing up SQLite"
mkdir -p "${APP_DIR}/deploy"
cp "${SQLITE_PATH}" "${BACKUP_PATH}"
echo "Backup: ${BACKUP_PATH}"

echo "==> Installing dependencies"
.venv/bin/pip install -q -r requirements.txt

echo "==> Exporting data from SQLite"
FITLAB_USE_SQLITE=1 .venv/bin/python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --indent 2 \
  --exclude contenttypes \
  --exclude auth.permission \
  --exclude sessions \
  --exclude axes.accessattempt \
  --exclude axes.accesslog \
  --exclude axes.accessfailurelog \
  > "${DUMP_PATH}"

set -a
# shellcheck disable=SC1091
source .env
set +a

echo "==> Preparing PostgreSQL schema"
.venv/bin/python manage.py migrate --noinput

echo "==> Loading data into PostgreSQL"
.venv/bin/python manage.py loaddata "${DUMP_PATH}"

echo "==> Verifying PostgreSQL connection"
.venv/bin/python manage.py shell -c "from django.contrib.auth import get_user_model; print('users:', get_user_model().objects.count())"

if [ -f "${SQLITE_PATH}" ]; then
  mv "${SQLITE_PATH}" "${SQLITE_PATH}.migrated"
  echo "Renamed SQLite file to ${SQLITE_PATH}.migrated"
fi

chown -R www-data:www-data "$APP_DIR"
chmod 640 "$APP_DIR/.env"

echo "==> Restarting app"
systemctl restart fitlab
systemctl is-active fitlab

echo "Migration complete. PostgreSQL is now the active database."

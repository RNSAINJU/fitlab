#!/usr/bin/env bash
# Provision PostgreSQL for Fitlab on Ubuntu/Debian.
# Run as root on the VPS:
#   sudo bash deploy/setup-postgres.sh
#
# Optional env vars:
#   FITLAB_APP_DIR=/var/www/fitlab
#   POSTGRES_DB=fitlab
#   POSTGRES_USER=fitlab
#   POSTGRES_PASSWORD=...   # generated if unset

set -euo pipefail

APP_DIR="${FITLAB_APP_DIR:-/var/www/fitlab}"
POSTGRES_DB="${POSTGRES_DB:-fitlab}"
POSTGRES_USER="${POSTGRES_USER:-fitlab}"
POSTGRES_HOST="${POSTGRES_HOST:-127.0.0.1}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

if [ -z "${POSTGRES_PASSWORD:-}" ]; then
  POSTGRES_PASSWORD="$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")"
fi

echo "==> Installing PostgreSQL"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq postgresql postgresql-contrib

systemctl enable postgresql
systemctl start postgresql

echo "==> Creating database role and database"
sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER}') THEN
    CREATE ROLE ${POSTGRES_USER} LOGIN PASSWORD '${POSTGRES_PASSWORD}';
  ELSE
    ALTER ROLE ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
  END IF;
END
\$\$;

SELECT 'CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}')\gexec

GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};
SQL

sudo -u postgres psql -v ON_ERROR_STOP=1 -d "${POSTGRES_DB}" <<SQL
GRANT ALL ON SCHEMA public TO ${POSTGRES_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${POSTGRES_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${POSTGRES_USER};
SQL

if [ ! -f "${APP_DIR}/.env" ]; then
  echo "No ${APP_DIR}/.env found; skipping env update."
  echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}"
  exit 0
fi

echo "==> Updating ${APP_DIR}/.env"
ENV_FILE="${APP_DIR}/.env"
touch "${ENV_FILE}"

upsert_env() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" "${ENV_FILE}"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "${ENV_FILE}"
  else
    printf '\n%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

upsert_env "POSTGRES_DB" "${POSTGRES_DB}"
upsert_env "POSTGRES_USER" "${POSTGRES_USER}"
upsert_env "POSTGRES_PASSWORD" "${POSTGRES_PASSWORD}"
upsert_env "POSTGRES_HOST" "${POSTGRES_HOST}"
upsert_env "POSTGRES_PORT" "${POSTGRES_PORT}"

chown www-data:www-data "${ENV_FILE}"
chmod 640 "${ENV_FILE}"

echo "PostgreSQL ready."
echo "  Database: ${POSTGRES_DB}"
echo "  User:     ${POSTGRES_USER}"
echo "  Password: saved in ${ENV_FILE} (POSTGRES_PASSWORD)"

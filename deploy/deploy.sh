#!/usr/bin/env bash
# Redeploy after code changes. Run on the VPS as root:
#   cd /var/www/fitlab && sudo bash deploy/deploy.sh

set -euo pipefail

APP_DIR="/var/www/fitlab"
cd "$APP_DIR"

git config --global --add safe.directory "$APP_DIR" 2>/dev/null || true

echo "==> Pull latest code from GitHub"
git pull origin main

echo "==> Install dependencies"
.venv/bin/pip install -r requirements.txt

echo "==> Migrate & static"
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
  if [ -n "${FITLAB_ADMIN_PASSWORD:-}" ]; then
    echo "==> Rotate admin password from FITLAB_ADMIN_PASSWORD"
    .venv/bin/python manage.py rotate_admin_password || true
  fi
fi

USER_COUNT=$(.venv/bin/python manage.py shell -c "from accounts.models import User; print(User.objects.count())")
if [ "${USER_COUNT}" = "0" ] && [ -n "${FITLAB_ADMIN_PASSWORD:-}" ]; then
  echo "==> No users found; running setup_fitlab"
  .venv/bin/python manage.py setup_fitlab
fi

if [ -f deploy/nginx-fitlab.conf ] && [ -f /etc/nginx/sites-available/fitlab ]; then
  echo "==> Refresh nginx config"
  GUNICORN_PORT=$(grep -oP 'bind = "127\.0\.0\.1:\K[0-9]+' /etc/systemd/system/fitlab.service 2>/dev/null || echo "8004")
  NGINX_PORT=$(grep -oP 'listen \K[0-9]+' /etc/nginx/sites-available/fitlab | head -1)
  SERVER_NAME=$(grep -oP 'server_name \K[^;]+' /etc/nginx/sites-available/fitlab | head -1)
  sed -e "s/__FITLAB_SERVER_NAME__/${SERVER_NAME}/g" \
      -e "s/__FITLAB_NGINX_PORT__/${NGINX_PORT}/g" \
      -e "s/__FITLAB_GUNICORN_PORT__/${GUNICORN_PORT}/g" \
      deploy/nginx-fitlab.conf > /etc/nginx/sites-available/fitlab
  nginx -t
  systemctl reload nginx
fi

chown -R www-data:www-data "$APP_DIR"

echo "==> Restart app"
systemctl restart fitlab
systemctl status fitlab --no-pager -l

echo "Deploy complete."

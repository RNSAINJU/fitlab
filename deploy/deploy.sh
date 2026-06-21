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

chown -R www-data:www-data "$APP_DIR"

echo "==> Restart app"
systemctl restart fitlab
systemctl status fitlab --no-pager -l

echo "Deploy complete."

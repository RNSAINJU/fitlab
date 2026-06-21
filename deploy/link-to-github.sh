#!/usr/bin/env bash
# Link an existing VPS deployment to GitHub and sync to main.
# Run on the VPS as root:
#   cd /var/www/fitlab && sudo bash deploy/link-to-github.sh

set -euo pipefail

APP_DIR="/var/www/fitlab"
REPO_URL="${FITLAB_REPO_URL:-https://github.com/RNSAINJU/fitlab.git}"
GUNICORN_PORT="${FITLAB_GUNICORN_PORT:-8004}"
NGINX_PORT="${FITLAB_NGINX_PORT:-8083}"
SERVER_IP="${FITLAB_SERVER_IP:-82.197.69.121}"

cd "$APP_DIR"

echo "==> Linking ${APP_DIR} to ${REPO_URL}"
git config --global --add safe.directory "$APP_DIR" 2>/dev/null || true

if [ -d .git ]; then
  git remote set-url origin "$REPO_URL" 2>/dev/null || git remote add origin "$REPO_URL"
else
  git init
  git remote add origin "$REPO_URL"
fi

git fetch origin main
git checkout -B main origin/main

# Ensure production .env has CSRF origin with nginx port
if [ -f .env ] && ! grep -q ":${NGINX_PORT}" .env; then
  sed -i "s|DJANGO_CSRF_TRUSTED_ORIGINS=.*|DJANGO_CSRF_TRUSTED_ORIGINS=http://${SERVER_IP}:${NGINX_PORT},http://${SERVER_IP},http://localhost|" .env
fi

echo "==> Install dependencies"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -r requirements.txt

echo "==> Migrate & static"
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput

chown -R www-data:www-data "$APP_DIR"
chmod 640 "$APP_DIR/.env"

echo "==> Refresh nginx & systemd"
SERVER_NAME="${FITLAB_DOMAIN:-${SERVER_IP}}"
sed -e "s/__FITLAB_SERVER_NAME__/${SERVER_NAME}/g" \
    -e "s/__FITLAB_NGINX_PORT__/${NGINX_PORT}/g" \
    -e "s/__FITLAB_GUNICORN_PORT__/${GUNICORN_PORT}/g" \
    deploy/nginx-fitlab.conf > /etc/nginx/sites-available/fitlab
ln -sf /etc/nginx/sites-available/fitlab /etc/nginx/sites-enabled/fitlab
sed "s/__FITLAB_GUNICORN_PORT__/${GUNICORN_PORT}/g" deploy/fitlab.service > /etc/systemd/system/fitlab.service
nginx -t
systemctl daemon-reload
systemctl restart nginx
systemctl restart fitlab

echo ""
echo "Linked to GitHub. Redeploy updates with: sudo bash deploy/deploy.sh"
git remote -v
git log -1 --oneline

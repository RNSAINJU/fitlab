#!/usr/bin/env bash
# First-time Fitlab setup on Ubuntu/Debian VPS.
# Run as root on the server:
#   curl -sSL https://raw.githubusercontent.com/RNSAINJU/fitlab/main/deploy/server-setup.sh | bash
# Or after cloning:
#   sudo bash deploy/server-setup.sh
#
# Optional env vars:
#   FITLAB_SERVER_IP=82.197.69.121
#   FITLAB_GUNICORN_PORT=8004
#   FITLAB_NGINX_PORT=8083
#   FITLAB_REPO_URL=https://github.com/RNSAINJU/fitlab.git

set -euo pipefail

APP_DIR="/var/www/fitlab"
REPO_URL="${FITLAB_REPO_URL:-https://github.com/RNSAINJU/fitlab.git}"
SERVER_IP="${FITLAB_SERVER_IP:-82.197.69.121}"
GUNICORN_PORT="${FITLAB_GUNICORN_PORT:-8004}"
NGINX_PORT="${FITLAB_NGINX_PORT:-8083}"
PUBLIC_URL="http://${SERVER_IP}:${NGINX_PORT}"

echo "==> Installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip nginx git curl

echo "==> Preparing app directory"
mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  cd "$APP_DIR"
  git pull origin main
fi

cd "$APP_DIR"

echo "==> Python virtualenv"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
  cat > .env <<EOF
DJANGO_SECRET_KEY=${SECRET}
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=${SERVER_IP},localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://${SERVER_IP}:${NGINX_PORT},http://${SERVER_IP},http://localhost
FITLAB_SITE_DOMAIN=${SERVER_IP}:${NGINX_PORT}
DJANGO_HTTPS=0
REFERRAL_BONUS_POINTS=500
SIGNUP_BONUS_POINTS=100
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
APPLE_CLIENT_ID=
APPLE_TEAM_ID=
APPLE_KEY_ID=
APPLE_PRIVATE_KEY=
EOF
  echo "Created .env with a new secret key"
fi

echo "==> Django setup"
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py setup_fitlab --with-customer || true

chown -R www-data:www-data "$APP_DIR"
chmod 640 "$APP_DIR/.env"

echo "==> Nginx"
SERVER_NAME="${FITLAB_DOMAIN:-${SERVER_IP}}"
sed -e "s/__FITLAB_SERVER_NAME__/${SERVER_NAME}/g" \
    -e "s/__FITLAB_NGINX_PORT__/${NGINX_PORT}/g" \
    -e "s/__FITLAB_GUNICORN_PORT__/${GUNICORN_PORT}/g" \
    deploy/nginx-fitlab.conf > /etc/nginx/sites-available/fitlab
ln -sf /etc/nginx/sites-available/fitlab /etc/nginx/sites-enabled/fitlab
nginx -t
systemctl enable nginx
systemctl restart nginx

if command -v ufw >/dev/null 2>&1; then
  ufw allow OpenSSH >/dev/null 2>&1 || true
  ufw allow "${NGINX_PORT}/tcp" >/dev/null 2>&1 || true
fi

echo "==> Systemd service"
sed "s/__FITLAB_GUNICORN_PORT__/${GUNICORN_PORT}/g" deploy/fitlab.service > /etc/systemd/system/fitlab.service
systemctl daemon-reload
systemctl enable fitlab
systemctl restart fitlab

echo ""
echo "Fitlab is live at: ${PUBLIC_URL}/"
echo "Admin portal:      ${PUBLIC_URL}/admin-portal/"
echo "Default admin:     admin@fitlab.com / admin123"
echo "GitHub repo:       ${REPO_URL}"
echo ""
systemctl status fitlab --no-pager -l

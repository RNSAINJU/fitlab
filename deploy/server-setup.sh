#!/usr/bin/env bash
# First-time Fitlab setup on Ubuntu/Debian VPS.
# Run as root on the server:
#   curl -sSL https://raw.githubusercontent.com/RNSAINJU/fitlab/main/deploy/server-setup.sh | bash
# Or after cloning:
#   sudo bash deploy/server-setup.sh

set -euo pipefail

APP_DIR="/var/www/fitlab"
REPO_URL="${FITLAB_REPO_URL:-https://github.com/RNSAINJU/fitlab.git}"
SERVER_IP="${FITLAB_SERVER_IP:-82.197.69.121}"

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
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
  cat > .env <<EOF
DJANGO_SECRET_KEY=${SECRET}
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=${SERVER_IP},localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://${SERVER_IP},http://localhost
DJANGO_HTTPS=0
REFERRAL_BONUS_POINTS=500
SIGNUP_BONUS_POINTS=100
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
sed "s/__FITLAB_SERVER_NAME__/${SERVER_NAME}/g" deploy/nginx-fitlab.conf > /etc/nginx/sites-available/fitlab
ln -sf /etc/nginx/sites-available/fitlab /etc/nginx/sites-enabled/fitlab
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx
systemctl restart nginx

if command -v ufw >/dev/null 2>&1; then
  ufw allow OpenSSH >/dev/null 2>&1 || true
  ufw allow 'Nginx Full' >/dev/null 2>&1 || ufw allow 80/tcp >/dev/null 2>&1 || true
fi

echo "==> Systemd service"
cp deploy/fitlab.service /etc/systemd/system/fitlab.service
systemctl daemon-reload
systemctl enable fitlab
systemctl restart fitlab

echo ""
echo "Fitlab is live at: http://${SERVER_IP}/"
echo "Admin portal:      http://${SERVER_IP}/admin-portal/"
echo "Default admin:     admin@fitlab.com / admin123"
echo ""
systemctl status fitlab --no-pager -l

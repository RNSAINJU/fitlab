#!/usr/bin/env bash
# Attach a custom domain to Fitlab on this VPS.
# Run on the server as root:
#   cd /var/www/fitlab && sudo FITLAB_DOMAIN=thefitlab.com.np bash deploy/setup-domain.sh
#
# Prerequisites:
#   1. DNS A record for the domain → this server's public IP
#   2. If using Cloudflare: set A record to server IP (proxy on is OK after nginx is ready)

set -euo pipefail

APP_DIR="/var/www/fitlab"
DOMAIN="${FITLAB_DOMAIN:-thefitlab.com.np}"
GUNICORN_PORT="${FITLAB_GUNICORN_PORT:-8004}"
SERVER_IP="${FITLAB_SERVER_IP:-82.197.69.121}"

cd "$APP_DIR"

echo "==> Configuring domain: ${DOMAIN}"

if ! grep -q "limit_req_zone.*fitlab_login" /etc/nginx/sites-available/fitlab 2>/dev/null; then
  echo "ERROR: Fitlab nginx base config missing. Run deploy/deploy.sh first."
  exit 1
fi

echo "==> Nginx domain vhost"
sed -e "s/__FITLAB_DOMAIN__/${DOMAIN}/g" \
    -e "s/__FITLAB_GUNICORN_PORT__/${GUNICORN_PORT}/g" \
    deploy/nginx-fitlab-domain.conf > /etc/nginx/sites-available/fitlab-domain
ln -sf /etc/nginx/sites-available/fitlab-domain /etc/nginx/sites-enabled/fitlab-domain
nginx -t
systemctl reload nginx

echo "==> Update .env for Django"
ENV_FILE="${APP_DIR}/.env"
touch "$ENV_FILE"

update_env() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

update_env "DJANGO_ALLOWED_HOSTS" "${SERVER_IP},${DOMAIN},www.${DOMAIN},localhost,127.0.0.1"
update_env "FITLAB_SITE_DOMAIN" "${DOMAIN}"
update_env "DJANGO_CSRF_TRUSTED_ORIGINS" "http://${SERVER_IP}:8083,http://${SERVER_IP},http://${DOMAIN},http://www.${DOMAIN},https://${DOMAIN},https://www.${DOMAIN},http://localhost"
# Secure cookies for HTTPS visitors; do not enable FITLAB_SSL_REDIRECT behind Cloudflare (redirect loop).
update_env "FITLAB_SSL_REDIRECT" "0"
chmod 640 "$ENV_FILE"

echo "==> Update Django Site framework domain"
.venv/bin/python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(pk=1, defaults={'domain': '${DOMAIN}', 'name': 'Fitlab'})
print('Site domain set to ${DOMAIN}')
"

if command -v certbot >/dev/null 2>&1; then
  echo "==> Requesting Let's Encrypt certificate"
  if certbot --nginx -d "${DOMAIN}" -d "www.${DOMAIN}" --non-interactive --agree-tos --register-unsafely-without-email --no-redirect 2>/dev/null; then
    update_env "DJANGO_HTTPS" "1"
    echo "HTTPS enabled (origin cert installed; use Cloudflare Full strict)."
  else
    echo "WARN: certbot failed (DNS may not point here yet). Site will work on HTTP until DNS propagates."
    echo "      Re-run: sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --no-redirect"
    update_env "DJANGO_HTTPS" "0"
  fi
else
  echo "WARN: certbot not installed. Run: apt install certbot python3-certbot-nginx"
  if [[ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]]; then
    update_env "DJANGO_HTTPS" "1"
  else
    update_env "DJANGO_HTTPS" "0"
  fi
fi

# Re-apply domain nginx (includes HTTPS block) after certbot may have modified files
sed -e "s/__FITLAB_DOMAIN__/${DOMAIN}/g" \
    -e "s/__FITLAB_GUNICORN_PORT__/${GUNICORN_PORT}/g" \
    deploy/nginx-fitlab-domain.conf > /etc/nginx/sites-available/fitlab-domain
nginx -t
systemctl reload nginx

chown -R www-data:www-data "$APP_DIR"
systemctl restart fitlab

echo ""
echo "Domain setup complete."
echo "  http://${DOMAIN}/"
echo "  https://${DOMAIN}/  (if certbot succeeded)"
echo ""
echo "If the domain does not load yet, set DNS:"
echo "  A  ${DOMAIN}  →  ${SERVER_IP}"
echo "  A  www.${DOMAIN}  →  ${SERVER_IP}"

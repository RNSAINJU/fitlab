#!/usr/bin/env bash
# Origin SSL for Fitlab behind Cloudflare (when Let's Encrypt HTTP-01 fails).
# Run on the VPS as root:
#   sudo FITLAB_DOMAIN=thefitlab.com.np bash deploy/setup-origin-ssl.sh
#
# Then in Cloudflare: SSL/TLS → Overview → Full
# (Use "Full (strict)" only with a Cloudflare Origin Certificate instead of self-signed.)

set -euo pipefail

DOMAIN="${FITLAB_DOMAIN:-thefitlab.com.np}"
GUNICORN_PORT="${FITLAB_GUNICORN_PORT:-8004}"
CERT_DIR="/etc/ssl/fitlab"
CERT_FILE="${CERT_DIR}/${DOMAIN}.crt"
KEY_FILE="${CERT_DIR}/${DOMAIN}.key"
NGINX_SITE="/etc/nginx/sites-available/fitlab-domain"

mkdir -p "$CERT_DIR"
chmod 700 "$CERT_DIR"

if [[ ! -f "$CERT_FILE" || ! -f "$KEY_FILE" ]]; then
  echo "==> Generating origin certificate for ${DOMAIN}"
  openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/CN=${DOMAIN}/O=Fitlab" \
    -addext "subjectAltName=DNS:${DOMAIN},DNS:www.${DOMAIN}"
  chmod 600 "$KEY_FILE"
  chmod 644 "$CERT_FILE"
fi

echo "==> Writing nginx SSL vhost"
cat > "$NGINX_SITE" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} www.${DOMAIN};
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate ${CERT_FILE};
    ssl_certificate_key ${KEY_FILE};
    ssl_protocols TLSv1.2 TLSv1.3;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/fitlab/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location = /accounts/login/ {
        limit_req zone=fitlab_login burst=3 nodelay;
        proxy_pass http://127.0.0.1:${GUNICORN_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    location / {
        limit_req zone=fitlab_general burst=50 nodelay;
        proxy_pass http://127.0.0.1:${GUNICORN_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
}
EOF

ln -sf "$NGINX_SITE" /etc/nginx/sites-enabled/fitlab-domain
nginx -t
systemctl reload nginx

ENV_FILE="/var/www/fitlab/.env"
if [[ -f "$ENV_FILE" ]]; then
  if grep -q '^DJANGO_HTTPS=' "$ENV_FILE"; then
    sed -i 's/^DJANGO_HTTPS=.*/DJANGO_HTTPS=1/' "$ENV_FILE"
  else
    echo "DJANGO_HTTPS=1" >> "$ENV_FILE"
  fi
  systemctl restart fitlab
fi

echo ""
echo "Origin SSL installed."
echo "  1. Cloudflare → SSL/TLS → set mode to Full (not strict, unless using Origin Certificate)"
echo "  2. Visit https://${DOMAIN}/"
echo ""
echo "For Full (strict), replace cert with Cloudflare Origin Certificate:"
echo "  Cloudflare → SSL/TLS → Origin Server → Create Certificate"

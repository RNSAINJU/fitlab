# Fitlab

Django loyalty web app for a gym. Customers register, earn **TFL Points**, redeem rewards, and refer friends. Admins approve registrations and redemptions.

## Local setup

```powershell
cd C:\Users\Aryan\Projects\fitlab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_fitlab --with-customer
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Default accounts (after `setup_fitlab`)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@fitlab.com | admin123 |
| Customer | customer@fitlab.com | customer123 |

## Features

- **Registration** ’ pending approval screen until admin approves
- **Login** with email + password
- **TFL Points** ledger with admin adjustments
- **Rewards marketplace**  redemption requests need admin approval before points are deducted
- **Referrals**  referrer earns bonus when referred user is approved
- **Activity feed** for customer events
- **Admin portal** at `/admin-portal/` (customer directory, approvals, ledger)

## Google Stitch (design sync)

Fitlab's design system is documented in [`DESIGN.md`](DESIGN.md) for [Google Stitch](https://stitch.withgoogle.com/).

**Quick link steps:**
1. Open Stitch ? import `DESIGN.md` from this repo, **or** extract design system from `http://82.197.69.121:8083/`
2. New Stitch screens will match Fitlab's dark theme, Lexend typography, and red accent.

Full guide: [`docs/google-stitch.md`](docs/google-stitch.md)

## Production (VPS + GitHub)

GitHub repo: https://github.com/RNSAINJU/fitlab  
VPS path: `/var/www/fitlab` (linked to `origin/main`)

Production stack: **Nginx** ? **Gunicorn** ? **Django** (SQLite).  
Fitlab runs on **port 8083** (port 80 is used by other sites on this server).

| URL | Purpose |
|-----|---------|
| https://thefitlab.com.np/ | Customer app (domain) |
| http://82.197.69.121:8083/ | Customer app (IP fallback) |
| https://thefitlab.com.np/admin-portal/ | Admin portal |

**Change the default admin password immediately** after first login.

Production uses `FITLAB_ADMIN_PASSWORD` in `.env` (generated on first VPS setup). After deploy, run on the server:

```bash
cd /var/www/fitlab
# Set a new strong password in .env, then:
sudo bash deploy/deploy.sh
```

Login brute-force protection is enabled via **django-axes** (5 failures, 30-minute lockout) and nginx rate limits on `/accounts/login/`.

### Update the live site

1. Push your changes to GitHub (`main` branch).
2. SSH into the VPS and pull:

```bash
ssh root@82.197.69.121
cd /var/www/fitlab
sudo bash deploy/deploy.sh
```

That runs `git pull`, installs dependencies, migrates, collects static files, and restarts the app.

### First-time VPS setup (new server only)

```bash
sudo git clone https://github.com/RNSAINJU/fitlab.git /var/www/fitlab
cd /var/www/fitlab
sudo FITLAB_SERVER_IP=82.197.69.121 FITLAB_GUNICORN_PORT=8004 FITLAB_NGINX_PORT=8083 bash deploy/server-setup.sh
```

### Environment variables (`.env` on server)

Copy from `.env.example`. Important values:

- `DJANGO_SECRET_KEY`  long random string (auto-generated on first setup)
- `DJANGO_DEBUG=0`  required in production
- `DJANGO_ALLOWED_HOSTS=82.197.69.121,yourdomain.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=http://82.197.69.121:8083,https://yourdomain.com` (include port if not 80)
- `FITLAB_SITE_DOMAIN=82.197.69.121:8083` (required for Google/Apple OAuth)

### Google & Apple sign-in

Add OAuth credentials to `.env` on the server, then restart Fitlab:

```bash
sudo systemctl restart fitlab
```

**Google** — [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

- Create OAuth client (Web application)
- Authorized redirect URI: `http://82.197.69.121:8083/oauth/google/login/callback/`
- Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`

**Apple** — [Apple Developer](https://developer.apple.com/account/resources)

- Create a Services ID and Sign in with Apple key
- Return URL: `http://82.197.69.121:8083/oauth/apple/login/callback/`
- Set `APPLE_CLIENT_ID` (Services ID), `APPLE_TEAM_ID`, `APPLE_KEY_ID`, and `APPLE_PRIVATE_KEY` in `.env`

Social sign-up creates a pending account (same approval flow as email registration). Referral codes from the register page or `?ref=CODE` are applied automatically.

### Connect a custom domain

Point DNS **A records** to `82.197.69.121`:

| Type | Name | Value |
|------|------|-------|
| A | `@` | `82.197.69.121` |
| A | `www` | `82.197.69.121` |

If the domain uses **Cloudflare**, add those A records in the Cloudflare DNS panel. Orange-cloud (proxied) is fine once the origin responds on port 80.

On the VPS:

```bash
cd /var/www/fitlab
sudo FITLAB_DOMAIN=thefitlab.com.np bash deploy/setup-domain.sh
```

That configures nginx on port 80, updates Django `.env`, and requests a Let's Encrypt certificate. If certbot fails, fix DNS first, then re-run:

```bash
sudo certbot --nginx -d thefitlab.com.np -d www.thefitlab.com.np
```

Set `DJANGO_HTTPS=1` in `.env` after HTTPS works, then `sudo systemctl restart fitlab`.

Update Google/Apple OAuth redirect URIs to `https://thefitlab.com.np/oauth/...`.

### HTTPS (optional, when you have a domain)

Point DNS to `82.197.69.121`, then on the VPS:

```bash
sudo FITLAB_DOMAIN=thefitlab.com.np bash deploy/setup-domain.sh
```

Or manually:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d thefitlab.com.np -d www.thefitlab.com.np
```

Set in `.env`: `DJANGO_HTTPS=1` and update `DJANGO_CSRF_TRUSTED_ORIGINS` to include `https://thefitlab.com.np`, then:

```bash
sudo systemctl restart fitlab
```

## Project structure

```
accounts/       Auth, registration, dashboard, approval gate
loyalty/        TFL Points transactions
rewards/        Marketplace and redemption requests
referrals/      Referral codes and bonus logic
activity/       Customer activity feed
admin_portal/   Custom admin UI
deploy/         Nginx, systemd, setup scripts
```

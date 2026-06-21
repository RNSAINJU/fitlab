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

## Production (VPS + GitHub)

GitHub repo: https://github.com/RNSAINJU/fitlab  
VPS path: `/var/www/fitlab` (linked to `origin/main`)

Production stack: **Nginx** ? **Gunicorn** ? **Django** (SQLite).  
Fitlab runs on **port 8083** (port 80 is used by other sites on this server).

| URL | Purpose |
|-----|---------|
| http://82.197.69.121:8083/ | Customer app |
| http://82.197.69.121:8083/admin-portal/ | Admin portal |

**Change the default admin password immediately** after first login.

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

### HTTPS (optional, when you have a domain)

Point DNS to `82.197.69.121`, then on the VPS:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Set in `.env`: `DJANGO_HTTPS=1` and update `DJANGO_CSRF_TRUSTED_ORIGINS` to `https://...`, then:

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

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

- **Registration** → pending approval screen until admin approves
- **Login** with email + password
- **TFL Points** ledger with admin adjustments
- **Rewards marketplace** — redemption requests need admin approval before points are deducted
- **Referrals** — referrer earns bonus when referred user is approved
- **Activity feed** for customer events
- **Admin portal** at `/admin-portal/` (customer directory, approvals, ledger)

## Push to GitHub

```powershell
cd C:\Users\Aryan\Projects\fitlab
git init
git remote add origin https://github.com/RNSAINJU/fitlab.git
git add .
git commit -m "Initial Fitlab Django loyalty app"
git branch -M main
git push -u origin main
```

If the remote repo already has commits, use `git pull origin main --rebase` first or force-push only if you intend to replace remote history.

## Environment variables (optional)

- `DJANGO_SECRET_KEY` — production secret key
- `DJANGO_DEBUG=0` — disable debug mode
- `REFERRAL_BONUS_POINTS=500` — points for referrer on approval
- `SIGNUP_BONUS_POINTS=100` — reserved for future signup bonus

## Project structure

```
accounts/       Auth, registration, dashboard, approval gate
loyalty/        TFL Points transactions
rewards/        Marketplace and redemption requests
referrals/      Referral codes and bonus logic
activity/       Customer activity feed
admin_portal/   Custom admin UI
```

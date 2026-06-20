# Fitlab local setup script
Set-Location $PSScriptRoot

Write-Host "Creating virtual environment..."
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Running migrations..."
python manage.py makemigrations accounts loyalty rewards referrals activity
python manage.py migrate

Write-Host "Seeding demo data..."
python manage.py setup_fitlab --with-customer

Write-Host ""
Write-Host "Done! Start the server with:"
Write-Host "  python manage.py runserver"
Write-Host ""
Write-Host "Admin:    admin@fitlab.com / admin123"
Write-Host "Customer: customer@fitlab.com / customer123"

# Deploy Fitlab to VPS from Windows (requires OpenSSH client).
# Usage:
#   cd C:\Users\Aryan\Projects\fitlab
#   powershell -ExecutionPolicy Bypass -File .\deploy-to-vps.ps1
#
# Optional env vars:
#   $env:VPS_USER = "root"
#   $env:VPS_HOST = "82.197.69.121"

param(
    [string]$VpsUser = $(if ($env:VPS_USER) { $env:VPS_USER } else { "root" }),
    [string]$VpsHost = $(if ($env:VPS_HOST) { $env:VPS_HOST } else { "82.197.69.121" })
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "==> Fitlab VPS deploy -> ${VpsUser}@${VpsHost}" -ForegroundColor Cyan

Write-Host "`n[1/3] Push latest code to GitHub (commit if needed)..." -ForegroundColor Yellow
git add .
$status = git status --porcelain
if ($status) {
    git commit -m "Prepare VPS deployment"
}
git push origin main

Write-Host "`n[2/3] Run first-time server setup (safe to re-run)..." -ForegroundColor Yellow
ssh "${VpsUser}@${VpsHost}" "export FITLAB_SERVER_IP='${VpsHost}'; bash -s" < deploy/server-setup.sh

Write-Host "`n[3/3] Done." -ForegroundColor Green
Write-Host "Open: http://${VpsHost}/" -ForegroundColor Green
Write-Host "Admin: http://${VpsHost}/admin-portal/ (admin@fitlab.com / admin123)" -ForegroundColor Green

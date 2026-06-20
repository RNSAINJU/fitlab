# Push Fitlab to GitHub (SSH) — run in PowerShell:
#   cd C:\Users\Aryan\Projects\fitlab
#   powershell -ExecutionPolicy Bypass -File .\push-to-github.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "==> Fitlab push (SSH)" -ForegroundColor Cyan

# Skip: echo "# fitlab" >> README.md  — README already exists with full docs

if (-not (Test-Path ".git")) {
    git init
}

git remote remove origin 2>$null
git remote add origin git@github.com:RNSAINJU/fitlab.git

git add .
git status --short

$pending = git status --porcelain
if ($pending) {
    git commit -m "first commit"
} else {
    Write-Host "Nothing to commit." -ForegroundColor Yellow
}

git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDone: https://github.com/RNSAINJU/fitlab" -ForegroundColor Green
} else {
    Write-Host "`nPush failed. Ensure SSH key is added to GitHub (ssh -T git@github.com)" -ForegroundColor Red
    exit 1
}

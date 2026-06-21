#!/usr/bin/env bash
# Deploy Fitlab to VPS from Linux/macOS (requires OpenSSH client).
# Usage:
#   ./deploy-to-vps.sh
#
# Optional env vars:
#   VPS_USER=root
#   VPS_HOST=82.197.69.121

set -euo pipefail

VPS_USER="${VPS_USER:-root}"
VPS_HOST="${VPS_HOST:-82.197.69.121}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> Fitlab VPS deploy -> ${VPS_USER}@${VPS_HOST}"

echo ""
echo "[1/3] Push latest code to GitHub (commit if needed)..."
git add .
if ! git diff --staged --quiet; then
  git commit -m "Prepare VPS deployment"
fi
git push origin main

echo ""
echo "[2/3] Run server setup on VPS (clone/pull from GitHub)..."
ssh "${VPS_USER}@${VPS_HOST}" "export FITLAB_SERVER_IP='${VPS_HOST}'; bash -s" < deploy/server-setup.sh

echo ""
echo "[3/3] Done."
echo "Open:  http://${VPS_HOST}:8083/"
echo "Admin: http://${VPS_HOST}:8083/admin-portal/ (admin@fitlab.com / admin123)"

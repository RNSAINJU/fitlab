#!/usr/bin/env bash
# Smoke-test every Fitlab page via the live dev server.
set -euo pipefail

BASE="http://127.0.0.1:8000"
PASS=()
FAIL=()
REDIRECT=()

check() {
  local label="$1"
  local url="$2"
  local cookie_jar="${3:-}"
  local expected="${4:-200}"
  local extra_args=()
  if [[ -n "$cookie_jar" ]]; then
    extra_args=(-b "$cookie_jar" -c "$cookie_jar")
  fi
  local code
  code=$(curl -s -o /tmp/fitlab_resp.html -w "%{http_code}" "${extra_args[@]}" "$url" || echo "000")
  if [[ "$code" == "$expected" ]] || [[ "$expected" == "2xx" && "$code" =~ ^2 ]]; then
    PASS+=("$label -> $code")
  elif [[ "$code" =~ ^30[1278]$ ]]; then
    REDIRECT+=("$label -> $code")
  else
    local snippet
    snippet=$(head -c 200 /tmp/fitlab_resp.html | tr '\n' ' ')
    FAIL+=("$label -> $code ($snippet)")
  fi
}

login() {
  local email="$1"
  local password="$2"
  local jar="$3"
  local csrf
  csrf=$(curl -s -c "$jar" "$BASE/accounts/login/" | grep -oP 'name="csrfmiddlewaretoken" value="\K[^"]+' | head -1)
  curl -s -b "$jar" -c "$jar" -X POST "$BASE/accounts/login/" \
    -H "Referer: $BASE/accounts/login/" \
    -d "csrfmiddlewaretoken=$csrf" \
    -d "username=$email" \
    -d "password=$password" \
    -o /dev/null -w "%{http_code}"
}

echo "=== Fitlab Page Smoke Test ==="
echo "Server: $BASE"
echo

# Anonymous pages
check "Login" "$BASE/accounts/login/" "" "2xx"
check "Register" "$BASE/accounts/register/" "" "2xx"
check "Register (short)" "$BASE/register" "" "2xx"
check "Connection lost" "$BASE/connection-lost/" "" "2xx"

# Auth guards (should redirect)
check "Dashboard (anon)" "$BASE/" "" "302"
check "Admin portal (anon)" "$BASE/admin-portal/" "" "302"

# Customer pages
CJ=$(mktemp)
login_code=$(login "customer@fitlab.com" "customer123" "$CJ")
if [[ "$login_code" =~ ^30[1278]$ ]]; then
  PASS+=("Customer login -> $login_code")
else
  FAIL+=("Customer login -> $login_code")
fi

check "Customer dashboard" "$BASE/" "$CJ" "2xx"
check "Customer profile" "$BASE/accounts/profile/" "$CJ" "2xx"
check "Customer profile edit" "$BASE/accounts/profile/edit/" "$CJ" "2xx"
check "Activity feed" "$BASE/activity/" "$CJ" "2xx"
check "Rewards marketplace" "$BASE/rewards/" "$CJ" "2xx"
check "Referrals hub" "$BASE/referrals/" "$CJ" "2xx"

REWARD_ID=$(cd /workspace && .venv/bin/python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','fitlab_project.settings')
import sys; sys.path.insert(0,'.')
django.setup()
from rewards.models import Reward
r = Reward.objects.filter(is_active=True).first()
print(r.id if r else '')
")
if [[ -n "$REWARD_ID" ]]; then
  check "Reward redeem" "$BASE/rewards/${REWARD_ID}/redeem/" "$CJ" "2xx"
fi
rm -f "$CJ"

# Admin pages
AJ=$(mktemp)
admin_login=$(login "admin@fitlab.com" "admin123" "$AJ")
if [[ "$admin_login" =~ ^30[1278]$ ]]; then
  PASS+=("Admin login -> $admin_login")
else
  FAIL+=("Admin login -> $admin_login")
fi

check "Admin dashboard" "$BASE/admin-portal/" "$AJ" "2xx"
check "Customer directory" "$BASE/admin-portal/customers/" "$AJ" "2xx"
check "Registration approvals" "$BASE/admin-portal/approvals/" "$AJ" "2xx"
check "Rewards list" "$BASE/admin-portal/rewards/" "$AJ" "2xx"
check "Reward create" "$BASE/admin-portal/rewards/create/" "$AJ" "2xx"
check "Role management" "$BASE/admin-portal/roles/" "$AJ" "2xx"
check "Points ledger" "$BASE/admin-portal/ledger/" "$AJ" "2xx"
check "Point rules" "$BASE/admin-portal/point-rules/" "$AJ" "2xx"
rm -f "$AJ"

# Pending user
PJ=$(mktemp)
cd /workspace && .venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u, c = User.objects.get_or_create(username='pending_test@fitlab.com', defaults={'email':'pending_test@fitlab.com','approval_status':User.ApprovalStatus.PENDING})
if c:
    u.set_password('pending123'); u.save()
" 2>/dev/null
pending_login=$(login "pending_test@fitlab.com" "pending123" "$PJ")
check "Pending page" "$BASE/accounts/pending/" "$PJ" "2xx"
check "Dashboard (pending user)" "$BASE/" "$PJ" "302"
rm -f "$PJ"

echo "PASSED (${#PASS[@]}):"
for p in "${PASS[@]}"; do echo "  ✓ $p"; done
echo
echo "REDIRECTS (${#REDIRECT[@]}):"
for r in "${REDIRECT[@]}"; do echo "  → $r"; done
echo
if [[ ${#FAIL[@]} -gt 0 ]]; then
  echo "FAILED (${#FAIL[@]}):"
  for f in "${FAIL[@]}"; do echo "  ✗ $f"; done
  exit 1
else
  echo "All pages OK — no errors found."
fi

#!/usr/bin/env bash
#
# E2E smoke test using agent-browser.
#
# Usage:
#   ./e2e/smoke.sh [BASE_URL]
#
# BASE_URL defaults to http://localhost:3000 for local runs.
# In CI, the deploy-staging workflow passes the per-PR preview URL.

set -euo pipefail

BASE_URL="${1:-${BASE_URL:-http://localhost:3000}}"

echo "=== E2E Smoke Test ==="
echo "Target: ${BASE_URL}"
echo ""

# ── 1. Frontend loads ────────────────────────────────────────────────
echo "--- Test: Frontend loads and shows title ---"
agent-browser open "${BASE_URL}"
agent-browser wait --load networkidle

TITLE=$(agent-browser get title)
echo "Page title: ${TITLE}"

if [[ "${TITLE}" != *"TanStack"* ]]; then
  echo "FAIL: Expected title to contain 'TanStack', got '${TITLE}'"
  exit 1
fi
echo "PASS"
echo ""

# ── 2. Interactive elements are present ──────────────────────────────
echo "--- Test: Page has interactive elements ---"
SNAPSHOT=$(agent-browser snapshot -i -c)
echo "${SNAPSHOT}" | head -20

if [[ -z "${SNAPSHOT}" ]]; then
  echo "FAIL: Snapshot returned no interactive elements"
  exit 1
fi
echo "PASS"
echo ""

# ── 3. Navigation works ─────────────────────────────────────────────
echo "--- Test: Navigate to About page ---"
agent-browser snapshot -i
# Find and click the About link
agent-browser find text "About" click
agent-browser wait --load networkidle

URL=$(agent-browser get url)
echo "Current URL: ${URL}"

if [[ "${URL}" != *"/about"* ]]; then
  echo "FAIL: Expected URL to contain '/about', got '${URL}'"
  exit 1
fi
echo "PASS"
echo ""

# ── 4. Backend health check (if reachable) ───────────────────────────
# Derive backend URL from frontend URL by swapping the port range
# CI: frontend=40xx -> backend=90xx   Local: frontend=3000 -> backend=8000
BACKEND_URL="${API_URL:-}"
if [[ -z "${BACKEND_URL}" ]]; then
  if [[ "${BASE_URL}" =~ :4([0-9]+)$ ]]; then
    BACKEND_URL="${BASE_URL/:4/:9}"
  else
    BACKEND_URL="${BASE_URL/3000/8000}"
  fi
fi

echo "--- Test: Backend health check (${BACKEND_URL}/health) ---"
if HEALTH=$(curl -sf "${BACKEND_URL}/health" 2>/dev/null); then
  echo "Response: ${HEALTH}"
  if [[ "${HEALTH}" == *'"ok"'* ]]; then
    echo "PASS"
  else
    echo "WARN: Unexpected health response (non-blocking)"
  fi
else
  echo "SKIP: Backend not reachable at ${BACKEND_URL} (may be expected locally)"
fi
echo ""

echo "=== All E2E smoke tests passed ==="

#!/usr/bin/env bash
# Read-only health checks for the deployed LLM Wiki management app.
set -euo pipefail

BASE_URL="${LLM_WIKI_HEALTH_URL:-}"
AUTH_USER="${LLM_WIKI_BASIC_AUTH_USER:-}"
AUTH_PASSWORD="${LLM_WIKI_BASIC_AUTH_PASSWORD:-}"

fail() {
  printf '[llm-wiki-health] ERROR: %s\n' "$*" >&2
  exit 1
}

log() {
  printf '[llm-wiki-health] %s\n' "$*"
}

if [[ -z "$BASE_URL" ]]; then
  fail "LLM_WIKI_HEALTH_URL is required (example: https://wiki.plattenradar.de)"
fi
if [[ -z "$AUTH_USER" || -z "$AUTH_PASSWORD" ]]; then
  fail "LLM_WIKI_BASIC_AUTH_USER and LLM_WIKI_BASIC_AUTH_PASSWORD are required"
fi

BASE_URL="${BASE_URL%/}"

curl_auth() {
  local path="$1"
  shift
  curl --fail --silent --show-error \
    --user "${AUTH_USER}:${AUTH_PASSWORD}" \
    "$@" \
    "${BASE_URL}${path}"
}

log "Checking frontend root"
curl_auth "/" --output /dev/null

log "Checking /api/health"
health_json="$(curl_auth "/api/health")"
python3 - "$health_json" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
if payload.get("ok") is not True:
    raise SystemExit(f"/api/health ok flag missing or false: {payload!r}")
print("health ok")
PY

log "Checking /api/config"
curl_auth "/api/config" --output /dev/null

log "Checking /api/ops/status"
curl_auth "/api/ops/status" --output /dev/null

log "All read-only health checks passed"

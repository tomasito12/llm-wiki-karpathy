#!/usr/bin/env bash
# Read-only health checks for the deployed LLM Wiki management app.
set -euo pipefail

BASE_URL="${LLM_WIKI_HEALTH_URL:-}"
AUTH_USER="${LLM_WIKI_BASIC_AUTH_USER:-}"
AUTH_PASSWORD="${LLM_WIKI_BASIC_AUTH_PASSWORD:-}"
MAX_ATTEMPTS="${LLM_WIKI_HEALTH_ATTEMPTS:-12}"
SLEEP_SECONDS="${LLM_WIKI_HEALTH_SLEEP_SECONDS:-5}"

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

wait_for_endpoint() {
  local path="$1"
  local label="$2"
  local attempt=1
  local body=""

  log "Checking ${label}"
  while (( attempt <= MAX_ATTEMPTS )); do
    if body="$(curl_auth "${path}" 2>/dev/null)"; then
      if [[ "${path}" == "/api/health" ]]; then
        if python3 - "$body" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
if payload.get("ok") is not True:
    raise SystemExit(f"/api/health ok flag missing or false: {payload!r}")
print("health ok")
PY
        then
          return 0
        fi
      else
        return 0
      fi
    fi
    log "Attempt ${attempt}/${MAX_ATTEMPTS} failed for ${label}; retrying in ${SLEEP_SECONDS}s"
    sleep "${SLEEP_SECONDS}"
    attempt=$((attempt + 1))
  done
  fail "${label} did not become healthy after ${MAX_ATTEMPTS} attempts"
}

wait_for_endpoint "/" "frontend root"
wait_for_endpoint "/api/health" "/api/health"

log "Checking /api/config"
curl_auth "/api/config" --output /dev/null

log "Checking /api/ops/status"
curl_auth "/api/ops/status" --output /dev/null

log "All read-only health checks passed"

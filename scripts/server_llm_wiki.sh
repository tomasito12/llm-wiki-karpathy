#!/usr/bin/env bash
# SSH helper for LLM Wiki server operations.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f "$ROOT_DIR/.env.server" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ROOT_DIR/.env.server"
  set +a
fi

# Prefer DEPLOY_* (GHA / .env.server). Fall back to Music Review sync vars so the
# same local key/host setup works for both projects.
SERVER_USER="${DEPLOY_USER:-${MUSIC_REVIEW_SYNC_USER:-deploy}}"
SERVER_HOST="${DEPLOY_HOST:-${MUSIC_REVIEW_SYNC_HOST:-167.233.138.166}}"
SERVER_PATH="${DEPLOY_PATH:-/srv/llm-wiki/app}"
SSH_KEY="${DEPLOY_SSH_KEY:-${MUSIC_REVIEW_SYNC_KEY:-$HOME/.ssh/music_review_deploy}}"
SSH_PORT="${DEPLOY_PORT:-${MUSIC_REVIEW_SYNC_PORT:-22}}"
DRY_RUN="${LLM_WIKI_SERVER_DRY_RUN:-false}"
COMPOSE_FILE="${LLM_WIKI_COMPOSE_FILE:-compose.llm-wiki.yml}"

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/server_llm_wiki.sh <command> [args]

Commands:
  status                 Show remote compose status
  ssh                    Open an interactive SSH session
  logs api|frontend [N]  Tail container logs (default 100 lines)
  compose <args...>      Run docker compose on the server
  compose ps             Shortcut for compose ps
  compose pull           Shortcut for compose pull
  compose up             Shortcut for compose up -d --remove-orphans
  health                 Run remote deploy health script

Options:
  --dry-run              Print remote commands without executing them
  -h, --help             Show this help

Environment (from .env.server when present):
  DEPLOY_HOST / MUSIC_REVIEW_SYNC_HOST
  DEPLOY_USER / MUSIC_REVIEW_SYNC_USER
  DEPLOY_PATH (default: /srv/llm-wiki/app)
  DEPLOY_PORT / MUSIC_REVIEW_SYNC_PORT
  DEPLOY_SSH_KEY / MUSIC_REVIEW_SYNC_KEY
  LLM_WIKI_COMPOSE_FILE   Default: compose.llm-wiki.yml
  LLM_WIKI_SERVER_DRY_RUN=true

Interactive login shortcut:
  hatch run server

This script never prints secret values from the environment.
USAGE
}

log() {
  printf '[llm-wiki-server] %s\n' "$*"
}

fail() {
  printf '[llm-wiki-server] ERROR: %s\n' "$*" >&2
  exit 1
}

require_host() {
  if [[ "$DRY_RUN" == true && -z "$SERVER_HOST" ]]; then
    SERVER_HOST="example.invalid"
    return 0
  fi
  if [[ -z "$SERVER_HOST" ]]; then
    fail "DEPLOY_HOST or MUSIC_REVIEW_SYNC_HOST is required (set it in .env.server)."
  fi
}

build_ssh_base() {
  SSH_BASE_ARGS=(-p "$SSH_PORT" -o IdentitiesOnly=yes)
  if [[ -n "$SSH_KEY" && -f "$SSH_KEY" ]]; then
    SSH_BASE_ARGS+=(-i "$SSH_KEY")
  fi
}

run_ssh() {
  require_host
  build_ssh_base
  if [[ "$DRY_RUN" == true ]]; then
    log "DRY_RUN ssh ${SERVER_USER}@${SERVER_HOST} (args redacted)"
    log "DRY_RUN remote: $*"
    return 0
  fi
  ssh "${SSH_BASE_ARGS[@]}" "${SERVER_USER}@${SERVER_HOST}" "$@"
}

run_remote() {
  local remote_cmd="$1"
  run_ssh "cd $(printf '%q' "$SERVER_PATH") && ${remote_cmd}"
}

compose_remote() {
  run_remote "docker compose -f $(printf '%q' "$COMPOSE_FILE") $*"
}

cmd_status() {
  compose_remote ps
}

cmd_logs() {
  local service="${1:-}"
  local lines="${2:-100}"
  case "$service" in
    api) service="llm-wiki-api" ;;
    frontend) service="llm-wiki-frontend" ;;
    "") fail "Usage: logs api|frontend [LINES]" ;;
  esac
  run_remote "docker logs --tail $(printf '%q' "$lines") $(printf '%q' "$service")"
}

cmd_health() {
  run_remote "./scripts/check_llm_wiki_deploy_health.sh"
}

cmd_compose() {
  if (($# == 0)); then
    fail "Usage: compose <docker compose args...>"
  fi
  if [[ "${1:-}" == "up" && $# -eq 1 ]]; then
    compose_remote up -d --remove-orphans
    return 0
  fi
  compose_remote "$@"
}

main() {
  local cmd="${1:-}"
  if [[ "$cmd" == "--dry-run" ]]; then
    DRY_RUN=true
    shift
    cmd="${1:-}"
  fi
  case "$cmd" in
    ""|-h|--help) usage ;;
    status) shift; cmd_status "$@" ;;
    ssh)
      require_host
      build_ssh_base
      if [[ "$DRY_RUN" == true ]]; then
        log "DRY_RUN interactive ssh ${SERVER_USER}@${SERVER_HOST}"
        return 0
      fi
      ssh "${SSH_BASE_ARGS[@]}" "${SERVER_USER}@${SERVER_HOST}"
      ;;
    logs) shift; cmd_logs "$@" ;;
    compose) shift; cmd_compose "$@" ;;
    health) shift; cmd_health "$@" ;;
    --dry-run)
      DRY_RUN=true
      shift
      main "$@"
      ;;
    *) fail "Unknown command: $cmd" ;;
  esac
}

main "$@"

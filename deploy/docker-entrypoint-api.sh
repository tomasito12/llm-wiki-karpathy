#!/bin/sh
set -eu

if [ -z "${LLM_WIKI_PATHS_CONFIG:-}" ]; then
  echo "ERROR: LLM_WIKI_PATHS_CONFIG is empty. Set it to the server path config file." >&2
  exit 1
fi

if [ ! -f "${LLM_WIKI_PATHS_CONFIG}" ]; then
  echo "ERROR: Path config file not found: ${LLM_WIKI_PATHS_CONFIG}" >&2
  exit 1
fi

echo "Starting LLM Wiki management API on 0.0.0.0:8000"
echo "Using paths config: ${LLM_WIKI_PATHS_CONFIG}"

exec hatch run management-api \
  --host 0.0.0.0 \
  --port 8000 \
  --paths-config "${LLM_WIKI_PATHS_CONFIG}"

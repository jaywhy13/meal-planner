#!/usr/bin/env bash
# Prefix any command with this script to run it under a worktree-scoped
# environment. Derives a stable project name and host-port offset from the
# worktree's root path, then execs the passed command with those exported.
#
# Usage:
#   scripts/isolate-env-vars.sh make start
#   scripts/isolate-env-vars.sh docker-compose ps
#
# Without this prefix, the project runs on its default ports (8000/3000/5432)
# under the default Compose project name — same as before this script existed.

set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: $0 <command> [args...]" >&2
  exit 64
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HASH="$(printf '%s' "$ROOT" | sha1sum | cut -c1-6)"
# 2 hex chars -> 0..255, mod 100, *10 -> port offset of 0..990 in steps of 10.
OFFSET=$(( 0x${HASH:0:2} % 100 * 10 ))

export COMPOSE_PROJECT_NAME="mealplanner_${HASH}"
export BACKEND_PORT=$(( 8000 + OFFSET ))
export FRONTEND_PORT=$(( 3000 + OFFSET ))
export DB_PORT=$(( 5432 + OFFSET ))
export REACT_APP_API_URL="http://localhost:${BACKEND_PORT}/api"

exec "$@"

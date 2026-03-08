#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing required command: ${cmd}" >&2
    exit 1
  fi
}

load_git_env_optional() {
  local candidates=(
    "${PROJECT_ROOT}/.env.local"
    "${PROJECT_ROOT}/.env"
  )

  local env_file=""
  local candidate
  for candidate in "${candidates[@]}"; do
    if [ -f "${candidate}" ]; then
      env_file="${candidate}"
      break
    fi
  done

  if [ -z "${env_file}" ]; then
    return 1
  fi

  # shellcheck disable=SC1090
  set -a
  source "${env_file}"
  set +a
}

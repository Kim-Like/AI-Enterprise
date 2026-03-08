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

load_remote_env_optional() {
  if [ -n "${CPANEL_SSH_HOST:-}" ] && [ -n "${CPANEL_SSH_USER:-}" ] && [ -n "${CPANEL_SSH_PORT:-}" ] && [ -n "${CPANEL_SSH_KEY_PATH:-}" ]; then
    return 0
  fi

  local candidates=(
    "${PROJECT_ROOT}/.env.local"
    "${PROJECT_ROOT}/.env"
  )

  local env_file=""
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

  [ -n "${CPANEL_SSH_HOST:-}" ] || return 1
  [ -n "${CPANEL_SSH_USER:-}" ] || return 1
  [ -n "${CPANEL_SSH_PORT:-}" ] || return 1
  [ -n "${CPANEL_SSH_KEY_PATH:-}" ] || return 1
}

ssh_exec() {
  ssh \
    -o BatchMode=yes \
    -o StrictHostKeyChecking=accept-new \
    -o ConnectTimeout=20 \
    -p "${CPANEL_SSH_PORT}" \
    -i "${CPANEL_SSH_KEY_PATH}" \
    "${CPANEL_SSH_USER}@${CPANEL_SSH_HOST}" \
    "$@"
}

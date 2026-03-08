#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/_git_governance_common.sh"

require_cmd git
load_git_env_optional || true

usage() {
  cat <<'EOF'
Usage:
  bootstrap_primary_remote.sh \
    --repo-path <path> \
    --primary-remote <url> \
    [--mirror-remote <url>] \
    [--create-bare --ssh-target <user@host> --bare-path <path>]

Examples:
  bootstrap_primary_remote.sh \
    --repo-path /Users/IAn/Agent/AI-Enterprise \
    --primary-remote git@tailnet-git:/srv/git/AI-Enterprise.git

  bootstrap_primary_remote.sh \
    --repo-path /Users/IAn/Agent/AI-Enterprise \
    --primary-remote-env AI_ENTERPRISE_PRIMARY_GIT_REMOTE \
    --mirror-remote-env AI_ENTERPRISE_GIT_MIRROR_REMOTE
EOF
}

REPO_PATH=""
PRIMARY_REMOTE=""
PRIMARY_REMOTE_ENV=""
MIRROR_REMOTE=""
MIRROR_REMOTE_ENV=""
CREATE_BARE=0
SSH_TARGET=""
BARE_PATH=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-path) REPO_PATH="${2:-}"; shift 2 ;;
    --primary-remote) PRIMARY_REMOTE="${2:-}"; shift 2 ;;
    --primary-remote-env) PRIMARY_REMOTE_ENV="${2:-}"; shift 2 ;;
    --mirror-remote) MIRROR_REMOTE="${2:-}"; shift 2 ;;
    --mirror-remote-env) MIRROR_REMOTE_ENV="${2:-}"; shift 2 ;;
    --create-bare) CREATE_BARE=1; shift ;;
    --ssh-target) SSH_TARGET="${2:-}"; shift 2 ;;
    --bare-path) BARE_PATH="${2:-}"; shift 2 ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

[ -n "${REPO_PATH}" ] || {
  usage
  exit 1
}

if [ -n "${PRIMARY_REMOTE_ENV}" ] && [ -z "${PRIMARY_REMOTE}" ]; then
  PRIMARY_REMOTE="${!PRIMARY_REMOTE_ENV:-}"
fi

if [ -n "${MIRROR_REMOTE_ENV}" ] && [ -z "${MIRROR_REMOTE}" ]; then
  MIRROR_REMOTE="${!MIRROR_REMOTE_ENV:-}"
fi

if [ "${CREATE_BARE}" -eq 1 ]; then
  require_cmd ssh
  [ -n "${SSH_TARGET}" ] || {
    echo "--ssh-target is required with --create-bare" >&2
    exit 1
  }
  [ -n "${BARE_PATH}" ] || {
    echo "--bare-path is required with --create-bare" >&2
    exit 1
  }

  ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new "${SSH_TARGET}" \
    "mkdir -p \"$(dirname "${BARE_PATH}")\" && if [ ! -d \"${BARE_PATH}\" ]; then git init --bare \"${BARE_PATH}\" >/dev/null; fi"
fi

[ -n "${PRIMARY_REMOTE}" ] || {
  echo "Primary remote is required." >&2
  exit 1
}

mkdir -p "${REPO_PATH}"

if [ ! -d "${REPO_PATH}/.git" ]; then
  git -C "${REPO_PATH}" init >/dev/null
fi

if git -C "${REPO_PATH}" remote get-url origin >/dev/null 2>&1; then
  git -C "${REPO_PATH}" remote set-url origin "${PRIMARY_REMOTE}"
else
  git -C "${REPO_PATH}" remote add origin "${PRIMARY_REMOTE}"
fi

if [ -n "${MIRROR_REMOTE}" ]; then
  if git -C "${REPO_PATH}" remote get-url mirror >/dev/null 2>&1; then
    git -C "${REPO_PATH}" remote set-url mirror "${MIRROR_REMOTE}"
  else
    git -C "${REPO_PATH}" remote add mirror "${MIRROR_REMOTE}"
  fi
fi

git -C "${REPO_PATH}" remote -v
echo "bootstrap_primary_remote=ok"

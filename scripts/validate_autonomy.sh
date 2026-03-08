#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/_git_governance_common.sh"

require_cmd bash
require_cmd python3
require_cmd rg

load_git_env_optional || true

required_files=(
  "${PROJECT_ROOT}/docs/autonomy-executor-host.md"
  "${PROJECT_ROOT}/ops/systemd/ai-enterprise-api.service"
  "${PROJECT_ROOT}/ops/systemd/ai-enterprise-autonomy.service"
  "${PROJECT_ROOT}/ops/systemd/ai-enterprise-autonomy.timer"
  "${PROJECT_ROOT}/scripts/run_autonomy_executor.sh"
)

for path in "${required_files[@]}"; do
  [ -f "${path}" ] || {
    echo "Missing autonomy host artifact: ${path}" >&2
    exit 1
  }
done

rg -n "validate_autonomy.sh" "${PROJECT_ROOT}/scripts/validate_ai_enterprise.sh" >/dev/null
rg -n "AUTONOMY_EXECUTOR_HOST_ID|AUTONOMY_API_URL|AUTONOMY_HOST_KILL_SWITCH_FILE" "${PROJECT_ROOT}/.env.example" >/dev/null

bash "${PROJECT_ROOT}/scripts/run_autonomy_executor.sh" --help >/dev/null

preflight_json="$(bash "${PROJECT_ROOT}/scripts/provision_governed_remote.sh" --repo-id ai-enterprise --mode dry_run --json)"
python3 - "${preflight_json}" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
assert payload["status"] == "ok"
assert payload["requested_mode"] == "dry_run"
assert payload["repositories"]
assert payload["repositories"][0]["repo_id"] == "ai-enterprise"
PY

hard_kill_switch_file="${AUTONOMY_HOST_KILL_SWITCH_FILE:-/etc/ai-enterprise/autonomy.disabled}"
hard_kill_switch_active=false
if [ "${AUTONOMY_HARD_DISABLE:-0}" = "1" ] || [ -f "${hard_kill_switch_file}" ]; then
  hard_kill_switch_active=true
fi

echo "executor_hard_kill_switch=${hard_kill_switch_file} active=${hard_kill_switch_active}"
echo "credential_status IAN_AUTONOMY_KEY=$([ -n "${IAN_AUTONOMY_KEY:-}" ] && echo present || echo missing)"
echo "credential_status GITHUB_AUTONOMY_TOKEN=$([ -n "${GITHUB_AUTONOMY_TOKEN:-}" ] && echo present || echo missing)"

if [ "${AUTONOMY_VALIDATE_REQUIRE_HOST_ENV:-0}" = "1" ]; then
  [ -n "${IAN_AUTONOMY_KEY:-}" ] || {
    echo "IAN_AUTONOMY_KEY must be present when AUTONOMY_VALIDATE_REQUIRE_HOST_ENV=1" >&2
    exit 1
  }
  [ -n "${GITHUB_AUTONOMY_TOKEN:-}" ] || {
    echo "GITHUB_AUTONOMY_TOKEN must be present when AUTONOMY_VALIDATE_REQUIRE_HOST_ENV=1" >&2
    exit 1
  }
fi

export PYTHONPATH="${PROJECT_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
if [ "${AI_ENTERPRISE_PARENT_VALIDATION:-0}" != "1" ]; then
  cd "${PROJECT_ROOT}"
  python3 -m pytest -q tests/test_phase10_contracts.py -k executor
  python3 -m pytest -q tests/api/test_autonomy_api.py -k executor
  python3 -m pytest -q tests/api/test_autonomy_api.py -k audit
  python3 -m pytest -q tests/api/test_autonomy_api.py -k sync
fi

echo "validate_autonomy=ok"

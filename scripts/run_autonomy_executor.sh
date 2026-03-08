#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/_git_governance_common.sh"

require_cmd curl
require_cmd python3
load_git_env_optional || true

usage() {
  cat <<'EOF'
Usage:
  run_autonomy_executor.sh [--repo-id <id> ...] [--all] [--actor-agent-id <id>] [--mode dry_run|provision] [--trigger-source <source>] [--json]

Examples:
  run_autonomy_executor.sh --all --actor-agent-id ian-master --mode dry_run --trigger-source systemd_timer
  run_autonomy_executor.sh --repo-id ai-enterprise --actor-agent-id engineer --mode provision --json
EOF
}

REPO_IDS=()
RUN_ALL=0
ACTOR_AGENT_ID="${AUTONOMY_EXECUTOR_ACTOR:-ian-master}"
REQUESTED_MODE="${AUTONOMY_EXECUTOR_MODE:-dry_run}"
TRIGGER_SOURCE="${AUTONOMY_EXECUTOR_TRIGGER_SOURCE:-manual_cli}"
JSON_OUTPUT=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-id) REPO_IDS+=("${2:-}"); shift 2 ;;
    --all) RUN_ALL=1; shift ;;
    --actor-agent-id) ACTOR_AGENT_ID="${2:-}"; shift 2 ;;
    --mode) REQUESTED_MODE="${2:-}"; shift 2 ;;
    --trigger-source) TRIGGER_SOURCE="${2:-}"; shift 2 ;;
    --json) JSON_OUTPUT=1; shift ;;
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

API_URL="${AUTONOMY_API_URL:-http://127.0.0.1:${PORT:-8001}}"
AUTONOMY_HEADER="${IAN_AUTONOMY_HEADER:-X-Autonomy-Key}"
AUTONOMY_KEY="${IAN_AUTONOMY_KEY:-}"
HARD_KILL_SWITCH_FILE="${AUTONOMY_HOST_KILL_SWITCH_FILE:-/etc/ai-enterprise/autonomy.disabled}"

if [ "${AUTONOMY_HARD_DISABLE:-0}" = "1" ] || [ -f "${HARD_KILL_SWITCH_FILE}" ]; then
  echo "Autonomy executor hard kill switch is active: ${HARD_KILL_SWITCH_FILE}" >&2
  exit 1
fi

[ -n "${AUTONOMY_KEY}" ] || {
  echo "IAN_AUTONOMY_KEY is required for authenticated autonomy execution." >&2
  exit 1
}

if [ "${RUN_ALL}" -eq 1 ]; then
  REPO_IDS=()
fi

payload="$(
  ACTOR_AGENT_ID="${ACTOR_AGENT_ID}" \
  REQUESTED_MODE="${REQUESTED_MODE}" \
  TRIGGER_SOURCE="${TRIGGER_SOURCE}" \
  REPO_IDS="$(IFS=,; echo "${REPO_IDS[*]}")" \
  python3 - <<'PY'
import json
import os

repo_ids = [item.strip() for item in os.getenv("REPO_IDS", "").split(",") if item.strip()]
print(
    json.dumps(
        {
            "actor_agent_id": os.getenv("ACTOR_AGENT_ID", "ian-master"),
            "repo_ids": repo_ids,
            "requested_mode": os.getenv("REQUESTED_MODE", "dry_run"),
            "trigger_source": os.getenv("TRIGGER_SOURCE", "manual_cli"),
        }
    )
)
PY
)"

response="$(
  curl -fsS \
    -H "Content-Type: application/json" \
    -H "${AUTONOMY_HEADER}: ${AUTONOMY_KEY}" \
    --data "${payload}" \
    "${API_URL}/api/autonomy/executor/run"
)"

if [ "${JSON_OUTPUT}" -eq 1 ]; then
  echo "${response}"
  exit 0
fi

python3 - "${response}" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
run = payload["run"]
print(
    "autonomy_run_id={id} status={status} validation_status={validation} mode={mode} actor={actor}".format(
        id=run["id"],
        status=run["status"],
        validation=run["validation_status"],
        mode=run["requested_mode"],
        actor=run["actor_agent_id"],
    )
)
for repo in payload.get("repositories", []):
    print(
        "repo_id={repo_id} status={status} validation_status={validation} quarantine={quarantine}".format(
            repo_id=repo["repo_id"],
            status=repo["status"],
            validation=repo["validation_status"],
            quarantine=repo["quarantine_status"],
        )
    )
PY

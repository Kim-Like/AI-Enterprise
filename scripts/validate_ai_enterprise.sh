#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PARKED_NODE_MODULES="$(cd "$ROOT/.." && pwd)/node_modules.ai-enterprise-temp"
LIVE_NODE_MODULES="$ROOT/node_modules"

restore_node_modules() {
  if [[ -d "$LIVE_NODE_MODULES" ]]; then
    return
  fi
  if [[ -d "$PARKED_NODE_MODULES" ]]; then
    mv "$PARKED_NODE_MODULES" "$LIVE_NODE_MODULES"
    return
  fi
  (cd "$ROOT" && npm install)
}

park_node_modules() {
  if [[ -d "$LIVE_NODE_MODULES" ]]; then
    rm -rf "$PARKED_NODE_MODULES"
    mv "$LIVE_NODE_MODULES" "$PARKED_NODE_MODULES"
  fi
}

cleanup() {
  park_node_modules
}

trap cleanup EXIT

restore_node_modules

cd "$ROOT"
npm run test -- --run
npm run build

if rg -n "localStorage|sessionStorage|VITE_[A-Z0-9_]*API_KEY|DASHBOARD_ADMIN_KEY|IAN_AUTONOMY_KEY" src dist; then
  echo "Forbidden frontend or bundle patterns detected." >&2
  exit 1
fi

park_node_modules

export PYTHONPATH="$ROOT"
python3 -m pytest -p no:cacheprovider tests/api tests/test_agent_hierarchy.py tests/test_program_payloads.py tests/test_phase10_contracts.py -q

bash "$ROOT/scripts/validate_git_governance.sh"
bash "$ROOT/scripts/check_remote_config_contract.sh"
bash "$ROOT/scripts/verify_remote_portfolio.sh"

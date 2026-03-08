#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8001}"

if [[ ! -f "$ROOT/dist/index.html" ]]; then
  echo "Frontend build missing at $ROOT/dist/index.html. Run 'bash scripts/validate_ai_enterprise.sh' or 'npm run build' first." >&2
  exit 1
fi

cd "$ROOT"
export PYTHONPATH="$ROOT"
exec python3 -m uvicorn api.app:create_app --factory --host "$HOST" --port "$PORT"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/_cpanel_common.sh"

require_cmd ssh

if ! load_remote_env_optional; then
  echo "SKIP remote config contract check: CPANEL SSH env not configured."
  exit 0
fi

ssh_exec 'bash -s' <<'REMOTE'
set -euo pipefail

domains=(
  "lavprishjemmeside.dk"
  "ljdesignstudio.dk"
  "reporting.theartisan.dk"
)

hits=0

for domain in "${domains[@]}"; do
  candidates=(
    "/home/theartis/${domain}/.htaccess"
    "/home/theartis/${domain}/api/.htaccess"
    "/home/theartis/repositories/${domain}/.htaccess"
    "/home/theartis/repositories/${domain}/api/.htaccess"
  )

  for candidate in "${candidates[@]}"; do
    if [ ! -f "${candidate}" ]; then
      continue
    fi

    if grep -nE 'SetEnv|PassengerEnvVar|(_KEY=|_TOKEN=|_PASSWORD=|_SECRET=|ghp_[A-Za-z0-9_]+)' "${candidate}" >/tmp/phase8_remote_hits.txt 2>/dev/null; then
      echo "forbidden_config=${candidate}"
      cut -d: -f1-2 /tmp/phase8_remote_hits.txt
      hits=1
    fi
  done
done

rm -f /tmp/phase8_remote_hits.txt

if [ "${hits}" -ne 0 ]; then
  exit 1
fi

echo "remote_config_contract=ok"
REMOTE

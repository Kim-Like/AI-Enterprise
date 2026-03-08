#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/_git_governance_common.sh"

require_cmd git
require_cmd python3

load_git_env_optional || true

STRICT="${GIT_GOVERNANCE_STRICT:-0}"
MANIFEST="${PROJECT_ROOT}/ops/repository-topology.json"
DOCS=(
  "${PROJECT_ROOT}/docs/infrastructure-topology.md"
  "${PROJECT_ROOT}/docs/repository-governance.md"
  "${PROJECT_ROOT}/docs/deployment-provenance.md"
)

[ -f "${MANIFEST}" ] || {
  echo "Missing repository topology manifest: ${MANIFEST}" >&2
  exit 1
}

for doc in "${DOCS[@]}"; do
  [ -f "${doc}" ] || {
    echo "Missing required infrastructure doc: ${doc}" >&2
    exit 1
  }
done

nested_git_dirs="$(find "${PROJECT_ROOT}" -mindepth 2 -type d -name .git -print)"
if [ -n "${nested_git_dirs}" ]; then
  printf 'Nested git directories found:\n' >&2
  while IFS= read -r git_dir; do
    [ -n "${git_dir}" ] || continue
    printf ' - %s\n' "${git_dir}" >&2
  done <<EOF
${nested_git_dirs}
EOF
  exit 1
fi

manifest_report="$(python3 - "${MANIFEST}" <<'PY'
import json
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
data = json.loads(manifest.read_text())
allowed = {"main", "independent", "embedded", "archive"}
if data.get("policy", {}).get("code_source_of_truth") != "git":
    raise SystemExit("policy.code_source_of_truth must be 'git'")
if not data.get("policy", {}).get("no_nested_repos"):
    raise SystemExit("policy.no_nested_repos must be true")
if data.get("policy", {}).get("autonomy_rollout_stage") != "wave2_audited_execution":
    raise SystemExit("policy.autonomy_rollout_stage must be 'wave2_audited_execution'")

repos = data.get("repositories", [])
repo_ids = {repo["id"] for repo in repos}
if sum(1 for repo in repos if repo.get("classification") == "main") != 1:
    raise SystemExit("exactly one repository must be classified as main")

for repo in repos:
    if repo.get("classification") not in {"main", "independent"}:
        raise SystemExit(f"repository {repo.get('id')} has invalid classification")
    primary_remote = repo.get("primary_remote")
    autonomy = repo.get("autonomy")
    if not isinstance(primary_remote, dict):
        raise SystemExit(f"repository {repo.get('id')} is missing primary_remote metadata")
    if not isinstance(autonomy, dict):
        raise SystemExit(f"repository {repo.get('id')} is missing autonomy metadata")
    if primary_remote.get("provider") != "github":
        raise SystemExit(f"repository {repo.get('id')} must use provider github in phase 10")
    if primary_remote.get("protocol") not in {"ssh", "https"}:
        raise SystemExit(f"repository {repo.get('id')} has unsupported protocol")
    for field in ("namespace", "repo_name", "credential_ref"):
        if not str(primary_remote.get(field) or "").strip():
            raise SystemExit(f"repository {repo.get('id')} is missing primary_remote.{field}")
    if not isinstance(primary_remote.get("create_if_missing"), bool):
        raise SystemExit(f"repository {repo.get('id')} must declare primary_remote.create_if_missing")
    allowed_modes = autonomy.get("allowed_modes")
    if not isinstance(allowed_modes, list) or "dry_run" not in allowed_modes or "provision" not in allowed_modes:
        raise SystemExit(f"repository {repo.get('id')} must allow dry_run and provision autonomy modes")
    if autonomy.get("preflight_only") is not False:
        raise SystemExit(f"repository {repo.get('id')} must clear preflight_only in wave 2")
    if autonomy.get("wave") != 2:
        raise SystemExit(f"repository {repo.get('id')} must declare autonomy.wave = 2")
    if not str(autonomy.get("scope") or "").strip():
        raise SystemExit(f"repository {repo.get('id')} is missing autonomy.scope")
    print(
        "REPO|{id}|{cls}|{env}|{mirror}".format(
            id=repo["id"],
            cls=repo["classification"],
            env=repo.get("primary_remote_env", ""),
            mirror=repo.get("mirror_remote_env", ""),
        )
    )
    print(
        "PROVISIONING|{id}|{provider}|{namespace}|{repo_name}|{credential_ref}|{create_if_missing}|{modes}".format(
            id=repo["id"],
            provider=primary_remote.get("provider", ""),
            namespace=primary_remote.get("namespace", ""),
            repo_name=primary_remote.get("repo_name", ""),
            credential_ref=primary_remote.get("credential_ref", ""),
            create_if_missing=str(primary_remote.get("create_if_missing", False)).lower(),
            modes=",".join(str(item).strip() for item in allowed_modes if str(item).strip()),
        )
    )

for surface in data.get("surfaces", []):
    if surface.get("classification") not in allowed:
      raise SystemExit(f"surface {surface.get('id')} has invalid classification")
    repo_id = surface.get("repository_id")
    if repo_id and repo_id not in repo_ids:
      raise SystemExit(f"surface {surface.get('id')} references unknown repository {repo_id}")

print("SUMMARY|{repo_count}|{surface_count}".format(
    repo_count=len(repos),
    surface_count=len(data.get("surfaces", [])),
))
PY
)"

checked=0
skipped=0

while IFS= read -r line; do
  case "${line}" in
    REPO\|*)
      IFS='|' read -r _ repo_id classification env_name mirror_env_name <<< "${line}"
      remote_url=""
      mirror_url=""
      if [ -n "${env_name}" ]; then
        remote_url="${!env_name:-}"
      fi
      if [ -n "${mirror_env_name}" ]; then
        mirror_url="${!mirror_env_name:-}"
      fi

      if [ -n "${remote_url}" ]; then
        if git ls-remote "${remote_url}" HEAD >/dev/null 2>&1; then
          echo "primary_remote_ok=${repo_id}"
          checked=$((checked + 1))
        elif [ "${STRICT}" = "1" ]; then
          echo "primary_remote_failed=${repo_id}" >&2
          exit 1
        else
          echo "WARN primary_remote_unreachable=${repo_id}" >&2
          skipped=$((skipped + 1))
        fi
      elif [ "${STRICT}" = "1" ]; then
        echo "primary_remote_missing=${repo_id} (${env_name})" >&2
        exit 1
      else
        echo "WARN primary_remote_not_configured=${repo_id} (${env_name})" >&2
        skipped=$((skipped + 1))
      fi

      if [ -n "${mirror_url}" ]; then
        if git ls-remote "${mirror_url}" HEAD >/dev/null 2>&1; then
          echo "mirror_remote_ok=${repo_id}"
          checked=$((checked + 1))
        elif [ "${STRICT}" = "1" ]; then
          echo "mirror_remote_failed=${repo_id}" >&2
          exit 1
        else
          echo "WARN mirror_remote_unreachable=${repo_id}" >&2
          skipped=$((skipped + 1))
        fi
      fi
      ;;
    SUMMARY\|*)
      IFS='|' read -r _ repo_count surface_count <<< "${line}"
      echo "topology_repositories=${repo_count}"
      echo "topology_surfaces=${surface_count}"
      ;;
    PROVISIONING\|*)
      IFS='|' read -r _ repo_id provider namespace repo_name credential_ref create_if_missing modes <<< "${line}"
      echo "provisioning_contract_ok=${repo_id} provider=${provider} namespace=${namespace} repo_name=${repo_name} credential_ref=${credential_ref} create_if_missing=${create_if_missing} modes=${modes}"
      ;;
  esac
done <<< "${manifest_report}"

echo "git_governance=ok checked=${checked} skipped=${skipped}"

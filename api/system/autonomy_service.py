"""Autonomy policy and governed-remote provisioning preflight helpers."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import HTTPException


VALID_AUTONOMY_MODES = frozenset({"off", "dry_run", "provision"})
VALID_REMOTE_PROVIDERS = frozenset({"github"})
VALID_REMOTE_PROTOCOLS = frozenset({"ssh", "https"})
VALID_REPOSITORY_CLASSIFICATIONS = frozenset({"main", "independent"})
WAVE_1_ONLY_MODE = "dry_run"


@dataclass(frozen=True)
class SettingDefault:
    value: str
    description: str


AUTONOMY_SETTING_DEFAULTS: dict[str, SettingDefault] = {
    "AUTONOMY_ENABLED": SettingDefault("0", "Soft kill switch for all autonomous actions"),
    "AUTONOMY_MODE": SettingDefault("dry_run", "Autonomy mode (off|dry_run|provision)"),
    "AUTONOMY_REPO_PROVISIONING_ENABLED": SettingDefault(
        "0",
        "Allow topology-driven repo provisioning preflight and later live execution",
    ),
    "AUTONOMY_ALLOWED_REPOSITORY_IDS": SettingDefault(
        "",
        "Comma-separated repository ids allowed for autonomous repo provisioning",
    ),
    "AUTONOMY_REQUIRE_STRICT_VALIDATION": SettingDefault(
        "1",
        "Require strict validation before autonomy escalates beyond preflight",
    ),
    "AUTONOMY_ALLOW_DESTRUCTIVE_ACTIONS": SettingDefault(
        "0",
        "Allow destructive autonomy actions such as remote deletion",
    ),
    "AUTONOMY_AUDIT_READY": SettingDefault(
        "0",
        "Durable audit plumbing readiness gate for live autonomy writes",
    ),
}


def _project_root_default() -> Path:
    return Path(__file__).resolve().parents[2]


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None) -> list[str]:
    seen: set[str] = set()
    items: list[str] = []
    for raw in str(value or "").split(","):
        item = raw.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        items.append(item)
    return items


def _topology_path(project_root: Path) -> Path:
    return project_root / "ops" / "repository-topology.json"


def load_topology(project_root: Path) -> dict[str, Any]:
    path = _topology_path(project_root)
    return json.loads(path.read_text())


def _validate_repo_contract(repo: dict[str, Any]) -> None:
    repo_id = str(repo.get("id") or "").strip()
    classification = str(repo.get("classification") or "").strip().lower()
    if not repo_id:
        raise ValueError("repository id is required")
    if classification not in VALID_REPOSITORY_CLASSIFICATIONS:
        raise ValueError(f"repository {repo_id} must be main or independent")

    primary_remote = repo.get("primary_remote")
    if not isinstance(primary_remote, dict):
        raise ValueError(f"repository {repo_id} is missing primary_remote metadata")

    provider = str(primary_remote.get("provider") or "").strip().lower()
    if provider not in VALID_REMOTE_PROVIDERS:
        raise ValueError(f"repository {repo_id} has unsupported provider {provider or '<empty>'}")

    protocol = str(primary_remote.get("protocol") or "").strip().lower()
    if protocol not in VALID_REMOTE_PROTOCOLS:
        raise ValueError(f"repository {repo_id} has unsupported protocol {protocol or '<empty>'}")

    for field in ("namespace", "repo_name", "credential_ref"):
        if not str(primary_remote.get(field) or "").strip():
            raise ValueError(f"repository {repo_id} is missing primary_remote.{field}")

    if not isinstance(primary_remote.get("create_if_missing"), bool):
        raise ValueError(f"repository {repo_id} must declare primary_remote.create_if_missing")

    autonomy = repo.get("autonomy")
    if not isinstance(autonomy, dict):
        raise ValueError(f"repository {repo_id} is missing autonomy metadata")

    if not str(autonomy.get("scope") or "").strip():
        raise ValueError(f"repository {repo_id} is missing autonomy.scope")

    allowed_modes_raw = autonomy.get("allowed_modes")
    if not isinstance(allowed_modes_raw, list) or not allowed_modes_raw:
        raise ValueError(f"repository {repo_id} must declare autonomy.allowed_modes")

    allowed_modes = {str(item).strip().lower() for item in allowed_modes_raw if str(item).strip()}
    if not allowed_modes:
        raise ValueError(f"repository {repo_id} has no valid autonomy.allowed_modes")
    if not allowed_modes <= {"dry_run", "provision"}:
        raise ValueError(f"repository {repo_id} has unsupported autonomy mode(s)")
    if WAVE_1_ONLY_MODE not in allowed_modes:
        raise ValueError(f"repository {repo_id} must allow dry_run in Wave 1")

    if not isinstance(autonomy.get("preflight_only"), bool):
        raise ValueError(f"repository {repo_id} must declare autonomy.preflight_only")
    if not isinstance(autonomy.get("wave"), int):
        raise ValueError(f"repository {repo_id} must declare autonomy.wave as an integer")

    if not str(repo.get("primary_remote_env") or "").strip():
        raise ValueError(f"repository {repo_id} is missing primary_remote_env")


def derive_expected_primary_remote(repo: dict[str, Any]) -> str:
    primary_remote = repo["primary_remote"]
    provider = str(primary_remote["provider"]).strip().lower()
    protocol = str(primary_remote["protocol"]).strip().lower()
    namespace = str(primary_remote["namespace"]).strip()
    repo_name = str(primary_remote["repo_name"]).strip()

    if provider == "github":
        if protocol == "ssh":
            return f"git@github.com:{namespace}/{repo_name}.git"
        return f"https://github.com/{namespace}/{repo_name}.git"

    raise ValueError(f"Unsupported provider/protocol combination: {provider}/{protocol}")


def load_repository_contracts(project_root: Path) -> list[dict[str, Any]]:
    data = load_topology(project_root)
    repositories = data.get("repositories", [])
    if not isinstance(repositories, list):
        raise ValueError("topology repositories must be a list")

    normalized: list[dict[str, Any]] = []
    for repo in repositories:
        if not isinstance(repo, dict):
            raise ValueError("repository entries must be objects")
        _validate_repo_contract(repo)
        normalized.append(repo)
    return normalized


def _local_origin_url(repo_path: Path) -> str:
    if not (repo_path / ".git").exists():
        return ""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _bootstrap_command(project_root: Path, repo: dict[str, Any], effective_remote: str) -> str:
    command = [
        "bash",
        str(project_root / "scripts" / "bootstrap_primary_remote.sh"),
        "--repo-path",
        str(repo["local_path"]),
    ]
    primary_remote_env = str(repo.get("primary_remote_env") or "").strip()
    mirror_remote_env = str(repo.get("mirror_remote_env") or "").strip()
    if primary_remote_env and os.getenv(primary_remote_env, "").strip():
        command.extend(["--primary-remote-env", primary_remote_env])
    else:
        command.extend(["--primary-remote", effective_remote])
    if mirror_remote_env:
        command.extend(["--mirror-remote-env", mirror_remote_env])
    return shlex.join(command)


def build_autonomy_policy_payload(db_client, project_root: Path) -> dict[str, Any]:
    raw_settings = {key: item.value for key, item in AUTONOMY_SETTING_DEFAULTS.items()}
    for row in db_client.fetch_all(
        "SELECT key, value FROM settings WHERE key LIKE 'AUTONOMY_%' ORDER BY key"
    ):
        key = str(row.get("key") or "").strip()
        if key in raw_settings:
            raw_settings[key] = str(row.get("value") or "")

    mode = str(raw_settings["AUTONOMY_MODE"]).strip().lower() or "off"
    invalid_settings: list[str] = []
    if mode not in VALID_AUTONOMY_MODES:
        invalid_settings.append("AUTONOMY_MODE")
        mode = "off"

    enabled = _parse_bool(raw_settings["AUTONOMY_ENABLED"])
    repo_provisioning_enabled = _parse_bool(raw_settings["AUTONOMY_REPO_PROVISIONING_ENABLED"])
    require_strict_validation = _parse_bool(raw_settings["AUTONOMY_REQUIRE_STRICT_VALIDATION"], default=True)
    allow_destructive_actions = _parse_bool(raw_settings["AUTONOMY_ALLOW_DESTRUCTIVE_ACTIONS"])
    audit_ready = _parse_bool(raw_settings["AUTONOMY_AUDIT_READY"])
    allowed_repository_ids = _parse_csv(raw_settings["AUTONOMY_ALLOWED_REPOSITORY_IDS"])
    known_repository_ids = [repo["id"] for repo in load_repository_contracts(project_root)]
    unknown_repository_ids = [repo_id for repo_id in allowed_repository_ids if repo_id not in known_repository_ids]

    preflight_block_reasons: list[str] = []
    if not enabled:
        preflight_block_reasons.append("autonomy_disabled")
    if mode == "off":
        preflight_block_reasons.append("autonomy_mode_off")
    if not repo_provisioning_enabled:
        preflight_block_reasons.append("repo_provisioning_disabled")
    if not allowed_repository_ids:
        preflight_block_reasons.append("allowed_repository_scope_empty")
    if unknown_repository_ids:
        preflight_block_reasons.append("allowed_repository_scope_invalid")
    if invalid_settings:
        preflight_block_reasons.extend(f"invalid_setting:{item}" for item in invalid_settings)

    live_block_reasons = ["wave1_preflight_only"]
    if mode == "provision" and not audit_ready:
        live_block_reasons.append("audit_not_ready")

    return {
        "enabled": enabled,
        "mode": mode,
        "repo_provisioning_enabled": repo_provisioning_enabled,
        "allowed_repository_ids": allowed_repository_ids,
        "unknown_repository_ids": unknown_repository_ids,
        "require_strict_validation": require_strict_validation,
        "allow_destructive_actions": allow_destructive_actions,
        "audit_ready": audit_ready,
        "kill_switch_active": (not enabled) or mode == "off",
        "preflight_allowed": not preflight_block_reasons,
        "preflight_block_reasons": preflight_block_reasons,
        "live_provisioning_allowed": False,
        "live_block_reasons": live_block_reasons,
        "wave": 1,
        "settings": raw_settings,
        "known_repository_ids": known_repository_ids,
    }


def enforce_provisioning_policy(
    *,
    db_client,
    project_root: Path,
    repo_ids: list[str],
    requested_mode: str,
) -> dict[str, Any]:
    policy = build_autonomy_policy_payload(db_client=db_client, project_root=project_root)
    if requested_mode != WAVE_1_ONLY_MODE:
        raise HTTPException(
            status_code=409,
            detail="Wave 1 provisioning remains dry_run preflight only until durable audit plumbing lands in Plan 10-02.",
        )

    if policy["preflight_block_reasons"]:
        raise HTTPException(
            status_code=403,
            detail="Autonomy repo provisioning blocked: " + ", ".join(policy["preflight_block_reasons"]),
        )

    scope = policy["allowed_repository_ids"]
    requested = repo_ids or scope
    disallowed = [repo_id for repo_id in requested if repo_id not in scope]
    if disallowed:
        raise HTTPException(
            status_code=403,
            detail="Autonomy repo provisioning blocked for repository scope: " + ", ".join(disallowed),
        )

    return policy


def build_provisioning_preflight_payload(
    *,
    project_root: Path,
    repo_ids: list[str] | None = None,
    requested_mode: str = WAVE_1_ONLY_MODE,
) -> dict[str, Any]:
    normalized_repo_ids = [item.strip() for item in repo_ids or [] if str(item).strip()]
    if requested_mode != WAVE_1_ONLY_MODE:
        raise ValueError(
            "Wave 1 provisioning remains dry_run preflight only until durable audit plumbing lands in Plan 10-02."
        )

    contracts = load_repository_contracts(project_root)
    repo_map = {repo["id"]: repo for repo in contracts}
    selected_ids = normalized_repo_ids or [repo["id"] for repo in contracts]
    unknown_ids = [repo_id for repo_id in selected_ids if repo_id not in repo_map]
    if unknown_ids:
        raise HTTPException(status_code=404, detail="Unknown repository id(s): " + ", ".join(unknown_ids))

    repositories: list[dict[str, Any]] = []
    for repo_id in selected_ids:
        repo = repo_map[repo_id]
        expected_remote = derive_expected_primary_remote(repo)
        primary_remote_env = str(repo["primary_remote_env"]).strip()
        configured_remote = os.getenv(primary_remote_env, "").strip()
        effective_remote = configured_remote or expected_remote
        credential_ref = str(repo["primary_remote"]["credential_ref"]).strip()
        credential_present = bool(os.getenv(credential_ref, "").strip())
        local_origin = _local_origin_url(Path(str(repo["local_path"])))
        if local_origin == effective_remote:
            origin_status = "origin_matches_expected_remote"
        elif local_origin:
            origin_status = "origin_mismatch"
        else:
            origin_status = "origin_missing"

        planned_actions: list[str] = []
        if configured_remote:
            planned_actions.append("use_primary_remote_env_override")
        else:
            planned_actions.append("derive_primary_remote_from_manifest")
        if bool(repo["primary_remote"]["create_if_missing"]):
            planned_actions.append("preflight_provider_create_if_missing")
        if origin_status == "origin_missing":
            planned_actions.append("bootstrap_origin_remote")
        elif origin_status == "origin_mismatch":
            planned_actions.append("repoint_origin_to_expected_remote")
        else:
            planned_actions.append("origin_already_matches_expected_remote")
        if str(repo.get("mirror_remote_env") or "").strip():
            planned_actions.append("preserve_mirror_remote_contract")

        validation_errors: list[str] = []
        if bool(repo["primary_remote"]["create_if_missing"]) and not credential_present:
            validation_errors.append("missing_provider_credential")

        repositories.append(
            {
                "repo_id": repo["id"],
                "classification": repo["classification"],
                "provider": repo["primary_remote"]["provider"],
                "namespace": repo["primary_remote"]["namespace"],
                "repo_name": repo["primary_remote"]["repo_name"],
                "credential_ref": credential_ref,
                "credential_present": credential_present,
                "create_if_missing": repo["primary_remote"]["create_if_missing"],
                "autonomy_scope": repo["autonomy"]["scope"],
                "allowed_modes": repo["autonomy"]["allowed_modes"],
                "preflight_only": repo["autonomy"]["preflight_only"],
                "local_path": repo["local_path"],
                "primary_remote_env": primary_remote_env,
                "configured_primary_remote": configured_remote,
                "expected_primary_remote": expected_remote,
                "effective_primary_remote": effective_remote,
                "local_origin_remote": local_origin,
                "origin_status": origin_status,
                "bootstrap_command": _bootstrap_command(project_root, repo, effective_remote),
                "planned_actions": planned_actions,
                "validation_errors": validation_errors,
                "status": "preflight_ready" if not validation_errors else "blocked",
                "dry_run": True,
                "live_writes_blocked": True,
                "wave": 1,
            }
        )

    return {
        "status": "ok",
        "requested_mode": requested_mode,
        "dry_run": True,
        "preflight_only": True,
        "live_writes_blocked": True,
        "repository_count": len(repositories),
        "repositories": repositories,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight governed remote provisioning from topology.")
    parser.add_argument("--project-root", default=str(_project_root_default()))
    parser.add_argument("--repo-id", dest="repo_ids", action="append", default=[])
    parser.add_argument("--all", action="store_true", help="Preflight all governed repositories")
    parser.add_argument("--mode", default=WAVE_1_ONLY_MODE, choices=["dry_run", "provision"])
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser.parse_args(argv)


def _format_cli_report(payload: dict[str, Any]) -> str:
    lines = [
        f"provisioning_status={payload['status']}",
        f"requested_mode={payload['requested_mode']}",
        f"dry_run={str(payload['dry_run']).lower()}",
        f"preflight_only={str(payload['preflight_only']).lower()}",
        f"repository_count={payload['repository_count']}",
    ]
    for repo in payload["repositories"]:
        lines.extend(
            [
                f"repo_id={repo['repo_id']} status={repo['status']} origin_status={repo['origin_status']}",
                f"  effective_primary_remote={repo['effective_primary_remote']}",
                f"  credential_ref={repo['credential_ref']} present={str(repo['credential_present']).lower()}",
                f"  bootstrap_command={repo['bootstrap_command']}",
                f"  planned_actions={','.join(repo['planned_actions'])}",
            ]
        )
        if repo["validation_errors"]:
            lines.append(f"  validation_errors={','.join(repo['validation_errors'])}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    project_root = Path(args.project_root).resolve()
    repo_ids = [] if args.all else list(args.repo_ids)
    try:
        payload = build_provisioning_preflight_payload(
            project_root=project_root,
            repo_ids=repo_ids,
            requested_mode=args.mode,
        )
    except HTTPException as exc:
        print(str(exc.detail), file=sys.stderr)
        return int(exc.status_code)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.json_output:
        print(json.dumps(payload, indent=2))
    else:
        print(_format_cli_report(payload))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())

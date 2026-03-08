"""Autonomy policy, executor, audit, and governed-remote helpers."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from api.security.admin_auth import CONTROL_AUTHORITY_AGENTS


VALID_AUTONOMY_MODES = frozenset({"off", "dry_run", "provision"})
VALID_REMOTE_PROVIDERS = frozenset({"github"})
VALID_REMOTE_PROTOCOLS = frozenset({"ssh", "https"})
VALID_REPOSITORY_CLASSIFICATIONS = frozenset({"main", "independent"})
DEFAULT_AUTONOMY_MODE = "dry_run"
WAVE_1_ONLY_MODE = DEFAULT_AUTONOMY_MODE
LIVE_AUTONOMY_MODE = "provision"
AUTONOMY_ROLLOUT_STAGE = "wave2_audited_execution"
AUTONOMY_SERVICE_UNIT = "ai-enterprise-autonomy.service"
AUTONOMY_TIMER_UNIT = "ai-enterprise-autonomy.timer"
AUTONOMY_API_SERVICE_UNIT = "ai-enterprise-api.service"


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
    "AUTONOMY_EXECUTOR_ENABLED": SettingDefault(
        "0",
        "Allow the always-on autonomy executor to trigger IAn or Engineer runs",
    ),
    "AUTONOMY_EXECUTOR_ALLOWED_AGENTS": SettingDefault(
        "ian-master,engineer",
        "Comma-separated agent ids allowed to run on the autonomy executor host",
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


def _normalize_actor_agent_id(actor_agent_id: str | None) -> str:
    normalized = str(actor_agent_id or "").strip().lower()
    if not normalized:
        return "ian-master"
    if normalized in {"ian", "father"}:
        return "ian-master"
    return normalized


def _topology_path(project_root: Path) -> Path:
    return project_root / "ops" / "repository-topology.json"


def _safe_json_loads(raw: str | None, *, default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default


def _truncate_output(value: str | None, *, limit: int = 3000) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def load_topology(project_root: Path) -> dict[str, Any]:
    path = _topology_path(project_root)
    return json.loads(path.read_text())


def _rollout_stage(project_root: Path) -> str:
    return str(load_topology(project_root).get("policy", {}).get("autonomy_rollout_stage") or "").strip()


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
    if DEFAULT_AUTONOMY_MODE not in allowed_modes:
        raise ValueError(f"repository {repo_id} must allow dry_run in autonomy.allowed_modes")

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


def _current_head_sha(repo_path: Path) -> str:
    if not (repo_path / ".git").exists():
        return ""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _current_branch(repo_path: Path) -> str:
    if not (repo_path / ".git").exists():
        return ""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _bootstrap_command_parts(project_root: Path, repo: dict[str, Any], effective_remote: str) -> list[str]:
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
    return command


def _bootstrap_command(project_root: Path, repo: dict[str, Any], effective_remote: str) -> str:
    return shlex.join(_bootstrap_command_parts(project_root, repo, effective_remote))


def _validation_command_parts(project_root: Path) -> list[str]:
    configured = str(os.getenv("AUTONOMY_VALIDATION_COMMAND") or "").strip()
    if configured:
        parts = shlex.split(configured)
        if parts:
            return parts
    return ["bash", str(project_root / "scripts" / "validate_git_governance.sh")]


def _provider_validation_errors(repo: dict[str, Any], *, credential_present: bool) -> list[str]:
    validation_errors: list[str] = []
    if bool(repo["primary_remote"]["create_if_missing"]) and not credential_present:
        validation_errors.append("missing_provider_credential")
    return validation_errors


def _load_autonomy_settings(db_client) -> dict[str, str]:
    raw_settings = {key: item.value for key, item in AUTONOMY_SETTING_DEFAULTS.items()}
    for row in db_client.fetch_all(
        "SELECT key, value FROM settings WHERE key LIKE 'AUTONOMY_%' ORDER BY key"
    ):
        key = str(row.get("key") or "").strip()
        if key in raw_settings:
            raw_settings[key] = str(row.get("value") or "")
    return raw_settings


def build_autonomy_policy_payload(db_client, project_root: Path) -> dict[str, Any]:
    raw_settings = _load_autonomy_settings(db_client)

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
    executor_enabled = _parse_bool(raw_settings["AUTONOMY_EXECUTOR_ENABLED"])
    allowed_repository_ids = _parse_csv(raw_settings["AUTONOMY_ALLOWED_REPOSITORY_IDS"])
    executor_allowed_agent_ids = [_normalize_actor_agent_id(item) for item in _parse_csv(raw_settings["AUTONOMY_EXECUTOR_ALLOWED_AGENTS"])]

    known_repository_ids = [repo["id"] for repo in load_repository_contracts(project_root)]
    unknown_repository_ids = [repo_id for repo_id in allowed_repository_ids if repo_id not in known_repository_ids]
    unknown_executor_agent_ids = [
        agent_id for agent_id in executor_allowed_agent_ids if agent_id not in CONTROL_AUTHORITY_AGENTS
    ]

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

    live_block_reasons: list[str] = []
    if mode != LIVE_AUTONOMY_MODE:
        live_block_reasons.append("autonomy_mode_not_provision")
    if not audit_ready:
        live_block_reasons.append("audit_not_ready")
    if not executor_enabled:
        live_block_reasons.append("executor_disabled")
    if not executor_allowed_agent_ids:
        live_block_reasons.append("executor_agent_scope_empty")
    if unknown_executor_agent_ids:
        live_block_reasons.append("executor_agent_scope_invalid")

    repo_waves = [int(repo["autonomy"]["wave"]) for repo in load_repository_contracts(project_root)]
    return {
        "enabled": enabled,
        "mode": mode,
        "repo_provisioning_enabled": repo_provisioning_enabled,
        "allowed_repository_ids": allowed_repository_ids,
        "unknown_repository_ids": unknown_repository_ids,
        "require_strict_validation": require_strict_validation,
        "allow_destructive_actions": allow_destructive_actions,
        "audit_ready": audit_ready,
        "executor_enabled": executor_enabled,
        "executor_allowed_agent_ids": executor_allowed_agent_ids,
        "executor_unknown_agent_ids": unknown_executor_agent_ids,
        "kill_switch_active": (not enabled) or mode == "off",
        "preflight_allowed": not preflight_block_reasons,
        "preflight_block_reasons": preflight_block_reasons,
        "live_provisioning_allowed": not preflight_block_reasons and not live_block_reasons,
        "live_block_reasons": live_block_reasons,
        "wave": max(repo_waves) if repo_waves else 0,
        "rollout_stage": _rollout_stage(project_root),
        "settings": raw_settings,
        "known_repository_ids": known_repository_ids,
    }


def build_executor_contract_payload(*, db_client, project_root: Path, settings) -> dict[str, Any]:
    policy = build_autonomy_policy_payload(db_client=db_client, project_root=project_root)
    hard_kill_switch_path = Path(str(settings.autonomy_host_kill_switch_file))
    hard_kill_switch_active = bool(settings.autonomy_hard_disable) or hard_kill_switch_path.exists()
    return {
        "host_id": str(settings.autonomy_executor_host_id),
        "tailnet_tag": str(settings.autonomy_executor_tag),
        "state_root": str(settings.autonomy_state_root),
        "api_url": str(settings.autonomy_api_url),
        "service_unit": AUTONOMY_SERVICE_UNIT,
        "timer_unit": AUTONOMY_TIMER_UNIT,
        "api_service_unit": AUTONOMY_API_SERVICE_UNIT,
        "runner_script": str(project_root / "scripts" / "run_autonomy_executor.sh"),
        "docs_path": str(project_root / "docs" / "autonomy-executor-host.md"),
        "hard_kill_switch_path": str(hard_kill_switch_path),
        "hard_kill_switch_active": hard_kill_switch_active,
        "allowed_actor_ids": policy["executor_allowed_agent_ids"],
        "default_trigger_source": "systemd_timer",
        "event_trigger_source": "manual_api",
    }


def sync_autonomy_topology_state(db_client, project_root: Path) -> dict[str, Any]:
    topology = load_topology(project_root)
    rollout_stage = str(topology.get("policy", {}).get("autonomy_rollout_stage") or "").strip()
    synced = 0
    for repo in load_repository_contracts(project_root):
        expected_remote = derive_expected_primary_remote(repo)
        primary_remote_env = str(repo["primary_remote_env"]).strip()
        configured_remote = os.getenv(primary_remote_env, "").strip()
        effective_remote = configured_remote or expected_remote
        db_client.execute(
            "INSERT INTO autonomy_repo_sync "
            "(repo_id, classification, local_path, expected_primary_remote, effective_primary_remote, autonomy_scope, "
            "allowed_modes_json, preflight_only, wave, manifest_stage, manifest_sync_status, last_status, "
            "last_validation_status, quarantine_status, last_synced_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'synchronized', 'never_run', 'pending', 'clear', datetime('now'), datetime('now')) "
            "ON CONFLICT(repo_id) DO UPDATE SET "
            "classification=excluded.classification, local_path=excluded.local_path, "
            "expected_primary_remote=excluded.expected_primary_remote, "
            "effective_primary_remote=excluded.effective_primary_remote, autonomy_scope=excluded.autonomy_scope, "
            "allowed_modes_json=excluded.allowed_modes_json, preflight_only=excluded.preflight_only, "
            "wave=excluded.wave, manifest_stage=excluded.manifest_stage, manifest_sync_status='synchronized', "
            "last_synced_at=datetime('now'), updated_at=datetime('now')",
            (
                repo["id"],
                repo["classification"],
                str(repo["local_path"]),
                expected_remote,
                effective_remote,
                str(repo["autonomy"]["scope"]),
                json.dumps(repo["autonomy"]["allowed_modes"]),
                1 if bool(repo["autonomy"]["preflight_only"]) else 0,
                int(repo["autonomy"]["wave"]),
                rollout_stage,
            ),
        )
        synced += 1
    return {"synced": synced, "rollout_stage": rollout_stage}


def _select_repository_scope(policy: dict[str, Any], repo_ids: list[str]) -> list[str]:
    scope = list(policy["allowed_repository_ids"])
    requested = [item.strip() for item in repo_ids or [] if str(item).strip()]
    selected = requested or scope
    disallowed = [repo_id for repo_id in selected if repo_id not in scope]
    if disallowed:
        raise HTTPException(
            status_code=403,
            detail="Autonomy repo provisioning blocked for repository scope: " + ", ".join(disallowed),
        )
    return selected


def enforce_provisioning_policy(
    *,
    db_client,
    project_root: Path,
    repo_ids: list[str],
    requested_mode: str,
) -> dict[str, Any]:
    policy = build_autonomy_policy_payload(db_client=db_client, project_root=project_root)
    if requested_mode != DEFAULT_AUTONOMY_MODE:
        raise HTTPException(
            status_code=409,
            detail="Preflight only supports dry_run. Use /api/autonomy/executor/run for provision mode.",
        )
    if policy["preflight_block_reasons"]:
        raise HTTPException(
            status_code=403,
            detail="Autonomy repo provisioning blocked: " + ", ".join(policy["preflight_block_reasons"]),
        )
    _select_repository_scope(policy, repo_ids)
    return policy


def build_provisioning_preflight_payload(
    *,
    project_root: Path,
    repo_ids: list[str] | None = None,
    requested_mode: str = DEFAULT_AUTONOMY_MODE,
) -> dict[str, Any]:
    normalized_repo_ids = [item.strip() for item in repo_ids or [] if str(item).strip()]
    if requested_mode != DEFAULT_AUTONOMY_MODE:
        raise ValueError("Preflight only supports dry_run. Use the executor run route for provision mode.")

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
        planned_actions.extend(["topology_sync", "audit_run", "provenance_sync"])
        if str(repo.get("mirror_remote_env") or "").strip():
            planned_actions.append("preserve_mirror_remote_contract")

        validation_errors = _provider_validation_errors(repo, credential_present=credential_present)

        repositories.append(
            {
                "repo_id": repo["id"],
                "classification": repo["classification"],
                "provider": repo["primary_remote"]["provider"],
                "namespace": repo["primary_remote"]["namespace"],
                "repo_name": repo["primary_remote"]["repo_name"],
                "credential_ref": credential_ref,
                "credential_present": credential_present,
                "credential_class": "service_env",
                "create_if_missing": repo["primary_remote"]["create_if_missing"],
                "autonomy_scope": repo["autonomy"]["scope"],
                "allowed_modes": repo["autonomy"]["allowed_modes"],
                "preflight_only": repo["autonomy"]["preflight_only"],
                "live_execution_supported": (LIVE_AUTONOMY_MODE in repo["autonomy"]["allowed_modes"])
                and not bool(repo["autonomy"]["preflight_only"]),
                "local_path": repo["local_path"],
                "primary_remote_env": primary_remote_env,
                "mirror_remote_env": str(repo.get("mirror_remote_env") or "").strip(),
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
                "wave": int(repo["autonomy"]["wave"]),
            }
        )

    return {
        "status": "ok",
        "requested_mode": requested_mode,
        "dry_run": True,
        "preflight_only": True,
        "live_writes_blocked": True,
        "rollout_stage": _rollout_stage(project_root),
        "repository_count": len(repositories),
        "repositories": repositories,
    }


def _restore_origin(repo_path: Path, previous_origin: str) -> bool:
    current_origin = _local_origin_url(repo_path)
    if previous_origin:
        if current_origin:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "remote", "set-url", "origin", previous_origin],
                capture_output=True,
                text=True,
                check=False,
            )
        else:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "remote", "add", "origin", previous_origin],
                capture_output=True,
                text=True,
                check=False,
            )
        return result.returncode == 0

    if not current_origin:
        return True
    result = subprocess.run(
        ["git", "-C", str(repo_path), "remote", "remove", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _insert_autonomy_run(
    db_client,
    *,
    run_id: str,
    trigger_source: str,
    actor_agent_id: str,
    requested_mode: str,
    credential_class: str,
    host_id: str,
    repo_ids: list[str],
) -> None:
    db_client.execute(
        "INSERT INTO autonomy_runs "
        "(id, trigger_source, actor_agent_id, requested_mode, credential_class, host_id, repo_ids_json, "
        "status, validation_status, quarantine_status, bootstrap_report_json, started_at, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 'running', 'pending', 'clear', '{}', datetime('now'), datetime('now'), datetime('now'))",
        (
            run_id,
            trigger_source,
            actor_agent_id,
            requested_mode,
            credential_class,
            host_id,
            json.dumps(repo_ids),
        ),
    )


def _update_autonomy_run(
    db_client,
    *,
    run_id: str,
    status: str,
    validation_status: str,
    commit_anchor: dict[str, str],
    rollback_anchor: dict[str, Any],
    quarantine_status: str,
    quarantine_reason: str,
    error_detail: str,
    bootstrap_report: dict[str, Any],
) -> None:
    db_client.execute(
        "UPDATE autonomy_runs SET "
        "status=?, validation_status=?, commit_anchor=?, rollback_anchor=?, quarantine_status=?, "
        "quarantine_reason=?, error_detail=?, bootstrap_report_json=?, completed_at=datetime('now'), updated_at=datetime('now') "
        "WHERE id = ?",
        (
            status,
            validation_status,
            json.dumps(commit_anchor, sort_keys=True),
            json.dumps(rollback_anchor, sort_keys=True),
            quarantine_status,
            quarantine_reason,
            error_detail,
            json.dumps(bootstrap_report, sort_keys=True),
            run_id,
        ),
    )


def _insert_autonomy_action(
    db_client,
    *,
    action_id: str,
    run_id: str,
    repo_id: str,
    action_type: str,
    planned_action: str,
    credential_ref: str,
    credential_class: str,
    requested_mode: str,
    rollback_anchor: dict[str, Any],
) -> None:
    db_client.execute(
        "INSERT INTO autonomy_actions "
        "(id, run_id, repo_id, action_type, planned_action, credential_ref, credential_class, requested_mode, "
        "status, validation_status, rollback_anchor, quarantine_status, detail_json, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'running', 'pending', ?, 'clear', '{}', datetime('now'), datetime('now'))",
        (
            action_id,
            run_id,
            repo_id,
            action_type,
            planned_action,
            credential_ref,
            credential_class,
            requested_mode,
            json.dumps(rollback_anchor, sort_keys=True),
        ),
    )


def _update_autonomy_action(
    db_client,
    *,
    action_id: str,
    status: str,
    validation_status: str,
    commit_anchor: str,
    rollback_anchor: dict[str, Any],
    quarantine_status: str,
    quarantine_reason: str,
    detail: dict[str, Any],
) -> None:
    db_client.execute(
        "UPDATE autonomy_actions SET "
        "status=?, validation_status=?, commit_anchor=?, rollback_anchor=?, quarantine_status=?, "
        "quarantine_reason=?, detail_json=?, updated_at=datetime('now') "
        "WHERE id = ?",
        (
            status,
            validation_status,
            commit_anchor,
            json.dumps(rollback_anchor, sort_keys=True),
            quarantine_status,
            quarantine_reason,
            json.dumps(detail, sort_keys=True),
            action_id,
        ),
    )


def _insert_provenance(
    db_client,
    *,
    repo_id: str,
    run_id: str,
    deploy_target: str,
    ref_name: str,
    commit_sha: str,
    rollback_anchor: dict[str, Any],
    validation_status: str,
    metadata: dict[str, Any],
) -> str:
    provenance_id = str(uuid.uuid4())
    db_client.execute(
        "INSERT INTO deployment_provenance "
        "(id, repo_id, autonomy_run_id, source, deploy_target, ref_name, commit_sha, rollback_anchor, "
        "validation_status, metadata_json, created_at) "
        "VALUES (?, ?, ?, 'autonomy', ?, ?, ?, ?, ?, ?, datetime('now'))",
        (
            provenance_id,
            repo_id,
            run_id,
            deploy_target,
            ref_name,
            commit_sha,
            json.dumps(rollback_anchor, sort_keys=True),
            validation_status,
            json.dumps(metadata, sort_keys=True),
        ),
    )
    return provenance_id


def _update_sync_state(
    db_client,
    *,
    repo_id: str,
    status: str,
    validation_status: str,
    commit_anchor: str,
    rollback_anchor: dict[str, Any],
    quarantine_status: str,
    quarantine_reason: str,
    provenance_id: str,
    run_id: str,
) -> None:
    db_client.execute(
        "UPDATE autonomy_repo_sync SET "
        "last_run_id=?, last_status=?, last_validation_status=?, last_commit_anchor=?, last_rollback_anchor=?, "
        "last_provenance_id=?, quarantine_status=?, quarantine_reason=?, last_synced_at=datetime('now'), updated_at=datetime('now') "
        "WHERE repo_id = ?",
        (
            run_id,
            status,
            validation_status,
            commit_anchor,
            json.dumps(rollback_anchor, sort_keys=True),
            provenance_id,
            quarantine_status,
            quarantine_reason,
            repo_id,
        ),
    )


def _executor_allowed(policy: dict[str, Any], actor_agent_id: str) -> bool:
    normalized = _normalize_actor_agent_id(actor_agent_id)
    return normalized in set(policy["executor_allowed_agent_ids"]) and normalized in CONTROL_AUTHORITY_AGENTS


def execute_autonomy_run(
    *,
    db_client,
    project_root: Path,
    settings,
    repo_ids: list[str],
    requested_mode: str,
    trigger_source: str,
    actor_agent_id: str,
) -> dict[str, Any]:
    normalized_mode = str(requested_mode or DEFAULT_AUTONOMY_MODE).strip().lower()
    if normalized_mode not in {DEFAULT_AUTONOMY_MODE, LIVE_AUTONOMY_MODE}:
        raise HTTPException(status_code=409, detail=f"Unsupported autonomy execution mode: {requested_mode}")

    policy = build_autonomy_policy_payload(db_client=db_client, project_root=project_root)
    executor = build_executor_contract_payload(db_client=db_client, project_root=project_root, settings=settings)
    actor = _normalize_actor_agent_id(actor_agent_id)
    if not _executor_allowed(policy, actor):
        raise HTTPException(status_code=403, detail=f"Autonomy executor blocked for actor: {actor}")
    if executor["hard_kill_switch_active"]:
        raise HTTPException(
            status_code=409,
            detail="Autonomy executor hard kill switch is active on the executor host.",
        )
    if normalized_mode == DEFAULT_AUTONOMY_MODE:
        if policy["preflight_block_reasons"]:
            raise HTTPException(
                status_code=403,
                detail="Autonomy executor blocked: " + ", ".join(policy["preflight_block_reasons"]),
            )
    else:
        if policy["preflight_block_reasons"]:
            raise HTTPException(
                status_code=403,
                detail="Autonomy executor blocked: " + ", ".join(policy["preflight_block_reasons"]),
            )
        if policy["live_block_reasons"]:
            raise HTTPException(
                status_code=409,
                detail="Autonomy live provisioning blocked: " + ", ".join(policy["live_block_reasons"]),
            )

    selected_repo_ids = _select_repository_scope(policy, repo_ids)
    sync_autonomy_topology_state(db_client=db_client, project_root=project_root)
    preflight = build_provisioning_preflight_payload(
        project_root=project_root,
        repo_ids=selected_repo_ids,
        requested_mode=DEFAULT_AUTONOMY_MODE,
    )

    run_id = str(uuid.uuid4())
    _insert_autonomy_run(
        db_client,
        run_id=run_id,
        trigger_source=str(trigger_source or "manual_api").strip() or "manual_api",
        actor_agent_id=actor,
        requested_mode=normalized_mode,
        credential_class="autonomy_service_key",
        host_id=executor["host_id"],
        repo_ids=selected_repo_ids,
    )

    repo_results: list[dict[str, Any]] = []
    commit_anchor_map: dict[str, str] = {}
    rollback_anchor_map: dict[str, Any] = {}

    for repo in preflight["repositories"]:
        repo_id = str(repo["repo_id"])
        repo_path = Path(str(repo["local_path"]))
        branch_name = _current_branch(repo_path)
        commit_anchor = _current_head_sha(repo_path)
        rollback_anchor = {
            "origin": str(repo.get("local_origin_remote") or ""),
            "commit": commit_anchor,
        }
        action_id = str(uuid.uuid4())
        _insert_autonomy_action(
            db_client,
            action_id=action_id,
            run_id=run_id,
            repo_id=repo_id,
            action_type="governed_remote_reconcile",
            planned_action=",".join(repo["planned_actions"]),
            credential_ref=str(repo["credential_ref"]),
            credential_class=str(repo["credential_class"]),
            requested_mode=normalized_mode,
            rollback_anchor=rollback_anchor,
        )

        result_detail = {
            "trigger_source": trigger_source,
            "actor_agent_id": actor,
            "planned_actions": repo["planned_actions"],
            "bootstrap_command": repo["bootstrap_command"],
            "origin_before": repo.get("local_origin_remote") or "",
        }
        provenance_id = ""
        rollback_applied = False
        post_origin = str(repo.get("local_origin_remote") or "")
        status = "dry_run"
        validation_status = "simulated"
        quarantine_status = "clear"
        quarantine_reason = ""

        if normalized_mode == DEFAULT_AUTONOMY_MODE:
            result_detail["validation_errors"] = list(repo["validation_errors"])
            _update_autonomy_action(
                db_client,
                action_id=action_id,
                status=status,
                validation_status=validation_status,
                commit_anchor=commit_anchor,
                rollback_anchor=rollback_anchor,
                quarantine_status=quarantine_status,
                quarantine_reason=quarantine_reason,
                detail=result_detail,
            )
            _update_sync_state(
                db_client,
                repo_id=repo_id,
                status=status,
                validation_status=validation_status,
                commit_anchor=commit_anchor,
                rollback_anchor=rollback_anchor,
                quarantine_status=quarantine_status,
                quarantine_reason=quarantine_reason,
                provenance_id=provenance_id,
                run_id=run_id,
            )
        elif repo["validation_errors"]:
            status = "blocked"
            validation_status = "blocked"
            result_detail["validation_errors"] = list(repo["validation_errors"])
            _update_autonomy_action(
                db_client,
                action_id=action_id,
                status=status,
                validation_status=validation_status,
                commit_anchor=commit_anchor,
                rollback_anchor=rollback_anchor,
                quarantine_status=quarantine_status,
                quarantine_reason=quarantine_reason,
                detail=result_detail,
            )
            _update_sync_state(
                db_client,
                repo_id=repo_id,
                status=status,
                validation_status=validation_status,
                commit_anchor=commit_anchor,
                rollback_anchor=rollback_anchor,
                quarantine_status=quarantine_status,
                quarantine_reason=quarantine_reason,
                provenance_id=provenance_id,
                run_id=run_id,
            )
        else:
            bootstrap_command = _bootstrap_command_parts(
                project_root,
                {
                    "local_path": repo["local_path"],
                    "primary_remote_env": repo["primary_remote_env"],
                    "mirror_remote_env": repo.get("mirror_remote_env", ""),
                },
                str(repo["effective_primary_remote"]),
            )
            bootstrap_proc = subprocess.run(
                bootstrap_command,
                capture_output=True,
                text=True,
                check=False,
            )
            result_detail["bootstrap_stdout"] = _truncate_output(bootstrap_proc.stdout)
            result_detail["bootstrap_stderr"] = _truncate_output(bootstrap_proc.stderr)
            post_origin = _local_origin_url(repo_path)
            result_detail["origin_after_bootstrap"] = post_origin

            if bootstrap_proc.returncode != 0:
                rollback_applied = _restore_origin(repo_path, str(repo.get("local_origin_remote") or ""))
                status = "quarantined"
                validation_status = "not_run"
                quarantine_status = "quarantined"
                quarantine_reason = "bootstrap_failed"
            else:
                validation_command = _validation_command_parts(project_root)
                validation_env = os.environ.copy()
                validation_env.setdefault(
                    "GIT_GOVERNANCE_STRICT",
                    "1" if policy["require_strict_validation"] else "0",
                )
                validation_proc = subprocess.run(
                    validation_command,
                    cwd=project_root,
                    env=validation_env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                result_detail["validation_command"] = shlex.join(validation_command)
                result_detail["validation_stdout"] = _truncate_output(validation_proc.stdout)
                result_detail["validation_stderr"] = _truncate_output(validation_proc.stderr)
                if validation_proc.returncode != 0:
                    rollback_applied = _restore_origin(repo_path, str(repo.get("local_origin_remote") or ""))
                    status = "quarantined"
                    validation_status = "failed"
                    quarantine_status = "quarantined"
                    quarantine_reason = "validation_failed"
                else:
                    status = "completed"
                    validation_status = "passed"
                    quarantine_status = "clear"
                    quarantine_reason = ""

            final_origin = _local_origin_url(repo_path)
            rollback_anchor["origin_after_rollback"] = final_origin
            rollback_anchor["rollback_applied"] = rollback_applied
            provenance_id = _insert_provenance(
                db_client,
                repo_id=repo_id,
                run_id=run_id,
                deploy_target=str(repo["effective_primary_remote"]),
                ref_name=branch_name,
                commit_sha=commit_anchor,
                rollback_anchor=rollback_anchor,
                validation_status=validation_status,
                metadata={
                    "trigger_source": trigger_source,
                    "actor_agent_id": actor,
                    "quarantine_status": quarantine_status,
                    "quarantine_reason": quarantine_reason,
                    "origin_before": repo.get("local_origin_remote") or "",
                    "origin_after": final_origin,
                    "bootstrap_command": repo["bootstrap_command"],
                },
            )
            result_detail["origin_after"] = final_origin
            result_detail["rollback_applied"] = rollback_applied
            result_detail["provenance_id"] = provenance_id
            _update_autonomy_action(
                db_client,
                action_id=action_id,
                status=status,
                validation_status=validation_status,
                commit_anchor=commit_anchor,
                rollback_anchor=rollback_anchor,
                quarantine_status=quarantine_status,
                quarantine_reason=quarantine_reason,
                detail=result_detail,
            )
            _update_sync_state(
                db_client,
                repo_id=repo_id,
                status=status,
                validation_status=validation_status,
                commit_anchor=commit_anchor,
                rollback_anchor=rollback_anchor,
                quarantine_status=quarantine_status,
                quarantine_reason=quarantine_reason,
                provenance_id=provenance_id,
                run_id=run_id,
            )

        commit_anchor_map[repo_id] = commit_anchor
        rollback_anchor_map[repo_id] = rollback_anchor
        repo_results.append(
            {
                "repo_id": repo_id,
                "status": status,
                "validation_status": validation_status,
                "quarantine_status": quarantine_status,
                "quarantine_reason": quarantine_reason,
                "commit_anchor": commit_anchor,
                "rollback_anchor": rollback_anchor,
                "rollback_applied": rollback_applied,
                "effective_primary_remote": repo["effective_primary_remote"],
                "bootstrap_command": repo["bootstrap_command"],
                "planned_actions": repo["planned_actions"],
                "validation_errors": repo["validation_errors"],
                "provenance_id": provenance_id,
                "detail": result_detail,
            }
        )

    repo_statuses = {item["status"] for item in repo_results}
    if normalized_mode == DEFAULT_AUTONOMY_MODE:
        run_status = "dry_run"
        run_validation_status = "simulated"
        run_quarantine_status = "clear"
        run_quarantine_reason = ""
    elif "quarantined" in repo_statuses:
        run_status = "quarantined"
        run_validation_status = "failed"
        run_quarantine_status = "quarantined"
        run_quarantine_reason = "validation_failed" if any(
            item["quarantine_reason"] == "validation_failed" for item in repo_results
        ) else "bootstrap_failed"
    elif "blocked" in repo_statuses:
        run_status = "blocked"
        run_validation_status = "blocked"
        run_quarantine_status = "clear"
        run_quarantine_reason = ""
    else:
        run_status = "completed"
        run_validation_status = "passed"
        run_quarantine_status = "clear"
        run_quarantine_reason = ""

    _update_autonomy_run(
        db_client,
        run_id=run_id,
        status=run_status,
        validation_status=run_validation_status,
        commit_anchor=commit_anchor_map,
        rollback_anchor=rollback_anchor_map,
        quarantine_status=run_quarantine_status,
        quarantine_reason=run_quarantine_reason,
        error_detail="; ".join(
            sorted({item["quarantine_reason"] for item in repo_results if item["quarantine_reason"]})
        ),
        bootstrap_report={
            "repository_count": len(repo_results),
            "statuses": {item["repo_id"]: item["status"] for item in repo_results},
        },
    )

    return {
        "status": "ok",
        "run": {
            "id": run_id,
            "status": run_status,
            "validation_status": run_validation_status,
            "quarantine_status": run_quarantine_status,
            "quarantine_reason": run_quarantine_reason,
            "requested_mode": normalized_mode,
            "trigger_source": trigger_source,
            "actor_agent_id": actor,
            "credential_class": "autonomy_service_key",
            "host_id": executor["host_id"],
            "commit_anchor": commit_anchor_map,
            "rollback_anchor": rollback_anchor_map,
        },
        "repositories": repo_results,
        "policy": policy,
    }


def list_autonomy_runs(db_client, *, limit: int = 20) -> list[dict[str, Any]]:
    run_rows = db_client.fetch_all(
        "SELECT id, trigger_source, actor_agent_id, requested_mode, credential_class, host_id, repo_ids_json, "
        "status, validation_status, commit_anchor, rollback_anchor, quarantine_status, quarantine_reason, "
        "bootstrap_report_json, error_detail, created_at, started_at, completed_at, updated_at "
        "FROM autonomy_runs ORDER BY created_at DESC LIMIT ?",
        (int(limit),),
    )
    action_rows = db_client.fetch_all(
        "SELECT id, run_id, repo_id, action_type, planned_action, credential_ref, credential_class, requested_mode, "
        "status, validation_status, commit_anchor, rollback_anchor, quarantine_status, quarantine_reason, "
        "detail_json, created_at, updated_at "
        "FROM autonomy_actions ORDER BY created_at DESC"
    )
    actions_by_run: dict[str, list[dict[str, Any]]] = {}
    for row in action_rows:
        payload = dict(row)
        payload["rollback_anchor"] = _safe_json_loads(payload.get("rollback_anchor"), default={})
        payload["detail"] = _safe_json_loads(payload.pop("detail_json", ""), default={})
        actions_by_run.setdefault(str(payload["run_id"]), []).append(payload)

    results: list[dict[str, Any]] = []
    for row in run_rows:
        payload = dict(row)
        payload["repo_ids"] = _safe_json_loads(payload.pop("repo_ids_json", ""), default=[])
        payload["commit_anchor"] = _safe_json_loads(payload.get("commit_anchor"), default={})
        payload["rollback_anchor"] = _safe_json_loads(payload.get("rollback_anchor"), default={})
        payload["bootstrap_report"] = _safe_json_loads(payload.pop("bootstrap_report_json", ""), default={})
        payload["actions"] = actions_by_run.get(str(payload["id"]), [])
        results.append(payload)
    return results


def list_autonomy_sync_rows(db_client) -> list[dict[str, Any]]:
    sync_rows = db_client.fetch_all(
        "SELECT repo_id, classification, local_path, expected_primary_remote, effective_primary_remote, autonomy_scope, "
        "allowed_modes_json, preflight_only, wave, manifest_stage, manifest_sync_status, last_run_id, last_status, "
        "last_validation_status, last_commit_anchor, last_rollback_anchor, last_provenance_id, quarantine_status, "
        "quarantine_reason, last_synced_at, updated_at "
        "FROM autonomy_repo_sync ORDER BY repo_id"
    )
    provenance_rows = db_client.fetch_all(
        "SELECT id, repo_id, autonomy_run_id, source, deploy_target, ref_name, commit_sha, rollback_anchor, "
        "validation_status, metadata_json, created_at "
        "FROM deployment_provenance ORDER BY created_at DESC"
    )
    latest_provenance_by_repo: dict[str, dict[str, Any]] = {}
    for row in provenance_rows:
        repo_id = str(row.get("repo_id") or "")
        if repo_id in latest_provenance_by_repo:
            continue
        payload = dict(row)
        payload["rollback_anchor"] = _safe_json_loads(payload.get("rollback_anchor"), default={})
        payload["metadata"] = _safe_json_loads(payload.pop("metadata_json", ""), default={})
        latest_provenance_by_repo[repo_id] = payload

    results: list[dict[str, Any]] = []
    for row in sync_rows:
        payload = dict(row)
        payload["allowed_modes"] = _safe_json_loads(payload.pop("allowed_modes_json", ""), default=[])
        payload["preflight_only"] = bool(payload["preflight_only"])
        payload["last_rollback_anchor"] = _safe_json_loads(payload.get("last_rollback_anchor"), default={})
        payload["latest_provenance"] = latest_provenance_by_repo.get(str(payload["repo_id"]))
        results.append(payload)
    return results


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight governed remote provisioning from topology.")
    parser.add_argument("--project-root", default=str(_project_root_default()))
    parser.add_argument("--repo-id", dest="repo_ids", action="append", default=[])
    parser.add_argument("--all", action="store_true", help="Preflight all governed repositories")
    parser.add_argument("--mode", default=DEFAULT_AUTONOMY_MODE, choices=[DEFAULT_AUTONOMY_MODE, LIVE_AUTONOMY_MODE])
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

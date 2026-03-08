"""Redacted secret inventory and connection status services."""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api.security.admin_auth import DEFAULT_ADMIN_KEY_PLACEHOLDERS
from api.system.program_registry import verify_datastores
from api.system.secret_catalog import SECRET_DEFINITIONS, SECRET_DEFINITIONS_BY_NAME


@dataclass(frozen=True)
class ConnectionTarget:
    id: str
    label: str
    provider: str
    kind: str
    env_keys: tuple[str, ...] = ()
    datastore_id: str | None = None


CONNECTION_TARGETS = (
    ConnectionTarget("claude-cli-oauth", "Claude CLI OAuth", "Anthropic", "claude_cli"),
    ConnectionTarget(
        "cpanel-ssh",
        "cPanel SSH",
        "cPanel",
        "ssh",
        ("CPANEL_SSH_HOST", "CPANEL_SSH_PORT", "CPANEL_SSH_USER", "CPANEL_SSH_KEY_PATH"),
    ),
    ConnectionTarget(
        "artisan-reporting-db",
        "Artisan Reporting MySQL",
        "Artisan Reporting",
        "env_group",
        (
            "ARTISAN_REPORTING_DB_HOST",
            "ARTISAN_REPORTING_DB_PORT",
            "ARTISAN_REPORTING_DB_NAME",
            "ARTISAN_REPORTING_DB_USER",
            "ARTISAN_REPORTING_DB_PASSWORD",
            "BILLY_API_TOKEN",
        ),
    ),
    ConnectionTarget(
        "artisan-wordpress-db",
        "Artisan WordPress MySQL",
        "Artisan WordPress",
        "env_group",
        (
            "ARTISAN_WP_DB_HOST",
            "ARTISAN_WP_DB_NAME",
            "ARTISAN_WP_DB_USER",
            "ARTISAN_WP_DB_PASSWORD",
        ),
    ),
    ConnectionTarget(
        "lavprishjemmeside-db",
        "Lavprishjemmeside MySQL",
        "Lavprishjemmeside",
        "env_group",
        ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"),
    ),
    ConnectionTarget(
        "baltzer-shopify",
        "Baltzer Shopify",
        "Shopify",
        "env_group",
        ("SHOPIFY_STORE_DOMAIN", "SHOPIFY_ADMIN_TOKEN"),
    ),
    ConnectionTarget(
        "samlino-module-storage",
        "Samlino Local SQLite",
        "Samlino",
        "datastore",
        datastore_id="samlino-module-storage",
    ),
)

CONNECTION_TARGETS_BY_ID = {item.id: item for item in CONNECTION_TARGETS}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _env_value(name: str) -> str:
    return os.getenv(name, "").strip()


def _safe_presence_status(name: str, value: str, allow_default_admin_key: bool) -> tuple[bool, str, str]:
    if not value:
        return False, "missing", "env_missing"
    if name == "DASHBOARD_ADMIN_KEY" and not allow_default_admin_key and value.lower() in DEFAULT_ADMIN_KEY_PLACEHOLDERS:
        return False, "invalid", "placeholder_rejected"
    return True, "present", "env_present"


def build_secret_status_payload(*, settings, project_root: Path, db_client) -> dict[str, Any]:
    secret_rows: list[dict[str, Any]] = []
    for definition in SECRET_DEFINITIONS:
        value = _env_value(definition.name)
        present, status, evidence = _safe_presence_status(
            definition.name,
            value,
            settings.allow_default_admin_key,
        )
        secret_rows.append(
            {
                "name": definition.name,
                "provider": definition.provider,
                "purpose": definition.purpose,
                "required_for": definition.required_for,
                "priority": definition.priority,
                "scope": definition.scope,
                "kind": definition.kind,
                "present": present,
                "status": status,
                "evidence": evidence,
            }
        )

    datastores = verify_datastores(db_client=db_client, project_root=project_root)
    connections = list_connection_statuses(
        settings=settings,
        project_root=project_root,
        db_client=db_client,
        datastore_rows=datastores,
        include_live_checks=False,
    )

    summary = {
        "present": sum(1 for row in secret_rows if row["present"]),
        "missing": sum(1 for row in secret_rows if row["status"] == "missing"),
        "invalid": sum(1 for row in secret_rows if row["status"] == "invalid"),
        "connections_live": sum(1 for row in connections if row["status"] == "live"),
        "connections_partial": sum(1 for row in connections if row["status"] == "partial"),
        "connections_missing": sum(1 for row in connections if row["status"] == "missing"),
        "connections_planned": sum(1 for row in connections if row["status"] == "planned"),
    }
    return {
        "status": "ok",
        "checked_at": _now_iso(),
        "summary": summary,
        "secrets": secret_rows,
        "connections": connections,
        "datastores": datastores,
    }


def list_connection_statuses(
    *,
    settings,
    project_root: Path,
    db_client,
    datastore_rows: list[dict[str, Any]] | None = None,
    include_live_checks: bool = False,
) -> list[dict[str, Any]]:
    datastores = datastore_rows if datastore_rows is not None else verify_datastores(db_client=db_client, project_root=project_root)
    datastore_by_id = {str(item["id"]): item for item in datastores}
    rows: list[dict[str, Any]] = []
    for target in CONNECTION_TARGETS:
        rows.append(
            evaluate_connection_target(
                target=target,
                settings=settings,
                project_root=project_root,
                datastore_by_id=datastore_by_id,
                include_live_checks=include_live_checks,
            )
        )
    return rows


def _run_claude_auth_status(settings) -> tuple[str, str]:
    binary = (settings.claude_binary or "claude").strip() or "claude"
    try:
        result = subprocess.run(
            [binary, "auth", "status"],
            capture_output=True,
            text=True,
            timeout=max(5, int(settings.claude_timeout)),
            check=False,
        )
    except FileNotFoundError:
        return "missing", "binary_missing"
    except Exception as exc:  # pragma: no cover - defensive
        return "partial", f"status_error:{exc}"

    if result.returncode != 0:
        return "partial", "cli_not_authenticated"
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return "partial", "invalid_status_payload"
    return ("live", "cli_auth_ok") if payload.get("loggedIn") else ("partial", "cli_not_authenticated")


def _evaluate_env_group(target: ConnectionTarget) -> tuple[str, str]:
    missing = [key for key in target.env_keys if not _env_value(key)]
    if missing:
        return "missing", f"missing_env:{','.join(missing)}"
    return "partial", "env_present"


def _evaluate_ssh_target(target: ConnectionTarget, include_live_checks: bool) -> tuple[str, str]:
    status, evidence = _evaluate_env_group(target)
    if status == "missing":
        return status, evidence
    key_path = Path(_env_value("CPANEL_SSH_KEY_PATH"))
    if not key_path.exists():
        return "missing", "ssh_key_missing"
    if not include_live_checks:
        return "partial", "ssh_configured"
    try:
        result = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=5",
                "-i",
                str(key_path),
                "-p",
                _env_value("CPANEL_SSH_PORT"),
                f"{_env_value('CPANEL_SSH_USER')}@{_env_value('CPANEL_SSH_HOST')}",
                "exit",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except FileNotFoundError:
        return "partial", "ssh_binary_missing"
    except Exception as exc:  # pragma: no cover - defensive
        return "partial", f"ssh_error:{exc}"
    return ("live", "ssh_handshake_ok") if result.returncode == 0 else ("partial", "ssh_connection_failed")


def _evaluate_datastore_target(target: ConnectionTarget, datastore_by_id: dict[str, dict[str, Any]]) -> tuple[str, str]:
    row = datastore_by_id.get(str(target.datastore_id or ""))
    if not row:
        return "missing", "datastore_unknown"
    status = str(row.get("status") or "unknown")
    if status == "verified":
        return "live", "path_verified"
    if status == "configured":
        return "partial", "env_present"
    if status == "planned":
        return "planned", "planned"
    if status == "missing_env":
        return "missing", "missing_env"
    if status == "missing_path":
        return "missing", "missing_path"
    return "partial", f"registry_status:{status}"


def evaluate_connection_target(
    *,
    target: ConnectionTarget,
    settings,
    project_root: Path,
    datastore_by_id: dict[str, dict[str, Any]],
    include_live_checks: bool,
) -> dict[str, Any]:
    if target.kind == "claude_cli":
        status, evidence = _run_claude_auth_status(settings)
    elif target.kind == "ssh":
        status, evidence = _evaluate_ssh_target(target, include_live_checks)
    elif target.kind == "env_group":
        status, evidence = _evaluate_env_group(target)
    elif target.kind == "datastore":
        status, evidence = _evaluate_datastore_target(target, datastore_by_id)
    else:  # pragma: no cover - defensive
        status, evidence = "missing", "unsupported"
    return {
        "target": target.id,
        "label": target.label,
        "provider": target.provider,
        "status": status,
        "evidence": evidence,
        "checked_at": _now_iso(),
    }


def test_secret_or_connection(
    *,
    key_name: str,
    settings,
    project_root: Path,
    db_client,
) -> dict[str, Any] | None:
    datastores = verify_datastores(db_client=db_client, project_root=project_root)
    datastore_by_id = {str(item["id"]): item for item in datastores}
    if key_name in CONNECTION_TARGETS_BY_ID:
        return evaluate_connection_target(
            target=CONNECTION_TARGETS_BY_ID[key_name],
            settings=settings,
            project_root=project_root,
            datastore_by_id=datastore_by_id,
            include_live_checks=True,
        )
    definition = SECRET_DEFINITIONS_BY_NAME.get(key_name)
    if not definition:
        return None
    present, status, evidence = _safe_presence_status(
        definition.name,
        _env_value(definition.name),
        settings.allow_default_admin_key,
    )
    return {
        "target": definition.name,
        "label": definition.name,
        "provider": definition.provider,
        "status": "live" if present else ("partial" if status == "invalid" else "missing"),
        "evidence": evidence,
        "checked_at": _now_iso(),
    }

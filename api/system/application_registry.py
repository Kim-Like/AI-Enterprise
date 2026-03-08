"""Application-level registry sync and query helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ALLOWED_STATUSES = {"active", "planned", "placeholder"}
ALLOWED_KINDS = {"core", "submodule", "placeholder"}
REQUIRED_FIELDS = ("id", "program_id", "name", "owner_master_id", "status", "kind", "repo_path")


def _is_external_ref(value: str) -> bool:
    lowered = (value or "").strip().lower()
    return lowered.startswith(("ssh://", "http://", "https://", "git@"))


def _normalize_catalog_path(project_root: Path, value: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        return ""
    if _is_external_ref(normalized):
        return normalized
    if normalized.lower().startswith("placeholder"):
        return normalized
    return str((project_root / normalized).resolve())


def _load_catalog(catalog_path: Path) -> list[dict[str, Any]]:
    if not catalog_path.exists():
        return []
    raw = json.loads(catalog_path.read_text())
    if not isinstance(raw, list):
        return []
    entries: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        missing = [field for field in REQUIRED_FIELDS if field not in item]
        if missing:
            continue
        status = str(item.get("status", "placeholder")).strip().lower()
        if status not in ALLOWED_STATUSES:
            status = "placeholder"
        kind = str(item.get("kind", "placeholder")).strip().lower()
        if kind not in ALLOWED_KINDS:
            kind = "placeholder"
        entries.append(
            {
                "id": str(item["id"]).strip(),
                "program_id": str(item["program_id"]).strip(),
                "name": str(item["name"]).strip(),
                "owner_master_id": str(item["owner_master_id"]).strip(),
                "status": status,
                "kind": kind,
                "repo_path": str(item["repo_path"]).strip(),
                "frontend_entry": str(item.get("frontend_entry", "")).strip(),
                "backend_entry": str(item.get("backend_entry", "")).strip(),
                "dev_url": str(item.get("dev_url", "")).strip(),
                "live_url": str(item.get("live_url", "")).strip(),
                "staging_url": str(item.get("staging_url", "")).strip(),
                "notes": str(item.get("notes", "")).strip(),
            }
        )
    return entries


def sync_application_registry(db_client, project_root: Path, catalog_path: Path) -> dict[str, int | str]:
    rows = _load_catalog(catalog_path)
    synced = 0
    for item in rows:
        repo_abs = _normalize_catalog_path(project_root=project_root, value=item["repo_path"])
        frontend_abs = _normalize_catalog_path(project_root=project_root, value=item["frontend_entry"])
        backend_abs = _normalize_catalog_path(project_root=project_root, value=item["backend_entry"])
        db_client.execute(
            "INSERT INTO application_registry "
            "(id, program_id, name, owner_master_id, status, kind, repo_path, frontend_entry, backend_entry, dev_url, live_url, staging_url, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now')) "
            "ON CONFLICT(id) DO UPDATE SET "
            "program_id=excluded.program_id, name=excluded.name, owner_master_id=excluded.owner_master_id, "
            "status=excluded.status, kind=excluded.kind, repo_path=excluded.repo_path, "
            "frontend_entry=excluded.frontend_entry, backend_entry=excluded.backend_entry, "
            "dev_url=excluded.dev_url, live_url=excluded.live_url, staging_url=excluded.staging_url, "
            "notes=excluded.notes, updated_at=datetime('now')",
            (
                item["id"],
                item["program_id"],
                item["name"],
                item["owner_master_id"],
                item["status"],
                item["kind"],
                repo_abs,
                frontend_abs,
                backend_abs,
                item["dev_url"],
                item["live_url"],
                item["staging_url"],
                item["notes"],
            ),
        )
        synced += 1
    return {"synced": synced, "catalog_path": str(catalog_path)}


def fetch_applications(
    db_client,
    *,
    status: str | None = None,
    domain: str | None = None,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[str] = []
    if status:
        clauses.append("LOWER(a.status) = ?")
        params.append(str(status).strip().lower())
    if domain:
        clauses.append("LOWER(p.domain) = ?")
        params.append(str(domain).strip().lower())
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return db_client.fetch_all(
        "SELECT a.id, a.program_id, a.name, a.owner_master_id, a.status, a.kind, a.repo_path, "
        "a.frontend_entry, a.backend_entry, a.dev_url, a.live_url, a.staging_url, a.notes, a.updated_at, "
        "p.name AS program_name, p.domain "
        "FROM application_registry a "
        "JOIN program_registry p ON p.id = a.program_id "
        f"{where} "
        "ORDER BY p.domain ASC, p.name ASC, a.name ASC",
        tuple(params),
    )


def get_application(db_client, app_id: str) -> dict[str, Any] | None:
    safe_id = str(app_id or "").strip()
    if not safe_id:
        return None
    return db_client.fetch_one(
        "SELECT a.id, a.program_id, a.name, a.owner_master_id, a.status, a.kind, a.repo_path, "
        "a.frontend_entry, a.backend_entry, a.dev_url, a.live_url, a.staging_url, a.notes, a.updated_at, "
        "p.name AS program_name, p.domain "
        "FROM application_registry a "
        "JOIN program_registry p ON p.id = a.program_id "
        "WHERE a.id = ?",
        (safe_id,),
    )


def fetch_application_map(db_client) -> dict[str, Any]:
    rows = fetch_applications(db_client)
    by_program: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_program.setdefault(str(row.get("program_id") or ""), []).append(row)
    return {
        "applications": rows,
        "totals": {
            "applications": len(rows),
            "programs": len(by_program),
        },
    }

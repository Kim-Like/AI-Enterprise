"""Program/data-store registry synchronization helpers."""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from api.agent.ownership_rules import MASTER_PROGRAMS

PROGRAM_BLUEPRINTS: List[Dict[str, str]] = [
    {
        "id": "ian-control-plane",
        "name": "IAn Agency Control Plane",
        "domain": "platform",
        "owner_master_id": "father",
        "repo_path": ".",
        "stack": "python-fastapi-sqlite",
        "app_status": "active",
        "notes": "Sellable IAn Agency governance layer, mission-control dashboard, and orchestration core",
    },
    {
        "id": "artisan-reporting",
        "name": "Artisan Reporting",
        "domain": "artisan",
        "owner_master_id": "artisan-master",
        "repo_path": "programs/artisan/reporting.theartisan.dk",
        "stack": "node-express-ejs",
        "app_status": "active",
        "notes": "Billy-integrated reporting application",
    },
    {
        "id": "artisan-wordpress",
        "name": "Artisan WordPress",
        "domain": "artisan",
        "owner_master_id": "artisan-master",
        "repo_path": "programs/artisan/the-artisan-wp",
        "stack": "wordpress-php-woocommerce",
        "app_status": "active",
        "notes": "cPanel-hosted WordPress/B2B",
    },
    {
        "id": "artisan-email-marketing",
        "name": "Artisan Email Marketing",
        "domain": "artisan",
        "owner_master_id": "artisan-master",
        "repo_path": "programs/artisan/e-mail-marketing",
        "stack": "html-email-brevo",
        "app_status": "planned",
        "notes": "Brevo campaign conversion workspace",
    },
    {
        "id": "lavprishjemmeside-cms",
        "name": "Lavprishjemmeside CMS",
        "domain": "lavprishjemmeside",
        "owner_master_id": "lavprishjemmeside-master",
        "repo_path": "ssh://theartis@cp10.nordicway.dk/home/theartis/repositories/lavprishjemmeside.dk",
        "stack": "astro-node-mysql",
        "app_status": "active",
        "notes": "Remote-first CMS that governs lavprishjemmeside.dk and ljdesignstudio.dk client sites",
    },
    {
        "id": "samlino-seo-agent-playground",
        "name": "Samlino Agency Context",
        "domain": "samlino",
        "owner_master_id": "samlino-master",
        "repo_path": "programs/ian-agency/contexts/samlino/seo-agent-playground",
        "stack": "react-fastapi-controlplane-sqlite",
        "app_status": "active",
        "notes": "Archive-mapped strategy and sandbox context carried under IAn Agency",
    },
    {
        "id": "baltzer-tcg-index",
        "name": "Baltzer TCG Index",
        "domain": "baltzer",
        "owner_master_id": "baltzer-master",
        "repo_path": "programs/baltzer/TCG-index",
        "stack": "react-migration-hold",
        "app_status": "planned",
        "notes": "Demoted from the live operational surface pending local datastore replacement",
    },
    {
        "id": "baltzer-reporting",
        "name": "Baltzer Reporting",
        "domain": "baltzer",
        "owner_master_id": "baltzer-master",
        "repo_path": "programs/baltzer/reporting.baltzergames.dk",
        "stack": "node-express-ejs",
        "app_status": "active",
        "notes": "Accounting/reporting application",
    },
    {
        "id": "baltzer-shopify",
        "name": "Baltzer Shopify",
        "domain": "baltzer",
        "owner_master_id": "baltzer-master",
        "repo_path": "programs/baltzer/shopify",
        "stack": "shopify-ecommerce",
        "app_status": "active",
        "notes": "Shopify operational workspace",
    },
    {
        "id": "personal-assistant-suite",
        "name": "Personal Assistant Suite",
        "domain": "personal-assistant",
        "owner_master_id": "personal-assistant-master",
        "repo_path": "programs/personal-assistant",
        "stack": "multi-tooling",
        "app_status": "planned",
        "notes": "Task/calendar/social/email/fitness assistant scope",
    },
]

DATASTORE_BLUEPRINTS: List[Dict[str, str]] = [
    {"id": "father-db", "program_id": "ian-control-plane", "name": "father.db", "engine": "sqlite", "role": "orchestration", "location": "father.db", "env_keys": "DB_PATH", "notes": "WAL-enabled orchestration DB"},
    {"id": "artisan-reporting-local-state", "program_id": "artisan-reporting", "name": "Artisan Reporting cPanel MySQL", "engine": "mysql_cpanel", "role": "app_primary", "location": "cpanel:mysql", "env_keys": "ARTISAN_REPORTING_DB_HOST,ARTISAN_REPORTING_DB_PORT,ARTISAN_REPORTING_DB_NAME,ARTISAN_REPORTING_DB_USER,ARTISAN_REPORTING_DB_PASSWORD,BILLY_API_TOKEN", "notes": "Dedicated reporting MySQL database on cPanel plus Billy API token"},
    {"id": "artisan-wordpress-cpanel-mysql", "program_id": "artisan-wordpress", "name": "Artisan WP cPanel MySQL", "engine": "mysql_cpanel", "role": "app_primary", "location": "cpanel:mysql", "env_keys": "ARTISAN_WP_DB_HOST,ARTISAN_WP_DB_USER,ARTISAN_WP_DB_PASSWORD,ARTISAN_WP_DB_NAME", "notes": "WordPress database on cPanel"},
    {"id": "lavprishjemmeside-cpanel-mysql", "program_id": "lavprishjemmeside-cms", "name": "Lavprishjemmeside cPanel MySQL", "engine": "mysql_cpanel", "role": "app_primary", "location": "cpanel:mysql", "env_keys": "DB_HOST,DB_USER,DB_PASSWORD,DB_NAME", "notes": "Primary CMS database on cPanel"},
    {"id": "samlino-module-storage", "program_id": "samlino-seo-agent-playground", "name": "Samlino Local SQLite", "engine": "sqlite", "role": "app_primary", "location": "programs/ian-agency/contexts/samlino/seo-agent-playground/data/samlino.db", "env_keys": "", "notes": "Program-local SQLite datastore for Samlino runtime modules"},
    {"id": "baltzer-tcg-migration-hold", "program_id": "baltzer-tcg-index", "name": "Baltzer TCG Migration Hold", "engine": "planned", "role": "app_primary", "location": "programs/baltzer/TCG-index/MIGRATION-HOLD.md", "env_keys": "", "notes": "Legacy hosted datastore removed from the live surface; local replacement pending"},
    {"id": "baltzer-reporting-local-state", "program_id": "baltzer-reporting", "name": "Baltzer Reporting Local State", "engine": "json_file", "role": "app_primary", "location": "programs/baltzer/reporting.baltzergames.dk/data", "env_keys": "BILLY_API_TOKEN", "notes": "JSON files and Billy API token"},
    {"id": "baltzer-shopify-cloud", "program_id": "baltzer-shopify", "name": "Baltzer Shopify", "engine": "shopify_cloud", "role": "app_primary", "location": "shopify:cloud", "env_keys": "SHOPIFY_STORE_DOMAIN,SHOPIFY_ADMIN_TOKEN", "notes": "Shopify managed platform"},
    {"id": "personal-assistant-local", "program_id": "personal-assistant-suite", "name": "Personal Assistant Local", "engine": "planned", "role": "app_primary", "location": "programs/personal-assistant", "env_keys": "", "notes": "Pending data-store implementation"},
]

_MASTER_AGENT_SEEDS: Dict[str, Dict[str, str]] = {
    "father": {"name": "IAn", "type": "orchestrator", "status": "active", "description": "Top-level orchestration authority"},
    "engineer": {"name": "Engineer Agent", "type": "special", "status": "idle", "description": "Builds and fixes the system"},
    "ian-master": {"name": "IAn Legacy Alias", "type": "domain", "status": "idle", "description": "Legacy compatibility alias for top-level IAn orchestration"},
}

_LEGACY_BALTZER_TCG_DATASTORE_ID = "baltzer-tcg-" + "supa" + "base"

_LEGACY_DATASTORE_MIGRATIONS: Dict[str, Dict[str, str]] = {
    _LEGACY_BALTZER_TCG_DATASTORE_ID: {
        "id": "baltzer-tcg-migration-hold",
        "name": "Baltzer TCG Migration Hold",
        "engine": "planned",
        "role": "app_primary",
        "location": "programs/baltzer/TCG-index/MIGRATION-HOLD.md",
        "env_keys": "",
        "status": "planned",
        "notes": "Legacy hosted datastore removed from the live surface; local replacement pending",
    }
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _git_remote_for_path(path: Path) -> str:
    if not (path / ".git").exists():
        return ""
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        return ""
    return ""


def _is_external_repo_path(repo_path: str) -> bool:
    lowered = (repo_path or "").strip().lower()
    return lowered.startswith(("ssh://", "http://", "https://", "git@"))


def _ensure_master_agent_rows(db_client) -> None:
    required_ids = set(MASTER_PROGRAMS.keys())
    for blueprint in PROGRAM_BLUEPRINTS:
        owner_master_id = str(blueprint.get("owner_master_id") or "").strip()
        if owner_master_id:
            required_ids.add(owner_master_id)
    required_ids.add("engineer")

    for agent_id in sorted(required_ids):
        seed = _MASTER_AGENT_SEEDS.get(agent_id)
        if not seed:
            seed = {
                "name": str(agent_id).replace("-", " ").title(),
                "type": "domain",
                "status": "idle",
                "description": f"Seeded master agent {agent_id}",
            }
        db_client.execute(
            "INSERT OR IGNORE INTO master_agents (id, name, type, status, description, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            (agent_id, seed["name"], seed["type"], seed["status"], seed["description"]),
        )


def _migrate_legacy_datastore_rows(db_client) -> None:
    for legacy_id, replacement in _LEGACY_DATASTORE_MIGRATIONS.items():
        existing = db_client.fetch_one(
            "SELECT id, program_id FROM data_store_registry WHERE id = ?",
            (legacy_id,),
        )
        if not existing:
            continue
        already_present = db_client.fetch_one(
            "SELECT id FROM data_store_registry WHERE id = ?",
            (replacement["id"],),
        )
        if already_present:
            db_client.execute("DELETE FROM data_store_registry WHERE id = ?", (legacy_id,))
            continue
        db_client.execute(
            "UPDATE data_store_registry SET id=?, name=?, engine=?, role=?, location=?, env_keys=?, status=?, notes=? WHERE id=?",
            (
                replacement["id"],
                replacement["name"],
                replacement["engine"],
                replacement["role"],
                replacement["location"],
                replacement["env_keys"],
                replacement["status"],
                replacement["notes"],
                legacy_id,
            ),
        )


def _verify_datastore_row(project_root: Path, row: Dict[str, Any]) -> Dict[str, Any]:
    engine = (row.get("engine") or "").strip().lower()
    location = str(row.get("location") or "")
    env_keys = [key.strip() for key in str(row.get("env_keys") or "").split(",") if key.strip()]

    status = "unknown"
    notes = str(row.get("notes", "")).split(" | Missing env:")[0].split(" | Missing path:")[0].strip()

    if engine in {"sqlite", "json_file", "mixed"} and not location.startswith(("cpanel:", "shopify:")):
        target = project_root / location
        status = "verified" if target.exists() else "missing_path"
        if status == "missing_path":
            notes = f"{notes} | Missing path: {target}"
    elif engine in {"mysql_cpanel", "shopify_cloud"}:
        missing = [key for key in env_keys if not os.getenv(key)]
        status = "configured" if not missing else "missing_env"
        if missing:
            notes = f"{notes} | Missing env: {', '.join(missing)}"
    elif engine == "planned":
        status = "planned"
    else:
        status = "external"

    return {"status": status, "notes": notes.strip()}


def sync_registry(db_client, project_root: Path) -> Dict[str, int]:
    synced_programs = 0
    synced_datastores = 0
    synced_assignments = 0

    now_iso = _now_iso()
    _ensure_master_agent_rows(db_client=db_client)
    _migrate_legacy_datastore_rows(db_client=db_client)

    for blueprint in PROGRAM_BLUEPRINTS:
        repo_rel = blueprint["repo_path"]
        if repo_rel == ".":
            repo_abs = str(project_root.resolve())
            remote = _git_remote_for_path(Path(repo_abs))
        elif _is_external_repo_path(repo_rel):
            repo_abs = repo_rel
            remote = ""
        else:
            repo_abs = str((project_root / repo_rel).resolve())
            remote = _git_remote_for_path(Path(repo_abs))
        db_client.execute(
            "INSERT INTO program_registry (id, name, domain, owner_master_id, repo_path, repo_remote, stack, app_status, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now')) "
            "ON CONFLICT(id) DO UPDATE SET "
            "name=excluded.name, domain=excluded.domain, owner_master_id=excluded.owner_master_id, "
            "repo_path=excluded.repo_path, repo_remote=excluded.repo_remote, stack=excluded.stack, "
            "app_status=excluded.app_status, notes=excluded.notes, updated_at=datetime('now')",
            (
                blueprint["id"],
                blueprint["name"],
                blueprint["domain"],
                blueprint["owner_master_id"],
                repo_abs,
                remote,
                blueprint["stack"],
                blueprint["app_status"],
                blueprint["notes"],
            ),
        )
        synced_programs += 1

    for blueprint in DATASTORE_BLUEPRINTS:
        verification = _verify_datastore_row(project_root=project_root, row=blueprint)
        db_client.execute(
            "INSERT INTO data_store_registry (id, program_id, name, engine, role, location, env_keys, status, last_verified_at, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET "
            "program_id=excluded.program_id, name=excluded.name, engine=excluded.engine, role=excluded.role, "
            "location=excluded.location, env_keys=excluded.env_keys, status=excluded.status, "
            "last_verified_at=excluded.last_verified_at, notes=excluded.notes",
            (
                blueprint["id"],
                blueprint["program_id"],
                blueprint["name"],
                blueprint["engine"],
                blueprint["role"],
                blueprint["location"],
                blueprint["env_keys"],
                verification["status"],
                now_iso,
                verification["notes"],
            ),
        )
        synced_datastores += 1

    for agent_id, programs in MASTER_PROGRAMS.items():
        for program_id in programs:
            assignment_id = f"{agent_id}:{program_id}"
            db_client.execute(
                "INSERT INTO agent_program_assignments (id, agent_id, program_id, responsibility, priority, status, notes, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now')) "
                "ON CONFLICT(id) DO UPDATE SET "
                "responsibility=excluded.responsibility, priority=excluded.priority, status=excluded.status, "
                "notes=excluded.notes, updated_at=datetime('now')",
                (
                    assignment_id,
                    agent_id,
                    program_id,
                    "owner",
                    "P1",
                    "active",
                    "Seeded ownership assignment",
                ),
            )
            synced_assignments += 1

    return {
        "programs": synced_programs,
        "datastores": synced_datastores,
        "assignments": synced_assignments,
    }


def verify_datastores(db_client, project_root: Path) -> List[Dict[str, Any]]:
    now_iso = _now_iso()
    blueprint_by_id = {row["id"]: row for row in DATASTORE_BLUEPRINTS}
    rows = db_client.fetch_all(
        "SELECT id, program_id, name, engine, role, location, env_keys, status, last_verified_at, notes "
        "FROM data_store_registry ORDER BY id"
    )
    verified_rows: List[Dict[str, Any]] = []
    for row in rows:
        blueprint = blueprint_by_id.get(str(row.get("id") or ""))
        source_row = dict(row)
        if blueprint:
            source_row.update(blueprint)
        verification = _verify_datastore_row(project_root=project_root, row=source_row)
        db_client.execute(
            "UPDATE data_store_registry SET status=?, last_verified_at=?, notes=? WHERE id=?",
            (verification["status"], now_iso, verification["notes"], row["id"]),
        )
        row["status"] = verification["status"]
        row["last_verified_at"] = now_iso
        row["notes"] = verification["notes"]
        verified_rows.append(row)
    return verified_rows

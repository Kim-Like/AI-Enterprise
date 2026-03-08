"""Specialist projection helpers for the clean AI-Enterprise target."""
from __future__ import annotations

from pathlib import Path
from typing import Any


MASTER_ROOTS = {
    "father": "agents/IAn",
    "engineer": "agents/Engineer",
    "ian-master": "agents/platform/ian-master",
    "artisan-master": "agents/artisan/artisan-master",
    "lavprishjemmeside-master": "agents/lavprishjemmeside/lavprishjemmeside-master",
    "samlino-master": "agents/samlino/samlino-master",
    "baltzer-master": "agents/baltzer/baltzer-master",
    "personal-assistant-master": "agents/personal-assistant/personal-assistant-master",
}

DOMAIN_PREFIX = {
    "engineer": "engineer",
    "ian-master": "platform",
    "artisan-master": "artisan",
    "lavprishjemmeside-master": "lavpris",
    "samlino-master": "samlino",
    "baltzer-master": "baltzer",
    "personal-assistant-master": "personal_assistant",
}


def _titleize(slug: str) -> str:
    words = [part for part in slug.replace("-", " ").replace("_", " ").split() if part]
    return " ".join(word.upper() if len(word) <= 3 else word.capitalize() for word in words)


def _program_id_for_task(owner_master_id: str, task_slug: str) -> str:
    slug = str(task_slug or "").strip().lower()
    if owner_master_id in {"engineer", "ian-master"}:
        return "ian-control-plane"
    if owner_master_id == "artisan-master":
        if "accounting" in slug:
            return "artisan-reporting"
        if "wp" in slug or "b2b" in slug:
            return "artisan-wordpress"
        return "artisan-email-marketing"
    if owner_master_id == "baltzer-master":
        if "tcg" in slug:
            return "baltzer-tcg-index"
        if "accounting" in slug:
            return "baltzer-reporting"
        return "baltzer-shopify"
    if owner_master_id == "lavprishjemmeside-master":
        return "lavprishjemmeside-cms"
    if owner_master_id == "samlino-master":
        return "samlino-seo-agent-playground"
    if owner_master_id == "personal-assistant-master":
        return "personal-assistant-suite"
    return "ian-control-plane"


def _specialist_id(owner_master_id: str, task_slug: str) -> str:
    prefix = DOMAIN_PREFIX.get(owner_master_id, owner_master_id.replace("-", "_"))
    task_key = str(task_slug or "").strip().lower().replace("-", "_")
    if task_key.endswith("_task"):
        task_key = task_key[:-5]
    return f"spec.{prefix}.{task_key}"


def _upsert_specialist(db_client, row: dict[str, Any]) -> None:
    db_client.execute(
        "INSERT INTO specialist_agents "
        "(id, name, agent_kind, owner_master_id, parent_agent_id, program_id, application_id, task_slug, "
        "prompt_agent_key, source_path, status, chat_enabled, delegation_enabled, allow_write_tools, description, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now')) "
        "ON CONFLICT(id) DO UPDATE SET "
        "name=excluded.name, agent_kind=excluded.agent_kind, owner_master_id=excluded.owner_master_id, "
        "parent_agent_id=excluded.parent_agent_id, program_id=excluded.program_id, application_id=excluded.application_id, "
        "task_slug=excluded.task_slug, prompt_agent_key=excluded.prompt_agent_key, source_path=excluded.source_path, "
        "status=excluded.status, chat_enabled=excluded.chat_enabled, delegation_enabled=excluded.delegation_enabled, "
        "allow_write_tools=excluded.allow_write_tools, description=excluded.description, updated_at=datetime('now')",
        (
            row["id"],
            row["name"],
            row["agent_kind"],
            row["owner_master_id"],
            row["parent_agent_id"],
            row.get("program_id"),
            row.get("application_id"),
            row.get("task_slug"),
            row.get("prompt_agent_key"),
            row["source_path"],
            row["status"],
            1 if row.get("chat_enabled", False) else 0,
            1 if row.get("delegation_enabled", True) else 0,
            1 if row.get("allow_write_tools", False) else 0,
            row.get("description", ""),
        ),
    )


def sync_specialists(db_client, project_root: Path) -> dict[str, int]:
    db_client.execute("UPDATE specialist_agents SET status = 'dormant', updated_at = datetime('now')")
    synced = 0

    orchestration_root = project_root / "agents" / "Engineer"
    if orchestration_root.exists():
        _upsert_specialist(
            db_client,
            {
                "id": "spec.engineer.orchestration",
                "name": "Engineer Orchestration Specialist",
                "agent_kind": "engineer_specialist",
                "owner_master_id": "engineer",
                "parent_agent_id": "engineer",
                "program_id": "ian-control-plane",
                "application_id": None,
                "task_slug": None,
                "prompt_agent_key": "engineer:orchestration",
                "source_path": "agents/Engineer",
                "status": "active",
                "chat_enabled": False,
                "delegation_enabled": False,
                "allow_write_tools": False,
                "description": "Virtual orchestration specialist for locked-flow routing.",
            },
        )
        synced += 1

    for owner_master_id, relative_root in MASTER_ROOTS.items():
        tasks_dir = project_root / relative_root / "tasks"
        if not tasks_dir.exists():
            continue
        for task_dir in sorted(path for path in tasks_dir.iterdir() if path.is_dir()):
            task_slug = task_dir.name
            program_id = _program_id_for_task(owner_master_id, task_slug)
            _upsert_specialist(
                db_client,
                {
                    "id": _specialist_id(owner_master_id, task_slug),
                    "name": _titleize(task_slug),
                    "agent_kind": "engineer_specialist" if owner_master_id == "engineer" else "task_specialist",
                    "owner_master_id": owner_master_id,
                    "parent_agent_id": owner_master_id,
                    "program_id": program_id,
                    "application_id": None,
                    "task_slug": task_slug,
                    "prompt_agent_key": f"{owner_master_id}:{task_slug}",
                    "source_path": str(task_dir.relative_to(project_root)),
                    "status": "active",
                    "chat_enabled": False,
                    "delegation_enabled": True,
                    "allow_write_tools": False,
                    "description": f"Projected specialist for {task_slug}.",
                },
            )
            synced += 1

    applications = db_client.fetch_all(
        "SELECT id, name, owner_master_id, program_id, status FROM application_registry ORDER BY id"
    )
    for app in applications:
        owner_master_id = str(app.get("owner_master_id") or "").strip() or "father"
        source_path = MASTER_ROOTS.get(owner_master_id, "agents/IAn")
        _upsert_specialist(
            db_client,
            {
                "id": f"gov.{app['id']}",
                "name": f"Governor: {app['name']}",
                "agent_kind": "app_governor",
                "owner_master_id": owner_master_id,
                "parent_agent_id": owner_master_id,
                "program_id": app.get("program_id"),
                "application_id": app.get("id"),
                "task_slug": None,
                "prompt_agent_key": f"governor:{app['id']}",
                "source_path": source_path,
                "status": "active" if str(app.get('status') or '').lower() == "active" else "dormant",
                "chat_enabled": False,
                "delegation_enabled": str(app.get("status") or "").lower() == "active",
                "allow_write_tools": False,
                "description": "Application governor specialist.",
            },
        )
        synced += 1

    return {"specialists": synced}


def list_specialists(
    db_client,
    *,
    owner_master_id: str | None = None,
    program_id: str | None = None,
    application_id: str | None = None,
    include_dormant: bool = False,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[str] = []
    if owner_master_id:
        clauses.append("owner_master_id = ?")
        params.append(str(owner_master_id).strip())
    if program_id:
        clauses.append("program_id = ?")
        params.append(str(program_id).strip())
    if application_id:
        clauses.append("application_id = ?")
        params.append(str(application_id).strip())
    if not include_dormant:
        clauses.append("status = 'active'")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return db_client.fetch_all(
        f"SELECT * FROM specialist_agents {where} ORDER BY owner_master_id ASC, id ASC",
        tuple(params),
    )


def get_specialist(db_client, specialist_id: str) -> dict[str, Any] | None:
    return db_client.fetch_one("SELECT * FROM specialist_agents WHERE id = ?", (str(specialist_id).strip(),))

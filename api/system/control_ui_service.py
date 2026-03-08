"""Control-plane aggregation payloads for AI-Enterprise."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from api.agent.identity_loader import IDENTITY_FILES
from api.system.application_registry import fetch_applications, get_application
from api.system.specialist_service import MASTER_ROOTS

CANONICAL_FILE_ORDER = list(IDENTITY_FILES)
STALE_AFTER_DAYS = 30
DISPLAY_NAMES = {
    "father": "IAn",
    "engineer": "Engineer",
    "ian-master": "IAn Master",
    "artisan-master": "Artisan Master",
    "lavprishjemmeside-master": "Lavprishjemmeside Master",
    "samlino-master": "Samlino Master",
    "baltzer-master": "Baltzer Master",
    "personal-assistant-master": "Personal Assistant Master",
}

AGENCY_OVERVIEW = {
    "id": "ian-agency",
    "label": "IAn Agency",
    "description": "Main agent program and governing layer for the operational portfolio.",
}

DOMAIN_PRESENTATION = {
    "platform": {
        "label": "IAn Agency",
        "description": "Governance, mission control, and the saleable operator layer.",
        "portfolio_role": "governance",
    },
    "lavprishjemmeside": {
        "label": "Lavprishjemmeside",
        "description": "Remote-first CMS governance plus explicit client-site ownership.",
        "portfolio_role": "program",
    },
    "artisan": {
        "label": "Artisan",
        "description": "Reporting, WordPress commerce, and campaign operations.",
        "portfolio_role": "program",
    },
    "baltzer": {
        "label": "Baltzer Games",
        "description": "Reporting, commerce, and product tracks with one demoted migration-hold workload.",
        "portfolio_role": "program",
    },
    "personal-assistant": {
        "label": "Personal assistance",
        "description": "Skeleton suite for personal workflow support modules.",
        "portfolio_role": "program",
    },
    "samlino": {
        "label": "IAn Agency Context",
        "description": "Archive-mapped context and sandbox material carried under IAn Agency.",
        "portfolio_role": "context",
    },
}

PROGRAM_PRESENTATION = {
    "ian-control-plane": {
        "summary": "Main agent program, dashboard, and governance surface.",
        "structure_badges": ["IAn Agency", "control-plane", "saleable-core"],
    },
    "lavprishjemmeside-cms": {
        "summary": "Remote-first CMS governance with explicit client-site oversight.",
        "structure_badges": ["CMS", "client-sites", "lavprishjemmeside.dk", "ljdesignstudio.dk"],
    },
    "artisan-reporting": {
        "summary": "Billy-backed reporting workflows and accounting operations.",
        "structure_badges": ["reporting", "billy", "cpanel"],
    },
    "artisan-wordpress": {
        "summary": "Primary Artisan website, B2B workflows, and commerce integrations.",
        "structure_badges": ["wordpress", "b2b", "commerce"],
    },
    "artisan-email-marketing": {
        "summary": "Campaign workspace retained as planned follow-on delivery.",
        "structure_badges": ["planned", "campaigns", "brevo"],
    },
    "baltzer-tcg-index": {
        "summary": "Retained as a migration-hold contract until a local datastore replacement lands.",
        "structure_badges": ["migration-hold", "pricing", "not-live"],
    },
    "baltzer-reporting": {
        "summary": "Reporting surface carried forward from the original portfolio.",
        "structure_badges": ["reporting", "operations", "json-state"],
    },
    "baltzer-shopify": {
        "summary": "Commerce operations and adjacent placeholder product tracks.",
        "structure_badges": ["shopify", "operations", "product-tracks"],
    },
    "personal-assistant-suite": {
        "summary": "Skeleton program preserved for future internal assistance modules.",
        "structure_badges": ["skeleton", "internal", "planned"],
    },
    "samlino-seo-agent-playground": {
        "summary": "Mapped context workspace, sandbox pages, and archive-carried operational research.",
        "structure_badges": ["context", "sandbox", "archive-mapped"],
    },
}

DOMAIN_ORDER = {
    "platform": 0,
    "lavprishjemmeside": 1,
    "artisan": 2,
    "baltzer": 3,
    "personal-assistant": 4,
    "samlino": 5,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _resolve_agent_id(agent_id: str) -> str:
    normalized = str(agent_id or "").strip().lower()
    return "father" if normalized in {"ian", ""} else normalized


def _display_name(agent_id: str, fallback: str | None = None) -> str:
    normalized = str(agent_id or "").strip().lower()
    return fallback or DISPLAY_NAMES.get(normalized, normalized.replace("-", " ").title())


def _token_estimate(text: str) -> int:
    return max(1, len(text) // 4) if text else 0


def _master_root(project_root: Path, agent_id: str) -> Path:
    rel = MASTER_ROOTS.get(str(agent_id).strip().lower())
    if not rel:
        return project_root / "agents" / str(agent_id)
    return project_root / rel


def _specialist_root(project_root: Path, row: dict[str, Any]) -> Path:
    source_path = str(row.get("source_path") or "").strip()
    return project_root / source_path if source_path else project_root / "agents"


def _file_health(agent_root: Path) -> dict[str, Any]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=STALE_AFTER_DAYS)
    files: list[dict[str, Any]] = []
    missing_required: list[str] = []
    present_count = 0
    token_total = 0
    for filename in CANONICAL_FILE_ORDER:
        path = agent_root / filename
        exists = path.is_file()
        stale = False
        updated_at = None
        tokens = 0
        if exists:
            present_count += 1
            stat = path.stat()
            updated_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(timespec="seconds")
            stale = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc) < cutoff
            text = path.read_text(errors="ignore")
            tokens = _token_estimate(text)
            token_total += tokens
        else:
            missing_required.append(filename)
        files.append(
            {
                "filename": filename,
                "present": exists,
                "stale": stale,
                "updated_at": updated_at,
                "token_estimate": tokens,
                "path": str(path),
            }
        )
    return {
        "files": files,
        "missing_required": missing_required,
        "completeness_pct": round((present_count / len(CANONICAL_FILE_ORDER)) * 100, 1),
        "token_estimate": token_total,
    }


def _program_lookup(db_client) -> dict[str, dict[str, Any]]:
    return {
        str(row["id"]): row
        for row in db_client.fetch_all(
            "SELECT id, name, domain, owner_master_id, app_status FROM program_registry ORDER BY domain, name"
        )
    }


def _active_routes(route_entries: list[dict[str, Any]] | None) -> set[str]:
    return {str(item.get("path") or "") for item in (route_entries or [])}


def _master_program_id(db_client, agent_id: str) -> str | None:
    rows = db_client.fetch_all(
        "SELECT program_id FROM agent_program_assignments WHERE agent_id = ? AND status = 'active' ORDER BY priority ASC, program_id ASC",
        (str(agent_id).strip(),),
    )
    unique = sorted({str(row.get("program_id") or "").strip() for row in rows if row.get("program_id")})
    return unique[0] if len(unique) == 1 else None


def _build_master_rows(db_client, project_root: Path) -> list[dict[str, Any]]:
    program_map = _program_lookup(db_client)
    rows = db_client.fetch_all("SELECT id, name, type, status, description FROM master_agents ORDER BY id ASC")
    result: list[dict[str, Any]] = []
    for row in rows:
        agent_id = str(row.get("id") or "").strip().lower()
        root = _master_root(project_root, agent_id)
        health = _file_health(root)
        program_id = _master_program_id(db_client, agent_id)
        program = program_map.get(program_id or "")
        role = "father" if agent_id == "father" else ("lead" if agent_id == "engineer" else "master")
        result.append(
            {
                "id": agent_id,
                "name": _display_name(agent_id, str(row.get("name") or "").strip() or None),
                "role": role,
                "program_id": program_id,
                "program_name": (program or {}).get("name"),
                "status": "online" if root.exists() else "missing",
                "root_path": str(root),
                "context_completeness_pct": health["completeness_pct"],
                "token_estimate": health["token_estimate"],
                "missing_required_files": health["missing_required"],
                "files": health["files"],
                "kind": str(row.get("type") or "master"),
            }
        )
    return result


def _build_specialist_rows(db_client, project_root: Path) -> list[dict[str, Any]]:
    program_map = _program_lookup(db_client)
    rows = db_client.fetch_all("SELECT * FROM specialist_agents ORDER BY owner_master_id ASC, id ASC")
    result: list[dict[str, Any]] = []
    for row in rows:
        specialist_id = str(row.get("id") or "").strip()
        root = _specialist_root(project_root, row)
        health = _file_health(root)
        program = program_map.get(str(row.get("program_id") or ""))
        result.append(
            {
                "id": specialist_id,
                "name": str(row.get("name") or specialist_id),
                "role": "specialist",
                "program_id": row.get("program_id"),
                "program_name": (program or {}).get("name"),
                "application_id": row.get("application_id"),
                "owner_master_id": row.get("owner_master_id"),
                "status": "online" if root.exists() and str(row.get("status") or "") != "dormant" else str(row.get("status") or "missing"),
                "root_path": str(root),
                "context_completeness_pct": health["completeness_pct"],
                "token_estimate": health["token_estimate"],
                "missing_required_files": health["missing_required"],
                "files": health["files"],
                "kind": str(row.get("agent_kind") or "specialist"),
            }
        )
    return result


def _all_agents(db_client, project_root: Path) -> list[dict[str, Any]]:
    agents = _build_master_rows(db_client, project_root) + _build_specialist_rows(db_client, project_root)
    return sorted(
        agents,
        key=lambda item: (
            item["role"] != "father",
            item["role"] != "lead",
            item["role"] != "master",
            str(item.get("name") or ""),
        ),
    )


def build_shell_hud_payload(db_client, project_root: Path) -> dict[str, Any]:
    runs_active = db_client.fetch_one(
        "SELECT COUNT(*) AS total FROM orchestration_flow_runs WHERE status IN ('queued','in_progress')"
    )
    errors = db_client.fetch_one("SELECT COUNT(*) AS total FROM error_log WHERE status = 'open'")
    escalations = db_client.fetch_one("SELECT COUNT(*) AS total FROM task_escalations WHERE status = 'open'")
    agents = _all_agents(db_client, project_root)
    agents_online = sum(1 for item in agents if str(item.get("status")) in {"online", "active"})
    last_event = db_client.fetch_one(
        "SELECT MAX(ts) AS last_event FROM ("
        "SELECT MAX(updated_at) AS ts FROM task_queue "
        "UNION ALL SELECT MAX(created_at) AS ts FROM orchestration_flow_runs "
        "UNION ALL SELECT MAX(created_at) AS ts FROM task_escalations"
        ") events"
    )
    return {
        "generated_at": _now_iso(),
        "runs_active": int((runs_active or {}).get("total") or 0),
        "agents_online": agents_online,
        "last_event": (last_event or {}).get("last_event"),
        "alerts_open": int((errors or {}).get("total") or 0) + int((escalations or {}).get("total") or 0),
        "clock_tz": "Europe/Copenhagen",
    }


def build_agents_payload(db_client, project_root: Path) -> dict[str, Any]:
    agents = _all_agents(db_client, project_root)
    return {
        "generated_at": _now_iso(),
        "agents": [
            {
                "id": item["id"],
                "name": item["name"],
                "role": item["role"],
                "program_id": item.get("program_id"),
                "program_name": item.get("program_name"),
                "status": item["status"],
                "context_completeness_pct": item["context_completeness_pct"],
                "token_estimate": item["token_estimate"],
                "missing_required_files": item["missing_required_files"],
                "kind": item["kind"],
            }
            for item in agents
        ],
        "totals": {
            "agents": len(agents),
            "masters": sum(1 for item in agents if item["role"] in {"father", "lead", "master"}),
            "specialists": sum(1 for item in agents if item["role"] == "specialist"),
        },
    }


def build_agent_context_payload(db_client, project_root: Path, agent_id: str) -> dict[str, Any]:
    lookup = _resolve_agent_id(agent_id)
    agents = {str(item["id"]).lower(): item for item in _all_agents(db_client, project_root)}
    agent = agents.get(lookup)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_id}")
    return {
        "generated_at": _now_iso(),
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "role": agent["role"],
        "program_id": agent.get("program_id"),
        "program_name": agent.get("program_name"),
        "root_path": agent["root_path"],
        "files": agent["files"],
        "effective_context_packet": {
            "token_estimate": agent["token_estimate"],
            "completeness_pct": agent["context_completeness_pct"],
        },
        "missing_required_files": agent["missing_required_files"],
    }


def build_agent_coverage_payload(db_client, project_root: Path) -> dict[str, Any]:
    agents = _all_agents(db_client, project_root)
    rows = []
    for item in agents:
        rows.append(
            {
                "agent_id": item["id"],
                "agent_name": item["name"],
                "role": item["role"],
                "program_id": item.get("program_id"),
                "program_name": item.get("program_name"),
                "files_present": sum(1 for file in item["files"] if file["present"]),
                "files_missing": sum(1 for file in item["files"] if not file["present"]),
                "missing_required_count": len(item["missing_required_files"]),
                "completeness_pct": item["context_completeness_pct"],
                "status": item["status"],
            }
        )
    return {
        "generated_at": _now_iso(),
        "agents": rows,
        "totals": {
            "agents": len(rows),
            "critical": sum(1 for item in rows if item["missing_required_count"] > 0),
            "complete": sum(1 for item in rows if item["missing_required_count"] == 0),
        },
    }


def build_floor_payload(db_client, project_root: Path) -> dict[str, Any]:
    program_rows = db_client.fetch_all(
        "SELECT id, name, domain, app_status FROM program_registry WHERE app_status IN ('active','planned') ORDER BY domain ASC, name ASC"
    )
    agents = _all_agents(db_client, project_root)
    by_program: dict[str, dict[str, Any]] = {}
    for program in program_rows:
        by_program[str(program["id"])] = {
            "program_id": program["id"],
            "program_name": program["name"],
            "domain": program["domain"],
            "status": program["app_status"],
            "masters": [],
            "specialists": [],
        }
    unassigned: list[dict[str, Any]] = []
    for item in agents:
        if item["role"] in {"father", "lead"}:
            continue
        program_id = str(item.get("program_id") or "")
        bucket = by_program.get(program_id)
        if not bucket:
            unassigned.append(item)
            continue
        if item["role"] == "specialist":
            bucket["specialists"].append(item)
        else:
            bucket["masters"].append(item)
    program_groups = []
    for program in program_rows:
        bucket = by_program[str(program["id"])]
        program_groups.append(
            {
                "program_id": bucket["program_id"],
                "program_name": bucket["program_name"],
                "domain": bucket["domain"],
                "status": bucket["status"],
                "masters": bucket["masters"],
                "specialists": bucket["specialists"],
                "master_count": len(bucket["masters"]),
                "specialist_count": len(bucket["specialists"]),
                "has_active_run": bool(
                    db_client.fetch_one(
                        "SELECT r.id FROM orchestration_flow_runs r JOIN orchestration_flows f ON f.id = r.flow_id "
                        "WHERE f.program_id = ? AND r.status IN ('queued','in_progress') LIMIT 1",
                        (program["id"],),
                    )
                ),
            }
        )
    desk_map = {item["id"]: item for item in agents}
    return {
        "generated_at": _now_iso(),
        "ian_desk": desk_map.get("father"),
        "engineer_desk": desk_map.get("engineer"),
        "program_groups": program_groups,
        "unassigned": unassigned,
        "totals": {
            "programs": len(program_rows),
            "agents": len(agents),
            "unassigned_agents": len(unassigned),
        },
    }


def build_floor_agent_drawer_payload(db_client, project_root: Path, agent_id: str) -> dict[str, Any]:
    payload = build_agent_context_payload(db_client, project_root, agent_id)
    payload["links"] = {
        "config": f"/agents/configs/{payload['agent_id']}",
        "activity": f"/agents/{payload['agent_id']}/activity",
        "chat": f"/agents/{payload['agent_id']}/chat",
    }
    return payload


def build_programs_overview_payload(db_client) -> dict[str, Any]:
    programs = db_client.fetch_all(
        "SELECT id, name, domain, owner_master_id, app_status FROM program_registry ORDER BY domain ASC, name ASC"
    )
    applications = fetch_applications(db_client)
    app_count_by_program: dict[str, int] = {}
    specialists_by_application: dict[str, int] = {}
    for row in db_client.fetch_all(
        "SELECT application_id, COUNT(*) AS total FROM specialist_agents WHERE application_id IS NOT NULL AND status = 'active' GROUP BY application_id"
    ):
        specialists_by_application[str(row["application_id"])] = int(row["total"])
    assignment_counts = {
        str(row["program_id"]): int(row["total"])
        for row in db_client.fetch_all(
            "SELECT program_id, COUNT(*) AS total FROM agent_program_assignments WHERE status = 'active' GROUP BY program_id"
        )
    }
    apps_by_program: dict[str, list[dict[str, Any]]] = {}
    for app in applications:
        program_id = str(app.get("program_id") or "")
        app_count_by_program[program_id] = app_count_by_program.get(program_id, 0) + 1
        apps_by_program.setdefault(program_id, []).append(
            {
                "id": app["id"],
                "name": app["name"],
                "status": app["status"],
                "kind": app["kind"],
                "health": "amber" if str(app["status"]).lower() != "active" else "green",
                "active_agents": specialists_by_application.get(str(app["id"]), 0),
            }
        )
    domains: dict[str, list[dict[str, Any]]] = {}
    for program in programs:
        nodes = apps_by_program.get(str(program["id"]), [])
        presentation = PROGRAM_PRESENTATION.get(str(program["id"]), {})
        domains.setdefault(str(program["domain"]), []).append(
            {
                "id": program["id"],
                "name": program["name"],
                "owner_master_id": program["owner_master_id"],
                "status": program["app_status"],
                "apps_count": app_count_by_program.get(str(program["id"]), 0),
                "agents_count": assignment_counts.get(str(program["id"]), 0),
                "summary": presentation.get("summary") or "",
                "structure_badges": presentation.get("structure_badges") or [],
                "active_run": bool(
                    db_client.fetch_one(
                        "SELECT r.id FROM orchestration_flow_runs r JOIN orchestration_flows f ON f.id = r.flow_id "
                        "WHERE f.program_id = ? AND r.status IN ('queued','in_progress') LIMIT 1",
                        (program["id"],),
                    )
                ),
                "applications": nodes,
            }
        )
    swimlanes = []
    for domain, rows in sorted(domains.items(), key=lambda item: (DOMAIN_ORDER.get(item[0], 99), item[0])):
        presentation = DOMAIN_PRESENTATION.get(domain, {})
        swimlanes.append(
            {
                "domain": domain,
                "label": presentation.get("label") or domain.replace("-", " ").title(),
                "description": presentation.get("description") or "",
                "portfolio_role": presentation.get("portfolio_role") or "program",
                "programs": rows,
            }
        )
    return {
        "generated_at": _now_iso(),
        "agency": AGENCY_OVERVIEW,
        "domains": swimlanes,
        "totals": {
            "domains": len(swimlanes),
            "programs": len(programs),
            "applications": len(applications),
        },
    }


def build_program_application_detail_payload(db_client, application_id: str) -> dict[str, Any]:
    app = get_application(db_client, application_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"Unknown application: {application_id}")
    specialists = db_client.fetch_all(
        "SELECT id, name, status, owner_master_id FROM specialist_agents WHERE application_id = ? ORDER BY id ASC",
        (str(application_id).strip(),),
    )
    latest_task = db_client.fetch_one(
        "SELECT id, status, objective, updated_at FROM task_queue WHERE application_id = ? "
        "ORDER BY datetime(COALESCE(updated_at, created_at)) DESC LIMIT 1",
        (str(application_id).strip(),),
    )
    notes = []
    if not specialists:
        notes.append("No application-specific specialists are currently projected into the runtime.")
    if latest_task and str(latest_task.get("status") or "") in {"failed", "blocked"}:
        notes.append("Latest task is failed or blocked.")
    if not notes:
        notes.append("No immediate risk markers detected.")
    return {
        "generated_at": _now_iso(),
        "application": app,
        "assigned_agents": specialists,
        "latest_task": latest_task,
        "health_notes": notes,
    }


def build_reporting_loss_pending_payload(
    db_client,
    project_root: Path,
    route_entries: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    active = _active_routes(route_entries)
    coverage = build_agent_coverage_payload(db_client, project_root)
    expected = [
        "/api/control-ui/agents",
        "/api/control-ui/orchestration/overview",
        "/api/control-ui/orchestration/runs",
        "/api/control-ui/programs/overview",
        "/api/control-ui/reporting/loss-pending",
        "/api/control-ui/reporting/agent-coverage",
        "/api/control-ui/secrets/status",
    ]
    api_health = [
        {"route": route, "status": "active" if route in active else "missing", "notes": "Phase 5 required route"}
        for route in expected
    ]
    lost_pending = [
        {"feature": "Normalized agent roster", "v1_status": "legacy", "v2_status": "partial", "v21_target": "active", "priority": "P0", "state": "healthy" if "/api/control-ui/agents" in active else "lost"},
        {"feature": "Orchestration overview", "v1_status": "legacy", "v2_status": "missing", "v21_target": "active", "priority": "P0", "state": "healthy" if "/api/control-ui/orchestration/overview" in active else "lost"},
        {"feature": "Program overview", "v1_status": "legacy", "v2_status": "partial", "v21_target": "active", "priority": "P0", "state": "healthy" if "/api/control-ui/programs/overview" in active else "lost"},
        {"feature": "Secrets status", "v1_status": "missing", "v2_status": "missing", "v21_target": "active", "priority": "P0", "state": "healthy" if "/api/control-ui/secrets/status" in active else "lost"},
    ]
    missing_counts = {filename: 0 for filename in CANONICAL_FILE_ORDER}
    for row in coverage["agents"]:
        missing = max(0, int(row["files_missing"]))
        if missing:
            for filename in CANONICAL_FILE_ORDER[:missing]:
                missing_counts[filename] += 1
    most_common_gap = max(missing_counts.items(), key=lambda item: item[1])[0] if missing_counts else None
    return {
        "generated_at": _now_iso(),
        "lost_vs_pending": lost_pending,
        "api_health": api_health,
        "agent_config_coverage": {
            "total_agents": coverage["totals"]["agents"],
            "files_missing": sum(item["files_missing"] for item in coverage["agents"]),
            "critical_agents": coverage["totals"]["critical"],
            "most_common_gap": most_common_gap,
            "critical_master_agents": [
                item["agent_name"]
                for item in coverage["agents"]
                if item["role"] in {"father", "lead", "master"} and item["files_missing"] > 0
            ],
        },
        "definition_of_done": [
            {"id": "routes", "label": "Normalized control-plane read routes exist", "checked": "/api/control-ui/agents" in active},
            {"id": "orchestration", "label": "Normalized orchestration routes exist", "checked": "/api/control-ui/orchestration/overview" in active},
            {"id": "programs", "label": "Programs overview route exists", "checked": "/api/control-ui/programs/overview" in active},
            {"id": "secrets", "label": "Secrets status route exists", "checked": "/api/control-ui/secrets/status" in active},
        ],
    }

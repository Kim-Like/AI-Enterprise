"""Explicit runtime bootstrap for AI-Enterprise."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import uuid

from api.config import Settings, load_settings
from api.db.client import DatabaseClient
from api.system.application_registry import sync_application_registry
from api.system.autonomy_service import sync_autonomy_topology_state
from api.system.program_registry import sync_registry
from api.system.specialist_service import sync_specialists


@dataclass
class RuntimeContext:
    settings: Settings
    db: DatabaseClient
    runtime_id: str
    started_at: str


def build_runtime(
    *,
    project_root: Path | None = None,
    db_path_override: str | None = None,
) -> RuntimeContext:
    settings = load_settings(project_root=project_root, db_path_override=db_path_override)
    db = DatabaseClient(db_path=str(settings.db_path), schema_path=str(settings.schema_path))
    return RuntimeContext(
        settings=settings,
        db=db,
        runtime_id=str(uuid.uuid4()),
        started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def run_startup(runtime: RuntimeContext) -> dict[str, object]:
    registry_sync = sync_registry(
        db_client=runtime.db,
        project_root=runtime.settings.project_root,
    )
    application_sync = sync_application_registry(
        db_client=runtime.db,
        project_root=runtime.settings.project_root,
        catalog_path=runtime.settings.application_catalog_path,
    )
    specialist_sync = sync_specialists(
        db_client=runtime.db,
        project_root=runtime.settings.project_root,
    )
    autonomy_sync = sync_autonomy_topology_state(
        db_client=runtime.db,
        project_root=runtime.settings.project_root,
    )
    return {
        "status": "ok",
        "db_path": str(runtime.settings.db_path),
        "project_root": str(runtime.settings.project_root),
        "steps": [
            "database_initialized",
            "registry_synchronized",
            "applications_synchronized",
            "specialists_synchronized",
            "autonomy_topology_synchronized",
        ],
        "registry_sync": registry_sync,
        "application_sync": application_sync,
        "specialist_sync": specialist_sync,
        "autonomy_sync": autonomy_sync,
    }

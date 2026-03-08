"""Application registry routes."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

from api.security.admin_auth import require_admin_key, require_write_authorization
from api.system.application_registry import (
    fetch_application_map,
    fetch_applications,
    get_application,
    sync_application_registry,
)
from api.system.program_registry import sync_registry
from api.system.specialist_service import sync_specialists

router = APIRouter(tags=["applications"])


@router.get("/applications")
def list_applications(
    request: Request,
    status: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
):
    require_write_authorization(request)
    rows = fetch_applications(request.app.state.db, status=status, domain=domain)
    return {"applications": rows}


@router.get("/applications/{app_id}")
def get_application_by_id(app_id: str, request: Request):
    require_write_authorization(request)
    row = get_application(request.app.state.db, app_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    return row


@router.post("/applications/rescan")
def rescan_applications(request: Request):
    require_admin_key(request)
    db = request.app.state.db
    project_root = Path(request.app.state.project_root)
    registry_sync = sync_registry(db_client=db, project_root=project_root)
    application_sync = sync_application_registry(
        db_client=db,
        project_root=project_root,
        catalog_path=request.app.state.settings.application_catalog_path,
    )
    specialist_sync = sync_specialists(db_client=db, project_root=project_root)
    return {
        "status": "rescanned",
        "registry_sync": registry_sync,
        "application_sync": application_sync,
        "specialist_sync": specialist_sync,
        "application_map": fetch_application_map(db),
    }

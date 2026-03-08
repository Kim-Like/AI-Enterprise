"""Datastore verification routes."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request

from api.security.admin_auth import require_write_authorization
from api.system.program_registry import verify_datastores

router = APIRouter(tags=["datastores"])


@router.get("/datastores/verify")
def verify_datastore_config(request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    project_root = Path(request.app.state.project_root)
    rows = verify_datastores(db_client=db, project_root=project_root)
    return {
        "status": "ok",
        "verified_count": len(rows),
        "datastores": rows,
    }

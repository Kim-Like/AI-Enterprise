"""Secrets and connection-status routes."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from api.security.admin_auth import require_admin_key, require_write_authorization
from api.system.connection_status import build_secret_status_payload, test_secret_or_connection

router = APIRouter(tags=["secrets"])


@router.get("/control-ui/secrets/status")
def get_secret_status(request: Request):
    require_write_authorization(request)
    return build_secret_status_payload(
        settings=request.app.state.settings,
        project_root=Path(request.app.state.project_root),
        db_client=request.app.state.db,
    )


@router.post("/control-ui/secrets/test/{key_name}")
def test_secret_connection(key_name: str, request: Request):
    require_admin_key(request)
    result = test_secret_or_connection(
        key_name=key_name,
        settings=request.app.state.settings,
        project_root=Path(request.app.state.project_root),
        db_client=request.app.state.db,
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown secret or connection target: {key_name}")
    return {"status": "ok", "result": result}

"""Settings routes with consistent admin-only authorization."""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from api.security.admin_auth import require_admin_key

router = APIRouter(tags=["settings"])


class SettingUpdate(BaseModel):
    value: str
    description: str = ""


@router.get("/settings")
def list_settings(request: Request):
    require_admin_key(request)
    db = request.app.state.db
    return db.fetch_all("SELECT key, value, description, updated_at FROM settings ORDER BY key")


@router.put("/settings/{key}")
def update_setting(key: str, payload: SettingUpdate, request: Request):
    require_admin_key(request)
    db = request.app.state.db
    db.set_setting(key, payload.value, payload.description)
    return {"key": key, "value": payload.value}

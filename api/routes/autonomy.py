"""Autonomy policy and governed provisioning routes."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from api.security.admin_auth import require_write_authorization
from api.system.autonomy_service import (
    WAVE_1_ONLY_MODE,
    build_autonomy_policy_payload,
    build_provisioning_preflight_payload,
    enforce_provisioning_policy,
)

router = APIRouter(tags=["autonomy"])


class ProvisioningPreflightRequest(BaseModel):
    repo_ids: list[str] = Field(default_factory=list)
    requested_mode: str = WAVE_1_ONLY_MODE


def _project_root(request: Request) -> Path:
    return Path(request.app.state.project_root)


@router.get("/autonomy/policy")
def get_autonomy_policy(request: Request):
    require_write_authorization(request)
    return {
        "status": "ok",
        "policy": build_autonomy_policy_payload(
            db_client=request.app.state.db,
            project_root=_project_root(request),
        ),
    }


@router.post("/autonomy/provisioning/preflight")
def post_autonomy_provisioning_preflight(payload: ProvisioningPreflightRequest, request: Request):
    require_write_authorization(request)
    policy = enforce_provisioning_policy(
        db_client=request.app.state.db,
        project_root=_project_root(request),
        repo_ids=payload.repo_ids,
        requested_mode=payload.requested_mode,
    )
    report = build_provisioning_preflight_payload(
        project_root=_project_root(request),
        repo_ids=payload.repo_ids or policy["allowed_repository_ids"],
        requested_mode=payload.requested_mode,
    )
    report["policy"] = policy
    return report

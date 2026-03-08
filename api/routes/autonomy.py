"""Autonomy policy and governed provisioning routes."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from api.security.admin_auth import require_write_authorization
from api.system.autonomy_service import (
    build_autonomy_policy_payload,
    build_executor_contract_payload,
    build_provisioning_preflight_payload,
    execute_autonomy_run,
    enforce_provisioning_policy,
    list_autonomy_runs,
    list_autonomy_sync_rows,
    DEFAULT_AUTONOMY_MODE,
)

router = APIRouter(tags=["autonomy"])


class ProvisioningPreflightRequest(BaseModel):
    repo_ids: list[str] = Field(default_factory=list)
    requested_mode: str = DEFAULT_AUTONOMY_MODE


class ExecutorRunRequest(BaseModel):
    actor_agent_id: str = "ian-master"
    repo_ids: list[str] = Field(default_factory=list)
    requested_mode: str = DEFAULT_AUTONOMY_MODE
    trigger_source: str = "manual_api"


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


@router.get("/autonomy/executor")
def get_autonomy_executor(request: Request):
    require_write_authorization(request)
    return {
        "status": "ok",
        "executor": build_executor_contract_payload(
            db_client=request.app.state.db,
            project_root=_project_root(request),
            settings=request.app.state.settings,
        ),
        "policy": build_autonomy_policy_payload(
            db_client=request.app.state.db,
            project_root=_project_root(request),
        ),
    }


@router.post("/autonomy/executor/run")
def post_autonomy_executor_run(payload: ExecutorRunRequest, request: Request):
    require_write_authorization(request)
    return execute_autonomy_run(
        db_client=request.app.state.db,
        project_root=_project_root(request),
        settings=request.app.state.settings,
        repo_ids=payload.repo_ids,
        requested_mode=payload.requested_mode,
        trigger_source=payload.trigger_source,
        actor_agent_id=payload.actor_agent_id,
    )


@router.get("/autonomy/audit/runs")
def get_autonomy_audit_runs(request: Request, limit: int = 20):
    require_write_authorization(request)
    return {
        "status": "ok",
        "runs": list_autonomy_runs(request.app.state.db, limit=max(1, min(int(limit), 100))),
    }


@router.get("/autonomy/sync/repositories")
def get_autonomy_sync_repositories(request: Request):
    require_write_authorization(request)
    return {
        "status": "ok",
        "repositories": list_autonomy_sync_rows(request.app.state.db),
    }

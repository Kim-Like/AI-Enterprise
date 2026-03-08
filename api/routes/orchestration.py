"""Compatibility and normalized orchestration routes."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from api.security.admin_auth import require_control_authority, require_write_authorization
from api.system.orchestration_service import (
    create_flow,
    create_flow_step,
    get_flow,
    get_flow_run,
    hub_activity,
    hub_overview,
    list_flow_runs,
    list_flow_steps,
    list_flows,
    retrigger_run_step,
    run_flow,
    update_flow,
    update_flow_step,
    update_run_context,
)

router = APIRouter(tags=["orchestration"])


def _generated_at() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class FlowCreateRequest(BaseModel):
    owner_agent_id: str
    name: str = Field(min_length=1)
    program_id: Optional[str] = None
    description: str = ""
    execution_mode: str = "locked_pipeline"
    schedule_kind: str = "placeholder"
    schedule_expr: str = ""
    status: str = "active"
    created_by: str = "workspace"


class FlowPatchRequest(BaseModel):
    owner_agent_id: Optional[str] = None
    name: Optional[str] = None
    program_id: Optional[str] = None
    description: Optional[str] = None
    execution_mode: Optional[str] = None
    schedule_kind: Optional[str] = None
    schedule_expr: Optional[str] = None
    status: Optional[str] = None


class FlowStepCreateRequest(BaseModel):
    step_order: int = Field(ge=1)
    agent_id: str
    objective_template: str = Field(min_length=1)
    input_contract_json: Dict[str, Any] = Field(default_factory=dict)
    output_schema_json: Dict[str, Any] = Field(default_factory=dict)
    retry_policy_json: Dict[str, Any] = Field(default_factory=dict)
    on_failure: str = "escalate"
    timeout_seconds: int = Field(default=120, ge=1)


class FlowStepPatchRequest(BaseModel):
    step_id: str
    step_order: Optional[int] = Field(default=None, ge=1)
    agent_id: Optional[str] = None
    objective_template: Optional[str] = None
    input_contract_json: Optional[Dict[str, Any]] = None
    output_schema_json: Optional[Dict[str, Any]] = None
    retry_policy_json: Optional[Dict[str, Any]] = None
    on_failure: Optional[str] = None
    timeout_seconds: Optional[int] = Field(default=None, ge=1)


class FlowRunRequest(BaseModel):
    trigger_type: str = "manual"
    triggered_by: str = "workspace"
    root_thread_id: Optional[str] = None
    run_context_json: Dict[str, Any] = Field(default_factory=dict)


class RunContextPatchRequest(BaseModel):
    run_context_json: Dict[str, Any] = Field(default_factory=dict)


class RunStepRetriggerRequest(BaseModel):
    triggered_by: str = "workspace"


class ControlUiTriggerRequest(BaseModel):
    flow_id: str
    trigger_type: str = "manual"
    triggered_by: str = "workspace"
    root_thread_id: Optional[str] = None
    run_context_json: Dict[str, Any] = Field(default_factory=dict)


@router.get("/orchestration/hub/overview")
def get_orchestration_hub_overview(request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    payload = hub_overview(db_client=db)
    payload["generated_at"] = _generated_at()
    return payload


@router.get("/orchestration/hub/activity")
def get_orchestration_hub_activity(
    request: Request,
    limit: int = Query(200, ge=1, le=500),
):
    require_write_authorization(request)
    db = request.app.state.db
    payload = hub_activity(db_client=db, limit=limit)
    payload["generated_at"] = _generated_at()
    return payload


@router.get("/orchestration/flows")
def get_orchestration_flows(
    request: Request,
    owner_agent_id: Optional[str] = Query(None),
    program_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    require_write_authorization(request)
    db = request.app.state.db
    return {
        "generated_at": _generated_at(),
        "flows": list_flows(
            db_client=db,
            owner_agent_id=owner_agent_id,
            program_id=program_id,
            status=status,
        ),
    }


@router.post("/orchestration/flows")
def post_orchestration_flow(payload: FlowCreateRequest, request: Request):
    require_write_authorization(request)
    require_control_authority(request=request, agent_id=payload.owner_agent_id)
    db = request.app.state.db
    return create_flow(
        db_client=db,
        owner_agent_id=payload.owner_agent_id,
        name=payload.name,
        program_id=payload.program_id,
        description=payload.description,
        execution_mode=payload.execution_mode,
        schedule_kind=payload.schedule_kind,
        schedule_expr=payload.schedule_expr,
        status=payload.status,
        created_by=payload.created_by,
    )


@router.patch("/orchestration/flows/{flow_id}")
def patch_orchestration_flow(flow_id: str, payload: FlowPatchRequest, request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    current = get_flow(db_client=db, flow_id=flow_id)
    require_control_authority(request=request, agent_id=current["owner_agent_id"])
    return update_flow(
        db_client=db,
        flow_id=flow_id,
        owner_agent_id=payload.owner_agent_id,
        name=payload.name,
        program_id=payload.program_id,
        description=payload.description,
        execution_mode=payload.execution_mode,
        schedule_kind=payload.schedule_kind,
        schedule_expr=payload.schedule_expr,
        status=payload.status,
    )


@router.get("/orchestration/flows/{flow_id}/steps")
def get_orchestration_flow_steps(flow_id: str, request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    return {
        "generated_at": _generated_at(),
        "flow_id": flow_id,
        "steps": list_flow_steps(db_client=db, flow_id=flow_id),
    }


@router.post("/orchestration/flows/{flow_id}/steps")
def post_orchestration_flow_step(flow_id: str, payload: FlowStepCreateRequest, request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    flow = get_flow(db_client=db, flow_id=flow_id)
    require_control_authority(request=request, agent_id=flow["owner_agent_id"])
    step = create_flow_step(
        db_client=db,
        flow_id=flow_id,
        step_order=payload.step_order,
        agent_id=payload.agent_id,
        objective_template=payload.objective_template,
        input_contract_json=payload.input_contract_json,
        output_schema_json=payload.output_schema_json,
        retry_policy_json=payload.retry_policy_json,
        on_failure=payload.on_failure,
        timeout_seconds=payload.timeout_seconds,
    )
    return {
        "generated_at": _generated_at(),
        "flow_id": flow_id,
        "step": step,
        "steps": list_flow_steps(db_client=db, flow_id=flow_id),
    }


@router.patch("/orchestration/flows/{flow_id}/steps")
def patch_orchestration_flow_step(flow_id: str, payload: FlowStepPatchRequest, request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    flow = get_flow(db_client=db, flow_id=flow_id)
    require_control_authority(request=request, agent_id=flow["owner_agent_id"])
    step = update_flow_step(
        db_client=db,
        flow_id=flow_id,
        step_id=payload.step_id,
        step_order=payload.step_order,
        agent_id=payload.agent_id,
        objective_template=payload.objective_template,
        input_contract_json=payload.input_contract_json,
        output_schema_json=payload.output_schema_json,
        retry_policy_json=payload.retry_policy_json,
        on_failure=payload.on_failure,
        timeout_seconds=payload.timeout_seconds,
    )
    return {
        "generated_at": _generated_at(),
        "flow_id": flow_id,
        "step": step,
        "steps": list_flow_steps(db_client=db, flow_id=flow_id),
    }


@router.post("/orchestration/flows/{flow_id}/run")
def post_orchestration_flow_run(flow_id: str, payload: FlowRunRequest, request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    flow = get_flow(db_client=db, flow_id=flow_id)
    require_control_authority(request=request, agent_id=flow["owner_agent_id"])
    return run_flow(
        db_client=db,
        flow_id=flow_id,
        trigger_type=payload.trigger_type,
        triggered_by=payload.triggered_by,
        root_thread_id=payload.root_thread_id,
        run_context_json=payload.run_context_json,
    )


@router.get("/orchestration/runs/{run_id}")
def get_orchestration_run(run_id: str, request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    payload = get_flow_run(db_client=db, run_id=run_id)
    payload["generated_at"] = _generated_at()
    return payload


@router.patch("/orchestration/runs/{run_id}/context")
def patch_orchestration_run_context(run_id: str, payload: RunContextPatchRequest, request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    current = get_flow_run(db_client=db, run_id=run_id)
    owner_agent_id = str((current.get("flow") or {}).get("owner_agent_id") or "")
    require_control_authority(request=request, agent_id=owner_agent_id)
    return update_run_context(
        db_client=db,
        run_id=run_id,
        run_context_json=payload.run_context_json,
    )


@router.post("/orchestration/runs/{run_id}/steps/{step_id}/retrigger")
def post_orchestration_run_step_retrigger(
    run_id: str,
    step_id: str,
    payload: RunStepRetriggerRequest,
    request: Request,
):
    require_write_authorization(request)
    db = request.app.state.db
    current = get_flow_run(db_client=db, run_id=run_id)
    owner_agent_id = str((current.get("flow") or {}).get("owner_agent_id") or "")
    require_control_authority(request=request, agent_id=owner_agent_id)
    return retrigger_run_step(
        db_client=db,
        run_id=run_id,
        step_id=step_id,
        triggered_by=payload.triggered_by,
    )


@router.get("/control-ui/orchestration/overview")
def get_control_ui_orchestration_overview(request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    overview = hub_overview(db_client=db)
    return {
        "generated_at": _generated_at(),
        "counts": overview["counts"],
        "health": overview["health"],
        "flows": overview["flows"],
        "sessions": overview["sessions"],
        "recent_runs": list_flow_runs(db_client=db, limit=20),
    }


@router.get("/control-ui/orchestration/runs")
def get_control_ui_orchestration_runs(
    request: Request,
    status: Optional[str] = Query(None),
    owner_agent_id: Optional[str] = Query(None),
    program_id: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=500),
):
    require_write_authorization(request)
    runs = list_flow_runs(
        db_client=request.app.state.db,
        status=status,
        owner_agent_id=owner_agent_id,
        program_id=program_id,
        limit=limit,
    )
    return {
        "generated_at": _generated_at(),
        "runs": runs,
        "filters": {
            "status": status,
            "owner_agent_id": owner_agent_id,
            "program_id": program_id,
            "limit": limit,
        },
        "totals": {
            "runs": len(runs),
            "in_progress": sum(1 for row in runs if row.get("status") == "in_progress"),
            "blocked": sum(1 for row in runs if row.get("status") == "blocked"),
            "completed": sum(1 for row in runs if row.get("status") == "completed"),
        },
    }


@router.get("/control-ui/orchestration/runs/{run_id}")
def get_control_ui_orchestration_run(run_id: str, request: Request):
    require_write_authorization(request)
    payload = get_flow_run(db_client=request.app.state.db, run_id=run_id)
    payload["generated_at"] = _generated_at()
    return payload


@router.post("/control-ui/orchestration/trigger")
def post_control_ui_orchestration_trigger(payload: ControlUiTriggerRequest, request: Request):
    require_write_authorization(request)
    db = request.app.state.db
    flow = get_flow(db_client=db, flow_id=payload.flow_id)
    require_control_authority(request=request, agent_id=flow["owner_agent_id"])
    result = run_flow(
        db_client=db,
        flow_id=payload.flow_id,
        trigger_type=payload.trigger_type,
        triggered_by=payload.triggered_by,
        root_thread_id=payload.root_thread_id,
        run_context_json=payload.run_context_json,
    )
    result["generated_at"] = _generated_at()
    return result

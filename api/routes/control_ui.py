"""Control-plane read routes and compatibility aliases."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request

from api.security.admin_auth import require_write_authorization
from api.system.control_ui_service import (
    build_agent_context_payload,
    build_agent_coverage_payload,
    build_agents_payload,
    build_floor_agent_drawer_payload,
    build_floor_payload,
    build_program_application_detail_payload,
    build_programs_overview_payload,
    build_reporting_loss_pending_payload,
    build_shell_hud_payload,
)

router = APIRouter(tags=["control-ui"])


def _project_root(request: Request) -> Path:
    return Path(request.app.state.project_root)


@router.get("/control-ui/shell/hud")
def get_control_ui_shell_hud(request: Request):
    require_write_authorization(request)
    return build_shell_hud_payload(request.app.state.db, _project_root(request))


@router.get("/control-ui/agents")
def get_control_ui_agents(request: Request):
    require_write_authorization(request)
    return build_agents_payload(request.app.state.db, _project_root(request))


@router.get("/control-ui/agents/{agent_id}/context-files")
def get_control_ui_agent_context_files(agent_id: str, request: Request):
    require_write_authorization(request)
    return build_agent_context_payload(request.app.state.db, _project_root(request), agent_id)


@router.get("/control-ui/programs/overview")
def get_control_ui_programs_overview(request: Request):
    require_write_authorization(request)
    return build_programs_overview_payload(request.app.state.db)


@router.get("/control-ui/programs/applications/{application_id}")
def get_control_ui_program_application_detail(application_id: str, request: Request):
    require_write_authorization(request)
    return build_program_application_detail_payload(request.app.state.db, application_id)


@router.get("/control-ui/reporting/agent-coverage")
def get_control_ui_agent_coverage(request: Request):
    require_write_authorization(request)
    return build_agent_coverage_payload(request.app.state.db, _project_root(request))


@router.get("/control-ui/reporting/loss-pending")
def get_control_ui_loss_pending(request: Request):
    require_write_authorization(request)
    routes = []
    for route in request.app.routes:
        methods = sorted(
            method
            for method in getattr(route, "methods", set())
            if method in {"GET", "POST", "PATCH", "PUT", "DELETE"}
        )
        routes.append({"path": getattr(route, "path", ""), "methods": methods})
    return build_reporting_loss_pending_payload(request.app.state.db, _project_root(request), routes)


@router.get("/control-ui/floor")
def get_control_ui_floor(request: Request):
    require_write_authorization(request)
    return build_floor_payload(request.app.state.db, _project_root(request))


@router.get("/control-ui/floor/agents/{agent_id}/drawer")
def get_control_ui_floor_agent_drawer(agent_id: str, request: Request):
    require_write_authorization(request)
    return build_floor_agent_drawer_payload(request.app.state.db, _project_root(request), agent_id)


@router.get("/control-ui/agents/configs")
def get_control_ui_agent_configs(request: Request):
    require_write_authorization(request)
    return build_agent_coverage_payload(request.app.state.db, _project_root(request))


@router.get("/control-ui/agents/configs/{agent_id}")
def get_control_ui_agent_config_detail(agent_id: str, request: Request):
    require_write_authorization(request)
    return build_agent_context_payload(request.app.state.db, _project_root(request), agent_id)


@router.get("/control-ui/report/state")
def get_control_ui_state_report(request: Request):
    require_write_authorization(request)
    routes = []
    for route in request.app.routes:
        methods = sorted(
            method
            for method in getattr(route, "methods", set())
            if method in {"GET", "POST", "PATCH", "PUT", "DELETE"}
        )
        routes.append({"path": getattr(route, "path", ""), "methods": methods})
    return build_reporting_loss_pending_payload(request.app.state.db, _project_root(request), routes)

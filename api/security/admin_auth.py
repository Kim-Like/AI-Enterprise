"""Header-based admin auth for mutating dashboard endpoints."""
from fastapi import HTTPException, Request

CONTROL_AUTHORITY_AGENTS = frozenset({"engineer", "father", "ian-master"})
DEFAULT_ADMIN_KEY_PLACEHOLDERS = frozenset(
    {
        "change-me-admin-key",
        "changeme",
        "replace-me",
        "your-admin-key",
    }
)


def _settings(request: Request):
    return request.app.state.settings


def _configured_admin_key(request: Request) -> str:
    settings = _settings(request)
    expected = (settings.dashboard_admin_key or "").strip()
    if not expected:
        return ""
    if not settings.allow_default_admin_key and expected.lower() in DEFAULT_ADMIN_KEY_PLACEHOLDERS:
        return ""
    return expected


def _configured_autonomy_key(request: Request) -> str:
    settings = _settings(request)
    return (settings.autonomy_key or "").strip()


def require_admin_key(request: Request) -> None:
    if not _configured_admin_key(request):
        raise HTTPException(status_code=503, detail="Admin key is not configured securely")
    if not has_admin_key(request):
        raise HTTPException(status_code=401, detail="Missing or invalid X-Admin-Key")


def has_admin_key(request: Request) -> bool:
    provided = request.headers.get("X-Admin-Key", "").strip()
    expected = _configured_admin_key(request)
    return bool(expected and provided and provided == expected)


def has_autonomy_key(request: Request) -> bool:
    settings = _settings(request)
    header_name = (settings.autonomy_header or "X-Autonomy-Key").strip() or "X-Autonomy-Key"
    provided = request.headers.get(header_name, "").strip()
    expected = _configured_autonomy_key(request)
    return bool(expected and provided and provided == expected)


def has_write_authorization(request: Request) -> bool:
    return has_admin_key(request) or has_autonomy_key(request)


def require_write_authorization(request: Request) -> None:
    if not (_configured_admin_key(request) or _configured_autonomy_key(request)):
        raise HTTPException(status_code=503, detail="Write authorization is not configured securely")
    if not has_write_authorization(request):
        raise HTTPException(status_code=401, detail="Missing or invalid write authorization key")


def is_control_authority_agent(agent_id: str) -> bool:
    return str(agent_id or "").strip().lower() in CONTROL_AUTHORITY_AGENTS


def require_control_authority(request: Request, agent_id: str) -> None:
    if not is_control_authority_agent(agent_id):
        return
    settings = _settings(request)
    header_name = (settings.autonomy_header or "X-Autonomy-Key").strip() or "X-Autonomy-Key"
    if not (_configured_admin_key(request) or _configured_autonomy_key(request)):
        raise HTTPException(status_code=503, detail="Write authorization is not configured securely")
    if not has_write_authorization(request):
        raise HTTPException(
            status_code=401,
            detail=f"Control authority for {agent_id} requires X-Admin-Key or {header_name}.",
        )

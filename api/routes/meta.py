"""Runtime diagnostics routes."""
from __future__ import annotations

import os
from typing import Dict, Set

from fastapi import APIRouter, Request

router = APIRouter(tags=["meta"])


REQUIRED_ROUTE_MAP: Dict[str, Set[str]] = {
    "/health": {"GET"},
    "/api/meta/runtime": {"GET"},
}


@router.get("/meta/runtime")
def get_runtime_meta(request: Request):
    app = request.app
    discovered: Dict[str, Set[str]] = {}
    for route in app.router.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not path or not methods:
            continue
        current = discovered.get(path, set())
        current.update(set(methods))
        discovered[path] = current

    required_status: Dict[str, bool] = {}
    for path, required_methods in REQUIRED_ROUTE_MAP.items():
        available = discovered.get(path, set())
        required_status[path] = required_methods.issubset(available)

    return {
        "status": "ok",
        "runtime_id": getattr(app.state, "runtime_id", "unknown"),
        "started_at": getattr(app.state, "started_at", None),
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "required_routes": required_status,
    }

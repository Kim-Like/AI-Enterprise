"""FastAPI entry point for AI-Enterprise."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from api.bootstrap import build_runtime, run_startup
from api.routes import (
    applications,
    autonomy,
    control_ui,
    datastores,
    health,
    meta,
    orchestration,
    secrets,
    settings,
)


def create_app(
    *,
    db_path_override: str | None = None,
    project_root_override: str | None = None,
) -> FastAPI:
    runtime = build_runtime(
        db_path_override=db_path_override,
        project_root=Path(project_root_override) if project_root_override else None,
    )
    dist_root = runtime.settings.project_root / "dist"
    dist_assets_root = dist_root / "assets"

    def ui_index_response():
        index_path = dist_root / "index.html"
        if not index_path.exists():
            return JSONResponse(
                status_code=503,
                content={"detail": "Frontend build not found. Run `npm run build` inside AI-Enterprise."},
            )
        return FileResponse(str(index_path))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.bootstrap_report = run_startup(runtime)
        yield

    app = FastAPI(
        title="AI-Enterprise Control Plane",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.db = runtime.db
    app.state.settings = runtime.settings
    app.state.project_root = str(runtime.settings.project_root)
    app.state.runtime_id = runtime.runtime_id
    app.state.started_at = runtime.started_at
    app.state.bootstrap_report = None

    app.add_middleware(
        CORSMiddleware,
        allow_origins=runtime.settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(applications.router, prefix="/api")
    app.include_router(autonomy.router, prefix="/api")
    app.include_router(control_ui.router, prefix="/api")
    app.include_router(datastores.router, prefix="/api")
    app.include_router(meta.router, prefix="/api")
    app.include_router(orchestration.router, prefix="/api")
    app.include_router(secrets.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")

    app.mount("/assets", StaticFiles(directory=str(dist_assets_root), check_dir=False), name="assets")

    @app.get("/", include_in_schema=False)
    def ui_home():
        return ui_index_response()

    @app.get("/programs", include_in_schema=False)
    def ui_programs():
        return ui_index_response()

    @app.get("/orchestration", include_in_schema=False)
    def ui_orchestration():
        return ui_index_response()

    @app.get("/orchestration-center", include_in_schema=False)
    def ui_orchestration_center():
        return ui_index_response()

    @app.get("/agents/configs", include_in_schema=False)
    def ui_agent_configs():
        return ui_index_response()

    @app.get("/agents/configs/{agent_id}", include_in_schema=False)
    def ui_agent_configs_detail(agent_id: str):
        _ = agent_id
        return ui_index_response()

    @app.get("/report", include_in_schema=False)
    def ui_report():
        return ui_index_response()

    @app.get("/secrets", include_in_schema=False)
    def ui_secrets():
        return ui_index_response()

    @app.get("/settings", include_in_schema=False)
    def ui_settings():
        return ui_index_response()

    @app.exception_handler(StarletteHTTPException)
    async def spa_not_found_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code != 404:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        path = request.url.path.lstrip("/").lower()
        accept = str(request.headers.get("accept") or "")
        wants_html = "text/html" in accept or "*/*" in accept
        if request.method == "GET" and wants_html and not path.startswith(("api", "assets", "docs", "redoc", "openapi.json", "health")):
            return ui_index_response()
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    return app

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app


def test_app_exposes_health_and_runtime_routes(tmp_path: Path):
    app = create_app(db_path_override=str(tmp_path / "runtime.db"))
    routes = {getattr(route, "path", "") for route in app.routes}
    assert "/health" in routes
    assert "/api/meta/runtime" in routes

    client = TestClient(app)
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"

    meta_response = client.get("/api/meta/runtime")
    assert meta_response.status_code == 200
    assert meta_response.json()["required_routes"]["/health"] is True
    assert meta_response.json()["required_routes"]["/api/meta/runtime"] is True


def test_schema_bootstrap_creates_core_tables(tmp_path: Path):
    db_path = tmp_path / "runtime.db"
    app = create_app(db_path_override=str(db_path))
    with TestClient(app):
        pass

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ("
            "'master_agents', 'program_registry', 'data_store_registry', 'application_registry'"
            ")"
        ).fetchall()
    finally:
        conn.close()

    assert {row[0] for row in rows} == {
        "master_agents",
        "program_registry",
        "data_store_registry",
        "application_registry",
    }


def test_phase_2_exclusions_are_not_present():
    project_root = Path("/Users/IAn/Agent/AI-Enterprise")
    assert not (project_root / "frontend").exists()
    assert not (project_root / "backend" / "static" / "ui").exists()
    assert not (project_root / "node_modules").exists()

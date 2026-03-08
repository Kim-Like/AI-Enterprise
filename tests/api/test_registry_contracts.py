from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app


EXPECTED_PROGRAM_IDS = {
    "ian-control-plane",
    "artisan-reporting",
    "artisan-wordpress",
    "artisan-email-marketing",
    "lavprishjemmeside-cms",
    "samlino-seo-agent-playground",
    "baltzer-tcg-index",
    "baltzer-reporting",
    "baltzer-shopify",
    "personal-assistant-suite",
}


def test_startup_sync_populates_registry_contracts(tmp_path: Path):
    app = create_app(db_path_override=str(tmp_path / "registry.db"))
    with TestClient(app):
        pass

    db = app.state.db
    programs = {row["id"] for row in db.fetch_all("SELECT id FROM program_registry")}
    applications = {row["id"] for row in db.fetch_all("SELECT id FROM application_registry")}
    datastores = {row["id"] for row in db.fetch_all("SELECT id FROM data_store_registry")}
    assignments = db.fetch_all("SELECT id FROM agent_program_assignments")

    assert programs == EXPECTED_PROGRAM_IDS
    assert "ian-mission-control" in applications
    assert "artisan-reporting-app" in applications
    assert "samlino-seo-agent-playground-app" in applications
    assert "baltzer-tcg-migration-hold" in datastores
    assert assignments


def test_phase_2_compatibility_artifacts_exist():
    project_root = Path("/Users/IAn/Agent/AI-Enterprise")
    compatibility = project_root / "docs" / "api-compatibility.md"
    assert compatibility.exists()
    text = compatibility.read_text()
    assert "ian-control-plane" in text
    assert "/api/meta/runtime" in text


def test_phase_2_exclusions_are_still_absent():
    project_root = Path("/Users/IAn/Agent/AI-Enterprise")
    assert not (project_root / "frontend").exists()
    assert not (project_root / "backend" / "static" / "ui").exists()
    assert not (project_root / "node_modules").exists()

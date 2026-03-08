from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app


def _client(monkeypatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "real-admin-key")
    monkeypatch.setenv("IAN_AUTONOMY_KEY", "auto-write")
    return TestClient(create_app(db_path_override=str(tmp_path / "control-ui.db")))


def test_specialist_sync_populates_runtime_projection(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        db = client.app.state.db
        total = db.fetch_one("SELECT COUNT(*) AS total FROM specialist_agents")
        assert int(total["total"]) >= 1
        assert db.fetch_one("SELECT id FROM specialist_agents WHERE id = 'spec.engineer.orchestration'") is not None
        assert db.fetch_one("SELECT id FROM specialist_agents WHERE id = 'gov.ian-mission-control'") is not None


def test_control_ui_routes_require_auth_and_return_agents(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        denied = client.get("/api/control-ui/agents")
        assert denied.status_code == 401

        allowed = client.get("/api/control-ui/agents", headers={"X-Autonomy-Key": "auto-write"})
        assert allowed.status_code == 200
        payload = allowed.json()
        agent_ids = {item["id"] for item in payload["agents"]}
        assert "father" in agent_ids
        assert "engineer" in agent_ids
        assert any(agent_id.startswith("spec.") for agent_id in agent_ids)

        detail = client.get(
            "/api/control-ui/agents/father/context-files",
            headers={"X-Autonomy-Key": "auto-write"},
        )
        assert detail.status_code == 200
        assert detail.json()["agent_id"] == "father"
        assert any(item["filename"] == "soul.md" and item["present"] for item in detail.json()["files"])


def test_program_and_application_routes_are_registry_backed(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        programs = client.get("/api/control-ui/programs/overview", headers={"X-Autonomy-Key": "auto-write"})
        assert programs.status_code == 200
        payload = programs.json()
        assert payload["agency"]["label"] == "IAn Agency"
        assert payload["totals"]["programs"] == 10
        lane_labels = {item["label"] for item in payload["domains"]}
        assert "Lavprishjemmeside" in lane_labels
        assert "IAn Agency Context" in lane_labels
        lavpris = next(
            program
            for lane in payload["domains"]
            for program in lane["programs"]
            if program["id"] == "lavprishjemmeside-cms"
        )
        assert "client-sites" in lavpris["structure_badges"]
        baltzer_tcg = next(
            program
            for lane in payload["domains"]
            for program in lane["programs"]
            if program["id"] == "baltzer-tcg-index"
        )
        assert baltzer_tcg["status"] == "planned"

        applications = client.get("/api/applications", headers={"X-Autonomy-Key": "auto-write"})
        assert applications.status_code == 200
        app_ids = {item["id"] for item in applications.json()["applications"]}
        assert "artisan-reporting-app" in app_ids

        detail = client.get(
            "/api/control-ui/programs/applications/artisan-reporting-app",
            headers={"X-Autonomy-Key": "auto-write"},
        )
        assert detail.status_code == 200
        assert detail.json()["application"]["id"] == "artisan-reporting-app"


def test_reporting_and_alias_routes_are_mapped(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        coverage = client.get("/api/control-ui/reporting/agent-coverage", headers={"X-Autonomy-Key": "auto-write"})
        assert coverage.status_code == 200
        assert coverage.json()["totals"]["agents"] >= 1

        report = client.get("/api/control-ui/reporting/loss-pending", headers={"X-Autonomy-Key": "auto-write"})
        assert report.status_code == 200
        assert any(item["route"] == "/api/control-ui/agents" for item in report.json()["api_health"])

        floor = client.get("/api/control-ui/floor", headers={"X-Autonomy-Key": "auto-write"})
        assert floor.status_code == 200
        assert floor.json()["ian_desk"]["id"] == "father"

        configs = client.get("/api/control-ui/agents/configs", headers={"X-Autonomy-Key": "auto-write"})
        assert configs.status_code == 200
        assert configs.json()["totals"]["agents"] >= 1

        state = client.get("/api/control-ui/report/state", headers={"X-Autonomy-Key": "auto-write"})
        assert state.status_code == 200
        assert "lost_vs_pending" in state.json()

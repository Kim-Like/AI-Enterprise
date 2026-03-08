from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app


def _client(monkeypatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "real-admin-key")
    monkeypatch.setenv("IAN_AUTONOMY_KEY", "auto-write")
    return TestClient(create_app(db_path_override=str(tmp_path / "orchestration.db")))


def _headers() -> dict[str, str]:
    return {"X-Autonomy-Key": "auto-write"}


def _create_flow_with_steps(client: TestClient) -> tuple[str, list[str]]:
    flow_response = client.post(
        "/api/orchestration/flows",
        headers=_headers(),
        json={
            "owner_agent_id": "engineer",
            "name": "Nightly Control Loop",
            "program_id": "ian-control-plane",
            "description": "Duplicate routing control loop",
            "created_by": "test",
        },
    )
    assert flow_response.status_code == 200
    flow_id = flow_response.json()["id"]

    step_ids: list[str] = []
    for step_order, agent_id in ((1, "spec.engineer.orchestration"), (2, "gov.ian-mission-control")):
        step_response = client.post(
            f"/api/orchestration/flows/{flow_id}/steps",
            headers=_headers(),
            json={
                "step_order": step_order,
                "agent_id": agent_id,
                "objective_template": f"Process step {step_order} for {{program_id}}",
                "input_contract_json": {"required": ["program_id"]},
                "output_schema_json": {"type": "object"},
            },
        )
        assert step_response.status_code == 200
        step_ids.append(step_response.json()["step"]["id"])
    return flow_id, step_ids


def _run_flow(client: TestClient, flow_id: str):
    return client.post(
        f"/api/orchestration/flows/{flow_id}/run",
        headers=_headers(),
        json={
            "trigger_type": "manual",
            "triggered_by": "test-suite",
            "run_context_json": {
                "priority": "P1",
                "program_id": "ian-control-plane",
                "application_id": "ian-mission-control",
            },
        },
    )


def test_flow_routes_require_write_auth(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        denied = client.post(
            "/api/orchestration/flows",
            json={"owner_agent_id": "engineer", "name": "Denied Flow"},
        )
        assert denied.status_code == 401


def test_flow_lifecycle_routes_create_and_list_runs(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        flow_id, _ = _create_flow_with_steps(client)
        run_response = _run_flow(client, flow_id)
        assert run_response.status_code == 200
        payload = run_response.json()
        assert payload["flow"]["id"] == flow_id
        assert payload["run"]["status"] == "in_progress"
        assert len(payload["steps"]) == 2
        assert payload["status_counts"]["in_progress"] == 1

        flows_response = client.get("/api/orchestration/flows?owner_agent_id=engineer", headers=_headers())
        assert flows_response.status_code == 200
        assert any(item["id"] == flow_id for item in flows_response.json()["flows"])

        runs_response = client.get("/api/control-ui/orchestration/runs", headers=_headers())
        assert runs_response.status_code == 200
        run_ids = {item["id"] for item in runs_response.json()["runs"]}
        assert payload["run"]["id"] in run_ids


def test_control_ui_overview_and_run_routes(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        flow_id, _ = _create_flow_with_steps(client)
        trigger_response = client.post(
            "/api/control-ui/orchestration/trigger",
            headers=_headers(),
            json={
                "flow_id": flow_id,
                "trigger_type": "manual",
                "triggered_by": "control-ui-test",
                "run_context_json": {"program_id": "ian-control-plane"},
            },
        )
        assert trigger_response.status_code == 200
        run_id = trigger_response.json()["run"]["id"]

        overview = client.get("/api/control-ui/orchestration/overview", headers=_headers())
        assert overview.status_code == 200
        overview_payload = overview.json()
        assert overview_payload["counts"]["total_flows"] >= 1
        assert any(item["id"] == flow_id for item in overview_payload["flows"])
        assert any(item["id"] == run_id for item in overview_payload["recent_runs"])

        detail = client.get(f"/api/control-ui/orchestration/runs/{run_id}", headers=_headers())
        assert detail.status_code == 200
        assert detail.json()["run"]["id"] == run_id

        hub = client.get("/api/orchestration/hub/overview", headers=_headers())
        assert hub.status_code == 200
        assert hub.json()["counts"]["total_flows"] >= 1


def test_retrigger_route_requeues_failed_step(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        flow_id, step_ids = _create_flow_with_steps(client)
        run_response = _run_flow(client, flow_id)
        assert run_response.status_code == 200
        run_id = run_response.json()["run"]["id"]
        failed_step_id = step_ids[0]
        failed_task_id = run_response.json()["steps"][0]["task_id"]

        db = client.app.state.db
        db.execute("UPDATE task_queue SET status = 'failed', execution_stage = 'failed' WHERE id = ?", (failed_task_id,))
        db.execute(
            "UPDATE orchestration_flow_run_steps SET status = 'failed', completed_at = datetime('now') WHERE run_id = ? AND step_id = ?",
            (run_id, failed_step_id),
        )
        db.execute("UPDATE orchestration_flow_runs SET status = 'failed', completed_at = datetime('now') WHERE id = ?", (run_id,))

        patch_response = client.patch(
            f"/api/orchestration/runs/{run_id}/context",
            headers=_headers(),
            json={"run_context_json": {"program_id": "ian-control-plane", "retry_reason": "test"}},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["updated_context_json"]["retry_reason"] == "test"

        retrigger = client.post(
            f"/api/orchestration/runs/{run_id}/steps/{failed_step_id}/retrigger",
            headers=_headers(),
            json={"triggered_by": "test-suite"},
        )
        assert retrigger.status_code == 200
        retrigger_payload = retrigger.json()
        assert retrigger_payload["retriggered_step"]["step_id"] == failed_step_id
        assert retrigger_payload["retriggered_step"]["previous_task_id"] == failed_task_id
        assert retrigger_payload["retriggered_step"]["new_task_id"] != failed_task_id
        assert retrigger_payload["run"]["status"] == "in_progress"

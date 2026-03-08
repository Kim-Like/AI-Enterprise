from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app


def _client(monkeypatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "real-admin-key")
    monkeypatch.setenv("IAN_AUTONOMY_KEY", "auto-write")
    return TestClient(create_app(db_path_override=str(tmp_path / "live-cutover.db")))


def _headers() -> dict[str, str]:
    return {"X-Autonomy-Key": "auto-write"}


def _lookup_specialist(db, *, application_id: str | None = None, owner_master_id: str | None = None, task_slug: str | None = None):
    clauses: list[str] = []
    params: list[str] = []
    if application_id:
        clauses.append("application_id = ?")
        params.append(application_id)
    if owner_master_id:
        clauses.append("owner_master_id = ?")
        params.append(owner_master_id)
    if task_slug:
        clauses.append("task_slug = ?")
        params.append(task_slug)
    row = db.fetch_one(
        f"SELECT id, owner_master_id, application_id, task_slug FROM specialist_agents WHERE {' AND '.join(clauses)}",
        tuple(params),
    )
    assert row is not None
    return row


def test_cutover_proves_hierarchy_routing_chain(monkeypatch, tmp_path: Path):
    with _client(monkeypatch, tmp_path) as client:
        db = client.app.state.db
        governor = _lookup_specialist(db, application_id="artisan-reporting-app")
        program_specialist = _lookup_specialist(
            db,
            owner_master_id="artisan-master",
            task_slug="artisan-accounting-integration-task",
        )
        engineer_specialist = _lookup_specialist(
            db,
            owner_master_id="engineer",
            task_slug="platform-reliability-task",
        )

        flow_response = client.post(
            "/api/orchestration/flows",
            headers=_headers(),
            json={
                "owner_agent_id": "father",
                "name": "IAn Cutover Routing Drill",
                "program_id": "artisan-reporting",
                "description": "Validate the clean hierarchy routing chain",
                "created_by": "phase-7-test",
            },
        )
        assert flow_response.status_code == 200
        flow_id = flow_response.json()["id"]

        for step_order, specialist_id in enumerate(
            [governor["id"], program_specialist["id"], engineer_specialist["id"]],
            start=1,
        ):
            step_response = client.post(
                f"/api/orchestration/flows/{flow_id}/steps",
                headers=_headers(),
                json={
                    "step_order": step_order,
                    "agent_id": specialist_id,
                    "objective_template": f"Step {step_order} for {{application_id}}",
                    "input_contract_json": {"required": ["program_id", "application_id"]},
                    "output_schema_json": {"type": "object"},
                },
            )
            assert step_response.status_code == 200

        trigger = client.post(
            "/api/control-ui/orchestration/trigger",
            headers=_headers(),
            json={
                "flow_id": flow_id,
                "trigger_type": "manual",
                "triggered_by": "cutover-validation",
                "run_context_json": {
                    "program_id": "artisan-reporting",
                    "application_id": "artisan-reporting-app",
                    "requested_by": "IAn",
                },
            },
        )
        assert trigger.status_code == 200
        run_id = trigger.json()["run"]["id"]

        detail = client.get(f"/api/control-ui/orchestration/runs/{run_id}", headers=_headers())
        assert detail.status_code == 200
        payload = detail.json()

        assert payload["flow"]["owner_agent_id"] == "father"
        assert [step["agent_id"] for step in payload["steps"]] == [
            governor["id"],
            program_specialist["id"],
            engineer_specialist["id"],
        ]
        assert payload["steps"][0]["status"] == "in_progress"
        assert payload["steps"][1]["status"] == "queued"
        assert payload["steps"][2]["status"] == "queued"

        ownership = {
            row["id"]: row["owner_master_id"]
            for row in db.fetch_all(
                "SELECT id, owner_master_id FROM specialist_agents WHERE id IN (?, ?, ?)",
                (governor["id"], program_specialist["id"], engineer_specialist["id"]),
            )
        }
        assert ownership[governor["id"]] == "artisan-master"
        assert ownership[program_specialist["id"]] == "artisan-master"
        assert ownership[engineer_specialist["id"]] == "engineer"

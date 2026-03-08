from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from api.app import create_app


def _client(monkeypatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "real-admin-key")
    monkeypatch.setenv("IAN_AUTONOMY_KEY", "auto-write")
    monkeypatch.setenv("GITHUB_AUTONOMY_TOKEN", "github-service-token")
    return TestClient(create_app(db_path_override=str(tmp_path / "autonomy.db")))


def _admin_headers() -> dict[str, str]:
    return {"X-Admin-Key": "real-admin-key"}


def _autonomy_headers() -> dict[str, str]:
    return {"X-Autonomy-Key": "auto-write"}


def _set_setting(client: TestClient, key: str, value: str, description: str = "phase10") -> None:
    response = client.put(
        f"/api/settings/{key}",
        headers=_admin_headers(),
        json={"value": value, "description": description},
    )
    assert response.status_code == 200, response.text


def _enable_repo_provisioning_policy(client: TestClient, *, repo_ids: str = "ai-enterprise") -> None:
    _set_setting(client, "AUTONOMY_ENABLED", "1")
    _set_setting(client, "AUTONOMY_MODE", "dry_run")
    _set_setting(client, "AUTONOMY_REPO_PROVISIONING_ENABLED", "1")
    _set_setting(client, "AUTONOMY_ALLOWED_REPOSITORY_IDS", repo_ids)


def _enable_live_executor_policy(
    client: TestClient,
    *,
    repo_ids: str = "ai-enterprise",
    actor_ids: str = "ian-master,engineer",
) -> None:
    _enable_repo_provisioning_policy(client, repo_ids=repo_ids)
    _set_setting(client, "AUTONOMY_MODE", "provision")
    _set_setting(client, "AUTONOMY_AUDIT_READY", "1")
    _set_setting(client, "AUTONOMY_EXECUTOR_ENABLED", "1")
    _set_setting(client, "AUTONOMY_EXECUTOR_ALLOWED_AGENTS", actor_ids)


def test_autonomy_policy_defaults_are_seeded(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    response = client.get("/api/autonomy/policy", headers=_autonomy_headers())

    assert response.status_code == 200
    policy = response.json()["policy"]
    assert policy["enabled"] is False
    assert policy["mode"] == "dry_run"
    assert policy["repo_provisioning_enabled"] is False
    assert policy["audit_ready"] is False
    assert policy["preflight_allowed"] is False
    assert "autonomy_disabled" in policy["preflight_block_reasons"]
    assert "autonomy_mode_not_provision" in policy["live_block_reasons"]
    assert "audit_not_ready" in policy["live_block_reasons"]
    assert "executor_disabled" in policy["live_block_reasons"]


def test_autonomy_policy_blocks_preflight_until_enabled(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/autonomy/provisioning/preflight",
        headers=_autonomy_headers(),
        json={"repo_ids": ["ai-enterprise"], "requested_mode": "dry_run"},
    )

    assert response.status_code == 403
    assert "autonomy_disabled" in response.json()["detail"]


def test_autonomy_policy_allows_scoped_preflight_when_enabled(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    _enable_repo_provisioning_policy(client)

    response = client.post(
        "/api/autonomy/provisioning/preflight",
        headers=_autonomy_headers(),
        json={"repo_ids": ["ai-enterprise"], "requested_mode": "dry_run"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["dry_run"] is True
    assert payload["preflight_only"] is True
    assert payload["policy"]["preflight_allowed"] is True
    assert payload["repositories"][0]["repo_id"] == "ai-enterprise"
    assert payload["repositories"][0]["live_writes_blocked"] is True


def test_autonomy_policy_scope_applies_to_admin_and_autonomy(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    _enable_repo_provisioning_policy(client, repo_ids="ai-enterprise")

    response = client.post(
        "/api/autonomy/provisioning/preflight",
        headers=_admin_headers(),
        json={"repo_ids": ["ljdesignstudio.dk"], "requested_mode": "dry_run"},
    )

    assert response.status_code == 403
    assert "ljdesignstudio.dk" in response.json()["detail"]


def test_autonomy_executor_contract_exposes_host_and_actor_scope(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    _enable_live_executor_policy(client)

    response = client.get("/api/autonomy/executor", headers=_autonomy_headers())

    assert response.status_code == 200, response.text
    payload = response.json()
    executor = payload["executor"]
    assert executor["host_id"] == "ai-enterprise-autonomy"
    assert executor["tailnet_tag"] == "tag:ai-autonomy"
    assert executor["service_unit"] == "ai-enterprise-autonomy.service"
    assert executor["timer_unit"] == "ai-enterprise-autonomy.timer"
    assert "ian-master" in executor["allowed_actor_ids"]
    assert "engineer" in executor["allowed_actor_ids"]


def test_autonomy_executor_run_dry_run_records_audit_rows(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    _enable_repo_provisioning_policy(client)
    _set_setting(client, "AUTONOMY_EXECUTOR_ENABLED", "1")
    _set_setting(client, "AUTONOMY_EXECUTOR_ALLOWED_AGENTS", "ian-master,engineer")

    response = client.post(
        "/api/autonomy/executor/run",
        headers=_autonomy_headers(),
        json={
            "actor_agent_id": "engineer",
            "repo_ids": ["ai-enterprise"],
            "requested_mode": "dry_run",
            "trigger_source": "test-suite",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    run = payload["run"]
    assert run["status"] == "dry_run"
    assert run["validation_status"] == "simulated"
    assert run["actor_agent_id"] == "engineer"
    assert payload["repositories"][0]["repo_id"] == "ai-enterprise"
    assert payload["repositories"][0]["status"] == "dry_run"

    audit = client.get("/api/autonomy/audit/runs", headers=_autonomy_headers())
    assert audit.status_code == 200
    runs = audit.json()["runs"]
    assert runs[0]["id"] == run["id"]
    assert runs[0]["actions"][0]["repo_id"] == "ai-enterprise"

    sync = client.get("/api/autonomy/sync/repositories", headers=_autonomy_headers())
    assert sync.status_code == 200
    sync_row = next(item for item in sync.json()["repositories"] if item["repo_id"] == "ai-enterprise")
    assert sync_row["last_run_id"] == run["id"]
    assert sync_row["last_status"] == "dry_run"
    assert sync_row["manifest_sync_status"] == "synchronized"


def test_autonomy_executor_run_provision_mode_updates_provenance_and_sync(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    _enable_live_executor_policy(client)

    import api.system.autonomy_service as autonomy_service

    real_run = autonomy_service.subprocess.run

    def fake_run(args, *run_args, **run_kwargs):
        command = list(args)
        joined = " ".join(command)
        if "bootstrap_primary_remote.sh" in joined:
            return SimpleNamespace(returncode=0, stdout="bootstrap_primary_remote=ok\n", stderr="")
        if "validate_git_governance.sh" in joined:
            return SimpleNamespace(returncode=0, stdout="git_governance=ok checked=1 skipped=0\n", stderr="")
        return real_run(args, *run_args, **run_kwargs)

    monkeypatch.setattr(autonomy_service.subprocess, "run", fake_run)

    response = client.post(
        "/api/autonomy/executor/run",
        headers=_autonomy_headers(),
        json={
            "actor_agent_id": "ian-master",
            "repo_ids": ["ai-enterprise"],
            "requested_mode": "provision",
            "trigger_source": "test-suite",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    run = payload["run"]
    repo = payload["repositories"][0]
    assert run["status"] == "completed"
    assert run["validation_status"] == "passed"
    assert repo["status"] == "completed"
    assert repo["validation_status"] == "passed"
    assert repo["provenance_id"]

    sync = client.get("/api/autonomy/sync/repositories", headers=_autonomy_headers())
    assert sync.status_code == 200
    sync_row = next(item for item in sync.json()["repositories"] if item["repo_id"] == "ai-enterprise")
    assert sync_row["last_status"] == "completed"
    assert sync_row["last_validation_status"] == "passed"
    assert sync_row["last_provenance_id"] == repo["provenance_id"]
    assert sync_row["latest_provenance"]["id"] == repo["provenance_id"]

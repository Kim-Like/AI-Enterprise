from __future__ import annotations

from pathlib import Path

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
    assert "wave1_preflight_only" in policy["live_block_reasons"]


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


def test_autonomy_policy_rejects_live_mode_during_wave1(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    _enable_repo_provisioning_policy(client)
    _set_setting(client, "AUTONOMY_MODE", "provision")
    _set_setting(client, "AUTONOMY_AUDIT_READY", "1")

    response = client.post(
        "/api/autonomy/provisioning/preflight",
        headers=_autonomy_headers(),
        json={"repo_ids": ["ai-enterprise"], "requested_mode": "provision"},
    )

    assert response.status_code == 409
    assert "preflight only" in response.json()["detail"].lower()

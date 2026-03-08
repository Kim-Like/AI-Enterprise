from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from api.app import create_app


def _client(monkeypatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "real-admin-key")
    monkeypatch.setenv("IAN_AUTONOMY_KEY", "auto-write")
    return TestClient(create_app(db_path_override=str(tmp_path / "connections.db")))


def test_secret_status_route_is_redacted(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-secret-value")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-secret-value")
    client = _client(monkeypatch, tmp_path)

    response = client.get("/api/control-ui/secrets/status", headers={"X-Autonomy-Key": "auto-write"})
    assert response.status_code == 200

    payload = response.json()
    secret_rows = {item["name"]: item for item in payload["secrets"]}
    assert secret_rows["ANTHROPIC_API_KEY"]["present"] is True
    assert secret_rows["ANTHROPIC_API_KEY"]["status"] == "present"
    removed_prefixes = ("SUPA" + "BASE_", "HOSTED" + "_DB_")
    assert not any(name.startswith(prefix) for prefix in removed_prefixes for name in secret_rows)
    assert "anthropic-secret-value" not in response.text
    assert "openai-secret-value" not in response.text


def test_datastores_verify_route_is_protected_and_registry_backed(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)

    denied = client.get("/api/datastores/verify")
    assert denied.status_code == 401

    allowed = client.get("/api/datastores/verify", headers={"X-Autonomy-Key": "auto-write"})
    assert allowed.status_code == 200
    payload = allowed.json()
    assert payload["status"] == "ok"
    assert payload["verified_count"] >= 1
    assert any(item["id"] == "father-db" for item in payload["datastores"])
    assert any(item["id"] == "baltzer-tcg-migration-hold" and item["status"] == "planned" for item in payload["datastores"])


def test_secret_test_endpoint_returns_evidence_without_values(monkeypatch, tmp_path: Path):
    key_path = tmp_path / "cpanel_key"
    key_path.write_text("not-a-real-key")
    monkeypatch.setenv("CPANEL_SSH_HOST", "cp10.nordicway.dk")
    monkeypatch.setenv("CPANEL_SSH_PORT", "33")
    monkeypatch.setenv("CPANEL_SSH_USER", "theartis")
    monkeypatch.setenv("CPANEL_SSH_KEY_PATH", str(key_path))

    import api.system.connection_status as connection_status

    monkeypatch.setattr(
        connection_status.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )

    client = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/control-ui/secrets/test/cpanel-ssh",
        headers={"X-Admin-Key": "real-admin-key"},
    )
    assert response.status_code == 200
    payload = response.json()["result"]
    assert payload["target"] == "cpanel-ssh"
    assert payload["status"] == "live"
    assert payload["evidence"] == "ssh_handshake_ok"
    assert str(key_path) not in response.text


def test_unknown_secret_test_target_returns_404(monkeypatch, tmp_path: Path):
    client = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/control-ui/secrets/test/does-not-exist",
        headers={"X-Admin-Key": "real-admin-key"},
    )
    assert response.status_code == 404

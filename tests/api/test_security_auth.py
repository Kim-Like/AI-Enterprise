from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app


def test_default_admin_key_is_rejected(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "change-me-admin-key")
    monkeypatch.delenv("ALLOW_DEFAULT_ADMIN_KEY", raising=False)

    client = TestClient(create_app(db_path_override=str(tmp_path / "security.db")))
    response = client.get("/api/settings", headers={"X-Admin-Key": "change-me-admin-key"})

    assert response.status_code == 503
    assert "not configured securely" in response.json()["detail"]


def test_settings_routes_require_real_admin_key(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "real-admin-key")
    monkeypatch.setenv("IAN_AUTONOMY_KEY", "auto-write")

    client = TestClient(create_app(db_path_override=str(tmp_path / "settings.db")))

    denied = client.get("/api/settings")
    assert denied.status_code == 401

    listed = client.get("/api/settings", headers={"X-Admin-Key": "real-admin-key"})
    assert listed.status_code == 200
    assert isinstance(listed.json(), list)

    updated = client.put(
        "/api/settings/test_flag",
        headers={"X-Admin-Key": "real-admin-key"},
        json={"value": "enabled", "description": "phase4"},
    )
    assert updated.status_code == 200
    assert updated.json() == {"key": "test_flag", "value": "enabled"}

    autonomy_denied = client.put(
        "/api/settings/test_flag",
        headers={"X-Autonomy-Key": "auto-write"},
        json={"value": "disabled", "description": "phase4"},
    )
    assert autonomy_denied.status_code == 401


def test_env_example_and_manifest_remove_placeholder_defaults():
    root = Path("/Users/IAn/Agent/AI-Enterprise")
    env_text = (root / ".env.example").read_text()
    manifest_text = (root / "SECRETS-MANIFEST.md").read_text()

    assert "change-me-admin-key" not in env_text
    assert "ALLOW_DEFAULT_ADMIN_KEY=0" in env_text
    assert "ANTHROPIC_API_KEY" in env_text
    assert "OPENAI_API_KEY" in manifest_text


def test_clean_target_contains_no_localstorage_auth_pattern():
    root = Path("/Users/IAn/Agent/AI-Enterprise")
    scanned_dirs = [root / "api", root / "src", root / "frontend"]
    code_suffixes = {".py", ".ts", ".tsx", ".js", ".jsx", ".html", ".css"}

    for base in scanned_dirs:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix not in code_suffixes:
                continue
            text = path.read_text(errors="ignore")
            assert "localStorage" not in text, path

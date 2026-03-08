from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app


def test_backend_serves_built_frontend_routes(monkeypatch, tmp_path: Path):
    root = Path("/Users/IAn/Agent/AI-Enterprise")
    dist_index = root / "dist" / "index.html"
    asset_dir = root / "dist" / "assets"

    assert dist_index.exists(), "Run `npm run build` before frontend delivery tests"

    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "real-admin-key")
    monkeypatch.setenv("IAN_AUTONOMY_KEY", "auto-write")

    with TestClient(create_app(db_path_override=str(tmp_path / "frontend-delivery.db"))) as client:
        home = client.get("/", headers={"accept": "text/html"})
        assert home.status_code == 200
        assert "text/html" in home.headers["content-type"]
        assert '<div id="root"></div>' in home.text

        programs = client.get("/programs", headers={"accept": "text/html"})
        assert programs.status_code == 200
        assert programs.text == home.text

        configs = client.get("/agents/configs/father", headers={"accept": "text/html"})
        assert configs.status_code == 200
        assert configs.text == home.text

        legacy_alias = client.get("/orchestration-center", headers={"accept": "text/html"})
        assert legacy_alias.status_code == 200
        assert legacy_alias.text == home.text

        sample_asset = next(asset_dir.glob("*.js"), None)
        assert sample_asset is not None
        asset_response = client.get(f"/assets/{sample_asset.name}")
        assert asset_response.status_code == 200
        assert "javascript" in asset_response.headers["content-type"]


def test_spa_fallback_does_not_swallow_api_routes(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("DASHBOARD_ADMIN_KEY", "real-admin-key")
    monkeypatch.setenv("IAN_AUTONOMY_KEY", "auto-write")

    with TestClient(create_app(db_path_override=str(tmp_path / "frontend-api-boundary.db"))) as client:
        api_not_found = client.get("/api/not-a-real-route", headers={"X-Autonomy-Key": "auto-write"})
        assert api_not_found.status_code == 404
        assert api_not_found.json() == {"detail": "Not found"}

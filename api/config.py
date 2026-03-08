"""Configuration and path loading for AI-Enterprise."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    project_root: Path
    db_path: Path
    schema_path: Path
    application_catalog_path: Path
    task_catalog_path: Path
    host: str
    port: int
    cors_origins: list[str]
    dashboard_admin_key: str
    allow_default_admin_key: bool
    autonomy_key: str
    autonomy_header: str
    default_model_provider: str
    default_model: str
    claude_binary: str
    claude_timeout: int


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_settings(
    *,
    project_root: Path | None = None,
    db_path_override: str | None = None,
) -> Settings:
    root = project_root or Path(__file__).resolve().parent.parent
    load_dotenv(root / ".env")
    load_dotenv(root / ".env.local", override=True)
    db_path = Path(db_path_override or os.getenv("DB_PATH", str(root / "ai_enterprise.db")))
    cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:8001")
    cors_origins = [item.strip() for item in cors_origin.split(",") if item.strip()]
    return Settings(
        project_root=root,
        db_path=db_path,
        schema_path=root / "api" / "db" / "schema.sql",
        application_catalog_path=root / "api" / "config" / "application_catalog.json",
        task_catalog_path=root / "api" / "config" / "task_catalog.json",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8001")),
        cors_origins=cors_origins,
        dashboard_admin_key=os.getenv("DASHBOARD_ADMIN_KEY", "").strip(),
        allow_default_admin_key=_env_flag("ALLOW_DEFAULT_ADMIN_KEY", default=False),
        autonomy_key=os.getenv("IAN_AUTONOMY_KEY", ""),
        autonomy_header=os.getenv("IAN_AUTONOMY_HEADER", "X-Autonomy-Key"),
        default_model_provider=os.getenv("DEFAULT_MODEL_PROVIDER", "claude"),
        default_model=os.getenv("DEFAULT_MODEL", "sonnet"),
        claude_binary=os.getenv("CLAUDE_BINARY", "claude"),
        claude_timeout=int(os.getenv("CLAUDE_TIMEOUT", "120")),
    )

"""SQLite client with WAL mode and schema bootstrapping."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any


class DatabaseClient:
    def __init__(self, db_path: str, schema_path: str | None = None):
        self.db_path = db_path
        self.schema_path = schema_path
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("PRAGMA foreign_keys=ON")
            if self.schema_path and Path(self.schema_path).exists():
                conn.executescript(Path(self.schema_path).read_text())
            self._run_migrations(conn)

    def _column_exists(self, conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        return any(str(row["name"]) == column_name for row in rows)

    def _run_migrations(self, conn: sqlite3.Connection) -> None:
        if not self._column_exists(conn, "chat_threads", "execution_mode"):
            conn.execute(
                "ALTER TABLE chat_threads ADD COLUMN execution_mode TEXT NOT NULL DEFAULT 'free_reasoning'"
            )

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, sql: str, params: tuple = ()) -> None:
        with self._connect() as conn:
            conn.execute(sql, params)

    def fetch_one(self, sql: str, params: tuple = ()) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else None

    def fetch_all(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(item) for item in rows]

    def set_setting(self, key: str, value: str, description: str = "") -> None:
        self.execute(
            "INSERT INTO settings (key, value, description, updated_at) "
            "VALUES (?, ?, ?, datetime('now')) "
            "ON CONFLICT(key) DO UPDATE SET "
            "value=excluded.value, description=excluded.description, updated_at=datetime('now')",
            (key, value, description),
        )

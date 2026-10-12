from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import current_app, g


def connect_database(path: str | Path) -> sqlite3.Connection:
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect_database(current_app.config["DATABASE"])
    return g.db


def close_db(_error: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db(path: str | Path, schema_path: str | Path | None = None) -> None:
    schema_file = Path(schema_path) if schema_path else Path(__file__).with_name("schema.sql")
    connection = connect_database(path)
    try:
        connection.executescript(schema_file.read_text(encoding="utf-8"))
    finally:
        connection.close()


def rows_as_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]

"""Database helper for the webapp backend.

Delegates to the existing car_tracker.database module so we share all
schema knowledge (migrations, SQL, etc.) from a single source of truth.
The webapp DB path is resolved from config.yaml at the project root.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path


def get_db_path(config_path: str | Path = "config.yaml") -> Path:
    """Read database.path from config.yaml and return it as an absolute Path."""
    import yaml

    with open(config_path) as f:
        raw = yaml.safe_load(f)
    db_path = raw["database"]["path"]
    return Path(db_path)


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Open a read/write SQLite connection with FK enforcement."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

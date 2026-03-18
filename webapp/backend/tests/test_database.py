"""Tests for webapp backend database helper."""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest
import yaml

from webapp.backend.database import connect, get_db_path


def _write_config(tmp_path: Path, db_rel: str) -> Path:
    config = tmp_path / "config.yaml"
    config.write_text(
        yaml.dump({"database": {"path": db_rel}, "bookings": []})
    )
    return config


def test_get_db_path_returns_path(tmp_path):
    config = _write_config(tmp_path, "data/results.db")
    result = get_db_path(config)
    assert isinstance(result, Path)
    assert str(result) == "data/results.db"


def test_get_db_path_reads_correct_key(tmp_path):
    config = _write_config(tmp_path, "some/other.db")
    result = get_db_path(config)
    assert str(result) == "some/other.db"


def test_connect_creates_connection(tmp_path):
    db = tmp_path / "test.db"
    conn = connect(db)
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_connect_enables_foreign_keys(tmp_path):
    db = tmp_path / "test.db"
    conn = connect(db)
    row = conn.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1
    conn.close()


def test_connect_uses_row_factory(tmp_path):
    db = tmp_path / "test.db"
    conn = connect(db)
    conn.execute("CREATE TABLE t (x INTEGER)")
    conn.execute("INSERT INTO t VALUES (42)")
    row = conn.execute("SELECT x FROM t").fetchone()
    assert row["x"] == 42
    conn.close()

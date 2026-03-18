from __future__ import annotations

import json
from pathlib import Path

from car_tracker.state import read_app_state, write_app_state


def test_read_app_state_missing_file(tmp_path: Path) -> None:
    state = read_app_state(tmp_path / "nonexistent.json")
    assert state["monitoring_paused_notified"] is False
    assert state["last_rowid"] == 0


def test_read_app_state_existing_file_preserves_last_rowid(tmp_path: Path) -> None:
    f = tmp_path / "state.json"
    f.write_text('{"last_rowid": 42}')
    state = read_app_state(f)
    assert state["last_rowid"] == 42
    assert state["monitoring_paused_notified"] is False


def test_read_app_state_with_flag_true(tmp_path: Path) -> None:
    f = tmp_path / "state.json"
    f.write_text('{"last_rowid": 10, "monitoring_paused_notified": true}')
    state = read_app_state(f)
    assert state["monitoring_paused_notified"] is True
    assert state["last_rowid"] == 10


def test_write_app_state_creates_file(tmp_path: Path) -> None:
    f = tmp_path / "state.json"
    write_app_state(f, {"last_rowid": 99, "monitoring_paused_notified": True})
    data = json.loads(f.read_text())
    assert data["last_rowid"] == 99
    assert data["monitoring_paused_notified"] is True


def test_write_app_state_overwrites_existing(tmp_path: Path) -> None:
    f = tmp_path / "state.json"
    f.write_text('{"last_rowid": 5}')
    write_app_state(f, {"last_rowid": 100, "monitoring_paused_notified": False})
    data = json.loads(f.read_text())
    assert data["last_rowid"] == 100
    assert data["monitoring_paused_notified"] is False

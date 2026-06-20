from __future__ import annotations

import json
from pathlib import Path

from car_tracker.state import read_app_state, write_app_state


def test_read_app_state_missing_file(tmp_path: Path) -> None:
    state = read_app_state(tmp_path / "nonexistent.json")
    assert state["monitoring_paused_notified"] is False
    assert "last_rowid" not in state


def test_read_app_state_existing_file_merges_with_defaults(tmp_path: Path) -> None:
    f = tmp_path / "state.json"
    f.write_text('{"monitoring_paused_notified": true}')
    state = read_app_state(f)
    assert state["monitoring_paused_notified"] is True


def test_read_app_state_unknown_keys_preserved(tmp_path: Path) -> None:
    f = tmp_path / "state.json"
    f.write_text('{"monitoring_paused_notified": false, "extra_key": 42}')
    state = read_app_state(f)
    assert state["extra_key"] == 42
    assert state["monitoring_paused_notified"] is False


def test_write_app_state_creates_file(tmp_path: Path) -> None:
    f = tmp_path / "state.json"
    write_app_state(f, {"monitoring_paused_notified": True})
    data = json.loads(f.read_text())
    assert data["monitoring_paused_notified"] is True


def test_write_app_state_overwrites_existing(tmp_path: Path) -> None:
    f = tmp_path / "state.json"
    f.write_text('{"monitoring_paused_notified": true}')
    write_app_state(f, {"monitoring_paused_notified": False})
    data = json.loads(f.read_text())
    assert data["monitoring_paused_notified"] is False

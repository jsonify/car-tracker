from __future__ import annotations

import json
from pathlib import Path

_DEFAULTS: dict = {
    "last_rowid": 0,
    "monitoring_paused_notified": False,
}


def read_app_state(state_path: Path) -> dict:
    """Read app state from JSON file, merging with defaults for missing keys."""
    if not state_path.exists():
        return dict(_DEFAULTS)
    with state_path.open() as f:
        data = json.load(f)
    return {**_DEFAULTS, **data}


def write_app_state(state_path: Path, state: dict) -> None:
    """Write app state to JSON file."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

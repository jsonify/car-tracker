"""Check iMessage for config update commands and apply them to config.yaml.

Usage:
    uv run python scripts/check_imessage.py
    uv run python scripts/check_imessage.py --config /path/to/config.yaml
    uv run python scripts/check_imessage.py --db /path/to/chat.db --state /path/to/state.json

Requires Full Disk Access granted to Terminal in macOS System Settings.
"""

import argparse
import json
import sqlite3
from pathlib import Path

from scripts.update_config import apply_config_update, parse_config_update

DEFAULT_DB = Path.home() / "Library" / "Messages" / "chat.db"
DEFAULT_STATE = Path("data/imessage_state.json")
DEFAULT_CONFIG = Path("config.yaml")


def read_pending_messages(
    db_path: str | Path = DEFAULT_DB,
    state_path: str | Path = DEFAULT_STATE,
) -> list[tuple[int, str]]:
    """Return messages from chat.db with rowid > last processed rowid.

    Creates ``state_path`` (with ``last_rowid=0``) if it does not exist.
    Skips messages with NULL text.
    Returns a list of ``(rowid, text)`` tuples ordered by rowid ascending.
    """
    db_path = Path(db_path)
    state_path = Path(state_path)

    if not state_path.exists():
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"last_rowid": 0}))

    state = json.loads(state_path.read_text())
    last_rowid = state.get("last_rowid", 0)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            "SELECT rowid, text FROM message WHERE rowid > ? AND text IS NOT NULL ORDER BY rowid ASC",
            (last_rowid,),
        ).fetchall()
    finally:
        conn.close()

    return [(rowid, text) for rowid, text in rows]


def main(
    db_path: str | Path = DEFAULT_DB,
    state_path: str | Path = DEFAULT_STATE,
    config_path: str | Path = DEFAULT_CONFIG,
) -> None:  # pragma: no cover
    """Read pending iMessages, parse for config updates, apply and push."""
    state_path = Path(state_path)

    messages = read_pending_messages(db_path, state_path)
    if not messages:
        print("No new messages.")
        return

    max_rowid = 0
    applied = 0

    for rowid, text in messages:
        max_rowid = max(max_rowid, rowid)
        updates = parse_config_update(text)
        if not updates:
            continue
        changed = apply_config_update(updates, config_path)
        if changed:
            applied += 1
            print(f"Applied update from message {rowid}: {updates}")
        else:
            print(f"No-op (values unchanged) from message {rowid}: {updates}")

    # Persist the highest rowid we've seen so we don't reprocess
    state = json.loads(state_path.read_text())
    state["last_rowid"] = max_rowid
    state_path.write_text(json.dumps(state, indent=2))

    if applied == 0:
        print("No config changes applied.")
    else:
        print(f"{applied} config update(s) committed and pushed.")


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Check iMessage for config update commands.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to chat.db")
    parser.add_argument("--state", default=str(DEFAULT_STATE), help="Path to state JSON file")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to config.yaml")
    args = parser.parse_args()
    main(db_path=args.db, state_path=args.state, config_path=args.config)

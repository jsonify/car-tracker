from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import yaml

# Default macOS Messages database location
_MESSAGES_DB = Path.home() / "Library" / "Messages" / "chat.db"

# Matches: "holding <price> <vehicle type>"  e.g. "holding 350.00 Standard Car"
_COMMAND_RE = re.compile(r"^holding\s+(\d+(?:\.\d+)?)\s+(.+?)\s*$", re.IGNORECASE)


def _state_path(config_path: Path) -> Path:
    return config_path.parent / "data" / "imessage_state.json"


def _load_last_date(config_path: Path) -> int:
    """Return the Messages date of the last processed message, or 0 if none."""
    path = _state_path(config_path)
    if path.exists():
        try:
            return int(json.loads(path.read_text()).get("last_date", 0))
        except (ValueError, KeyError):
            return 0
    return 0


def _save_last_date(config_path: Path, date: int) -> None:
    path = _state_path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"last_date": date}))


def read_pending_messages(
    phone: str,
    since_date: int,
    messages_db: Path = _MESSAGES_DB,
) -> list[tuple[int, str]]:
    """Return (date, text) for messages received from phone after since_date.

    Reads from the macOS Messages SQLite database (read-only).
    Messages sent from the user's phone to themselves appear as is_from_me=0
    on the Mac side, with handle.id matching their own phone number.
    """
    conn = sqlite3.connect(f"file:{messages_db}?mode=ro", uri=True)
    try:
        rows = conn.execute(
            """
            SELECT m.date, m.text
            FROM message m
            JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
            JOIN chat_handle_join chj ON cmj.chat_id = chj.chat_id
            JOIN handle h ON chj.handle_id = h.ROWID
            WHERE h.id = ?
              AND m.is_from_me = 0
              AND m.text IS NOT NULL
              AND m.date > ?
            ORDER BY m.date ASC
            """,
            (phone, since_date),
        ).fetchall()
    finally:
        conn.close()
    return [(int(row[0]), str(row[1])) for row in rows]


def parse_holding_command(text: str) -> tuple[float, str] | None:
    """Parse a 'holding <price> <vehicle_type>' command.

    Returns (price, vehicle_type) on match, or None if the text is not a
    holding command.
    """
    m = _COMMAND_RE.match(text.strip())
    if not m:
        return None
    return float(m.group(1)), m.group(2).strip()


def update_config_yaml(config_path: Path, price: float, vehicle_type: str) -> None:
    """Update holding_price and holding_vehicle_type in config.yaml in-place.

    Preserves all other content including inline comments and formatting.
    """
    text = config_path.read_text()
    price_str = f"{price:g}"

    # Replace the numeric value for holding_price, leaving the rest of the line intact
    text = re.sub(
        r"^(\s*holding_price:\s*)[\d.]+",
        lambda m: f"{m.group(1)}{price_str}",
        text,
        flags=re.MULTILINE,
    )

    # Replace the (optionally quoted) string value for holding_vehicle_type
    text = re.sub(
        r'^(\s*holding_vehicle_type:\s*)("?)[^"\n#]*"?',
        lambda m: f'{m.group(1)}"{vehicle_type}"',
        text,
        flags=re.MULTILINE,
    )

    config_path.write_text(text)


def poll_and_apply(
    config_path: str | Path,
    messages_db: Path = _MESSAGES_DB,
) -> bool:
    """Check iMessage for holding update commands and apply to config.yaml.

    Reads imessage.phone_number from the config file itself. Tracks the last
    processed message date so commands are never applied twice.

    Returns True if config.yaml was updated.
    """
    config_path = Path(config_path)
    with config_path.open() as f:
        raw = yaml.safe_load(f) or {}

    phone = (raw.get("imessage") or {}).get("phone_number")
    if not phone:
        return False

    since = _load_last_date(config_path)
    messages = read_pending_messages(str(phone), since, messages_db)
    if not messages:
        return False

    updated = False
    last_date = since
    for date, text in messages:
        result = parse_holding_command(text)
        if result is not None:
            price, vehicle_type = result
            update_config_yaml(config_path, price, vehicle_type)
            print(f"iMessage: updated holding to {price:g} / {vehicle_type}")
            updated = True
        last_date = max(last_date, date)

    _save_last_date(config_path, last_date)
    return updated

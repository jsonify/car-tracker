"""Check iMessage for config update commands and apply them to config.yaml.

Usage:
    uv run python scripts/check_imessage.py
    uv run python scripts/check_imessage.py --config /path/to/config.yaml
    uv run python scripts/check_imessage.py --db /path/to/chat.db --state /path/to/state.json

Requires Full Disk Access granted to Terminal in macOS System Settings.
"""

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

from scripts.update_config import (
    apply_config_update,
    list_bookings_reply,
    parse_config_update,
    send_imessage,
)

import yaml

# Known TypedStream class/key names that precede the actual message text.
_STREAMTYPED_METADATA = frozenset({
    "streamtyped",
    "NSAttributedString",
    "NSMutableAttributedString",
    "NSObject",
    "NSString",
    "NSMutableString",
    "NSDictionary",
    "__kIMMessagePartAttributeName",
    "NSNumber",
    "NSValue",
    "NSColor",
    "NSFont",
    "NSParagraphStyle",
})


def _text_from_attributed_body(blob: bytes) -> str | None:
    """Extract plain text from an attributedBody TypedStream blob.

    macOS stores message content in a binary TypedStream (NSAttributedString
    archive) when the plain ``text`` column is NULL. The message string is the
    first printable-ASCII run that is not a known TypedStream metadata token.

    TypedStream encodes strings as ``"+" + <1-byte-length> + <text>``. When the
    length byte is itself printable ASCII the regex captures all three together,
    so we strip the two-character prefix in that case.
    """
    for raw in re.findall(rb"[ -~]+", blob):
        candidate = raw.decode("ascii", errors="ignore").strip()
        if not candidate or candidate in _STREAMTYPED_METADATA:
            continue
        # Skip single/double-character TypedStream artifacts (@, iI, +, &, …)
        if len(candidate) <= 2:
            continue
        # Strip length prefix when it's printable: "+" + length_char + text
        if candidate.startswith("+"):
            candidate = candidate[2:]
        if candidate and len(candidate) > 2:
            return candidate
    return None

DEFAULT_DB = Path.home() / "Library" / "Messages" / "chat.db"
DEFAULT_STATE = Path("data/imessage_state.json")
DEFAULT_CONFIG = Path("config.yaml")


def read_pending_messages(
    db_path: str | Path = DEFAULT_DB,
    state_path: str | Path = DEFAULT_STATE,
) -> list[tuple[int, str]]:
    """Return messages from chat.db with rowid > last processed rowid.

    Creates ``state_path`` (with ``last_rowid=0``) if it does not exist.
    Falls back to decoding ``attributedBody`` when ``text`` is NULL (macOS
    Ventura+ stores message content there instead).
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
            "SELECT rowid, text, attributedBody FROM message"
            " WHERE rowid > ? AND is_from_me = 0"
            " AND (text IS NOT NULL OR attributedBody IS NOT NULL)"
            " ORDER BY rowid ASC",
            (last_rowid,),
        ).fetchall()
    finally:
        conn.close()

    result = []
    for rowid, text, attributed_body in rows:
        resolved = text if text is not None else _text_from_attributed_body(attributed_body)
        if resolved:
            result.append((rowid, resolved))
    return result


def _get_phone(config_path: str | Path) -> str | None:
    """Return the configured iMessage phone number, or None if not set."""
    try:
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        return cfg.get("imessage", {}).get("phone_number")
    except Exception:
        return None


def main(
    db_path: str | Path = DEFAULT_DB,
    state_path: str | Path = DEFAULT_STATE,
    config_path: str | Path = DEFAULT_CONFIG,
) -> bool:  # pragma: no cover
    """Read pending iMessages, parse for config updates, apply and push.

    Returns True if car_tracker was run on demand (so callers like run.sh can
    skip their own scheduled tracker invocation).
    """
    state_path = Path(state_path)

    messages = read_pending_messages(db_path, state_path)
    if not messages:
        print("No new messages.")
        return False

    phone = _get_phone(config_path)
    max_rowid = 0
    applied = 0
    ran_ct = False

    for rowid, text in messages:
        max_rowid = max(max_rowid, rowid)
        updates = parse_config_update(text)
        if not updates:
            continue

        action = updates.get("action")

        # run car tracker on demand
        if action == "run_ct":
            print(f"Running car_tracker on demand (message {rowid})")
            ran_ct = True
            if phone:
                try:
                    send_imessage(phone, "Running car tracker...")
                except Exception as exc:
                    print(f"iMessage reply failed: {exc}")
            try:
                repo_dir = Path(config_path).parent
                result = subprocess.run(
                    [sys.executable, "-m", "car_tracker", "--config", str(config_path)],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode == 0:
                    print("car_tracker completed successfully")
                    if phone:
                        try:
                            send_imessage(phone, "Car tracker run complete.")
                        except Exception as exc:
                            print(f"iMessage reply failed: {exc}")
                else:
                    print(f"car_tracker failed: {result.stderr}")
                    if phone:
                        try:
                            send_imessage(phone, f"Car tracker failed: {result.stderr[:200]}")
                        except Exception as exc:
                            print(f"iMessage reply failed: {exc}")
            except subprocess.TimeoutExpired:
                print("car_tracker timed out after 5 minutes")
                if phone:
                    try:
                        send_imessage(phone, "Car tracker timed out after 5 minutes.")
                    except Exception:
                        pass
            except Exception as exc:
                print(f"Error running car_tracker: {exc}")
                if phone:
                    try:
                        send_imessage(phone, f"Error running car tracker: {exc}")
                    except Exception:
                        pass
            continue

        # list bookings — reply without modifying config
        if action == "list_bookings":
            try:
                with open(config_path) as f:
                    cfg = yaml.safe_load(f)
                reply = list_bookings_reply(cfg.get("bookings", []))
                print(f"Replying to list bookings request (message {rowid})")
                if phone:
                    try:
                        send_imessage(phone, reply)
                    except Exception as exc:
                        print(f"iMessage reply failed: {exc}")
                else:
                    print(reply)
            except Exception as exc:
                print(f"Error handling list bookings (message {rowid}): {exc}")
            continue

        # add booking or update holding — apply config change
        try:
            changed = apply_config_update(updates, config_path)
        except ValueError as exc:
            err_msg = str(exc)
            print(f"Invalid update in message {rowid}: {err_msg}")
            if phone:
                try:
                    send_imessage(phone, f"Error: {err_msg}")
                except Exception:
                    pass
            continue

        if changed:
            applied += 1
            print(f"Applied update from message {rowid}: {updates}")
            if phone:
                try:
                    with open(config_path) as f:
                        cfg = yaml.safe_load(f)
                    listing = list_bookings_reply(cfg.get("bookings", []))
                    if action == "add_booking":
                        reply = f"Added booking '{updates['name']}'.\n\n{listing}"
                    else:
                        reply = f"Updated.\n\n{listing}"
                    send_imessage(phone, reply)
                except Exception as exc:
                    print(f"iMessage reply failed: {exc}")
        else:
            print(f"No-op (values unchanged) from message {rowid}: {updates}")

    # Persist the highest rowid we've seen so we don't reprocess
    state = json.loads(state_path.read_text())
    state["last_rowid"] = max_rowid
    state_path.write_text(json.dumps(state, indent=2))

    if applied == 0 and not ran_ct:
        print("No config changes applied.")
    else:
        if applied > 0:
            print(f"{applied} config update(s) committed and pushed.")

    return ran_ct


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Check iMessage for config update commands.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to chat.db")
    parser.add_argument("--state", default=str(DEFAULT_STATE), help="Path to state JSON file")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to config.yaml")
    args = parser.parse_args()
    ran = main(db_path=args.db, state_path=args.state, config_path=args.config)
    sys.exit(2 if ran else 0)

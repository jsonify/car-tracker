"""Remote config update via iMessage.

parse_config_update(text) — extract action and fields from iMessage text.

apply_config_update(updates, config_path) — patch config.yaml and git push.

list_bookings_reply(bookings) — format booking list for iMessage reply.

send_imessage(phone, message) — send an iMessage via osascript.
"""

import re
import subprocess
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Natural language parser — legacy single-booking format
# ---------------------------------------------------------------------------

_PRICE_PATTERN = re.compile(
    r"""
    (?:holding\s+price|price)   # keyword anchor
    \s+to\s+                    # "to"
    \$?                         # optional dollar sign
    (\d+(?:\.\d+)?)             # capture: digits with optional decimal
    """,
    re.IGNORECASE | re.VERBOSE,
)

_TYPE_PATTERN = re.compile(
    r"""
    (?:holding\s+type|type|holding\s+vehicle\s+type)  # keyword anchor
    \s+to\s+                                          # "to"
    ([A-Za-z][A-Za-z\s]*)                             # capture: vehicle type (letters/spaces)
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Secondary pattern: "update holding price to 350 for Standard Car"
_PRICE_FOR_TYPE_PATTERN = re.compile(
    r"""
    (?:holding\s+price|price)
    \s+to\s+
    \$?(\d+(?:\.\d+)?)          # price
    \s+for\s+
    ([A-Za-z][A-Za-z\s]*)       # vehicle type after "for"
    """,
    re.IGNORECASE | re.VERBOSE,
)

# ---------------------------------------------------------------------------
# Structured multi-booking format:
#   update holding <name_or_index> <price> <vehicle_type>
#   e.g. "update holding san_april 450.00 Economy Car"
#        "update holding 1 375 Standard Car"
# ---------------------------------------------------------------------------

_BOOKING_UPDATE_PATTERN = re.compile(
    r"""
    update\s+holding\s+         # command anchor
    (\S+)                       # booking identifier (name or 1-based index)
    \s+
    \$?(\d+(?:\.\d+)?)          # price
    \s+
    ([A-Za-z][A-Za-z\s]*)       # vehicle type
    """,
    re.IGNORECASE | re.VERBOSE,
)

# ---------------------------------------------------------------------------
# Booking management commands:
#   add booking <name> <location> <pickup_date> <pickup_time> <dropoff_date> <dropoff_time>
#   list bookings
# ---------------------------------------------------------------------------

_DATE_RE = r"\d{4}-\d{2}-\d{2}"
_TIME_RE = r"\d{2}:\d{2}"

_ADD_BOOKING_PATTERN = re.compile(
    rf"""
    add\s+booking\s+            # command anchor
    (\S+)                       # name
    \s+
    (\S+)                       # pickup_location
    \s+
    ({_DATE_RE})                # pickup_date YYYY-MM-DD
    \s+
    ({_TIME_RE})                # pickup_time HH:MM
    \s+
    ({_DATE_RE})                # dropoff_date YYYY-MM-DD
    \s+
    ({_TIME_RE})                # dropoff_time HH:MM
    """,
    re.IGNORECASE | re.VERBOSE,
)

_LIST_BOOKINGS_PATTERN = re.compile(r"list\s+bookings?", re.IGNORECASE)


def parse_config_update(text: str) -> dict:
    """Parse text and return a dict describing the config action to take.

    Booking management commands (new):
        ``add booking <name> <location> <pickup_date> <pickup_time> <dropoff_date> <dropoff_time>``
        Returns: {"action": "add_booking", "name": ..., "pickup_location": ..., ...}

        ``list bookings``
        Returns: {"action": "list_bookings"}

    Structured update format (multi-booking):
        ``update holding <name_or_index> <price> <vehicle_type>``
        Returns: booking_identifier, holding_price, holding_vehicle_type

    Legacy natural-language format (no booking_identifier):
        ``update holding price to 375``
        ``update holding price to 350 for Standard Car``
        ``set holding type to SUV``
        Returns: holding_price and/or holding_vehicle_type

    Returns an empty dict if no recognised intent is found.
    """
    if not text:
        return {}

    # list bookings
    if _LIST_BOOKINGS_PATTERN.search(text):
        return {"action": "list_bookings"}

    # add booking
    m = _ADD_BOOKING_PATTERN.search(text)
    if m:
        return {
            "action": "add_booking",
            "name": m.group(1),
            "pickup_location": m.group(2),
            "pickup_date": m.group(3),
            "pickup_time": m.group(4),
            "dropoff_date": m.group(5),
            "dropoff_time": m.group(6),
        }

    # Structured update holding
    m = _BOOKING_UPDATE_PATTERN.search(text)
    if m:
        identifier = m.group(1)
        price = float(m.group(2))
        vehicle_type = m.group(3).strip()
        result: dict = {"booking_identifier": identifier}
        if price > 0:
            result["holding_price"] = price
        if vehicle_type:
            result["holding_vehicle_type"] = vehicle_type
        return result

    # Legacy: try combined "price ... for type" pattern
    result = {}
    m_combined = _PRICE_FOR_TYPE_PATTERN.search(text)
    if m_combined:
        price = float(m_combined.group(1))
        if price > 0:
            result["holding_price"] = price
        vehicle_type = m_combined.group(2).strip()
        if vehicle_type:
            result["holding_vehicle_type"] = vehicle_type
        return result

    # Legacy: price-only pattern
    m_price = _PRICE_PATTERN.search(text)
    if m_price:
        price = float(m_price.group(1))
        if price > 0:
            result["holding_price"] = price

    # Legacy: type-only pattern
    m_type = _TYPE_PATTERN.search(text)
    if m_type:
        vehicle_type = m_type.group(1).strip()
        vehicle_type = re.sub(r"\s+(and|with|price)\s.*$", "", vehicle_type, flags=re.IGNORECASE).strip()
        if vehicle_type:
            result["holding_vehicle_type"] = vehicle_type

    return result


# ---------------------------------------------------------------------------
# Booking resolver
# ---------------------------------------------------------------------------


def _resolve_booking(bookings: list, identifier: str | None) -> dict:
    """Return the booking dict for the given name or 1-based index.

    If ``identifier`` is None, returns the first booking.
    Raises ``ValueError`` for unknown names or out-of-range indices.
    """
    if identifier is None:
        return bookings[0]

    # Try 1-based integer index
    try:
        idx = int(identifier)
        if idx < 1 or idx > len(bookings):
            raise ValueError(
                f"Booking index {idx} out of range (1-{len(bookings)})"
            )
        return bookings[idx - 1]
    except ValueError as exc:
        if "out of range" in str(exc):
            raise

    # Try by name
    for booking in bookings:
        if booking.get("name") == identifier:
            return booking

    raise ValueError(f"Booking '{identifier}' not found")


# ---------------------------------------------------------------------------
# Config update + git push
# ---------------------------------------------------------------------------


def apply_config_update(updates: dict, config_path: str | Path = "config.yaml") -> bool:
    """Apply ``updates`` to ``config.yaml`` and git push.

    Dispatches on ``updates["action"]``:
    - ``"add_booking"``: append new booking to bookings list
    - ``"list_bookings"``: no-op (handled by caller via list_bookings_reply)
    - No ``action`` key: update holding fields on existing booking

    Returns ``True`` if a commit was made, ``False`` if no change.
    Raises ``FileNotFoundError`` if ``config_path`` does not exist.
    Raises ``ValueError`` for invalid booking identifiers or duplicate names.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    action = updates.get("action")

    if action == "add_booking":
        bookings = config["bookings"]
        name = updates["name"]
        if any(b.get("name") == name for b in bookings):
            raise ValueError(f"Booking '{name}' already exists")
        new_booking = {
            "name": name,
            "pickup_location": updates["pickup_location"],
            "pickup_date": updates["pickup_date"],
            "pickup_time": updates["pickup_time"],
            "dropoff_date": updates["dropoff_date"],
            "dropoff_time": updates["dropoff_time"],
        }
        bookings.append(new_booking)

    elif action == "list_bookings":
        return False

    else:
        # Update holding fields on existing booking
        bookings = config["bookings"]
        identifier = updates.get("booking_identifier")
        booking = _resolve_booking(bookings, identifier)
        changed = False
        for key, value in updates.items():
            if key == "booking_identifier":
                continue
            if booking.get(key) != value:
                booking[key] = value
                changed = True
        if not changed:
            return False

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    repo_dir = config_path.parent
    subprocess.run(["git", "add", str(config_path)], cwd=repo_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore(config): update holding config via iMessage"],
        cwd=repo_dir,
        check=True,
    )
    subprocess.run(["git", "pull", "--rebase", "--autostash"], cwd=repo_dir, check=True)
    subprocess.run(["git", "push"], cwd=repo_dir, check=True)

    return True


# ---------------------------------------------------------------------------
# iMessage reply helpers
# ---------------------------------------------------------------------------


def list_bookings_reply(bookings: list) -> str:
    """Format a bookings list into a human-readable iMessage reply string."""
    if not bookings:
        return "No bookings configured."

    lines = []
    for i, booking in enumerate(bookings, start=1):
        name = booking.get("name", f"booking-{i}")
        price = booking.get("holding_price")
        vehicle_type = booking.get("holding_vehicle_type")
        if price and vehicle_type:
            holding = f"${price:.2f} {vehicle_type}"
        else:
            holding = "no holding"
        lines.append(f"{i}. {name} — {holding}")
    return "\n".join(lines)


def send_imessage(phone: str, message: str) -> None:  # pragma: no cover
    """Send an iMessage to ``phone`` via osascript."""
    script = (
        f'tell application "Messages" to send "{message}" '
        f'to buddy "{phone}" of (first service whose service type is iMessage)'
    )
    subprocess.run(["osascript", "-e", script], check=True)

"""Remote config update via iMessage.

parse_config_update(text) — extract holding_price / holding_vehicle_type from
natural-language text.

apply_config_update(updates, config_path) — patch config.yaml and git push.
"""

import re
import subprocess
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Natural language parser
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


def parse_config_update(text: str) -> dict:
    """Parse natural-language text and return a dict of config fields to update.

    Recognised keys: ``holding_price`` (float) and ``holding_vehicle_type`` (str).
    Returns an empty dict if no recognised update intent is found.
    """
    if not text:
        return {}

    result: dict = {}

    # Try combined "price ... for type" pattern first
    m_combined = _PRICE_FOR_TYPE_PATTERN.search(text)
    if m_combined:
        price = float(m_combined.group(1))
        if price > 0:
            result["holding_price"] = price
        vehicle_type = m_combined.group(2).strip()
        if vehicle_type:
            result["holding_vehicle_type"] = vehicle_type
        return result

    # Price-only pattern
    m_price = _PRICE_PATTERN.search(text)
    if m_price:
        price = float(m_price.group(1))
        if price > 0:
            result["holding_price"] = price

    # Type-only pattern
    m_type = _TYPE_PATTERN.search(text)
    if m_type:
        vehicle_type = m_type.group(1).strip()
        # Trim trailing noise words (and, with, price, etc.)
        vehicle_type = re.sub(r"\s+(and|with|price)\s.*$", "", vehicle_type, flags=re.IGNORECASE).strip()
        if vehicle_type:
            result["holding_vehicle_type"] = vehicle_type

    return result


# ---------------------------------------------------------------------------
# Config update + git push
# ---------------------------------------------------------------------------


def apply_config_update(updates: dict, config_path: str | Path = "config.yaml") -> bool:
    """Apply ``updates`` to ``config.yaml`` and git add/commit/push.

    Returns ``True`` if a commit was made, ``False`` if values were unchanged
    (no-op).  Raises ``FileNotFoundError`` if ``config_path`` does not exist.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    changed = False
    for key, value in updates.items():
        if config["search"].get(key) != value:
            config["search"][key] = value
            changed = True

    if not changed:
        return False

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    repo_dir = config_path.parent
    subprocess.run(
        ["git", "add", str(config_path)],
        cwd=repo_dir,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "chore(config): update holding config via iMessage"],
        cwd=repo_dir,
        check=True,
    )
    subprocess.run(
        ["git", "pull", "--rebase", "--autostash"],
        cwd=repo_dir,
        check=True,
    )
    subprocess.run(
        ["git", "push"],
        cwd=repo_dir,
        check=True,
    )

    return True

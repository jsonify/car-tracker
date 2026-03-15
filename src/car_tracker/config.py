from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class SearchConfig:
    pickup_location: str
    pickup_date: str
    pickup_time: str
    dropoff_date: str
    dropoff_time: str
    holding_price: float | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.pickup_location, "search.pickup_location")
        _require_date(self.pickup_date, "search.pickup_date")
        _require_time(self.pickup_time, "search.pickup_time")
        _require_date(self.dropoff_date, "search.dropoff_date")
        _require_time(self.dropoff_time, "search.dropoff_time")


@dataclass
class DatabaseConfig:
    path: str

    def __post_init__(self) -> None:
        _require_non_empty(self.path, "database.path")


@dataclass
class Config:
    search: SearchConfig
    database: DatabaseConfig


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def _require_non_empty(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Config field '{field}' must be a non-empty string.")


def _require_date(value: str, field: str) -> None:
    _require_non_empty(value, field)
    if not _DATE_RE.match(value):
        raise ValueError(
            f"Config field '{field}' must be in YYYY-MM-DD format, got: {value!r}"
        )


def _require_time(value: str, field: str) -> None:
    _require_non_empty(value, field)
    if not _TIME_RE.match(value):
        raise ValueError(
            f"Config field '{field}' must be in HH:MM format, got: {value!r}"
        )


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_config(path: str | Path = "config.yaml") -> Config:
    """Load and validate configuration from a YAML file."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open() as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Config file must be a YAML mapping.")

    try:
        search_raw = raw["search"]
        db_raw = raw["database"]
    except KeyError as exc:
        raise ValueError(f"Config missing required section: {exc}") from exc

    holding_raw = search_raw.get("holding_price")
    holding_price = float(holding_raw) if holding_raw is not None else None

    search = SearchConfig(
        pickup_location=str(search_raw.get("pickup_location", "")),
        pickup_date=str(search_raw.get("pickup_date", "")),
        pickup_time=str(search_raw.get("pickup_time", "")),
        dropoff_date=str(search_raw.get("dropoff_date", "")),
        dropoff_time=str(search_raw.get("dropoff_time", "")),
        holding_price=holding_price,
    )
    database = DatabaseConfig(path=str(db_raw.get("path", "")))

    return Config(search=search, database=database)

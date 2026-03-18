from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import yaml


class ConfigError(ValueError):
    """Raised for invalid or unsupported configuration."""


@dataclass
class BookingConfig:
    name: str
    pickup_location: str
    pickup_date: str
    pickup_time: str
    dropoff_date: str
    dropoff_time: str
    holding_price: float | None = None
    holding_vehicle_type: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.name, "bookings[].name")
        _require_non_empty(self.pickup_location, "bookings[].pickup_location")
        _require_date(self.pickup_date, "bookings[].pickup_date")
        _require_time(self.pickup_time, "bookings[].pickup_time")
        _require_date(self.dropoff_date, "bookings[].dropoff_date")
        _require_time(self.dropoff_time, "bookings[].dropoff_time")


@dataclass
class DatabaseConfig:
    path: str

    def __post_init__(self) -> None:
        _require_non_empty(self.path, "database.path")


@dataclass
class AppConfig:
    bookings: list[BookingConfig]
    database: DatabaseConfig

    @property
    def search(self) -> BookingConfig:
        """Backward-compatible accessor — returns the first booking."""
        return self.bookings[0]

    def get_booking_by_name(self, name: str) -> BookingConfig:
        """Return the booking with the given name, or raise KeyError."""
        for b in self.bookings:
            if b.name == name:
                return b
        raise KeyError(f"No booking with name '{name}'")

    def get_booking_by_index(self, n: int) -> BookingConfig:
        """Return the booking at 1-based index n, or raise IndexError."""
        if n < 1 or n > len(self.bookings):
            raise IndexError(
                f"Booking index {n} out of range (1-{len(self.bookings)})"
            )
        return self.bookings[n - 1]


# Backward-compatibility aliases
Config = AppConfig
SearchConfig = BookingConfig


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


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    """Load and validate configuration from a YAML file."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open() as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Config file must be a YAML mapping.")

    if "search" in raw:
        raise ConfigError(
            "Config uses old 'search:' format. Migrate to a 'bookings:' list. "
            "See README for the new format."
        )

    if "bookings" not in raw:
        raise ConfigError("Config missing required 'bookings' section.")

    if "database" not in raw:
        raise ConfigError("Config missing required 'database' section.")

    bookings_raw = raw["bookings"]
    if bookings_raw is None:
        bookings_raw = []
    if not isinstance(bookings_raw, list):
        raise ConfigError("'bookings' must be a list.")

    bookings: list[BookingConfig] = []
    for i, b in enumerate(bookings_raw):
        if not isinstance(b, dict):
            raise ConfigError(f"bookings[{i}] must be a YAML mapping.")

        holding_raw = b.get("holding_price")
        holding_type_raw = b.get("holding_vehicle_type")
        # Both fields must be present to form a valid pair; one without the other → both None
        if holding_raw is not None and holding_type_raw is not None:
            holding_price: float | None = float(holding_raw)
            holding_vehicle_type: str | None = str(holding_type_raw)
        else:
            holding_price = None
            holding_vehicle_type = None

        bookings.append(
            BookingConfig(
                name=str(b.get("name", "")),
                pickup_location=str(b.get("pickup_location", "")),
                pickup_date=str(b.get("pickup_date", "")),
                pickup_time=str(b.get("pickup_time", "")),
                dropoff_date=str(b.get("dropoff_date", "")),
                dropoff_time=str(b.get("dropoff_time", "")),
                holding_price=holding_price,
                holding_vehicle_type=holding_vehicle_type,
            )
        )

    names = [b.name for b in bookings]
    if len(names) != len(set(names)):
        raise ConfigError("Booking names must be unique.")

    db_raw = raw["database"]
    database = DatabaseConfig(path=str(db_raw.get("path", "")))

    return AppConfig(bookings=bookings, database=database)

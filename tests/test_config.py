from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from car_tracker.config import AppConfig, BookingConfig, Config, ConfigError, DatabaseConfig, SearchConfig, load_config


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_yaml(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "san"
            pickup_location: "LAX"
            pickup_date: "2026-04-01"
            pickup_time: "10:00"
            dropoff_date: "2026-04-05"
            dropoff_time: "10:00"
        database:
          path: "data/results.db"
        """)
    )
    return cfg


@pytest.fixture
def two_booking_yaml(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "hawaii"
            pickup_location: "HNL"
            pickup_date: "2026-05-01"
            pickup_time: "10:00"
            dropoff_date: "2026-05-08"
            dropoff_time: "10:00"
            holding_price: 450.00
            holding_vehicle_type: "Economy Car"
          - name: "vegas"
            pickup_location: "LAS"
            pickup_date: "2026-06-01"
            pickup_time: "09:00"
            dropoff_date: "2026-06-05"
            dropoff_time: "09:00"
        database:
          path: "data/results.db"
        """)
    )
    return cfg


# ---------------------------------------------------------------------------
# Happy path — single booking
# ---------------------------------------------------------------------------


def test_load_valid_config(valid_yaml: Path) -> None:
    cfg = load_config(valid_yaml)
    assert isinstance(cfg, AppConfig)
    assert len(cfg.bookings) == 1
    b = cfg.bookings[0]
    assert b.name == "san"
    assert b.pickup_location == "LAX"
    assert b.pickup_date == "2026-04-01"
    assert b.pickup_time == "10:00"
    assert b.dropoff_date == "2026-04-05"
    assert b.dropoff_time == "10:00"
    assert cfg.database.path == "data/results.db"
    assert b.holding_price is None


def test_search_property_returns_first_booking(valid_yaml: Path) -> None:
    """AppConfig.search is a backward-compat property returning bookings[0]."""
    cfg = load_config(valid_yaml)
    assert cfg.search is cfg.bookings[0]


def test_config_alias_is_appconfig() -> None:
    """Config is an alias for AppConfig for backward compatibility."""
    assert Config is AppConfig


def test_searchconfig_alias_is_bookingconfig() -> None:
    """SearchConfig is an alias for BookingConfig for backward compatibility."""
    assert SearchConfig is BookingConfig


# ---------------------------------------------------------------------------
# Happy path — multiple bookings
# ---------------------------------------------------------------------------


def test_multi_booking_config_loads(two_booking_yaml: Path) -> None:
    cfg = load_config(two_booking_yaml)
    assert len(cfg.bookings) == 2
    hawaii = cfg.bookings[0]
    vegas = cfg.bookings[1]
    assert hawaii.name == "hawaii"
    assert hawaii.pickup_location == "HNL"
    assert hawaii.holding_price == 450.00
    assert hawaii.holding_vehicle_type == "Economy Car"
    assert vegas.name == "vegas"
    assert vegas.pickup_location == "LAS"
    assert vegas.holding_price is None


def test_booking_holding_pair_both_present(two_booking_yaml: Path) -> None:
    cfg = load_config(two_booking_yaml)
    b = cfg.bookings[0]
    assert b.holding_price == 450.00
    assert b.holding_vehicle_type == "Economy Car"


def test_booking_without_holding_pair(two_booking_yaml: Path) -> None:
    cfg = load_config(two_booking_yaml)
    b = cfg.bookings[1]
    assert b.holding_price is None
    assert b.holding_vehicle_type is None


# ---------------------------------------------------------------------------
# Holding price pair logic
# ---------------------------------------------------------------------------


def test_holding_price_parsed(tmp_path: Path) -> None:
    """Both holding_price and holding_vehicle_type required for the pair to be active."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "test"
            pickup_location: "LAX"
            pickup_date: "2026-04-01"
            pickup_time: "10:00"
            dropoff_date: "2026-04-05"
            dropoff_time: "10:00"
            holding_price: 396.63
            holding_vehicle_type: "Economy Car"
        database:
          path: "data/results.db"
        """)
    )
    result = load_config(cfg)
    assert result.bookings[0].holding_price == 396.63
    assert result.bookings[0].holding_vehicle_type == "Economy Car"


def test_holding_price_omitted_is_none(valid_yaml: Path) -> None:
    result = load_config(valid_yaml)
    assert result.bookings[0].holding_price is None


def test_holding_pair_both_present(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "test"
            pickup_location: "LAX"
            pickup_date: "2026-04-01"
            pickup_time: "10:00"
            dropoff_date: "2026-04-05"
            dropoff_time: "10:00"
            holding_price: 396.63
            holding_vehicle_type: "Economy Car"
        database:
          path: "data/results.db"
        """)
    )
    result = load_config(cfg)
    assert result.bookings[0].holding_price == 396.63
    assert result.bookings[0].holding_vehicle_type == "Economy Car"


def test_holding_pair_price_only_sets_both_none(tmp_path: Path) -> None:
    """holding_price without holding_vehicle_type → both set to None."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "test"
            pickup_location: "LAX"
            pickup_date: "2026-04-01"
            pickup_time: "10:00"
            dropoff_date: "2026-04-05"
            dropoff_time: "10:00"
            holding_price: 396.63
        database:
          path: "data/results.db"
        """)
    )
    result = load_config(cfg)
    assert result.bookings[0].holding_price is None
    assert result.bookings[0].holding_vehicle_type is None


def test_holding_pair_type_only_sets_both_none(tmp_path: Path) -> None:
    """holding_vehicle_type without holding_price → both set to None."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "test"
            pickup_location: "LAX"
            pickup_date: "2026-04-01"
            pickup_time: "10:00"
            dropoff_date: "2026-04-05"
            dropoff_time: "10:00"
            holding_vehicle_type: "Economy Car"
        database:
          path: "data/results.db"
        """)
    )
    result = load_config(cfg)
    assert result.bookings[0].holding_price is None
    assert result.bookings[0].holding_vehicle_type is None


def test_holding_vehicle_type_omitted_is_none(valid_yaml: Path) -> None:
    result = load_config(valid_yaml)
    assert result.bookings[0].holding_vehicle_type is None


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def test_get_booking_by_name_found(two_booking_yaml: Path) -> None:
    cfg = load_config(two_booking_yaml)
    b = cfg.get_booking_by_name("vegas")
    assert b.pickup_location == "LAS"


def test_get_booking_by_name_not_found(two_booking_yaml: Path) -> None:
    cfg = load_config(two_booking_yaml)
    with pytest.raises(KeyError, match="No booking with name 'unknown'"):
        cfg.get_booking_by_name("unknown")


def test_get_booking_by_index_valid(two_booking_yaml: Path) -> None:
    cfg = load_config(two_booking_yaml)
    assert cfg.get_booking_by_index(1).name == "hawaii"
    assert cfg.get_booking_by_index(2).name == "vegas"


def test_get_booking_by_index_zero_raises(two_booking_yaml: Path) -> None:
    cfg = load_config(two_booking_yaml)
    with pytest.raises(IndexError, match="out of range"):
        cfg.get_booking_by_index(0)


def test_get_booking_by_index_out_of_range(two_booking_yaml: Path) -> None:
    cfg = load_config(two_booking_yaml)
    with pytest.raises(IndexError, match="out of range"):
        cfg.get_booking_by_index(3)


# ---------------------------------------------------------------------------
# File-level errors
# ---------------------------------------------------------------------------


def test_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_config("nonexistent.yaml")


def test_old_search_format_raises_config_error(tmp_path: Path) -> None:
    """Old single-booking 'search:' format raises ConfigError with migration hint."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
          pickup_location: "LAX"
          pickup_date: "2026-04-01"
          pickup_time: "10:00"
          dropoff_date: "2026-04-05"
          dropoff_time: "10:00"
        database:
          path: "data/results.db"
        """)
    )
    with pytest.raises(ConfigError, match="old 'search:' format"):
        load_config(cfg)


def test_missing_bookings_section(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("database:\n  path: data/results.db\n")
    with pytest.raises(ConfigError, match="missing required"):
        load_config(cfg)


def test_empty_bookings_list_raises(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("bookings: []\ndatabase:\n  path: data/results.db\n")
    with pytest.raises(ConfigError, match="non-empty"):
        load_config(cfg)


def test_duplicate_booking_names_raises(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "trip"
            pickup_location: "LAX"
            pickup_date: "2026-04-01"
            pickup_time: "10:00"
            dropoff_date: "2026-04-05"
            dropoff_time: "10:00"
          - name: "trip"
            pickup_location: "SFO"
            pickup_date: "2026-05-01"
            pickup_time: "10:00"
            dropoff_date: "2026-05-05"
            dropoff_time: "10:00"
        database:
          path: "data/results.db"
        """)
    )
    with pytest.raises(ConfigError, match="unique"):
        load_config(cfg)


def test_missing_database_section(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "test"
            pickup_location: "LAX"
            pickup_date: "2026-04-01"
            pickup_time: "10:00"
            dropoff_date: "2026-04-05"
            dropoff_time: "10:00"
        """)
    )
    with pytest.raises(ConfigError, match="missing required"):
        load_config(cfg)


def test_non_mapping_yaml(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("- just a list\n")
    with pytest.raises(ValueError, match="must be a YAML mapping"):
        load_config(cfg)


# ---------------------------------------------------------------------------
# Field validation — dates
# ---------------------------------------------------------------------------


def test_invalid_pickup_date_format() -> None:
    with pytest.raises(ValueError, match="pickup_date"):
        BookingConfig(
            name="test",
            pickup_location="LAX",
            pickup_date="01-04-2026",  # wrong format
            pickup_time="10:00",
            dropoff_date="2026-04-05",
            dropoff_time="10:00",
        )


def test_invalid_dropoff_date_format() -> None:
    with pytest.raises(ValueError, match="dropoff_date"):
        BookingConfig(
            name="test",
            pickup_location="LAX",
            pickup_date="2026-04-01",
            pickup_time="10:00",
            dropoff_date="April 5",  # wrong format
            dropoff_time="10:00",
        )


# ---------------------------------------------------------------------------
# Field validation — times
# ---------------------------------------------------------------------------


def test_invalid_pickup_time_format() -> None:
    with pytest.raises(ValueError, match="pickup_time"):
        BookingConfig(
            name="test",
            pickup_location="LAX",
            pickup_date="2026-04-01",
            pickup_time="10am",  # wrong format
            dropoff_date="2026-04-05",
            dropoff_time="10:00",
        )


# ---------------------------------------------------------------------------
# Field validation — empty strings
# ---------------------------------------------------------------------------


def test_empty_pickup_location() -> None:
    with pytest.raises(ValueError, match="pickup_location"):
        BookingConfig(
            name="test",
            pickup_location="",
            pickup_date="2026-04-01",
            pickup_time="10:00",
            dropoff_date="2026-04-05",
            dropoff_time="10:00",
        )


def test_empty_database_path() -> None:
    with pytest.raises(ValueError, match="database.path"):
        DatabaseConfig(path="")


# ---------------------------------------------------------------------------
# Config safety — repo config.yaml has no secrets
# ---------------------------------------------------------------------------


_CREDENTIAL_KEYS = {
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "smtp_password",
    "smtp_user",
    "smtp_username",
    "email_password",
    "auth",
}

_REPO_CONFIG = Path(__file__).parent.parent / "config.yaml"


def _collect_keys(obj: object) -> set[str]:
    """Recursively collect all mapping keys from a YAML document."""
    keys: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.add(str(k).lower())
            keys |= _collect_keys(v)
    elif isinstance(obj, list):
        for item in obj:
            keys |= _collect_keys(item)
    return keys


def test_repo_config_is_parseable_yaml() -> None:
    """The committed config.yaml must be valid YAML."""
    import yaml

    raw = _REPO_CONFIG.read_text()
    doc = yaml.safe_load(raw)
    assert doc is not None, "config.yaml parsed to None — file may be empty"
    assert isinstance(doc, dict), "config.yaml must be a YAML mapping at the top level"


def test_repo_config_has_no_credential_keys() -> None:
    """Guard against accidentally committing secrets into config.yaml."""
    import yaml

    doc = yaml.safe_load(_REPO_CONFIG.read_text())
    found = _collect_keys(doc) & _CREDENTIAL_KEYS
    assert not found, (
        f"Credential-related key(s) found in config.yaml: {sorted(found)}. "
        "Move secrets to .env instead."
    )


def test_repo_config_loads_via_load_config() -> None:
    """The committed config.yaml must be accepted by load_config without errors."""
    cfg = load_config(_REPO_CONFIG)
    assert isinstance(cfg, AppConfig)
    assert len(cfg.bookings) >= 1
    assert cfg.bookings[0].pickup_location  # non-empty
    assert cfg.database.path  # non-empty

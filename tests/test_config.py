from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from car_tracker.config import Config, DatabaseConfig, SearchConfig, load_config


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_yaml(tmp_path: Path) -> Path:
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
    return cfg


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_load_valid_config(valid_yaml: Path) -> None:
    cfg = load_config(valid_yaml)
    assert isinstance(cfg, Config)
    assert cfg.search.pickup_location == "LAX"
    assert cfg.search.pickup_date == "2026-04-01"
    assert cfg.search.pickup_time == "10:00"
    assert cfg.search.dropoff_date == "2026-04-05"
    assert cfg.search.dropoff_time == "10:00"
    assert cfg.database.path == "data/results.db"
    assert cfg.search.holding_price is None


def test_holding_price_parsed(tmp_path: Path) -> None:
    """Both holding_price and holding_vehicle_type required for the pair to be active."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
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
    assert result.search.holding_price == 396.63
    assert result.search.holding_vehicle_type == "Economy Car"


def test_holding_price_omitted_is_none(valid_yaml: Path) -> None:
    result = load_config(valid_yaml)
    assert result.search.holding_price is None


def test_holding_pair_both_present(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
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
    assert result.search.holding_price == 396.63
    assert result.search.holding_vehicle_type == "Economy Car"


def test_holding_pair_price_only_sets_both_none(tmp_path: Path) -> None:
    """holding_price without holding_vehicle_type → both set to None."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
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
    assert result.search.holding_price is None
    assert result.search.holding_vehicle_type is None


def test_holding_pair_type_only_sets_both_none(tmp_path: Path) -> None:
    """holding_vehicle_type without holding_price → both set to None."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
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
    assert result.search.holding_price is None
    assert result.search.holding_vehicle_type is None


def test_holding_vehicle_type_omitted_is_none(valid_yaml: Path) -> None:
    result = load_config(valid_yaml)
    assert result.search.holding_vehicle_type is None


# ---------------------------------------------------------------------------
# File-level errors
# ---------------------------------------------------------------------------


def test_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_config("nonexistent.yaml")


def test_missing_search_section(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("database:\n  path: data/results.db\n")
    with pytest.raises(ValueError, match="missing required section"):
        load_config(cfg)


def test_missing_database_section(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
          pickup_location: "LAX"
          pickup_date: "2026-04-01"
          pickup_time: "10:00"
          dropoff_date: "2026-04-05"
          dropoff_time: "10:00"
        """)
    )
    with pytest.raises(ValueError, match="missing required section"):
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
        SearchConfig(
            pickup_location="LAX",
            pickup_date="01-04-2026",  # wrong format
            pickup_time="10:00",
            dropoff_date="2026-04-05",
            dropoff_time="10:00",
        )


def test_invalid_dropoff_date_format() -> None:
    with pytest.raises(ValueError, match="dropoff_date"):
        SearchConfig(
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
        SearchConfig(
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
        SearchConfig(
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
    assert isinstance(cfg, Config)
    assert cfg.search.pickup_location  # non-empty
    assert cfg.database.path  # non-empty

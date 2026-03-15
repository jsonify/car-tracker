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
    assert result.search.holding_price == 396.63


def test_holding_price_omitted_is_none(valid_yaml: Path) -> None:
    result = load_config(valid_yaml)
    assert result.search.holding_price is None


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

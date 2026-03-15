from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from car_tracker.__main__ import main, parse_args
from car_tracker.scraper import VehicleResult


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------


def test_defaults():
    args = parse_args([])
    assert args.debug is False
    assert args.config == "config.yaml"


def test_debug_flag():
    args = parse_args(["--debug"])
    assert args.debug is True


def test_custom_config():
    args = parse_args(["--config", "my_config.yaml"])
    assert args.config == "my_config.yaml"


def test_debug_and_config():
    args = parse_args(["--debug", "--config", "other.yaml"])
    assert args.debug is True
    assert args.config == "other.yaml"


# ---------------------------------------------------------------------------
# main() integration (mocked scraper)
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_config_file(tmp_path: Path) -> Path:
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


def test_main_missing_config_returns_1():
    result = main(["--config", "nonexistent.yaml"])
    assert result == 1


def test_main_success(valid_config_file: Path, tmp_path: Path):
    db_path = str(tmp_path / "results.db")
    # Patch the config to use a temp DB path
    with patch("car_tracker.__main__.load_config") as mock_load, \
         patch("car_tracker.__main__.init_db") as mock_init, \
         patch("car_tracker.__main__.save_run", return_value=1) as mock_run, \
         patch("car_tracker.__main__.save_vehicles") as mock_veh, \
         patch("car_tracker.__main__.scrape") as mock_scrape:

        mock_config = MagicMock()
        mock_config.database.path = db_path
        mock_config.search.pickup_location = "LAX"
        mock_config.search.pickup_date = "2026-04-01"
        mock_config.search.pickup_time = "10:00"
        mock_config.search.dropoff_date = "2026-04-05"
        mock_config.search.dropoff_time = "10:00"
        mock_load.return_value = mock_config

        mock_scrape.return_value = [
            VehicleResult(1, "Economy Car", "Alamo", 396.63, 99.16),
            VehicleResult(2, "Compact Car", "Avis", 410.00, 102.50),
        ]

        result = main(["--config", str(valid_config_file)])

    assert result == 0
    mock_init.assert_called_once_with(db_path)
    mock_run.assert_called_once()
    mock_veh.assert_called_once()
    # Verify vehicle records were created with correct format
    call_args = mock_veh.call_args
    records = call_args[0][2]
    assert len(records) == 2
    assert records[0].name == "Economy Car (Alamo)"
    assert records[0].total_price == 396.63


def test_main_scrape_failure_returns_1(valid_config_file: Path):
    with patch("car_tracker.__main__.load_config") as mock_load, \
         patch("car_tracker.__main__.init_db"), \
         patch("car_tracker.__main__.scrape", side_effect=RuntimeError("Scrape failed")):

        mock_config = MagicMock()
        mock_config.database.path = "data/results.db"
        mock_config.search.pickup_location = "LAX"
        mock_config.search.pickup_date = "2026-04-01"
        mock_config.search.pickup_time = "10:00"
        mock_config.search.dropoff_date = "2026-04-05"
        mock_config.search.dropoff_time = "10:00"
        mock_load.return_value = mock_config

        result = main(["--config", str(valid_config_file)])

    assert result == 1

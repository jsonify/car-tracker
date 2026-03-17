from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, call, patch

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
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_config_file(tmp_path: Path) -> Path:
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


def _make_booking_mock(
    name: str = "san",
    location: str = "LAX",
    pickup_date: str = "2026-04-01",
    dropoff_date: str = "2026-04-05",
    holding_price: float | None = None,
    holding_type: str | None = None,
) -> MagicMock:
    m = MagicMock()
    m.name = name
    m.pickup_location = location
    m.pickup_date = pickup_date
    m.pickup_time = "10:00"
    m.dropoff_date = dropoff_date
    m.dropoff_time = "10:00"
    m.holding_price = holding_price
    m.holding_vehicle_type = holding_type
    return m


_FAKE_RESULTS = [
    VehicleResult(1, "Economy Car", "Alamo", 396.63, 99.16),
    VehicleResult(2, "Compact Car", "Avis", 410.00, 102.50),
]


# ---------------------------------------------------------------------------
# main() integration (mocked scraper + emailer)
# ---------------------------------------------------------------------------


def test_main_missing_config_returns_1():
    result = main(["--config", "nonexistent.yaml"])
    assert result == 1


def test_main_success(valid_config_file: Path, tmp_path: Path):
    db_path = str(tmp_path / "results.db")
    booking = _make_booking_mock(holding_price=420.00, holding_type="Economy Car")

    with patch("car_tracker.__main__.load_config") as mock_load, \
         patch("car_tracker.__main__.init_db") as mock_init, \
         patch("car_tracker.__main__.save_run", return_value=1) as mock_run, \
         patch("car_tracker.__main__.save_vehicles") as mock_veh, \
         patch("car_tracker.__main__.get_prior_run_vehicles", return_value={}) as mock_prior, \
         patch("car_tracker.__main__.scrape") as mock_scrape, \
         patch("car_tracker.__main__.load_email_config"), \
         patch("car_tracker.__main__.send_email") as mock_send:

        mock_config = MagicMock()
        mock_config.database.path = db_path
        mock_config.bookings = [booking]
        mock_load.return_value = mock_config
        mock_scrape.return_value = _FAKE_RESULTS

        result = main(["--config", str(valid_config_file)])

    assert result == 0
    mock_init.assert_called_once_with(db_path)
    mock_run.assert_called_once()
    mock_veh.assert_called_once()
    mock_prior.assert_called_once()
    mock_send.assert_called_once()
    # Verify holding pair passed to save_run
    run_kwargs = mock_run.call_args[1]
    assert run_kwargs["holding_price"] == 420.00
    assert run_kwargs["holding_vehicle_type"] == "Economy Car"
    assert run_kwargs["booking_name"] == "san"
    # Verify success subject contains booking name
    subject = mock_send.call_args[0][0]
    assert subject.startswith("Costco Travel Rental Prices —")
    assert "san" in subject
    # Verify vehicle records created with correct format
    records = mock_veh.call_args[0][2]
    assert len(records) == 2
    assert records[0].name == "Economy Car (Alamo)"
    assert records[0].total_price == 396.63


def test_main_iterates_all_bookings(valid_config_file: Path, tmp_path: Path):
    """Scrape is called once per booking; a single combined email is sent."""
    db_path = str(tmp_path / "results.db")
    booking1 = _make_booking_mock("hawaii", "HNL", "2026-05-01", "2026-05-08")
    booking2 = _make_booking_mock("vegas", "LAS", "2026-06-01", "2026-06-05")

    with patch("car_tracker.__main__.load_config") as mock_load, \
         patch("car_tracker.__main__.init_db"), \
         patch("car_tracker.__main__.save_run", return_value=1), \
         patch("car_tracker.__main__.save_vehicles"), \
         patch("car_tracker.__main__.get_prior_run_vehicles", return_value={}), \
         patch("car_tracker.__main__.scrape") as mock_scrape, \
         patch("car_tracker.__main__.load_email_config"), \
         patch("car_tracker.__main__.send_email") as mock_send:

        mock_config = MagicMock()
        mock_config.database.path = db_path
        mock_config.bookings = [booking1, booking2]
        mock_load.return_value = mock_config
        mock_scrape.return_value = [VehicleResult(1, "Economy Car", "Alamo", 400.0, 100.0)]

        result = main(["--config", str(valid_config_file)])

    assert result == 0
    assert mock_scrape.call_count == 2
    mock_send.assert_called_once()  # single combined email
    subject = mock_send.call_args[0][0]
    assert "hawaii" in subject
    assert "vegas" in subject


def test_main_saves_booking_name_per_run(valid_config_file: Path, tmp_path: Path):
    """save_run is called with the booking's name."""
    db_path = str(tmp_path / "results.db")
    booking = _make_booking_mock("hawaii", "HNL")

    with patch("car_tracker.__main__.load_config") as mock_load, \
         patch("car_tracker.__main__.init_db"), \
         patch("car_tracker.__main__.save_run", return_value=1) as mock_run, \
         patch("car_tracker.__main__.save_vehicles"), \
         patch("car_tracker.__main__.get_prior_run_vehicles", return_value={}), \
         patch("car_tracker.__main__.scrape") as mock_scrape, \
         patch("car_tracker.__main__.load_email_config"), \
         patch("car_tracker.__main__.send_email"):

        mock_config = MagicMock()
        mock_config.database.path = db_path
        mock_config.bookings = [booking]
        mock_load.return_value = mock_config
        mock_scrape.return_value = [VehicleResult(1, "Economy Car", "Alamo", 400.0, 100.0)]

        main(["--config", str(valid_config_file)])

    run_kwargs = mock_run.call_args[1]
    assert run_kwargs["booking_name"] == "hawaii"


def test_main_scrape_failure_returns_1(valid_config_file: Path):
    booking = _make_booking_mock()

    with patch("car_tracker.__main__.load_config") as mock_load, \
         patch("car_tracker.__main__.init_db"), \
         patch("car_tracker.__main__.scrape", side_effect=RuntimeError("Scrape failed")), \
         patch("car_tracker.__main__.load_email_config"), \
         patch("car_tracker.__main__.send_email") as mock_send:

        mock_config = MagicMock()
        mock_config.database.path = "data/results.db"
        mock_config.bookings = [booking]
        mock_load.return_value = mock_config

        result = main(["--config", str(valid_config_file)])

    assert result == 1
    mock_send.assert_called_once()
    subject = mock_send.call_args[0][0]
    assert subject.startswith("Costco Travel Scrape Failed —")
    assert "san" in subject


def test_main_scrape_failure_email_error_still_returns_1(valid_config_file: Path):
    """Email send failure on scrape error should not mask the scrape failure."""
    booking = _make_booking_mock()

    with patch("car_tracker.__main__.load_config") as mock_load, \
         patch("car_tracker.__main__.init_db"), \
         patch("car_tracker.__main__.scrape", side_effect=RuntimeError("Scrape failed")), \
         patch("car_tracker.__main__.load_email_config", side_effect=ValueError("no creds")):

        mock_config = MagicMock()
        mock_config.database.path = "data/results.db"
        mock_config.bookings = [booking]
        mock_load.return_value = mock_config

        result = main(["--config", str(valid_config_file)])

    assert result == 1

"""Tests for the new Discord-oriented DB query functions:
  - get_latest_run_vehicles
  - get_price_history
"""

from __future__ import annotations

from pathlib import Path

import pytest

from car_tracker.database import (
    VehicleRecord,
    get_latest_run_vehicles,
    get_price_history,
    init_db,
    save_run,
    save_vehicles,
)


@pytest.fixture
def db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return db_path


def _save(db: Path, booking: str = "trip", vehicles: list[tuple] | None = None) -> int:
    run_id = save_run(db, "SAN", "2026-04-02", "10:00", "2026-04-08", "10:00", booking_name=booking)
    if vehicles:
        recs = [VehicleRecord(i + 1, name, price, price / 6) for i, (name, price) in enumerate(vehicles)]
        save_vehicles(db, run_id, recs)
    return run_id


# ---------------------------------------------------------------------------
# get_latest_run_vehicles
# ---------------------------------------------------------------------------


def test_get_latest_run_vehicles_no_runs(db: Path) -> None:
    run_at, vehicles = get_latest_run_vehicles(db, "trip")
    assert run_at is None
    assert vehicles == []


def test_get_latest_run_vehicles_single_run(db: Path) -> None:
    _save(db, vehicles=[("Economy Car (Alamo)", 200.0)])
    run_at, vehicles = get_latest_run_vehicles(db, "trip")
    assert run_at is not None
    assert len(vehicles) == 1
    assert vehicles[0].name == "Economy Car (Alamo)"
    assert vehicles[0].total_price == 200.0


def test_get_latest_run_vehicles_returns_most_recent(db: Path) -> None:
    _save(db, vehicles=[("Economy Car (Alamo)", 200.0)])
    _save(db, vehicles=[("Economy Car (Alamo)", 180.0), ("Standard Car (Budget)", 300.0)])
    _, vehicles = get_latest_run_vehicles(db, "trip")
    # Most recent run had 2 vehicles
    assert len(vehicles) == 2


def test_get_latest_run_vehicles_sorted_by_price(db: Path) -> None:
    _save(db, vehicles=[
        ("Standard Car (Budget)", 300.0),
        ("Economy Car (Alamo)", 200.0),
        ("Compact Car (Avis)", 250.0),
    ])
    _, vehicles = get_latest_run_vehicles(db, "trip")
    prices = [v.total_price for v in vehicles]
    assert prices == sorted(prices)


def test_get_latest_run_vehicles_scoped_by_booking(db: Path) -> None:
    _save(db, booking="trip_a", vehicles=[("Economy Car (Alamo)", 200.0)])
    _save(db, booking="trip_b", vehicles=[("Standard Car (Budget)", 350.0)])
    _, vehicles = get_latest_run_vehicles(db, "trip_a")
    assert len(vehicles) == 1
    assert vehicles[0].name == "Economy Car (Alamo)"


def test_get_latest_run_vehicles_unknown_booking(db: Path) -> None:
    _save(db, booking="trip", vehicles=[("Economy Car (Alamo)", 200.0)])
    run_at, vehicles = get_latest_run_vehicles(db, "unknown")
    assert run_at is None
    assert vehicles == []


# ---------------------------------------------------------------------------
# get_price_history
# ---------------------------------------------------------------------------


def test_get_price_history_no_data(db: Path) -> None:
    result = get_price_history(db, "trip", "Economy Car")
    assert result == []


def test_get_price_history_exact_name_match(db: Path) -> None:
    _save(db, vehicles=[("Economy Car", 200.0)])
    result = get_price_history(db, "trip", "Economy Car")
    assert len(result) == 1
    assert result[0][1] == 200.0


def test_get_price_history_brand_suffix_match(db: Path) -> None:
    """Should match 'Economy Car (Alamo)' when searching for 'Economy Car'."""
    _save(db, vehicles=[("Economy Car (Alamo)", 200.0)])
    result = get_price_history(db, "trip", "Economy Car")
    assert len(result) == 1
    assert result[0][1] == 200.0


def test_get_price_history_multiple_runs_ordered_most_recent_first(db: Path) -> None:
    _save(db, vehicles=[("Economy Car (Alamo)", 220.0)])
    _save(db, vehicles=[("Economy Car (Alamo)", 210.0)])
    _save(db, vehicles=[("Economy Car (Alamo)", 200.0)])
    result = get_price_history(db, "trip", "Economy Car")
    assert len(result) == 3
    prices = [r[1] for r in result]
    # Most recent run (200.0) should be first
    assert prices[0] == 200.0
    assert prices[-1] == 220.0


def test_get_price_history_returns_best_price_per_run(db: Path) -> None:
    """When multiple brands exist for same category, should return the cheapest."""
    run_id = save_run(db, "SAN", "2026-04-02", "10:00", "2026-04-08", "10:00", booking_name="trip")
    save_vehicles(db, run_id, [
        VehicleRecord(1, "Economy Car (Alamo)", 200.0, 33.33),
        VehicleRecord(2, "Economy Car (Budget)", 185.0, 30.83),
        VehicleRecord(3, "Economy Car (Hertz)", 210.0, 35.0),
    ])
    result = get_price_history(db, "trip", "Economy Car")
    assert len(result) == 1
    assert result[0][1] == 185.0  # cheapest of the three


def test_get_price_history_respects_limit(db: Path) -> None:
    for price in range(100, 110):
        _save(db, vehicles=[("Economy Car (Alamo)", float(price))])
    result = get_price_history(db, "trip", "Economy Car", limit=5)
    assert len(result) == 5


def test_get_price_history_scoped_by_booking(db: Path) -> None:
    _save(db, booking="trip_a", vehicles=[("Economy Car (Alamo)", 200.0)])
    _save(db, booking="trip_b", vehicles=[("Economy Car (Alamo)", 350.0)])
    result = get_price_history(db, "trip_a", "Economy Car")
    assert len(result) == 1
    assert result[0][1] == 200.0


def test_get_price_history_no_match_for_different_category(db: Path) -> None:
    _save(db, vehicles=[("Standard Car (Budget)", 300.0)])
    result = get_price_history(db, "trip", "Economy Car")
    assert result == []


def test_get_price_history_returns_run_at_timestamps(db: Path) -> None:
    _save(db, vehicles=[("Economy Car (Alamo)", 200.0)])
    result = get_price_history(db, "trip", "Economy Car")
    assert len(result) == 1
    run_at, price = result[0]
    assert isinstance(run_at, str)
    assert len(run_at) > 0

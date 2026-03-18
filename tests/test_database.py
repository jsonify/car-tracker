from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from car_tracker.database import VehicleRecord, get_category_price_history, get_prior_run_vehicles, init_db, migrate_db, save_run, save_vehicles


@pytest.fixture
def db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return db_path


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------


def test_init_creates_runs_table(db: Path) -> None:
    conn = sqlite3.connect(db)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "runs" in tables


def test_init_creates_vehicles_table(db: Path) -> None:
    conn = sqlite3.connect(db)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "vehicles" in tables


def test_init_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "idempotent.db"
    init_db(db_path)
    init_db(db_path)  # second call must not raise


def test_init_creates_parent_dirs(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "dir" / "results.db"
    init_db(db_path)
    assert db_path.exists()


# ---------------------------------------------------------------------------
# save_run
# ---------------------------------------------------------------------------


def test_save_run_returns_id(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    assert isinstance(run_id, int)
    assert run_id >= 1


def test_save_run_stores_fields(db: Path) -> None:
    save_run(db, "SFO", "2026-05-01", "09:00", "2026-05-05", "18:00")
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT pickup_location, pickup_date FROM runs WHERE id=1").fetchone()
    assert row == ("SFO", "2026-05-01")


def test_save_run_increments_id(db: Path) -> None:
    id1 = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    id2 = save_run(db, "JFK", "2026-04-01", "10:00", "2026-04-05", "10:00")
    assert id2 == id1 + 1


# ---------------------------------------------------------------------------
# save_vehicles
# ---------------------------------------------------------------------------


def test_save_vehicles_inserts_rows(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    vehicles = [
        VehicleRecord(position=1, name="Economy", total_price=120.0, price_per_day=30.0),
        VehicleRecord(position=2, name="Full-Size SUV", total_price=280.0, price_per_day=70.0),
    ]
    save_vehicles(db, run_id, vehicles)
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT position, name, total_price, price_per_day FROM vehicles").fetchall()
    assert len(rows) == 2
    assert rows[0] == (1, "Economy", 120.0, 30.0)
    assert rows[1] == (2, "Full-Size SUV", 280.0, 70.0)


def test_save_vehicles_empty_list(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run_id, [])  # must not raise
    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
    assert count == 0


def test_save_vehicles_associates_run_id(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run_id, [VehicleRecord(1, "Compact", 100.0, 25.0)])
    conn = sqlite3.connect(db)
    stored_run_id = conn.execute("SELECT run_id FROM vehicles").fetchone()[0]
    assert stored_run_id == run_id


def test_save_vehicles_preserves_order(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    vehicles = [VehicleRecord(i, f"Car {i}", float(i * 10), float(i * 2)) for i in range(1, 6)]
    save_vehicles(db, run_id, vehicles)
    conn = sqlite3.connect(db)
    positions = [r[0] for r in conn.execute("SELECT position FROM vehicles ORDER BY id")]
    assert positions == list(range(1, 6))


# ---------------------------------------------------------------------------
# get_prior_run_vehicles
# ---------------------------------------------------------------------------


def test_get_prior_run_vehicles_no_prior_run(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run_id, [VehicleRecord(1, "Economy Car (Alamo)", 200.0, 50.0)])
    result = get_prior_run_vehicles(db, run_id, "LAX", "2026-04-01", "2026-04-05")
    assert result == {}


def test_get_prior_run_vehicles_one_prior_run(db: Path) -> None:
    run1 = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run1, [
        VehicleRecord(1, "Economy Car (Alamo)", 200.0, 50.0),
        VehicleRecord(2, "Compact Car (Avis)", 250.0, 62.5),
    ])
    run2 = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run2, [VehicleRecord(1, "Economy Car (Alamo)", 210.0, 52.5)])
    result = get_prior_run_vehicles(db, run2, "LAX", "2026-04-01", "2026-04-05")
    assert result == {"Economy Car (Alamo)": 200.0, "Compact Car (Avis)": 250.0}


def test_get_prior_run_vehicles_multiple_prior_runs_returns_most_recent(db: Path) -> None:
    run1 = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run1, [VehicleRecord(1, "Economy Car (Alamo)", 100.0, 25.0)])
    run2 = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run2, [VehicleRecord(1, "Economy Car (Alamo)", 150.0, 37.5)])
    run3 = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run3, [VehicleRecord(1, "Economy Car (Alamo)", 200.0, 50.0)])
    result = get_prior_run_vehicles(db, run3, "LAX", "2026-04-01", "2026-04-05")
    assert result == {"Economy Car (Alamo)": 150.0}


def test_migrate_db_idempotent(db: Path) -> None:
    migrate_db(db)  # first call happens in init_db; second must not raise
    migrate_db(db)


def test_migrate_db_adds_holding_price_column(db: Path) -> None:
    conn = sqlite3.connect(db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(runs)")}
    assert "holding_price" in cols


def test_save_run_stores_holding_price(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00", holding_price=396.63)
    conn = sqlite3.connect(db)
    val = conn.execute("SELECT holding_price FROM runs WHERE id=?", (run_id,)).fetchone()[0]
    assert val == 396.63


def test_save_run_null_holding_price(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    conn = sqlite3.connect(db)
    val = conn.execute("SELECT holding_price FROM runs WHERE id=?", (run_id,)).fetchone()[0]
    assert val is None


def test_migrate_db_adds_holding_vehicle_type_column(db: Path) -> None:
    conn = sqlite3.connect(db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(runs)")}
    assert "holding_vehicle_type" in cols


def test_save_run_stores_holding_vehicle_type(db: Path) -> None:
    run_id = save_run(
        db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00",
        holding_price=396.63, holding_vehicle_type="Economy Car",
    )
    conn = sqlite3.connect(db)
    val = conn.execute("SELECT holding_vehicle_type FROM runs WHERE id=?", (run_id,)).fetchone()[0]
    assert val == "Economy Car"


def test_save_run_null_holding_vehicle_type(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    conn = sqlite3.connect(db)
    val = conn.execute("SELECT holding_vehicle_type FROM runs WHERE id=?", (run_id,)).fetchone()[0]
    assert val is None


def test_get_prior_run_vehicles_different_params_not_returned(db: Path) -> None:
    run1 = save_run(db, "SFO", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run1, [VehicleRecord(1, "Economy Car (Alamo)", 300.0, 75.0)])
    run2 = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    save_vehicles(db, run2, [VehicleRecord(1, "Economy Car (Alamo)", 200.0, 50.0)])
    run3 = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    result = get_prior_run_vehicles(db, run3, "LAX", "2026-04-01", "2026-04-05")
    assert result == {"Economy Car (Alamo)": 200.0}


# ---------------------------------------------------------------------------
# booking_name column (v4 migration)
# ---------------------------------------------------------------------------


def test_migrate_db_adds_booking_name_column(db: Path) -> None:
    conn = sqlite3.connect(db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(runs)")}
    assert "booking_name" in cols


def test_migrate_db_booking_name_column_idempotent(db: Path) -> None:
    migrate_db(db)  # should not raise even if column already exists
    migrate_db(db)


def test_save_run_stores_booking_name(db: Path) -> None:
    run_id = save_run(
        db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00",
        booking_name="hawaii",
    )
    conn = sqlite3.connect(db)
    val = conn.execute("SELECT booking_name FROM runs WHERE id=?", (run_id,)).fetchone()[0]
    assert val == "hawaii"


def test_save_run_default_booking_name_is_empty(db: Path) -> None:
    run_id = save_run(db, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    conn = sqlite3.connect(db)
    val = conn.execute("SELECT booking_name FROM runs WHERE id=?", (run_id,)).fetchone()[0]
    assert val == ""


def test_get_prior_run_vehicles_scoped_by_booking_name(db: Path) -> None:
    """Prior run lookup must match booking_name — different bookings don't cross-contaminate."""
    run1 = save_run(
        db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00",
        booking_name="hawaii",
    )
    save_vehicles(db, run1, [VehicleRecord(1, "Economy Car (Alamo)", 450.0, 64.29)])

    run2 = save_run(
        db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00",
        booking_name="vegas",
    )
    save_vehicles(db, run2, [VehicleRecord(1, "Economy Car (Alamo)", 300.0, 42.86)])

    # Current run for hawaii — prior should only see run1, not run2
    run3 = save_run(
        db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00",
        booking_name="hawaii",
    )
    result = get_prior_run_vehicles(db, run3, "HNL", "2026-05-01", "2026-05-08", booking_name="hawaii")
    assert result == {"Economy Car (Alamo)": 450.0}


def test_get_prior_run_vehicles_different_booking_names_isolated(db: Path) -> None:
    """No prior run for this booking_name returns empty dict."""
    run1 = save_run(
        db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00",
        booking_name="hawaii",
    )
    save_vehicles(db, run1, [VehicleRecord(1, "Economy Car (Alamo)", 450.0, 64.29)])

    run2 = save_run(
        db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00",
        booking_name="vegas",
    )
    result = get_prior_run_vehicles(db, run2, "HNL", "2026-05-01", "2026-05-08", booking_name="vegas")
    assert result == {}


# ---------------------------------------------------------------------------
# get_category_price_history
# ---------------------------------------------------------------------------


def test_get_category_price_history_no_runs(db: Path) -> None:
    result = get_category_price_history(db, "hawaii")
    assert result == {}


def test_get_category_price_history_single_run(db: Path) -> None:
    run1 = save_run(db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00", booking_name="hawaii")
    save_vehicles(db, run1, [VehicleRecord(1, "Economy Car (Alamo)", 380.0, 54.29)])
    result = get_category_price_history(db, "hawaii")
    assert result == {"Economy Car": [380.0]}


def test_get_category_price_history_multiple_runs_ordered_oldest_first(db: Path) -> None:
    run1 = save_run(db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00", booking_name="hawaii")
    save_vehicles(db, run1, [VehicleRecord(1, "Economy Car (Alamo)", 380.0, 54.29)])
    run2 = save_run(db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00", booking_name="hawaii")
    save_vehicles(db, run2, [VehicleRecord(1, "Economy Car (Alamo)", 360.0, 51.43)])
    run3 = save_run(db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00", booking_name="hawaii")
    save_vehicles(db, run3, [VehicleRecord(1, "Economy Car (Alamo)", 395.0, 56.43)])
    result = get_category_price_history(db, "hawaii")
    assert result == {"Economy Car": [380.0, 360.0, 395.0]}


def test_get_category_price_history_multiple_categories(db: Path) -> None:
    run1 = save_run(db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00", booking_name="hawaii")
    save_vehicles(db, run1, [
        VehicleRecord(1, "Economy Car (Alamo)", 380.0, 54.29),
        VehicleRecord(2, "Standard Car (Avis)", 420.0, 60.0),
    ])
    result = get_category_price_history(db, "hawaii")
    assert result == {"Economy Car": [380.0], "Standard Car": [420.0]}


def test_get_category_price_history_best_price_per_run(db: Path) -> None:
    """When multiple brands exist for a category in a run, only the cheapest is kept."""
    run1 = save_run(db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00", booking_name="hawaii")
    save_vehicles(db, run1, [
        VehicleRecord(1, "Economy Car (Alamo)", 380.0, 54.29),
        VehicleRecord(2, "Economy Car (Avis)", 410.0, 58.57),
    ])
    result = get_category_price_history(db, "hawaii")
    assert result == {"Economy Car": [380.0]}


def test_get_category_price_history_isolated_by_booking_name(db: Path) -> None:
    """Data from other booking names must not appear."""
    run1 = save_run(db, "HNL", "2026-05-01", "10:00", "2026-05-08", "10:00", booking_name="hawaii")
    save_vehicles(db, run1, [VehicleRecord(1, "Economy Car (Alamo)", 380.0, 54.29)])
    run2 = save_run(db, "LAS", "2026-06-01", "12:00", "2026-06-06", "12:00", booking_name="vegas")
    save_vehicles(db, run2, [VehicleRecord(1, "Economy Car (Alamo)", 200.0, 40.0)])
    result = get_category_price_history(db, "hawaii")
    assert result == {"Economy Car": [380.0]}


# ---------------------------------------------------------------------------
# v5 migration: brand column + backfill
# ---------------------------------------------------------------------------


def _seed_dirty_vehicle(db_path: Path, run_id: int, name: str, total_price: float) -> None:
    """Insert a vehicle row directly (bypassing save_vehicles) to simulate pre-migration data."""
    import sqlite3 as _sqlite3
    conn = _sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO vehicles (run_id, position, name, total_price, price_per_day) VALUES (?, ?, ?, ?, ?)",
        (run_id, 1, name, total_price, total_price / 4),
    )
    conn.commit()
    conn.close()


def test_migrate_db_adds_brand_column(db: Path) -> None:
    conn = sqlite3.connect(db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(vehicles)")}
    assert "brand" in cols


def test_migrate_db_strips_brand_suffix_from_name(tmp_path: Path) -> None:
    """Dirty rows seeded before migrate_db get name/brand split correctly."""
    db_path = tmp_path / "pre_migration.db"
    # Build a DB without the brand column by calling init_db on a fresh path,
    # but we can't easily avoid migrate_db running. Instead, seed dirty rows
    # AFTER init_db (simulating legacy data left in DB before v5 ran) and
    # run migrate_db again — it must clean them because the UPDATE re-fires.
    init_db(db_path)
    run_id = save_run(db_path, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    _seed_dirty_vehicle(db_path, run_id, "Economy Car (Alamo)", 200.0)
    # Re-run migration to pick up the newly inserted dirty row.
    migrate_db(db_path)
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT name, brand FROM vehicles WHERE run_id = ?", (run_id,)).fetchone()
    assert row == ("Economy Car", "Alamo")


def test_migrate_db_brand_migration_idempotent(tmp_path: Path) -> None:
    """Running migrate_db twice on an already-clean DB must not raise or corrupt data."""
    db_path = tmp_path / "idempotent_brand.db"
    init_db(db_path)
    run_id = save_run(db_path, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    _seed_dirty_vehicle(db_path, run_id, "Economy Car (Alamo)", 200.0)
    migrate_db(db_path)
    migrate_db(db_path)  # second run — must be a no-op
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT name, brand FROM vehicles WHERE run_id = ?", (run_id,)).fetchone()
    assert row == ("Economy Car", "Alamo")


def test_migrate_db_clean_names_untouched(tmp_path: Path) -> None:
    """Rows without a brand suffix must not be modified by the v5 migration."""
    db_path = tmp_path / "clean_names.db"
    init_db(db_path)
    run_id = save_run(db_path, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    _seed_dirty_vehicle(db_path, run_id, "Economy Car", 200.0)
    migrate_db(db_path)
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT name, brand FROM vehicles WHERE run_id = ?", (run_id,)).fetchone()
    assert row == ("Economy Car", None)


def test_migrate_db_multiple_dirty_rows_all_cleaned(tmp_path: Path) -> None:
    """All dirty rows in the table get cleaned in one migrate_db call."""
    db_path = tmp_path / "multi_dirty.db"
    init_db(db_path)
    run_id = save_run(db_path, "LAX", "2026-04-01", "10:00", "2026-04-05", "10:00")
    _seed_dirty_vehicle(db_path, run_id, "Economy Car (Alamo)", 200.0)
    _seed_dirty_vehicle(db_path, run_id, "Full-Size SUV (Budget)", 350.0)
    migrate_db(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name, brand FROM vehicles WHERE run_id = ? ORDER BY id", (run_id,)).fetchall()
    assert rows == [("Economy Car", "Alamo"), ("Full-Size SUV", "Budget")]

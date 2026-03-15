import csv
import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from scripts.import_history import import_csv, parse_prices, run_already_imported
from src.car_tracker.database import VehicleRecord


# ---------------------------------------------------------------------------
# parse_prices
# ---------------------------------------------------------------------------

PRICES_JSON = json.dumps({
    "Economy Car": 100.00,
    "Standard Car": 60.00,
    "Compact Car": 80.00,
})

RENTAL_DAYS = 6


def test_parse_prices_returns_vehicle_records():
    result = parse_prices(PRICES_JSON)
    assert all(isinstance(r, VehicleRecord) for r in result)


def test_parse_prices_sorted_ascending_by_price():
    result = parse_prices(PRICES_JSON)
    prices = [r.total_price for r in result]
    assert prices == sorted(prices)


def test_parse_prices_position_starts_at_one():
    result = parse_prices(PRICES_JSON)
    assert result[0].position == 1


def test_parse_prices_positions_are_sequential():
    result = parse_prices(PRICES_JSON)
    positions = [r.position for r in result]
    assert positions == list(range(1, len(result) + 1))


def test_parse_prices_cheapest_first():
    result = parse_prices(PRICES_JSON)
    assert result[0].name == "Standard Car"
    assert result[0].total_price == 60.00


def test_parse_prices_price_per_day():
    result = parse_prices(PRICES_JSON)
    for r in result:
        assert r.price_per_day == pytest.approx(r.total_price / RENTAL_DAYS)


def test_parse_prices_all_categories_included():
    result = parse_prices(PRICES_JSON)
    names = {r.name for r in result}
    assert names == {"Economy Car", "Standard Car", "Compact Car"}


def test_parse_prices_single_category():
    single = json.dumps({"Economy Car": 427.16})
    result = parse_prices(single)
    assert len(result) == 1
    assert result[0].position == 1
    assert result[0].total_price == pytest.approx(427.16)
    assert result[0].price_per_day == pytest.approx(427.16 / 6)


# ---------------------------------------------------------------------------
# run_already_imported
# ---------------------------------------------------------------------------

PICKUP_LOCATION = "SAN"
PICKUP_DATE = "2026-04-02"
DROPOFF_DATE = "2026-04-08"
RUN_AT = "2026-02-05 14:22:09.568881+00"


def _make_db_with_run(run_at: str) -> Path:
    """Create a temp SQLite DB with one run record and return its path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = Path(tmp.name)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE runs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at           DATETIME NOT NULL,
            pickup_location  TEXT NOT NULL,
            pickup_date      TEXT NOT NULL,
            pickup_time      TEXT NOT NULL,
            dropoff_date     TEXT NOT NULL,
            dropoff_time     TEXT NOT NULL,
            holding_price    REAL,
            holding_vehicle_type TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO runs (run_at, pickup_location, pickup_date, pickup_time, dropoff_date, dropoff_time) VALUES (?, ?, ?, ?, ?, ?)",
        (run_at, PICKUP_LOCATION, PICKUP_DATE, "10:00", DROPOFF_DATE, "10:00"),
    )
    conn.commit()
    conn.close()
    return db_path


def test_run_already_imported_true_when_exists():
    db_path = _make_db_with_run(RUN_AT)
    assert run_already_imported(db_path, RUN_AT, PICKUP_LOCATION, PICKUP_DATE, DROPOFF_DATE) is True


def test_run_already_imported_false_when_different_run_at():
    db_path = _make_db_with_run(RUN_AT)
    other_run_at = "2026-03-01 10:00:00+00"
    assert run_already_imported(db_path, other_run_at, PICKUP_LOCATION, PICKUP_DATE, DROPOFF_DATE) is False


def test_run_already_imported_false_when_different_location():
    db_path = _make_db_with_run(RUN_AT)
    assert run_already_imported(db_path, RUN_AT, "LAX", PICKUP_DATE, DROPOFF_DATE) is False


def test_run_already_imported_false_when_different_pickup_date():
    db_path = _make_db_with_run(RUN_AT)
    assert run_already_imported(db_path, RUN_AT, PICKUP_LOCATION, "2026-05-01", DROPOFF_DATE) is False


def test_run_already_imported_false_when_different_dropoff_date():
    db_path = _make_db_with_run(RUN_AT)
    assert run_already_imported(db_path, RUN_AT, PICKUP_LOCATION, PICKUP_DATE, "2026-05-07") is False


def test_run_already_imported_false_on_empty_db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = Path(tmp.name)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at DATETIME NOT NULL,
            pickup_location TEXT NOT NULL,
            pickup_date TEXT NOT NULL,
            pickup_time TEXT NOT NULL,
            dropoff_date TEXT NOT NULL,
            dropoff_time TEXT NOT NULL,
            holding_price REAL,
            holding_vehicle_type TEXT
        )
        """
    )
    conn.commit()
    conn.close()
    assert run_already_imported(db_path, RUN_AT, PICKUP_LOCATION, PICKUP_DATE, DROPOFF_DATE) is False


# ---------------------------------------------------------------------------
# import_csv
# ---------------------------------------------------------------------------

SAMPLE_PRICES = json.dumps({"Economy Car": 427.16, "Standard Car": 453.20})
SAMPLE_PRICES_2 = json.dumps({"Economy Car": 410.00, "Standard Car": 440.00})


def _make_csv(tmp_dir: Path, rows: list[dict]) -> Path:
    csv_path = tmp_dir / "test.csv"
    fieldnames = ["id", "booking_id", "timestamp", "prices", "lowest_price", "created_at"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return csv_path


def test_import_csv_inserts_matching_rows(tmp_path):
    csv_path = _make_csv(tmp_path, [
        {
            "id": "abc",
            "booking_id": "SAN_04022026_04082026_StandardCar",
            "timestamp": "2026-02-05 14:22:09+00",
            "prices": SAMPLE_PRICES,
            "lowest_price": "{}",
            "created_at": "2026-02-05 14:23:00+00",
        }
    ])
    db_path = tmp_path / "test.db"
    import_csv(csv_path, db_path)

    conn = sqlite3.connect(db_path)
    runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    vehicles = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
    conn.close()

    assert runs == 1
    assert vehicles == 2


def test_import_csv_skips_non_matching_booking_id(tmp_path):
    csv_path = _make_csv(tmp_path, [
        {
            "id": "abc",
            "booking_id": "SAN_04022026_04082026_FullsizeCar",
            "timestamp": "2026-02-05 14:22:09+00",
            "prices": SAMPLE_PRICES,
            "lowest_price": "{}",
            "created_at": "2026-02-05 14:23:00+00",
        }
    ])
    db_path = tmp_path / "test.db"
    import_csv(csv_path, db_path)

    conn = sqlite3.connect(db_path)
    runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    conn.close()
    assert runs == 0


def test_import_csv_is_idempotent(tmp_path):
    row = {
        "id": "abc",
        "booking_id": "SAN_04022026_04082026_StandardCar",
        "timestamp": "2026-02-05 14:22:09+00",
        "prices": SAMPLE_PRICES,
        "lowest_price": "{}",
        "created_at": "2026-02-05 14:23:00+00",
    }
    csv_path = _make_csv(tmp_path, [row])
    db_path = tmp_path / "test.db"
    import_csv(csv_path, db_path)
    import_csv(csv_path, db_path)  # run again

    conn = sqlite3.connect(db_path)
    runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    conn.close()
    assert runs == 1


def test_import_csv_vehicles_sorted_by_price(tmp_path):
    csv_path = _make_csv(tmp_path, [
        {
            "id": "abc",
            "booking_id": "SAN_04022026_04082026_StandardCar",
            "timestamp": "2026-02-05 14:22:09+00",
            "prices": SAMPLE_PRICES,
            "lowest_price": "{}",
            "created_at": "2026-02-05 14:23:00+00",
        }
    ])
    db_path = tmp_path / "test.db"
    import_csv(csv_path, db_path)

    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT position, name, total_price FROM vehicles ORDER BY position"
    ).fetchall()
    conn.close()

    assert rows[0] == (1, "Economy Car", pytest.approx(427.16))
    assert rows[1] == (2, "Standard Car", pytest.approx(453.20))


def test_import_csv_multiple_rows_inserts_multiple_runs(tmp_path):
    csv_path = _make_csv(tmp_path, [
        {
            "id": "abc",
            "booking_id": "SAN_04022026_04082026_StandardCar",
            "timestamp": "2026-02-05 14:22:09+00",
            "prices": SAMPLE_PRICES,
            "lowest_price": "{}",
            "created_at": "2026-02-05 14:23:00+00",
        },
        {
            "id": "def",
            "booking_id": "SAN_04022026_04082026_StandardCar",
            "timestamp": "2026-03-02 14:26:09+00",
            "prices": SAMPLE_PRICES_2,
            "lowest_price": "{}",
            "created_at": "2026-03-02 14:27:00+00",
        },
    ])
    db_path = tmp_path / "test.db"
    import_csv(csv_path, db_path)

    conn = sqlite3.connect(db_path)
    runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    conn.close()
    assert runs == 2

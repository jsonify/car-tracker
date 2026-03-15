from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

from car_tracker.database import VehicleRecord, _connect, init_db, save_vehicles

BOOKING_ID = "SAN_04022026_04082026_StandardCar"
PICKUP_LOCATION = "SAN"
PICKUP_DATE = "2026-04-02"
PICKUP_TIME = "10:00"
DROPOFF_DATE = "2026-04-08"
DROPOFF_TIME = "10:00"
RENTAL_DAYS = 6


def parse_prices(prices_json: str) -> list[VehicleRecord]:
    """Parse prices JSON string into a list of VehicleRecords sorted by ascending price."""
    raw: dict[str, float] = json.loads(prices_json)
    sorted_items = sorted(raw.items(), key=lambda kv: kv[1])
    return [
        VehicleRecord(
            position=i + 1,
            name=name,
            total_price=price,
            price_per_day=price / RENTAL_DAYS,
        )
        for i, (name, price) in enumerate(sorted_items)
    ]


def run_already_imported(
    db_path: str | Path,
    run_at: str,
    pickup_location: str,
    pickup_date: str,
    dropoff_date: str,
) -> bool:
    """Return True if a run with these exact params already exists in the DB."""
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT 1 FROM runs
            WHERE run_at = ?
              AND pickup_location = ?
              AND pickup_date = ?
              AND dropoff_date = ?
            LIMIT 1
            """,
            (run_at, pickup_location, pickup_date, dropoff_date),
        ).fetchone()
        return row is not None


def import_csv(csv_path: str | Path, db_path: str | Path) -> None:
    """Read CSV, filter for the target booking_id, and seed runs + vehicles."""
    init_db(db_path)
    processed = 0
    inserted = 0
    skipped = 0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["booking_id"] != BOOKING_ID:
                continue
            processed += 1
            run_at = row["timestamp"]

            if run_already_imported(db_path, run_at, PICKUP_LOCATION, PICKUP_DATE, DROPOFF_DATE):
                skipped += 1
                continue

            with _connect(db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO runs
                        (run_at, pickup_location, pickup_date, pickup_time,
                         dropoff_date, dropoff_time, holding_price, holding_vehicle_type)
                    VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
                    """,
                    (run_at, PICKUP_LOCATION, PICKUP_DATE, PICKUP_TIME, DROPOFF_DATE, DROPOFF_TIME),
                )
                run_id = cursor.lastrowid

            vehicles = parse_prices(row["prices"])
            save_vehicles(db_path, run_id, vehicles)
            inserted += 1

    print(f"Processed {processed} rows → {inserted} runs inserted, {skipped} skipped")


if __name__ == "__main__":  # pragma: no cover
    import_csv("data/price_histories_rows.csv", "data/results.db")

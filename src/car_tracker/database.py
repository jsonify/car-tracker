from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class VehicleRecord:
    position: int
    name: str
    total_price: float
    price_per_day: float
    brand: str | None = None


def _connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate_db(db_path: str | Path) -> None:
    """Apply incremental schema migrations. Safe to run on any existing DB."""
    with _connect(db_path) as conn:
        # v2: add holding_price column to runs (nullable)
        try:
            conn.execute("ALTER TABLE runs ADD COLUMN holding_price REAL")
        except sqlite3.OperationalError:
            pass  # column already exists — idempotent
        # v3: add holding_vehicle_type column to runs (nullable)
        try:
            conn.execute("ALTER TABLE runs ADD COLUMN holding_vehicle_type TEXT")
        except sqlite3.OperationalError:
            pass  # column already exists — idempotent
        # v4: add booking_name column to runs (NOT NULL with empty-string default)
        try:
            conn.execute("ALTER TABLE runs ADD COLUMN booking_name TEXT NOT NULL DEFAULT ''")
        except sqlite3.OperationalError:
            pass  # column already exists — idempotent
        # v5: add brand column to vehicles; backfill from "Category (Brand)" name values
        try:
            conn.execute("ALTER TABLE vehicles ADD COLUMN brand TEXT")
        except sqlite3.OperationalError:
            pass  # column already exists — idempotent
        rows = conn.execute(
            "SELECT id, name FROM vehicles WHERE name LIKE '% (%)'"
        ).fetchall()
        for row_id, name in rows:
            paren = name.find(" (")
            category = name[:paren]
            brand = name[paren + 2 : -1]
            conn.execute(
                "UPDATE vehicles SET name = ?, brand = ? WHERE id = ?",
                (category, brand, row_id),
            )


def init_db(db_path: str | Path) -> None:
    """Create tables if they don't already exist, then apply migrations."""
    with _connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at           DATETIME NOT NULL,
                pickup_location  TEXT NOT NULL,
                pickup_date      TEXT NOT NULL,
                pickup_time      TEXT NOT NULL,
                dropoff_date     TEXT NOT NULL,
                dropoff_time     TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS vehicles (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id        INTEGER NOT NULL REFERENCES runs(id),
                position      INTEGER NOT NULL,
                name          TEXT NOT NULL,
                total_price   REAL NOT NULL,
                price_per_day REAL NOT NULL
            );
            """
        )
    migrate_db(db_path)


def save_run(
    db_path: str | Path,
    pickup_location: str,
    pickup_date: str,
    pickup_time: str,
    dropoff_date: str,
    dropoff_time: str,
    holding_price: float | None = None,
    holding_vehicle_type: str | None = None,
    booking_name: str = "",
) -> int:
    """Insert a run record and return its id."""
    run_at = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO runs
                (run_at, pickup_location, pickup_date, pickup_time, dropoff_date, dropoff_time,
                 holding_price, holding_vehicle_type, booking_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_at, pickup_location, pickup_date, pickup_time, dropoff_date, dropoff_time,
             holding_price, holding_vehicle_type, booking_name),
        )
        return cursor.lastrowid  # type: ignore[return-value]


def get_prior_run_vehicles(
    db_path: str | Path,
    current_run_id: int,
    pickup_location: str,
    pickup_date: str,
    dropoff_date: str,
    booking_name: str = "",
) -> dict[str, float]:
    """Return vehicle name → total_price from the most recent prior run with matching params.

    Returns an empty dict if no prior run exists for the given search parameters.
    """
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT id FROM runs
            WHERE id < ?
              AND pickup_location = ?
              AND pickup_date = ?
              AND dropoff_date = ?
              AND booking_name = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (current_run_id, pickup_location, pickup_date, dropoff_date, booking_name),
        ).fetchone()
        if row is None:
            return {}
        prior_run_id = row[0]
        rows = conn.execute(
            "SELECT name, MIN(total_price) FROM vehicles WHERE run_id = ? GROUP BY name",
            (prior_run_id,),
        ).fetchall()
        return {name: total_price for name, total_price in rows}


def get_category_price_history(
    db_path: str | Path,
    booking_name: str,
) -> dict[str, list[float]]:
    """Return price history per vehicle category for a booking, ordered oldest to newest.

    For each run, the best (lowest) price per category is kept. Categories are
    derived by stripping the brand suffix from vehicle names via extract_category.

    Returns an empty dict if no runs exist for the given booking_name.
    """
    from car_tracker.emailer import extract_category  # avoid circular at module level

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT r.id, v.name, v.total_price
            FROM vehicles v
            JOIN runs r ON v.run_id = r.id
            WHERE r.booking_name = ?
            ORDER BY r.id ASC
            """,
            (booking_name,),
        ).fetchall()

    # Group by run, then collapse to best price per category
    runs: dict[int, dict[str, float]] = {}
    for run_id, name, price in rows:
        cat = extract_category(name)
        if run_id not in runs:
            runs[run_id] = {}
        if cat not in runs[run_id] or price < runs[run_id][cat]:
            runs[run_id][cat] = price

    # Collect ordered price lists per category
    history: dict[str, list[float]] = {}
    for run_prices in runs.values():
        for cat, price in run_prices.items():
            history.setdefault(cat, []).append(price)

    return history


def save_vehicles(
    db_path: str | Path,
    run_id: int,
    vehicles: list[VehicleRecord],
) -> None:
    """Bulk insert vehicle records for a given run."""
    rows = [
        (run_id, v.position, v.name, v.total_price, v.price_per_day, v.brand)
        for v in vehicles
    ]
    with _connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO vehicles (run_id, position, name, total_price, price_per_day, brand)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

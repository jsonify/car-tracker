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
            "SELECT name, total_price FROM vehicles WHERE run_id = ?",
            (prior_run_id,),
        ).fetchall()
        return {name: total_price for name, total_price in rows}


def get_latest_run_vehicles(
    db_path: str | Path,
    booking_name: str,
) -> tuple[str | None, list[VehicleRecord]]:
    """Return (run_at, vehicles) for the most recent run of a booking.

    Returns (None, []) if no runs exist for the booking.
    """
    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, run_at FROM runs
            WHERE booking_name = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (booking_name,),
        ).fetchone()
        if row is None:
            return None, []
        run_id, run_at = row
        rows = conn.execute(
            "SELECT position, name, total_price, price_per_day FROM vehicles WHERE run_id = ? ORDER BY total_price ASC",
            (run_id,),
        ).fetchall()
        vehicles = [VehicleRecord(position=r[0], name=r[1], total_price=r[2], price_per_day=r[3]) for r in rows]
        return run_at, vehicles


def get_price_history(
    db_path: str | Path,
    booking_name: str,
    vehicle_type: str,
    limit: int = 10,
) -> list[tuple[str, float]]:
    """Return (run_at, best_price) tuples for vehicle_type across recent runs, most recent first.

    Matches vehicles whose name starts with vehicle_type (category prefix match).
    Returns an empty list if no data found.
    """
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT r.run_at, MIN(v.total_price) as best_price
            FROM runs r
            JOIN vehicles v ON v.run_id = r.id
            WHERE r.booking_name = ?
              AND (v.name = ? OR v.name LIKE ?)
            GROUP BY r.id, r.run_at
            ORDER BY r.id DESC
            LIMIT ?
            """,
            (booking_name, vehicle_type, f"{vehicle_type} (%", limit),
        ).fetchall()
        return [(run_at, best_price) for run_at, best_price in rows]


def save_vehicles(
    db_path: str | Path,
    run_id: int,
    vehicles: list[VehicleRecord],
) -> None:
    """Bulk insert vehicle records for a given run."""
    rows = [
        (run_id, v.position, v.name, v.total_price, v.price_per_day)
        for v in vehicles
    ]
    with _connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO vehicles (run_id, position, name, total_price, price_per_day)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )

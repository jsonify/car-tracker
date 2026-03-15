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


def init_db(db_path: str | Path) -> None:
    """Create tables if they don't already exist."""
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


def save_run(
    db_path: str | Path,
    pickup_location: str,
    pickup_date: str,
    pickup_time: str,
    dropoff_date: str,
    dropoff_time: str,
) -> int:
    """Insert a run record and return its id."""
    run_at = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO runs
                (run_at, pickup_location, pickup_date, pickup_time, dropoff_date, dropoff_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (run_at, pickup_location, pickup_date, pickup_time, dropoff_date, dropoff_time),
        )
        return cursor.lastrowid  # type: ignore[return-value]


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

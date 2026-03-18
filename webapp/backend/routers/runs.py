"""Runs and vehicles read-only routers."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from webapp.backend.database import connect, get_db_path

router = APIRouter()


def _db() -> Path:
    config = os.environ.get("CAR_TRACKER_CONFIG", "config.yaml")
    return get_db_path(config)


class RunSummary(BaseModel):
    id: int
    run_at: str
    pickup_location: str
    pickup_date: str
    dropoff_date: str
    booking_name: str
    holding_price: float | None
    holding_vehicle_type: str | None
    vehicle_count: int


class VehicleRow(BaseModel):
    id: int
    run_id: int
    run_at: str
    booking_name: str
    position: int
    name: str
    brand: str | None
    total_price: float
    price_per_day: float


@router.get("/", response_model=list[RunSummary])
def get_runs() -> list[dict]:
    conn = connect(_db())
    rows = conn.execute("""
        SELECT r.id, r.run_at, r.pickup_location, r.pickup_date, r.dropoff_date,
               r.booking_name, r.holding_price, r.holding_vehicle_type,
               COUNT(v.id) AS vehicle_count
        FROM runs r
        LEFT JOIN vehicles v ON v.run_id = r.id
        GROUP BY r.id
        ORDER BY r.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{run_id}/vehicles", response_model=list[VehicleRow])
def get_run_vehicles(run_id: int) -> list[dict]:
    conn = connect(_db())
    # Verify run exists
    run = conn.execute("SELECT id FROM runs WHERE id = ?", (run_id,)).fetchone()
    if run is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    rows = conn.execute("""
        SELECT v.id, v.run_id, r.run_at, r.booking_name,
               v.position, v.name, v.brand, v.total_price, v.price_per_day
        FROM vehicles v
        JOIN runs r ON r.id = v.run_id
        WHERE v.run_id = ?
        ORDER BY v.position
    """, (run_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

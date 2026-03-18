"""Vehicles read-only router with pagination, sort, filter."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Query
from pydantic import BaseModel

from webapp.backend.database import connect, get_db_path

router = APIRouter()


def _db() -> Path:
    config = os.environ.get("CAR_TRACKER_CONFIG", "config.yaml")
    return get_db_path(config)


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


_SORT_COLS = {"total_price", "price_per_day", "name", "run_at", "position"}


@router.get("/", response_model=list[VehicleRow])
def get_vehicles(
    booking_name: str | None = Query(None),
    category: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    sort: str = Query("run_at"),
    order: str = Query("desc"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[dict]:
    sort_col = sort if sort in _SORT_COLS else "run_at"
    order_dir = "ASC" if order.lower() == "asc" else "DESC"

    where_clauses = []
    params: list = []

    if booking_name:
        where_clauses.append("r.booking_name = ?")
        params.append(booking_name)
    if category:
        where_clauses.append("v.name LIKE ?")
        params.append(f"%{category}%")
    if date_from:
        where_clauses.append("r.pickup_date >= ?")
        params.append(date_from)
    if date_to:
        where_clauses.append("r.pickup_date <= ?")
        params.append(date_to)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    conn = connect(_db())
    rows = conn.execute(f"""
        SELECT v.id, v.run_id, r.run_at, r.booking_name,
               v.position, v.name, v.brand, v.total_price, v.price_per_day
        FROM vehicles v
        JOIN runs r ON r.id = v.run_id
        {where_sql}
        ORDER BY {sort_col} {order_dir}
        LIMIT ? OFFSET ?
    """, [*params, limit, offset]).fetchall()
    conn.close()
    return [dict(r) for r in rows]

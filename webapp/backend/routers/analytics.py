"""Analytics router: price history and dashboard summary."""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import yaml
from fastapi import APIRouter
from pydantic import BaseModel

from webapp.backend.database import connect, get_db_path

router = APIRouter()


def _db() -> Path:
    config = os.environ.get("CAR_TRACKER_CONFIG", "config.yaml")
    return get_db_path(config)


def _config_path() -> Path:
    return Path(os.environ.get("CAR_TRACKER_CONFIG", "config.yaml"))


def _load_bookings() -> list[dict]:
    with open(_config_path()) as f:
        raw = yaml.safe_load(f) or {}
    return raw.get("bookings") or []


# ---------------------------------------------------------------------------
# Price history
# ---------------------------------------------------------------------------

class PriceHistoryResponse(BaseModel):
    booking_name: str
    run_dates: list[str]
    categories: dict[str, list[float]]
    holding_price: float | None
    holding_vehicle_type: str | None


@router.get("/bookings/{booking_name}/price-history", response_model=PriceHistoryResponse)
def get_price_history(booking_name: str) -> dict:
    conn = connect(_db())
    rows = conn.execute("""
        SELECT r.id, r.run_at, v.name, v.total_price
        FROM vehicles v
        JOIN runs r ON v.run_id = r.id
        WHERE r.booking_name = ?
        ORDER BY r.id ASC
    """, (booking_name,)).fetchall()
    conn.close()

    # Group by run, collapse to best price per category
    runs_ordered: list[tuple[int, str]] = []
    run_map: dict[int, dict[str, float]] = {}
    seen_runs: set[int] = set()

    for run_id, run_at, name, price in rows:
        cat = _extract_category(name)
        if run_id not in seen_runs:
            runs_ordered.append((run_id, run_at))
            seen_runs.add(run_id)
            run_map[run_id] = {}
        if cat not in run_map[run_id] or price < run_map[run_id][cat]:
            run_map[run_id][cat] = price

    run_dates = [run_at for _, run_at in runs_ordered]
    all_cats: set[str] = set()
    for prices in run_map.values():
        all_cats.update(prices.keys())

    categories: dict[str, list[float]] = {}
    for cat in sorted(all_cats):
        series = []
        for run_id, _ in runs_ordered:
            if cat in run_map[run_id]:
                series.append(run_map[run_id][cat])
        if series:
            categories[cat] = series

    # Find holding info from config
    holding_price = None
    holding_vehicle_type = None
    for b in _load_bookings():
        if b["name"] == booking_name:
            holding_price = b.get("holding_price")
            holding_vehicle_type = b.get("holding_vehicle_type")
            break

    return {
        "booking_name": booking_name,
        "run_dates": run_dates,
        "categories": categories,
        "holding_price": holding_price,
        "holding_vehicle_type": holding_vehicle_type,
    }


# ---------------------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------------------

class BookingSummary(BaseModel):
    name: str
    pickup_date: str
    dropoff_date: str
    pickup_location: str
    holding_price: float | None
    holding_vehicle_type: str | None
    best_current_price: float | None
    savings: float | None
    days_remaining: int


class VolatileCategory(BaseModel):
    booking_name: str
    category: str
    min_price: float
    max_price: float
    range: float


class DashboardSummary(BaseModel):
    active_booking_count: int
    total_run_count: int
    bookings: list[BookingSummary]
    volatile_categories: list[VolatileCategory]
    recent_runs: list[dict]


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary() -> dict:
    today = date.today()
    bookings_cfg = _load_bookings()
    conn = connect(_db())

    total_run_count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]

    booking_summaries = []
    volatile_candidates: list[VolatileCategory] = []

    for b in bookings_cfg:
        pickup = date.fromisoformat(b["pickup_date"])
        days_remaining = (pickup - today).days

        # Best (lowest) price from latest run for this booking
        latest_run = conn.execute("""
            SELECT id FROM runs WHERE booking_name = ?
            ORDER BY id DESC LIMIT 1
        """, (b["name"],)).fetchone()

        best_current_price = None
        if latest_run:
            row = conn.execute("""
                SELECT MIN(total_price) FROM vehicles WHERE run_id = ?
            """, (latest_run[0],)).fetchone()
            best_current_price = row[0] if row else None

        holding_price = b.get("holding_price")
        savings = None
        if holding_price is not None and best_current_price is not None:
            savings = round(holding_price - best_current_price, 2)

        booking_summaries.append({
            "name": b["name"],
            "pickup_date": b["pickup_date"],
            "dropoff_date": b["dropoff_date"],
            "pickup_location": b["pickup_location"],
            "holding_price": holding_price,
            "holding_vehicle_type": b.get("holding_vehicle_type"),
            "best_current_price": best_current_price,
            "savings": savings,
            "days_remaining": days_remaining,
        })

        # Compute volatility per category
        rows = conn.execute("""
            SELECT v.name, v.total_price
            FROM vehicles v
            JOIN runs r ON v.run_id = r.id
            WHERE r.booking_name = ?
        """, (b["name"],)).fetchall()

        cat_prices: dict[str, list[float]] = {}
        for name, price in rows:
            cat = _extract_category(name)
            cat_prices.setdefault(cat, []).append(price)

        for cat, prices in cat_prices.items():
            if len(prices) > 1:
                mn, mx = min(prices), max(prices)
                volatile_candidates.append(VolatileCategory(
                    booking_name=b["name"],
                    category=cat,
                    min_price=mn,
                    max_price=mx,
                    range=round(mx - mn, 2),
                ))

    volatile_candidates.sort(key=lambda v: v.range, reverse=True)
    top_volatile = volatile_candidates[:3]

    recent_runs = conn.execute("""
        SELECT id, run_at, booking_name, holding_price, holding_vehicle_type
        FROM runs ORDER BY id DESC LIMIT 10
    """).fetchall()
    conn.close()

    active_count = sum(1 for b in booking_summaries if b["days_remaining"] >= 0)

    return {
        "active_booking_count": active_count,
        "total_run_count": total_run_count,
        "bookings": booking_summaries,
        "volatile_categories": [v.model_dump() for v in top_volatile],
        "recent_runs": [dict(r) for r in recent_runs],
    }


def _extract_category(name: str) -> str:
    """Strip brand suffix: 'Economy Car (Alamo)' → 'Economy Car'."""
    idx = name.find(" (")
    return name[:idx] if idx != -1 else name

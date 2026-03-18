"""Tests for analytics/dashboard endpoints."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient


def _setup_db(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
        CREATE TABLE runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at DATETIME NOT NULL,
            pickup_location TEXT NOT NULL,
            pickup_date TEXT NOT NULL,
            pickup_time TEXT NOT NULL,
            dropoff_date TEXT NOT NULL,
            dropoff_time TEXT NOT NULL,
            holding_price REAL,
            holding_vehicle_type TEXT,
            booking_name TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES runs(id),
            position INTEGER NOT NULL,
            name TEXT NOT NULL,
            total_price REAL NOT NULL,
            price_per_day REAL NOT NULL,
            brand TEXT
        );
    """)
    # Two runs for san_april
    conn.execute("""INSERT INTO runs VALUES
        (1, '2026-03-01T10:00:00', 'SAN', '2026-04-02', '10:00', '2026-04-08', '10:00',
         375.0, 'Standard Car', 'san_april')""")
    conn.execute("""INSERT INTO runs VALUES
        (2, '2026-03-05T10:00:00', 'SAN', '2026-04-02', '10:00', '2026-04-08', '10:00',
         375.0, 'Standard Car', 'san_april')""")
    conn.execute("INSERT INTO vehicles VALUES (1,1,1,'Economy Car',299.0,49.83,'Alamo')")
    conn.execute("INSERT INTO vehicles VALUES (2,1,2,'Standard Car',370.0,61.67,'Hertz')")
    conn.execute("INSERT INTO vehicles VALUES (3,2,1,'Economy Car',285.0,47.5,'Alamo')")
    conn.execute("INSERT INTO vehicles VALUES (4,2,2,'Standard Car',360.0,60.0,'Hertz')")
    conn.commit()
    conn.close()


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "results.db"
    _setup_db(db_path)
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({
        "bookings": [{
            "name": "san_april",
            "pickup_location": "SAN",
            "pickup_date": "2026-04-02",
            "pickup_time": "10:00",
            "dropoff_date": "2026-04-08",
            "dropoff_time": "10:00",
            "holding_price": 375.0,
            "holding_vehicle_type": "Standard Car",
        }],
        "database": {"path": str(db_path)},
    }))
    monkeypatch.setenv("CAR_TRACKER_CONFIG", str(cfg))
    from webapp.backend.main import app
    return TestClient(app)


def test_price_history_returns_categories(client):
    resp = client.get("/bookings/san_april/price-history")
    assert resp.status_code == 200
    data = resp.json()
    assert "categories" in data
    assert "run_dates" in data
    assert "Economy Car" in data["categories"]
    assert len(data["categories"]["Economy Car"]) == 2


def test_price_history_values_correct(client):
    resp = client.get("/bookings/san_april/price-history")
    data = resp.json()
    prices = data["categories"]["Economy Car"]
    assert prices[0] == 299.0
    assert prices[1] == 285.0


def test_price_history_unknown_booking(client):
    resp = client.get("/bookings/no_such/price-history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["categories"] == {}


def test_dashboard_summary_structure(client):
    resp = client.get("/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_booking_count" in data
    assert "total_run_count" in data
    assert "bookings" in data


def test_dashboard_summary_counts(client):
    resp = client.get("/dashboard/summary")
    data = resp.json()
    assert data["active_booking_count"] == 1
    assert data["total_run_count"] == 2


def test_dashboard_booking_has_savings(client):
    resp = client.get("/dashboard/summary")
    data = resp.json()
    booking = data["bookings"][0]
    assert "name" in booking
    assert "holding_price" in booking
    assert "best_current_price" in booking
    assert "savings" in booking
    assert "days_remaining" in booking


def test_dashboard_volatility(client):
    resp = client.get("/dashboard/summary")
    data = resp.json()
    assert "volatile_categories" in data

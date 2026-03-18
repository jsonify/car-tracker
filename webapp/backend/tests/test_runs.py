"""Tests for runs and vehicles endpoints."""
from __future__ import annotations

import sqlite3
import tempfile
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
    conn.execute("""
        INSERT INTO runs (run_at, pickup_location, pickup_date, pickup_time,
                          dropoff_date, dropoff_time, holding_price,
                          holding_vehicle_type, booking_name)
        VALUES ('2026-03-01T10:00:00', 'SAN', '2026-04-02', '10:00',
                '2026-04-08', '10:00', 375.0, 'Standard Car', 'san_april')
    """)
    conn.execute("""
        INSERT INTO vehicles (run_id, position, name, total_price, price_per_day, brand)
        VALUES (1, 1, 'Economy Car', 299.0, 49.83, 'Alamo')
    """)
    conn.execute("""
        INSERT INTO vehicles (run_id, position, name, total_price, price_per_day, brand)
        VALUES (1, 2, 'Standard Car', 370.0, 61.67, 'Hertz')
    """)
    conn.commit()
    conn.close()


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "results.db"
    _setup_db(db_path)
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({
        "bookings": [{"name": "san_april", "pickup_location": "SAN",
                      "pickup_date": "2026-04-02", "pickup_time": "10:00",
                      "dropoff_date": "2026-04-08", "dropoff_time": "10:00"}],
        "database": {"path": str(db_path)},
    }))
    monkeypatch.setenv("CAR_TRACKER_CONFIG", str(cfg))
    from webapp.backend.main import app
    return TestClient(app)


def test_get_runs_returns_list(client):
    resp = client.get("/runs/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["booking_name"] == "san_april"
    assert data[0]["vehicle_count"] == 2


def test_get_run_vehicles(client):
    resp = client.get("/runs/1/vehicles")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "Economy Car"


def test_get_run_vehicles_not_found(client):
    resp = client.get("/runs/999/vehicles")
    assert resp.status_code == 404


def test_get_vehicles_all(client):
    resp = client.get("/vehicles/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_get_vehicles_pagination(client):
    resp = client.get("/vehicles/?limit=1&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1


def test_get_vehicles_filter_booking(client):
    resp = client.get("/vehicles/?booking_name=san_april")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_get_vehicles_filter_category(client):
    resp = client.get("/vehicles/?category=Economy")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert "Economy" in data[0]["name"]


def test_get_vehicles_sort_price_asc(client):
    resp = client.get("/vehicles/?sort=total_price&order=asc")
    assert resp.status_code == 200
    prices = [v["total_price"] for v in resp.json()]
    assert prices == sorted(prices)


def test_get_vehicles_sort_price_desc(client):
    resp = client.get("/vehicles/?sort=total_price&order=desc")
    assert resp.status_code == 200
    prices = [v["total_price"] for v in resp.json()]
    assert prices == sorted(prices, reverse=True)

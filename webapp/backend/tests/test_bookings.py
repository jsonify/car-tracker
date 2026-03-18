"""Tests for bookings CRUD endpoints and model helpers."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from webapp.backend.models.booking import (
    BookingCreate,
    display_date_to_storage,
    display_time_to_storage,
    storage_date_to_display,
    storage_time_to_display,
)


# ---------------------------------------------------------------------------
# Model / conversion tests (TDD — run before router)
# ---------------------------------------------------------------------------

def test_display_date_to_storage():
    assert display_date_to_storage("04/02/2026") == "2026-04-02"


def test_display_date_to_storage_pads():
    assert display_date_to_storage("4/2/2026") == "2026-04-02"


def test_storage_date_to_display():
    assert storage_date_to_display("2026-04-02") == "04/02/2026"


def test_display_time_to_storage_am():
    assert display_time_to_storage("10:00 AM") == "10:00"


def test_display_time_to_storage_pm():
    assert display_time_to_storage("1:30 PM") == "13:30"


def test_display_time_to_storage_passthrough():
    assert display_time_to_storage("09:00") == "09:00"


def test_storage_time_to_display():
    result = storage_time_to_display("13:30")
    assert "1:30" in result and "PM" in result


def test_booking_create_valid():
    b = BookingCreate(
        name="test",
        pickup_location="SAN",
        pickup_date="2026-04-02",
        pickup_time="10:00",
        dropoff_date="2026-04-08",
        dropoff_time="10:00",
        holding_price=375.0,
        holding_vehicle_type="Standard Car",
    )
    assert b.holding_price == 375.0
    assert b.holding_vehicle_type == "Standard Car"


def test_booking_create_holding_pair_cleared_if_incomplete():
    b = BookingCreate(
        name="test",
        pickup_location="SAN",
        pickup_date="2026-04-02",
        pickup_time="10:00",
        dropoff_date="2026-04-08",
        dropoff_time="10:00",
        holding_price=375.0,  # no holding_vehicle_type
    )
    assert b.holding_price is None
    assert b.holding_vehicle_type is None


def test_booking_create_invalid_date():
    with pytest.raises(Exception):
        BookingCreate(
            name="x",
            pickup_location="SAN",
            pickup_date="04/02/2026",  # wrong format
            pickup_time="10:00",
            dropoff_date="2026-04-08",
            dropoff_time="10:00",
        )


# ---------------------------------------------------------------------------
# Router endpoint tests
# ---------------------------------------------------------------------------

def _write_config(tmp_path: Path, bookings: list) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.dump({
        "bookings": bookings,
        "database": {"path": str(tmp_path / "results.db")},
    }))
    return cfg


@pytest.fixture
def client(tmp_path, monkeypatch):
    config_path = _write_config(tmp_path, [
        {
            "name": "san_april",
            "pickup_location": "SAN",
            "pickup_date": "2026-04-02",
            "pickup_time": "10:00",
            "dropoff_date": "2026-04-08",
            "dropoff_time": "10:00",
            "holding_price": 375.0,
            "holding_vehicle_type": "Standard Car",
        }
    ])
    monkeypatch.setenv("CAR_TRACKER_CONFIG", str(config_path))
    from webapp.backend.main import app
    return TestClient(app)


def test_get_bookings_returns_list(client):
    resp = client.get("/bookings/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "san_april"


def test_post_booking_creates_new(client, tmp_path, monkeypatch):
    config_path = _write_config(tmp_path, [])
    monkeypatch.setenv("CAR_TRACKER_CONFIG", str(config_path))
    from webapp.backend.main import app
    c = TestClient(app)
    payload = {
        "name": "new_trip",
        "pickup_location": "LAX",
        "pickup_date": "2026-06-01",
        "pickup_time": "09:00",
        "dropoff_date": "2026-06-07",
        "dropoff_time": "09:00",
        "holding_price": None,
        "holding_vehicle_type": None,
    }
    resp = c.post("/bookings/", json=payload)
    assert resp.status_code == 201
    assert resp.json()["name"] == "new_trip"


def test_put_booking_updates_existing(client):
    resp = client.put("/bookings/san_april", json={
        "name": "san_april",
        "pickup_location": "SAN",
        "pickup_date": "2026-04-02",
        "pickup_time": "10:00",
        "dropoff_date": "2026-04-08",
        "dropoff_time": "10:00",
        "holding_price": 400.0,
        "holding_vehicle_type": "Standard Car",
    })
    assert resp.status_code == 200
    assert resp.json()["holding_price"] == 400.0


def test_delete_booking_removes_it(client):
    resp = client.delete("/bookings/san_april")
    assert resp.status_code == 204
    # Verify gone
    get_resp = client.get("/bookings/")
    assert all(b["name"] != "san_april" for b in get_resp.json())


def test_put_booking_not_found(client):
    resp = client.put("/bookings/no_such_booking", json={
        "name": "no_such_booking",
        "pickup_location": "SAN",
        "pickup_date": "2026-04-02",
        "pickup_time": "10:00",
        "dropoff_date": "2026-04-08",
        "dropoff_time": "10:00",
    })
    assert resp.status_code == 404


def test_delete_booking_not_found(client):
    resp = client.delete("/bookings/no_such_booking")
    assert resp.status_code == 404

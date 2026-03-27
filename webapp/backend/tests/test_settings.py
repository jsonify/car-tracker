"""Tests for settings/alerts endpoints."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient


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
            "alert_enabled": True,
            "target_price": 350.0,
            "email_notifications": True,
        },
        {
            "name": "lax_june",
            "pickup_location": "LAX",
            "pickup_date": "2026-06-01",
            "pickup_time": "09:00",
            "dropoff_date": "2026-06-07",
            "dropoff_time": "09:00",
        },
    ])
    monkeypatch.setenv("CAR_TRACKER_CONFIG", str(config_path))
    from webapp.backend.main import app
    return TestClient(app)


def test_get_alert_settings_returns_all_bookings(client):
    resp = client.get("/settings/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["alerts"]) == 2


def test_get_alert_settings_has_correct_defaults(client):
    resp = client.get("/settings/alerts")
    data = resp.json()
    # san_april has explicit alert_enabled=True
    san = next(a for a in data["alerts"] if a["booking_name"] == "san_april")
    assert san["alert_enabled"] is True
    assert san["target_price"] == 350.0
    assert san["email_notifications"] is True
    # lax_june has defaults
    lax = next(a for a in data["alerts"] if a["booking_name"] == "lax_june")
    assert lax["alert_enabled"] is False
    assert lax["target_price"] is None
    assert lax["email_notifications"] is True


def test_update_alert_settings(client):
    resp = client.put("/settings/alerts", json={
        "alerts": [
            {
                "booking_name": "san_april",
                "alert_enabled": False,
                "target_price": 300.0,
                "email_notifications": False,
            },
            {
                "booking_name": "lax_june",
                "alert_enabled": True,
                "target_price": 500.0,
                "email_notifications": True,
            },
        ]
    })
    assert resp.status_code == 200
    data = resp.json()
    san = next(a for a in data["alerts"] if a["booking_name"] == "san_april")
    assert san["alert_enabled"] is False
    assert san["target_price"] == 300.0
    lax = next(a for a in data["alerts"] if a["booking_name"] == "lax_june")
    assert lax["alert_enabled"] is True
    assert lax["target_price"] == 500.0


def test_update_persists_to_config(client, tmp_path, monkeypatch):
    client.put("/settings/alerts", json={
        "alerts": [
            {
                "booking_name": "san_april",
                "alert_enabled": True,
                "target_price": 299.0,
                "email_notifications": False,
            },
        ]
    })
    # Re-read to verify persistence
    resp = client.get("/settings/alerts")
    san = next(a for a in resp.json()["alerts"] if a["booking_name"] == "san_april")
    assert san["target_price"] == 299.0
    assert san["email_notifications"] is False

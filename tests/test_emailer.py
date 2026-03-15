from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from car_tracker.database import VehicleRecord
from car_tracker.emailer import EmailConfig, build_delta, load_email_config, render_failure, render_success


# ---------------------------------------------------------------------------
# build_delta
# ---------------------------------------------------------------------------


def _vehicles() -> list[VehicleRecord]:
    return [
        VehicleRecord(position=1, name="Economy Car (Alamo)", total_price=210.0, price_per_day=52.5),
        VehicleRecord(position=2, name="Compact Car (Avis)", total_price=240.0, price_per_day=60.0),
        VehicleRecord(position=3, name="Full-Size SUV (Enterprise)", total_price=400.0, price_per_day=100.0),
    ]


def test_build_delta_no_prior_run() -> None:
    result = build_delta(_vehicles(), {})
    for row in result:
        assert row["delta"] is None
        assert row["is_new"] is False


def test_build_delta_price_increase() -> None:
    prior = {"Economy Car (Alamo)": 200.0, "Compact Car (Avis)": 240.0, "Full-Size SUV (Enterprise)": 400.0}
    result = build_delta(_vehicles(), prior)
    eco = next(r for r in result if r["name"] == "Economy Car (Alamo)")
    assert eco["delta"] == pytest.approx(10.0)
    assert eco["is_new"] is False


def test_build_delta_price_decrease() -> None:
    prior = {"Economy Car (Alamo)": 220.0, "Compact Car (Avis)": 240.0, "Full-Size SUV (Enterprise)": 400.0}
    result = build_delta(_vehicles(), prior)
    eco = next(r for r in result if r["name"] == "Economy Car (Alamo)")
    assert eco["delta"] == pytest.approx(-10.0)
    assert eco["is_new"] is False


def test_build_delta_new_vehicle() -> None:
    prior = {"Economy Car (Alamo)": 200.0}
    result = build_delta(_vehicles(), prior)
    compact = next(r for r in result if r["name"] == "Compact Car (Avis)")
    assert compact["delta"] is None
    assert compact["is_new"] is True


def test_build_delta_preserves_vehicle_fields() -> None:
    result = build_delta(_vehicles(), {})
    assert result[0]["position"] == 1
    assert result[0]["name"] == "Economy Car (Alamo)"
    assert result[0]["total_price"] == 210.0
    assert result[0]["price_per_day"] == 52.5


def test_build_delta_order_preserved() -> None:
    result = build_delta(_vehicles(), {})
    assert [r["position"] for r in result] == [1, 2, 3]


# ---------------------------------------------------------------------------
# render_success
# ---------------------------------------------------------------------------


class _FakeConfig:
    class search:
        pickup_location = "LAX"
        pickup_date = "2026-04-01"
        pickup_time = "10:00"
        dropoff_date = "2026-04-05"
        dropoff_time = "10:00"


def test_render_success_contains_search_params() -> None:
    rows = build_delta(_vehicles(), {})
    html = render_success(rows, _FakeConfig(), "2026-03-14T12:00:00")
    assert "LAX" in html
    assert "2026-04-01" in html
    assert "2026-04-05" in html


def test_render_success_contains_vehicles() -> None:
    rows = build_delta(_vehicles(), {})
    html = render_success(rows, _FakeConfig(), "2026-03-14T12:00:00")
    assert "Economy Car (Alamo)" in html
    assert "210" in html


def test_render_success_no_prior_shows_dash() -> None:
    rows = build_delta(_vehicles(), {})
    html = render_success(rows, _FakeConfig(), "2026-03-14T12:00:00")
    assert "—" in html


def test_render_success_price_increase_shows_up_arrow() -> None:
    prior = {"Economy Car (Alamo)": 200.0, "Compact Car (Avis)": 240.0, "Full-Size SUV (Enterprise)": 400.0}
    rows = build_delta(_vehicles(), prior)
    html = render_success(rows, _FakeConfig(), "2026-03-14T12:00:00")
    assert "▲" in html


def test_render_success_price_decrease_shows_down_arrow() -> None:
    prior = {"Economy Car (Alamo)": 220.0, "Compact Car (Avis)": 240.0, "Full-Size SUV (Enterprise)": 400.0}
    rows = build_delta(_vehicles(), prior)
    html = render_success(rows, _FakeConfig(), "2026-03-14T12:00:00")
    assert "▼" in html


def test_render_success_new_vehicle_shows_new() -> None:
    prior = {"Economy Car (Alamo)": 200.0}
    rows = build_delta(_vehicles(), prior)
    html = render_success(rows, _FakeConfig(), "2026-03-14T12:00:00")
    assert "New" in html


def test_render_success_empty_vehicles() -> None:
    html = render_success([], _FakeConfig(), "2026-03-14T12:00:00")
    assert isinstance(html, str)
    assert len(html) > 0


# ---------------------------------------------------------------------------
# render_failure
# ---------------------------------------------------------------------------


def test_render_failure_contains_error() -> None:
    html = render_failure("Connection timed out", _FakeConfig())
    assert "Connection timed out" in html


def test_render_failure_contains_search_params() -> None:
    html = render_failure("oops", _FakeConfig())
    assert "LAX" in html
    assert "2026-04-01" in html


# ---------------------------------------------------------------------------
# load_email_config
# ---------------------------------------------------------------------------


def test_load_email_config_success() -> None:
    env_vars = {
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SENDER_EMAIL": "test@example.com",
        "SENDER_PASSWORD": "secret",
        "RECIPIENT_EMAIL": "dest@example.com",
    }
    with patch("car_tracker.emailer.load_dotenv"), patch.dict(os.environ, env_vars, clear=False):
        cfg = load_email_config()
    assert cfg.smtp_server == "smtp.gmail.com"
    assert cfg.smtp_port == 587
    assert cfg.sender_email == "test@example.com"
    assert cfg.sender_password == "secret"
    assert cfg.recipient_email == "dest@example.com"


def test_load_email_config_missing_field_raises() -> None:
    env_vars = {
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SENDER_EMAIL": "test@example.com",
        # SENDER_PASSWORD missing
        "RECIPIENT_EMAIL": "dest@example.com",
    }
    # Remove SENDER_PASSWORD from env if present
    clean_env = {k: v for k, v in os.environ.items() if k != "SENDER_PASSWORD"}
    clean_env.update(env_vars)
    with patch("car_tracker.emailer.load_dotenv"), patch.dict(os.environ, clean_env, clear=True):
        with pytest.raises(ValueError, match="SENDER_PASSWORD"):
            load_email_config()

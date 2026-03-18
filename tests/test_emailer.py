from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from datetime import date

from car_tracker.config import BookingConfig
from car_tracker.database import VehicleRecord
from car_tracker.emailer import BookingSection, EmailConfig, best_per_type, best_per_type_prices, build_delta, build_holding_summary, days_until_booking, extract_category, load_email_config, render_failure, render_success


# ---------------------------------------------------------------------------
# days_until_booking
# ---------------------------------------------------------------------------


def test_days_until_booking_future_date() -> None:
    today = date(2026, 3, 17)
    assert days_until_booking("2026-04-01", today) == 15


def test_days_until_booking_today_returns_zero() -> None:
    today = date(2026, 3, 17)
    assert days_until_booking("2026-03-17", today) == 0


def test_days_until_booking_past_date_returns_negative() -> None:
    today = date(2026, 3, 17)
    assert days_until_booking("2026-03-10", today) == -7


def test_days_until_booking_one_day_away() -> None:
    today = date(2026, 3, 17)
    assert days_until_booking("2026-03-18", today) == 1


# ---------------------------------------------------------------------------
# extract_category
# ---------------------------------------------------------------------------


def test_extract_category_standard() -> None:
    assert extract_category("Economy Car (Alamo)") == "Economy Car"


def test_extract_category_different_brand() -> None:
    assert extract_category("Compact Car (Hertz)") == "Compact Car"


def test_extract_category_no_brand() -> None:
    assert extract_category("Economy Car") == "Economy Car"


def test_extract_category_multi_word_brand() -> None:
    assert extract_category("Full-Size SUV (Enterprise Rent-A-Car)") == "Full-Size SUV"


# ---------------------------------------------------------------------------
# best_per_type
# ---------------------------------------------------------------------------


def _multi_brand_vehicles() -> list[dict]:
    """Multiple brands per category for testing best_per_type."""
    return [
        {"name": "Economy Car (Alamo)", "total_price": 210.0, "price_per_day": 52.5, "delta": None, "is_new": False},
        {"name": "Economy Car (Hertz)", "total_price": 195.0, "price_per_day": 48.75, "delta": None, "is_new": False},
        {"name": "Compact Car (Avis)", "total_price": 240.0, "price_per_day": 60.0, "delta": None, "is_new": False},
        {"name": "Compact Car (Enterprise)", "total_price": 255.0, "price_per_day": 63.75, "delta": None, "is_new": False},
        {"name": "Full-Size SUV (National)", "total_price": 400.0, "price_per_day": 100.0, "delta": None, "is_new": False},
    ]


def test_best_per_type_one_row_per_category() -> None:
    result = best_per_type(_multi_brand_vehicles())
    names = [r["name"] for r in result]
    assert len(result) == 3
    assert "Economy Car" in names
    assert "Compact Car" in names
    assert "Full-Size SUV" in names


def test_best_per_type_picks_cheapest() -> None:
    result = best_per_type(_multi_brand_vehicles())
    eco = next(r for r in result if r["name"] == "Economy Car")
    assert eco["total_price"] == 195.0


def test_best_per_type_sorted_by_price_ascending() -> None:
    result = best_per_type(_multi_brand_vehicles())
    prices = [r["total_price"] for r in result]
    assert prices == sorted(prices)


def test_best_per_type_empty_input() -> None:
    assert best_per_type([]) == []


def test_best_per_type_single_vehicle() -> None:
    vehicles = [{"name": "Economy Car (Alamo)", "total_price": 210.0, "price_per_day": 52.5, "delta": None, "is_new": False}]
    result = best_per_type(vehicles)
    assert len(result) == 1
    assert result[0]["name"] == "Economy Car"
    assert result[0]["total_price"] == 210.0


def test_best_per_type_tie_picks_first_encountered() -> None:
    vehicles = [
        {"name": "Economy Car (Alamo)", "total_price": 200.0, "price_per_day": 50.0, "delta": None, "is_new": False},
        {"name": "Economy Car (Hertz)", "total_price": 200.0, "price_per_day": 50.0, "delta": None, "is_new": False},
    ]
    result = best_per_type(vehicles)
    assert len(result) == 1
    assert result[0]["total_price"] == 200.0


# ---------------------------------------------------------------------------
# best_per_type_prices
# ---------------------------------------------------------------------------


def test_best_per_type_prices_returns_category_map() -> None:
    from car_tracker.database import VehicleRecord
    vehicles = [
        VehicleRecord(position=1, name="Economy Car (Alamo)", total_price=210.0, price_per_day=52.5),
        VehicleRecord(position=2, name="Economy Car (Hertz)", total_price=195.0, price_per_day=48.75),
        VehicleRecord(position=3, name="Compact Car (Avis)", total_price=240.0, price_per_day=60.0),
    ]
    result = best_per_type_prices(vehicles)
    assert result == {"Economy Car": 195.0, "Compact Car": 240.0}


def test_best_per_type_prices_empty() -> None:
    assert best_per_type_prices([]) == {}


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
# build_holding_summary
# ---------------------------------------------------------------------------


def _best_per_type_rows() -> list[dict]:
    """Collapsed best-per-type rows (as produced by best_per_type)."""
    return [
        {"name": "Economy Car", "total_price": 195.0, "price_per_day": 48.75, "delta": None, "is_new": False},
        {"name": "Compact Car", "total_price": 240.0, "price_per_day": 60.0, "delta": None, "is_new": False},
        {"name": "Full-Size SUV", "total_price": 400.0, "price_per_day": 100.0, "delta": None, "is_new": False},
    ]


def test_holding_summary_no_holding_price() -> None:
    assert build_holding_summary(_vehicles_with_delta(), None) is None


def test_holding_summary_no_vehicle_type_returns_none() -> None:
    """holding_price without holding_vehicle_type → None (pair rule)."""
    assert build_holding_summary(_best_per_type_rows(), 396.63, holding_vehicle_type=None) is None


def test_holding_summary_savings() -> None:
    result = build_holding_summary(_best_per_type_rows(), 396.63, holding_vehicle_type="Economy Car")
    assert result is not None
    assert result["holding_price"] == 396.63
    assert result["best_price"] == 195.0
    assert result["savings"] == pytest.approx(201.63)
    assert result["is_savings"] is True


def test_holding_summary_no_savings() -> None:
    rows = [{"name": "Economy Car", "total_price": 420.00}]
    result = build_holding_summary(rows, 396.63, holding_vehicle_type="Economy Car")
    assert result is not None
    assert result["best_price"] == 420.00
    assert result["savings"] == pytest.approx(23.37)
    assert result["is_savings"] is False


def test_holding_summary_break_even() -> None:
    rows = [{"name": "Economy Car", "total_price": 396.63}]
    result = build_holding_summary(rows, 396.63, holding_vehicle_type="Economy Car")
    assert result is not None
    assert result["savings"] == pytest.approx(0.0)
    assert result["is_savings"] is False


def test_holding_summary_empty_vehicles() -> None:
    assert build_holding_summary([], 396.63, holding_vehicle_type="Economy Car") is None


def test_holding_summary_vehicle_type_not_in_results() -> None:
    """If the held vehicle type has no current results, return None."""
    rows = [{"name": "Compact Car", "total_price": 240.0}]
    assert build_holding_summary(rows, 396.63, holding_vehicle_type="Economy Car") is None


def _vehicles_with_delta() -> list[dict]:
    return build_delta(_vehicles(), {})


# ---------------------------------------------------------------------------
# render_success helpers
# ---------------------------------------------------------------------------


def _fake_booking() -> BookingConfig:
    return BookingConfig(
        name="test",
        pickup_location="LAX",
        pickup_date="2026-04-01",
        pickup_time="10:00",
        dropoff_date="2026-04-05",
        dropoff_time="10:00",
    )


def _fake_section(vehicles: list[dict], holding_summary: dict | None = None) -> BookingSection:
    return BookingSection(booking=_fake_booking(), vehicles=vehicles, holding_summary=holding_summary)


# ---------------------------------------------------------------------------
# render_success
# ---------------------------------------------------------------------------


def test_render_success_contains_search_params() -> None:
    rows = build_delta(_vehicles(), {})
    html = render_success([_fake_section(rows)], "2026-03-14T12:00:00")
    assert "LAX" in html
    assert "2026-04-01" in html
    assert "2026-04-05" in html


def test_render_success_contains_booking_name() -> None:
    rows = build_delta(_vehicles(), {})
    html = render_success([_fake_section(rows)], "2026-03-14T12:00:00")
    assert "test" in html


def test_render_success_contains_vehicles() -> None:
    rows = build_delta(_vehicles(), {})
    html = render_success([_fake_section(rows)], "2026-03-14T12:00:00")
    assert "Economy Car (Alamo)" in html
    assert "210" in html


def test_render_success_no_prior_shows_dash() -> None:
    rows = build_delta(_vehicles(), {})
    html = render_success([_fake_section(rows)], "2026-03-14T12:00:00")
    assert "—" in html


def test_render_success_price_increase_shows_up_arrow() -> None:
    prior = {"Economy Car (Alamo)": 200.0, "Compact Car (Avis)": 240.0, "Full-Size SUV (Enterprise)": 400.0}
    rows = build_delta(_vehicles(), prior)
    html = render_success([_fake_section(rows)], "2026-03-14T12:00:00")
    assert "▲" in html


def test_render_success_price_decrease_shows_down_arrow() -> None:
    prior = {"Economy Car (Alamo)": 220.0, "Compact Car (Avis)": 240.0, "Full-Size SUV (Enterprise)": 400.0}
    rows = build_delta(_vehicles(), prior)
    html = render_success([_fake_section(rows)], "2026-03-14T12:00:00")
    assert "▼" in html


def test_render_success_new_vehicle_shows_new() -> None:
    prior = {"Economy Car (Alamo)": 200.0}
    rows = build_delta(_vehicles(), prior)
    html = render_success([_fake_section(rows)], "2026-03-14T12:00:00")
    assert "New" in html


def test_render_success_empty_vehicles() -> None:
    html = render_success([_fake_section([])], "2026-03-14T12:00:00")
    assert isinstance(html, str)
    assert len(html) > 0


def test_render_success_shows_savings_summary() -> None:
    rows = best_per_type(build_delta(_vehicles(), {}))
    summary = build_holding_summary(rows, 500.00, holding_vehicle_type="Economy Car")
    html = render_success([_fake_section(rows, holding_summary=summary)], "2026-03-14T12:00:00")
    assert "500.00" in html
    assert "Savings" in html


def test_render_success_shows_keep_booking_message() -> None:
    rows = best_per_type(build_delta(_vehicles(), {}))
    summary = build_holding_summary(rows, 100.00, holding_vehicle_type="Economy Car")
    html = render_success([_fake_section(rows, holding_summary=summary)], "2026-03-14T12:00:00")
    assert "keep your booking" in html


def test_render_success_no_holding_summary_omits_block() -> None:
    rows = build_delta(_vehicles(), {})
    html = render_success([_fake_section(rows)], "2026-03-14T12:00:00")
    assert "holding price" not in html.lower()
    assert "keep your booking" not in html


def test_render_success_two_bookings_both_appear() -> None:
    """Combined email renders a section for each booking."""
    booking1 = BookingConfig(
        name="hawaii", pickup_location="HNL",
        pickup_date="2026-05-01", pickup_time="10:00",
        dropoff_date="2026-05-08", dropoff_time="10:00",
    )
    booking2 = BookingConfig(
        name="vegas", pickup_location="LAS",
        pickup_date="2026-06-01", pickup_time="10:00",
        dropoff_date="2026-06-05", dropoff_time="10:00",
    )
    rows = build_delta(_vehicles(), {})
    sections = [
        BookingSection(booking=booking1, vehicles=rows, holding_summary=None),
        BookingSection(booking=booking2, vehicles=rows, holding_summary=None),
    ]
    html = render_success(sections, "2026-03-14T12:00:00")
    assert "hawaii" in html
    assert "HNL" in html
    assert "vegas" in html
    assert "LAS" in html


def test_render_success_per_booking_holding_summary_isolated() -> None:
    """Only the booking with a holding summary shows the holding block."""
    booking1 = BookingConfig(
        name="hawaii", pickup_location="HNL",
        pickup_date="2026-05-01", pickup_time="10:00",
        dropoff_date="2026-05-08", dropoff_time="10:00",
    )
    booking2 = BookingConfig(
        name="vegas", pickup_location="LAS",
        pickup_date="2026-06-01", pickup_time="10:00",
        dropoff_date="2026-06-05", dropoff_time="10:00",
    )
    rows = best_per_type(build_delta(_vehicles(), {}))
    summary = build_holding_summary(rows, 500.00, holding_vehicle_type="Economy Car")
    sections = [
        BookingSection(booking=booking1, vehicles=rows, holding_summary=summary),
        BookingSection(booking=booking2, vehicles=rows, holding_summary=None),
    ]
    html = render_success(sections, "2026-03-14T12:00:00")
    assert "Savings" in html  # hawaii has holding summary
    assert html.count("holding price") == 1  # only one section shows it


# ---------------------------------------------------------------------------
# render_failure
# ---------------------------------------------------------------------------


def test_render_failure_contains_error() -> None:
    html = render_failure("Connection timed out", _fake_booking())
    assert "Connection timed out" in html


def test_render_failure_contains_search_params() -> None:
    html = render_failure("oops", _fake_booking())
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

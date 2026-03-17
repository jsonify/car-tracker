"""Tests for discord_notifier.py — embed building functions."""

from __future__ import annotations

import pytest

from car_tracker.config import BookingConfig
from car_tracker.discord_notifier import (
    _COLOR_BLUE,
    _COLOR_GREEN,
    _COLOR_ORANGE,
    _COLOR_RED,
    _fmt_delta,
    _fmt_price,
    _section_color,
    build_failure_embed,
    build_success_embeds,
)
from car_tracker.emailer import BookingSection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _booking(name: str = "test", location: str = "SAN") -> BookingConfig:
    return BookingConfig(
        name=name,
        pickup_location=location,
        pickup_date="2026-04-02",
        pickup_time="10:00",
        dropoff_date="2026-04-08",
        dropoff_time="10:00",
    )


def _vehicle(
    name: str = "Economy Car",
    total_price: float = 200.0,
    price_per_day: float = 33.33,
    delta: float | None = None,
    is_new: bool = False,
) -> dict:
    return {
        "name": name,
        "total_price": total_price,
        "price_per_day": price_per_day,
        "delta": delta,
        "is_new": is_new,
    }


# ---------------------------------------------------------------------------
# _fmt_price
# ---------------------------------------------------------------------------


def test_fmt_price_integer() -> None:
    assert _fmt_price(375.0) == "$375.00"


def test_fmt_price_fractional() -> None:
    assert _fmt_price(123.456) == "$123.46"


def test_fmt_price_large() -> None:
    assert _fmt_price(1234.0) == "$1,234.00"


# ---------------------------------------------------------------------------
# _fmt_delta
# ---------------------------------------------------------------------------


def test_fmt_delta_none_no_prior() -> None:
    assert _fmt_delta(None, is_new=False) == "—"


def test_fmt_delta_new_vehicle() -> None:
    result = _fmt_delta(None, is_new=True)
    assert "New" in result


def test_fmt_delta_price_drop() -> None:
    result = _fmt_delta(-25.50, is_new=False)
    assert "▼" in result
    assert "25.50" in result


def test_fmt_delta_price_increase() -> None:
    result = _fmt_delta(15.0, is_new=False)
    assert "▲" in result
    assert "15.00" in result


def test_fmt_delta_no_change() -> None:
    assert _fmt_delta(0.0, is_new=False) == "—"


# ---------------------------------------------------------------------------
# _section_color
# ---------------------------------------------------------------------------


def test_section_color_no_deltas_returns_blue() -> None:
    vehicles = [_vehicle(delta=None)]
    assert _section_color(vehicles) == _COLOR_BLUE


def test_section_color_any_drop_returns_green() -> None:
    vehicles = [_vehicle(delta=-10.0), _vehicle(delta=5.0)]
    assert _section_color(vehicles) == _COLOR_GREEN


def test_section_color_all_increases_returns_red() -> None:
    vehicles = [_vehicle(delta=5.0), _vehicle(delta=20.0)]
    assert _section_color(vehicles) == _COLOR_RED


def test_section_color_empty_returns_blue() -> None:
    assert _section_color([]) == _COLOR_BLUE


# ---------------------------------------------------------------------------
# build_failure_embed
# ---------------------------------------------------------------------------


def test_build_failure_embed_has_title() -> None:
    booking = _booking(name="san_april")
    embed = build_failure_embed(booking, "Timeout error")
    assert "san_april" in embed["title"]


def test_build_failure_embed_has_orange_color() -> None:
    embed = build_failure_embed(_booking(), "error")
    assert embed["color"] == _COLOR_ORANGE


def test_build_failure_embed_contains_error_message() -> None:
    embed = build_failure_embed(_booking(), "Something went wrong")
    assert "Something went wrong" in embed["description"]


def test_build_failure_embed_truncates_long_error() -> None:
    long_error = "x" * 2000
    embed = build_failure_embed(_booking(), long_error)
    # description should not be excessively long
    assert len(embed["description"]) < 2000


def test_build_failure_embed_contains_location() -> None:
    embed = build_failure_embed(_booking(location="LAX"), "err")
    assert "LAX" in embed["description"]


# ---------------------------------------------------------------------------
# build_success_embeds
# ---------------------------------------------------------------------------


def test_build_success_embeds_empty_sections() -> None:
    result = build_success_embeds([], "2026-01-01 00:00 UTC")
    assert result == []


def test_build_success_embeds_one_section() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle()],
        holding_summary=None,
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    assert len(embeds) == 1


def test_build_success_embeds_multiple_sections() -> None:
    sections = [
        BookingSection(booking=_booking("a"), vehicles=[_vehicle()], holding_summary=None),
        BookingSection(booking=_booking("b"), vehicles=[_vehicle()], holding_summary=None),
    ]
    embeds = build_success_embeds(sections, "2026-01-01 00:00 UTC")
    assert len(embeds) == 2


def test_build_success_embeds_title_contains_location() -> None:
    section = BookingSection(
        booking=_booking(location="SAN"),
        vehicles=[_vehicle()],
        holding_summary=None,
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    assert "SAN" in embeds[0]["title"]


def test_build_success_embeds_description_contains_vehicle_name() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle(name="Economy Car")],
        holding_summary=None,
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    assert "Economy Car" in embeds[0]["description"]


def test_build_success_embeds_description_contains_price() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle(total_price=399.50)],
        holding_summary=None,
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    assert "399.50" in embeds[0]["description"]


def test_build_success_embeds_green_on_price_drop() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle(delta=-20.0)],
        holding_summary=None,
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    assert embeds[0]["color"] == _COLOR_GREEN


def test_build_success_embeds_red_on_all_increases() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle(delta=10.0)],
        holding_summary=None,
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    assert embeds[0]["color"] == _COLOR_RED


def test_build_success_embeds_holding_field_when_savings() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle()],
        holding_summary={
            "holding_price": 300.0,
            "best_price": 200.0,
            "savings": 100.0,
            "is_savings": True,
        },
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    fields = embeds[0]["fields"]
    assert len(fields) == 1
    assert "rebooking" in fields[0]["value"].lower() or "save" in fields[0]["value"].lower()


def test_build_success_embeds_holding_field_when_no_savings() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle()],
        holding_summary={
            "holding_price": 200.0,
            "best_price": 250.0,
            "savings": 50.0,
            "is_savings": False,
        },
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    fields = embeds[0]["fields"]
    assert len(fields) == 1
    assert "keep" in fields[0]["value"].lower()


def test_build_success_embeds_no_holding_field_when_none() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle()],
        holding_summary=None,
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    assert embeds[0]["fields"] == []


def test_build_success_embeds_footer_contains_run_ts() -> None:
    section = BookingSection(
        booking=_booking(),
        vehicles=[_vehicle()],
        holding_summary=None,
    )
    run_ts = "2026-03-17 14:30 UTC"
    embeds = build_success_embeds([section], run_ts)
    assert run_ts in embeds[0]["footer"]["text"]


def test_build_success_embeds_footer_contains_booking_name() -> None:
    section = BookingSection(
        booking=_booking(name="san_april"),
        vehicles=[_vehicle()],
        holding_summary=None,
    )
    embeds = build_success_embeds([section], "2026-01-01 00:00 UTC")
    assert "san_april" in embeds[0]["footer"]["text"]

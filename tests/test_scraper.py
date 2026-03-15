from __future__ import annotations

import pytest

from car_tracker.scraper import (
    VehicleResult,
    days_between,
    to_12h,
    _to_mmddyyyy,
)


# ---------------------------------------------------------------------------
# to_12h
# ---------------------------------------------------------------------------


def test_to_12h_morning():
    assert to_12h("10:00") == "10:00 AM"


def test_to_12h_noon():
    assert to_12h("12:00") == "12:00 PM"


def test_to_12h_afternoon():
    assert to_12h("14:30") == "02:30 PM"


def test_to_12h_midnight():
    assert to_12h("00:00") == "12:00 AM"


def test_to_12h_11pm():
    assert to_12h("23:00") == "11:00 PM"


def test_to_12h_1am():
    assert to_12h("01:00") == "01:00 AM"


# ---------------------------------------------------------------------------
# days_between
# ---------------------------------------------------------------------------


def test_days_between_four_days():
    assert days_between("2026-04-01", "2026-04-05") == 4


def test_days_between_one_day():
    assert days_between("2026-04-01", "2026-04-02") == 1


def test_days_between_same_day_returns_one():
    # Avoid division by zero
    assert days_between("2026-04-01", "2026-04-01") == 1


def test_days_between_week():
    assert days_between("2026-04-01", "2026-04-08") == 7


# ---------------------------------------------------------------------------
# _to_mmddyyyy
# ---------------------------------------------------------------------------


def test_to_mmddyyyy():
    assert _to_mmddyyyy("2026-04-01") == "04/01/2026"


def test_to_mmddyyyy_december():
    assert _to_mmddyyyy("2026-12-25") == "12/25/2026"


# ---------------------------------------------------------------------------
# VehicleResult
# ---------------------------------------------------------------------------


def test_vehicle_result_fields():
    v = VehicleResult(
        position=1,
        name="Economy Car",
        brand="Alamo",
        total_price=396.63,
        price_per_day=99.16,
    )
    assert v.position == 1
    assert v.name == "Economy Car"
    assert v.brand == "Alamo"
    assert v.total_price == 396.63
    assert v.price_per_day == 99.16


def test_price_per_day_calculation():
    total = 396.63
    days = days_between("2026-04-01", "2026-04-05")
    assert days == 4
    ppd = round(total / days, 2)
    assert ppd == 99.16

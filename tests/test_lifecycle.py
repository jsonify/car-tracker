from __future__ import annotations

import textwrap
from datetime import date
from pathlib import Path
from unittest.mock import call, patch

import pytest
import yaml

from car_tracker.lifecycle import remove_expired_bookings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_config(path: Path, booking: dict) -> None:
    """Write a minimal config.yaml with a single booking dict."""
    import yaml as _yaml

    doc = {
        "bookings": [booking],
        "database": {"path": "data/results.db"},
    }
    path.write_text(_yaml.dump(doc, default_flow_style=False, allow_unicode=True))


def _booking_dict(
    name: str = "hawaii",
    pickup_location: str = "HNL",
    pickup_date: str = "2026-05-01",
    pickup_time: str = "10:00",
    dropoff_date: str = "2026-05-08",
    dropoff_time: str = "10:00",
) -> dict:
    return {
        "name": name,
        "pickup_location": pickup_location,
        "pickup_date": pickup_date,
        "pickup_time": pickup_time,
        "dropoff_date": dropoff_date,
        "dropoff_time": dropoff_time,
    }


# ---------------------------------------------------------------------------
# Test: no expired bookings — no side effects
# ---------------------------------------------------------------------------


def test_no_expired_bookings_returns_empty_list(tmp_path: Path) -> None:
    """When no booking is expired, returns [] and does not write config or call git."""
    cfg = tmp_path / "config.yaml"
    _write_config(cfg, _booking_dict(pickup_date="2026-05-01"))

    today = date(2026, 4, 15)  # before pickup_date

    with patch("car_tracker.lifecycle.subprocess.run") as mock_run:
        removed = remove_expired_bookings(cfg, today)

    assert removed == []
    mock_run.assert_not_called()
    # Config file is unchanged — still has 1 booking
    raw = yaml.safe_load(cfg.read_text())
    assert len(raw["bookings"]) == 1


def test_no_expired_bookings_does_not_write_config(tmp_path: Path) -> None:
    """Config file content is identical when nothing is removed."""
    cfg = tmp_path / "config.yaml"
    _write_config(cfg, _booking_dict(pickup_date="2026-05-01"))
    original_content = cfg.read_text()

    today = date(2026, 4, 15)

    with patch("car_tracker.lifecycle.subprocess.run"):
        remove_expired_bookings(cfg, today)

    assert cfg.read_text() == original_content


# ---------------------------------------------------------------------------
# Test: today == pickup_date — NOT expired (strictly before required)
# ---------------------------------------------------------------------------


def test_pickup_date_today_is_not_expired(tmp_path: Path) -> None:
    """A booking whose pickup_date == today is NOT expired (today > pickup_date required)."""
    cfg = tmp_path / "config.yaml"
    _write_config(cfg, _booking_dict(pickup_date="2026-05-01"))

    today = date(2026, 5, 1)  # same as pickup_date → not expired

    with patch("car_tracker.lifecycle.subprocess.run") as mock_run:
        removed = remove_expired_bookings(cfg, today)

    assert removed == []
    mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# Test: one expired booking
# ---------------------------------------------------------------------------


def test_one_expired_booking_removed_and_returned(tmp_path: Path) -> None:
    """An expired booking is removed from config and returned in the list."""
    cfg = tmp_path / "config.yaml"
    _write_config(cfg, _booking_dict(name="hawaii", pickup_date="2026-03-01"))

    today = date(2026, 3, 17)  # today > 2026-03-01 → expired

    with patch("car_tracker.lifecycle.subprocess.run") as mock_run:
        removed = remove_expired_bookings(cfg, today)

    assert len(removed) == 1
    assert removed[0].name == "hawaii"
    assert removed[0].pickup_date == "2026-03-01"

    # Config file now has empty bookings list
    raw = yaml.safe_load(cfg.read_text())
    assert raw["bookings"] == [] or raw["bookings"] is None or raw.get("bookings") == []


def test_one_expired_booking_calls_git(tmp_path: Path) -> None:
    """When a booking is expired, git add/commit/pull/push are called."""
    cfg = tmp_path / "config.yaml"
    _write_config(cfg, _booking_dict(name="hawaii", pickup_date="2026-03-01"))

    today = date(2026, 3, 17)

    with patch("car_tracker.lifecycle.subprocess.run") as mock_run:
        remove_expired_bookings(cfg, today)

    assert mock_run.call_count == 4
    calls = mock_run.call_args_list
    assert calls[0] == call(["git", "add", str(cfg)], cwd=tmp_path, check=True)
    assert calls[1][0][0][0] == "git"
    assert calls[1][0][0][1] == "commit"
    assert calls[2] == call(["git", "pull", "--rebase", "--autostash"], cwd=tmp_path, check=True)
    assert calls[3] == call(["git", "push"], cwd=tmp_path, check=True)


# ---------------------------------------------------------------------------
# Test: multiple expired bookings
# ---------------------------------------------------------------------------


def test_multiple_expired_bookings_all_removed(tmp_path: Path) -> None:
    """All expired bookings are removed and returned."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "old1"
            pickup_location: "LAX"
            pickup_date: "2026-02-01"
            pickup_time: "10:00"
            dropoff_date: "2026-02-05"
            dropoff_time: "10:00"
          - name: "old2"
            pickup_location: "SFO"
            pickup_date: "2026-02-15"
            pickup_time: "10:00"
            dropoff_date: "2026-02-20"
            dropoff_time: "10:00"
        database:
          path: data/results.db
        """)
    )

    today = date(2026, 3, 17)  # both are before today

    with patch("car_tracker.lifecycle.subprocess.run") as mock_run:
        removed = remove_expired_bookings(cfg, today)

    assert len(removed) == 2
    names = {b.name for b in removed}
    assert names == {"old1", "old2"}

    raw = yaml.safe_load(cfg.read_text())
    assert raw["bookings"] == [] or raw["bookings"] is None or raw.get("bookings") == []
    mock_run.assert_called()


# ---------------------------------------------------------------------------
# Test: non-expired bookings are preserved
# ---------------------------------------------------------------------------


def test_non_expired_bookings_are_preserved(tmp_path: Path) -> None:
    """Future bookings are kept in the config when expired ones are removed."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "expired"
            pickup_location: "LAX"
            pickup_date: "2026-02-01"
            pickup_time: "10:00"
            dropoff_date: "2026-02-05"
            dropoff_time: "10:00"
          - name: "future"
            pickup_location: "HNL"
            pickup_date: "2026-06-01"
            pickup_time: "10:00"
            dropoff_date: "2026-06-08"
            dropoff_time: "10:00"
        database:
          path: data/results.db
        """)
    )

    today = date(2026, 3, 17)

    with patch("car_tracker.lifecycle.subprocess.run"):
        removed = remove_expired_bookings(cfg, today)

    assert len(removed) == 1
    assert removed[0].name == "expired"

    raw = yaml.safe_load(cfg.read_text())
    remaining = raw["bookings"]
    assert len(remaining) == 1
    assert remaining[0]["name"] == "future"


# ---------------------------------------------------------------------------
# Test: holding fields pair-validation preserved in returned BookingConfig
# ---------------------------------------------------------------------------


def test_expired_booking_with_holding_pair_preserved(tmp_path: Path) -> None:
    """Holding price + vehicle type are returned when both are present."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "hawaii"
            pickup_location: "HNL"
            pickup_date: "2026-02-01"
            pickup_time: "10:00"
            dropoff_date: "2026-02-08"
            dropoff_time: "10:00"
            holding_price: 450.00
            holding_vehicle_type: "Economy Car"
        database:
          path: data/results.db
        """)
    )

    today = date(2026, 3, 17)

    with patch("car_tracker.lifecycle.subprocess.run"):
        removed = remove_expired_bookings(cfg, today)

    assert len(removed) == 1
    assert removed[0].holding_price == 450.00
    assert removed[0].holding_vehicle_type == "Economy Car"


def test_expired_booking_with_holding_price_only_returns_none_pair(tmp_path: Path) -> None:
    """Holding price without vehicle type → both None (same pair-validation as load_config)."""
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        bookings:
          - name: "hawaii"
            pickup_location: "HNL"
            pickup_date: "2026-02-01"
            pickup_time: "10:00"
            dropoff_date: "2026-02-08"
            dropoff_time: "10:00"
            holding_price: 450.00
        database:
          path: data/results.db
        """)
    )

    today = date(2026, 3, 17)

    with patch("car_tracker.lifecycle.subprocess.run"):
        removed = remove_expired_bookings(cfg, today)

    assert removed[0].holding_price is None
    assert removed[0].holding_vehicle_type is None

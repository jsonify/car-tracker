from __future__ import annotations

import json
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from car_tracker.imessage_config import (
    parse_holding_command,
    poll_and_apply,
    update_config_yaml,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_conn(rows: list[tuple[int, str]]) -> MagicMock:
    cursor = MagicMock()
    cursor.fetchall.return_value = rows
    conn = MagicMock()
    conn.execute.return_value = cursor
    return conn


@pytest.fixture
def config_with_holding(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
          pickup_location: "SAN"
          pickup_date: "2026-04-02"
          pickup_time: "10:00"
          dropoff_date: "2026-04-08"
          dropoff_time: "10:00"
          holding_price: 375.23         # Holding price for the reservation
          holding_vehicle_type: "Standard Car"  # Vehicle type
        database:
          path: "data/results.db"
        """)
    )
    return cfg


@pytest.fixture
def config_with_imessage(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
          pickup_location: "SAN"
          pickup_date: "2026-04-02"
          pickup_time: "10:00"
          dropoff_date: "2026-04-08"
          dropoff_time: "10:00"
          holding_price: 375.23         # Holding price for the reservation
          holding_vehicle_type: "Standard Car"  # Vehicle type
        database:
          path: "data/results.db"
        imessage:
          phone_number: "+15555551234"
        """)
    )
    return cfg


# ---------------------------------------------------------------------------
# parse_holding_command
# ---------------------------------------------------------------------------


def test_parse_basic() -> None:
    assert parse_holding_command("holding 350.00 Standard Car") == (
        350.0,
        "Standard Car",
    )


def test_parse_integer_price() -> None:
    assert parse_holding_command("holding 400 Economy Car") == (400.0, "Economy Car")


def test_parse_case_insensitive() -> None:
    assert parse_holding_command("HOLDING 299.99 Compact Car") == (
        299.99,
        "Compact Car",
    )


def test_parse_multiword_type() -> None:
    assert parse_holding_command("holding 500.00 Full-Size SUV") == (
        500.0,
        "Full-Size SUV",
    )


def test_parse_leading_trailing_whitespace() -> None:
    assert parse_holding_command("  holding 350.00 Standard Car  ") == (
        350.0,
        "Standard Car",
    )


def test_parse_no_match_returns_none() -> None:
    assert parse_holding_command("check prices") is None


def test_parse_empty_returns_none() -> None:
    assert parse_holding_command("") is None


def test_parse_missing_type_returns_none() -> None:
    assert parse_holding_command("holding 350.00") is None


def test_parse_missing_price_returns_none() -> None:
    assert parse_holding_command("holding Standard Car") is None


# ---------------------------------------------------------------------------
# update_config_yaml
# ---------------------------------------------------------------------------


def test_update_price(config_with_holding: Path) -> None:
    update_config_yaml(config_with_holding, 320.0, "Standard Car")
    text = config_with_holding.read_text()
    assert "holding_price: 320" in text


def test_update_vehicle_type(config_with_holding: Path) -> None:
    update_config_yaml(config_with_holding, 375.23, "Economy Car")
    text = config_with_holding.read_text()
    assert '"Economy Car"' in text


def test_update_both(config_with_holding: Path) -> None:
    update_config_yaml(config_with_holding, 299.00, "Economy Car")
    text = config_with_holding.read_text()
    assert "holding_price: 299" in text
    assert '"Economy Car"' in text


def test_update_preserves_inline_comments(config_with_holding: Path) -> None:
    update_config_yaml(config_with_holding, 300.0, "Economy Car")
    text = config_with_holding.read_text()
    assert "# Holding price for the reservation" in text
    assert "# Vehicle type" in text


def test_update_preserves_other_fields(config_with_holding: Path) -> None:
    update_config_yaml(config_with_holding, 300.0, "Economy Car")
    text = config_with_holding.read_text()
    assert 'pickup_location: "SAN"' in text
    assert "data/results.db" in text


def test_update_old_value_absent(config_with_holding: Path) -> None:
    update_config_yaml(config_with_holding, 375.23, "Standard Car")
    text = config_with_holding.read_text()
    # Original value should be replaced, not duplicated
    assert text.count("375.23") == 1


# ---------------------------------------------------------------------------
# poll_and_apply
# ---------------------------------------------------------------------------


def test_poll_no_messages_returns_false(config_with_imessage: Path) -> None:
    with patch("car_tracker.imessage_config.sqlite3.connect") as mock_connect:
        mock_connect.return_value = _make_conn([])
        result = poll_and_apply(config_with_imessage)
    assert result is False


def test_poll_holding_command_updates_config(config_with_imessage: Path) -> None:
    rows = [(1_000_000, "holding 320.00 Economy Car")]
    with patch("car_tracker.imessage_config.sqlite3.connect") as mock_connect:
        mock_connect.return_value = _make_conn(rows)
        result = poll_and_apply(config_with_imessage)
    assert result is True
    text = config_with_imessage.read_text()
    assert "holding_price: 320" in text
    assert '"Economy Car"' in text


def test_poll_self_sent_message_updates_config(config_with_imessage: Path) -> None:
    """Self-sent iMessages (iPhone → own number) appear as is_from_me=1 on Mac."""
    rows = [(1_000_000, "holding 310.00 Standard Car")]
    with patch("car_tracker.imessage_config.sqlite3.connect") as mock_connect:
        mock_connect.return_value = _make_conn(rows)
        result = poll_and_apply(config_with_imessage)
    assert result is True
    text = config_with_imessage.read_text()
    assert "holding_price: 310" in text


def test_poll_non_command_message_returns_false(config_with_imessage: Path) -> None:
    rows = [(1_000_000, "hello there")]
    with patch("car_tracker.imessage_config.sqlite3.connect") as mock_connect:
        mock_connect.return_value = _make_conn(rows)
        result = poll_and_apply(config_with_imessage)
    assert result is False


def test_poll_saves_state_after_messages(config_with_imessage: Path) -> None:
    rows = [(9_999_999, "holding 350.00 Standard Car")]
    with patch("car_tracker.imessage_config.sqlite3.connect") as mock_connect:
        mock_connect.return_value = _make_conn(rows)
        poll_and_apply(config_with_imessage)
    state_path = config_with_imessage.parent / "data" / "imessage_state.json"
    state = json.loads(state_path.read_text())
    assert state["last_date"] == 9_999_999


def test_poll_state_saved_even_for_non_commands(config_with_imessage: Path) -> None:
    rows = [(5_000_000, "not a command")]
    with patch("car_tracker.imessage_config.sqlite3.connect") as mock_connect:
        mock_connect.return_value = _make_conn(rows)
        poll_and_apply(config_with_imessage)
    state_path = config_with_imessage.parent / "data" / "imessage_state.json"
    state = json.loads(state_path.read_text())
    assert state["last_date"] == 5_000_000


def test_poll_no_phone_configured_returns_false(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        textwrap.dedent("""\
        search:
          pickup_location: "SAN"
          pickup_date: "2026-04-02"
          pickup_time: "10:00"
          dropoff_date: "2026-04-08"
          dropoff_time: "10:00"
        database:
          path: "data/results.db"
        """)
    )
    result = poll_and_apply(cfg)
    assert result is False


def test_poll_latest_command_wins(config_with_imessage: Path) -> None:
    """When multiple commands arrive, the last one is the final applied state."""
    rows = [
        (1_000_000, "holding 320.00 Economy Car"),
        (2_000_000, "holding 400.00 Standard SUV"),
    ]
    with patch("car_tracker.imessage_config.sqlite3.connect") as mock_connect:
        mock_connect.return_value = _make_conn(rows)
        result = poll_and_apply(config_with_imessage)
    assert result is True
    text = config_with_imessage.read_text()
    assert "holding_price: 400" in text
    assert '"Standard SUV"' in text


def test_poll_skips_messages_before_state(config_with_imessage: Path) -> None:
    """State file prevents re-processing old messages."""
    state_path = config_with_imessage.parent / "data" / "imessage_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"last_date": 5_000_000}))

    # This message predates the stored state — should not be processed
    rows: list[tuple[int, str]] = []
    with patch("car_tracker.imessage_config.sqlite3.connect") as mock_connect:
        mock_connect.return_value = _make_conn(rows)
        result = poll_and_apply(config_with_imessage)
        # Verify query was called with since_date = 5_000_000
        call_args = mock_connect.return_value.execute.call_args
        assert call_args[0][1][1] == 5_000_000

    assert result is False

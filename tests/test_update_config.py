"""Tests for scripts/update_config.py — parse_config_update and apply_config_update."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from scripts.update_config import apply_config_update, parse_config_update


# ---------------------------------------------------------------------------
# parse_config_update tests — legacy natural-language format
# ---------------------------------------------------------------------------


class TestParseConfigUpdate:
    def test_extracts_holding_price_basic(self):
        result = parse_config_update("update holding price to 375")
        assert result == {"holding_price": 375.0}

    def test_extracts_holding_price_with_dollar_sign(self):
        result = parse_config_update("change my holding price to $400.50")
        assert result == {"holding_price": 400.50}

    def test_extracts_holding_vehicle_type(self):
        result = parse_config_update("set holding type to SUV")
        assert result == {"holding_vehicle_type": "SUV"}

    def test_extracts_holding_vehicle_type_multiword(self):
        result = parse_config_update("set holding type to Standard Car")
        assert result == {"holding_vehicle_type": "Standard Car"}

    def test_extracts_both_fields_combined(self):
        result = parse_config_update("update holding price to 350 for Standard Car")
        assert result == {"holding_price": 350.0, "holding_vehicle_type": "Standard Car"}

    def test_extracts_both_fields_type_first(self):
        result = parse_config_update("change holding type to Economy Car and price to 299")
        assert result.get("holding_vehicle_type") == "Economy Car"
        assert result.get("holding_price") == 299.0

    def test_returns_empty_dict_for_unrecognized_text(self):
        result = parse_config_update("what is the weather today")
        assert result == {}

    def test_returns_empty_dict_for_empty_string(self):
        result = parse_config_update("")
        assert result == {}

    def test_rejects_negative_price(self):
        result = parse_config_update("set holding price to -50")
        assert "holding_price" not in result

    def test_rejects_zero_price(self):
        result = parse_config_update("set holding price to 0")
        assert "holding_price" not in result

    def test_price_with_integer_value(self):
        result = parse_config_update("update holding price to 500")
        assert result == {"holding_price": 500.0}

    def test_case_insensitive(self):
        result = parse_config_update("UPDATE HOLDING PRICE TO 400")
        assert result == {"holding_price": 400.0}


# ---------------------------------------------------------------------------
# parse_config_update tests — structured multi-booking format
# ---------------------------------------------------------------------------


class TestParseConfigUpdateStructured:
    def test_parse_by_name(self):
        result = parse_config_update("update holding san_april 450.00 Economy Car")
        assert result == {
            "booking_identifier": "san_april",
            "holding_price": 450.0,
            "holding_vehicle_type": "Economy Car",
        }

    def test_parse_by_index(self):
        result = parse_config_update("update holding 1 375.00 Standard Car")
        assert result == {
            "booking_identifier": "1",
            "holding_price": 375.0,
            "holding_vehicle_type": "Standard Car",
        }

    def test_parse_by_name_with_dollar_sign(self):
        result = parse_config_update("update holding hawaii $299.99 Economy Car")
        assert result["booking_identifier"] == "hawaii"
        assert result["holding_price"] == 299.99
        assert result["holding_vehicle_type"] == "Economy Car"

    def test_parse_multiword_vehicle_type(self):
        result = parse_config_update("update holding vegas 500 Full Size Car")
        assert result["holding_vehicle_type"] == "Full Size Car"

    def test_parse_index_two(self):
        result = parse_config_update("update holding 2 199.00 Compact Car")
        assert result["booking_identifier"] == "2"
        assert result["holding_price"] == 199.0

    def test_structured_format_case_insensitive(self):
        result = parse_config_update("UPDATE HOLDING SAN_APRIL 400.00 Standard Car")
        assert result["booking_identifier"] == "SAN_APRIL"
        assert result["holding_price"] == 400.0


# ---------------------------------------------------------------------------
# apply_config_update tests
# ---------------------------------------------------------------------------

SAMPLE_CONFIG = {
    "bookings": [
        {
            "name": "san_april",
            "pickup_location": "SAN",
            "pickup_date": "2026-04-02",
            "pickup_time": "10:00",
            "dropoff_date": "2026-04-08",
            "dropoff_time": "10:00",
            "holding_price": 375.23,
            "holding_vehicle_type": "Standard Car",
        },
        {
            "name": "las_june",
            "pickup_location": "LAS",
            "pickup_date": "2026-06-10",
            "pickup_time": "12:00",
            "dropoff_date": "2026-06-15",
            "dropoff_time": "12:00",
            "holding_price": 200.0,
            "holding_vehicle_type": "Economy Car",
        },
    ],
    "database": {"path": "data/results.db"},
}


def _write_sample_config(path: Path) -> None:
    with open(path, "w") as f:
        yaml.dump(SAMPLE_CONFIG, f, default_flow_style=False, sort_keys=False)


class TestApplyConfigUpdate:
    def test_updates_holding_price_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with patch("subprocess.run"):
                result = apply_config_update({"holding_price": 400.0}, cfg)
            assert result is True
            with open(cfg) as f:
                updated = yaml.safe_load(f)
            assert updated["bookings"][0]["holding_price"] == 400.0
            # Other fields untouched
            assert updated["bookings"][0]["pickup_location"] == "SAN"
            assert updated["bookings"][0]["holding_vehicle_type"] == "Standard Car"

    def test_updates_holding_vehicle_type_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with patch("subprocess.run"):
                result = apply_config_update({"holding_vehicle_type": "SUV"}, cfg)
            assert result is True
            with open(cfg) as f:
                updated = yaml.safe_load(f)
            assert updated["bookings"][0]["holding_vehicle_type"] == "SUV"
            assert updated["bookings"][0]["holding_price"] == 375.23

    def test_updates_both_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with patch("subprocess.run"):
                result = apply_config_update(
                    {"holding_price": 299.0, "holding_vehicle_type": "Economy Car"}, cfg
                )
            assert result is True
            with open(cfg) as f:
                updated = yaml.safe_load(f)
            assert updated["bookings"][0]["holding_price"] == 299.0
            assert updated["bookings"][0]["holding_vehicle_type"] == "Economy Car"

    def test_noop_when_values_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with patch("subprocess.run") as mock_run:
                result = apply_config_update(
                    {"holding_price": 375.23, "holding_vehicle_type": "Standard Car"}, cfg
                )
            assert result is False
            mock_run.assert_not_called()

    def test_raises_on_missing_config(self):
        with pytest.raises(FileNotFoundError):
            apply_config_update({"holding_price": 400.0}, "/nonexistent/path/config.yaml")

    def test_git_commands_called_on_change(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with patch("subprocess.run") as mock_run:
                apply_config_update({"holding_price": 500.0}, cfg)
            calls = [c.args[0] for c in mock_run.call_args_list]
            assert any("git" in str(c) and "add" in str(c) for c in calls)
            assert any("git" in str(c) and "commit" in str(c) for c in calls)
            assert any("git" in str(c) and "push" in str(c) for c in calls)

    def test_update_by_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with patch("subprocess.run"):
                result = apply_config_update(
                    {"booking_identifier": "las_june", "holding_price": 250.0}, cfg
                )
            assert result is True
            with open(cfg) as f:
                updated = yaml.safe_load(f)
            # Second booking updated
            assert updated["bookings"][1]["holding_price"] == 250.0
            # First booking untouched
            assert updated["bookings"][0]["holding_price"] == 375.23

    def test_update_by_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with patch("subprocess.run"):
                result = apply_config_update(
                    {"booking_identifier": "2", "holding_price": 180.0}, cfg
                )
            assert result is True
            with open(cfg) as f:
                updated = yaml.safe_load(f)
            assert updated["bookings"][1]["holding_price"] == 180.0
            assert updated["bookings"][0]["holding_price"] == 375.23

    def test_update_by_index_1_is_first_booking(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with patch("subprocess.run"):
                apply_config_update(
                    {"booking_identifier": "1", "holding_vehicle_type": "Compact Car"}, cfg
                )
            with open(cfg) as f:
                updated = yaml.safe_load(f)
            assert updated["bookings"][0]["holding_vehicle_type"] == "Compact Car"
            assert updated["bookings"][1]["holding_vehicle_type"] == "Economy Car"

    def test_unknown_name_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with pytest.raises(ValueError, match="not found"):
                apply_config_update(
                    {"booking_identifier": "nonexistent", "holding_price": 100.0}, cfg
                )

    def test_out_of_range_index_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with pytest.raises(ValueError, match="out of range"):
                apply_config_update(
                    {"booking_identifier": "99", "holding_price": 100.0}, cfg
                )

    def test_zero_index_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Path(tmpdir) / "config.yaml"
            _write_sample_config(cfg)
            with pytest.raises(ValueError, match="out of range"):
                apply_config_update(
                    {"booking_identifier": "0", "holding_price": 100.0}, cfg
                )

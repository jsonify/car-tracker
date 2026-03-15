"""Tests for scripts/update_config.py — parse_config_update and apply_config_update."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from scripts.update_config import apply_config_update, parse_config_update


# ---------------------------------------------------------------------------
# parse_config_update tests
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

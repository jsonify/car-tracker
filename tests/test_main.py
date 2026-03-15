from __future__ import annotations

import pytest

from car_tracker.__main__ import parse_args


def test_defaults():
    args = parse_args([])
    assert args.debug is False
    assert args.config == "config.yaml"


def test_debug_flag():
    args = parse_args(["--debug"])
    assert args.debug is True


def test_custom_config():
    args = parse_args(["--config", "my_config.yaml"])
    assert args.config == "my_config.yaml"


def test_debug_and_config():
    args = parse_args(["--debug", "--config", "other.yaml"])
    assert args.debug is True
    assert args.config == "other.yaml"


def test_main_returns_zero(capsys):
    from car_tracker.__main__ import main

    result = main([])
    assert result == 0
    captured = capsys.readouterr()
    assert "config.yaml" in captured.out
    assert "False" in captured.out

"""Settings/alerts router — reads/writes alert preferences in config.yaml."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


def _config_path() -> Path:
    return Path(os.environ.get("CAR_TRACKER_CONFIG", "config.yaml"))


def _load_raw() -> dict:
    with open(_config_path()) as f:
        return yaml.safe_load(f) or {}


def _save_raw(raw: dict) -> None:
    with open(_config_path(), "w") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True)


class AlertConfig(BaseModel):
    booking_name: str
    alert_enabled: bool
    target_price: float | None
    email_notifications: bool


class AlertSettingsResponse(BaseModel):
    alerts: list[AlertConfig]


@router.get("/settings/alerts", response_model=AlertSettingsResponse)
def get_alert_settings() -> dict:
    raw = _load_raw()
    bookings = raw.get("bookings") or []
    alerts = []
    for b in bookings:
        alerts.append({
            "booking_name": b["name"],
            "alert_enabled": b.get("alert_enabled", False),
            "target_price": b.get("target_price"),
            "email_notifications": b.get("email_notifications", True),
        })
    return {"alerts": alerts}


@router.put("/settings/alerts", response_model=AlertSettingsResponse)
def update_alert_settings(settings: AlertSettingsResponse) -> dict:
    raw = _load_raw()
    bookings = raw.get("bookings") or []

    # Build lookup by booking name
    settings_map = {a.booking_name: a for a in settings.alerts}

    for b in bookings:
        if b["name"] in settings_map:
            alert = settings_map[b["name"]]
            b["alert_enabled"] = alert.alert_enabled
            b["target_price"] = alert.target_price
            b["email_notifications"] = alert.email_notifications

    raw["bookings"] = bookings
    _save_raw(raw)
    return get_alert_settings()

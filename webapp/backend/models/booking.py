"""Pydantic models for booking API requests and responses."""
from __future__ import annotations

from pydantic import BaseModel, field_validator
import re


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


class BookingBase(BaseModel):
    name: str
    pickup_location: str
    pickup_date: str  # YYYY-MM-DD
    pickup_time: str  # HH:MM
    dropoff_date: str  # YYYY-MM-DD
    dropoff_time: str  # HH:MM
    holding_price: float | None = None
    holding_vehicle_type: str | None = None
    city: str | None = None
    alert_enabled: bool = False
    target_price: float | None = None
    email_notifications: bool = True

    @field_validator("pickup_date", "dropoff_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        if not _DATE_RE.match(v):
            raise ValueError(f"Date must be YYYY-MM-DD, got: {v!r}")
        return v

    @field_validator("pickup_time", "dropoff_time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not _TIME_RE.match(v):
            raise ValueError(f"Time must be HH:MM, got: {v!r}")
        return v

    def model_post_init(self, __context: object) -> None:
        # Pair validation: both holding fields must be set or both None
        has_price = self.holding_price is not None
        has_type = self.holding_vehicle_type is not None
        if has_price != has_type:
            object.__setattr__(self, "holding_price", None)
            object.__setattr__(self, "holding_vehicle_type", None)


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BookingBase):
    pass


class BookingResponse(BookingBase):
    pass


# ---------------------------------------------------------------------------
# Date/time format helpers (UI ↔ storage)
# ---------------------------------------------------------------------------

def display_date_to_storage(d: str) -> str:
    """Convert MM/DD/YYYY → YYYY-MM-DD."""
    parts = d.split("/")
    if len(parts) != 3:
        raise ValueError(f"Expected MM/DD/YYYY, got: {d!r}")
    mm, dd, yyyy = parts
    return f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"


def storage_date_to_display(d: str) -> str:
    """Convert YYYY-MM-DD → MM/DD/YYYY."""
    parts = d.split("-")
    if len(parts) != 3:
        raise ValueError(f"Expected YYYY-MM-DD, got: {d!r}")
    yyyy, mm, dd = parts
    return f"{mm}/{dd}/{yyyy}"


def display_time_to_storage(t: str) -> str:
    """Convert 12h (10:00 AM) → HH:MM 24h."""
    t = t.strip()
    if "AM" in t.upper() or "PM" in t.upper():
        from datetime import datetime
        dt = datetime.strptime(t.upper(), "%I:%M %p")
        return dt.strftime("%H:%M")
    return t  # already 24h


def storage_time_to_display(t: str) -> str:
    """Convert HH:MM 24h → 12h (10:00 AM)."""
    from datetime import datetime
    dt = datetime.strptime(t, "%H:%M")
    return dt.strftime("%-I:%M %p")

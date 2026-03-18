"""Bookings CRUD router — reads/writes config.yaml bookings array."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException, Response

from webapp.backend.models.booking import BookingCreate, BookingResponse, BookingUpdate

router = APIRouter()

_DEFAULT_CONFIG = "config.yaml"


def _config_path() -> Path:
    return Path(os.environ.get("CAR_TRACKER_CONFIG", _DEFAULT_CONFIG))


def _load_raw() -> dict:
    with open(_config_path()) as f:
        return yaml.safe_load(f) or {}


def _save_raw(raw: dict) -> None:
    with open(_config_path(), "w") as f:
        yaml.dump(raw, f, default_flow_style=False, allow_unicode=True)


def _bookings_list(raw: dict) -> list[dict]:
    return raw.get("bookings") or []


@router.get("/", response_model=list[BookingResponse])
def get_bookings() -> list[dict]:
    raw = _load_raw()
    return _bookings_list(raw)


@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(booking: BookingCreate) -> dict:
    raw = _load_raw()
    bookings = _bookings_list(raw)
    if any(b["name"] == booking.name for b in bookings):
        raise HTTPException(status_code=409, detail=f"Booking '{booking.name}' already exists")
    bookings.append(booking.model_dump())
    raw["bookings"] = bookings
    _save_raw(raw)
    return booking.model_dump()


@router.put("/{booking_name}", response_model=BookingResponse)
def update_booking(booking_name: str, booking: BookingUpdate) -> dict:
    raw = _load_raw()
    bookings = _bookings_list(raw)
    idx = next((i for i, b in enumerate(bookings) if b["name"] == booking_name), None)
    if idx is None:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_name}' not found")
    bookings[idx] = booking.model_dump()
    raw["bookings"] = bookings
    _save_raw(raw)
    return booking.model_dump()


@router.delete("/{booking_name}", status_code=204)
def delete_booking(booking_name: str) -> Response:
    raw = _load_raw()
    bookings = _bookings_list(raw)
    new_bookings = [b for b in bookings if b["name"] != booking_name]
    if len(new_bookings) == len(bookings):
        raise HTTPException(status_code=404, detail=f"Booking '{booking_name}' not found")
    raw["bookings"] = new_bookings
    _save_raw(raw)
    return Response(status_code=204)

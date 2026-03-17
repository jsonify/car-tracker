"""Discord webhook notifications for car-tracker.

Sends rich embeds to a Discord channel via webhook URL.
No bot process required — webhooks are simple HTTPS POSTs.

Required env var:
    DISCORD_WEBHOOK_URL  — Discord webhook URL (from channel settings)
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from car_tracker.config import BookingConfig
from car_tracker.emailer import BookingSection

_ENV_PATH = Path("/Users/jasonrueckert/code/car-tracker/.env")

# Discord embed colors
_COLOR_GREEN = 0x2ECC71   # price drop / savings
_COLOR_RED = 0xE74C3C     # price increase
_COLOR_BLUE = 0x3498DB    # neutral / no prior data
_COLOR_ORANGE = 0xE67E22  # failure / warning


def load_webhook_url() -> str | None:
    """Load the Discord webhook URL from the .env file, or None if not configured."""
    load_dotenv(_ENV_PATH)
    return os.environ.get("DISCORD_WEBHOOK_URL") or None


def _fmt_price(price: float) -> str:
    return f"${price:,.2f}"


def _fmt_delta(delta: float | None, is_new: bool) -> str:
    if is_new:
        return "🆕 New"
    if delta is None:
        return "—"
    if delta < 0:
        return f"▼ ${abs(delta):.2f}"
    if delta > 0:
        return f"▲ ${delta:.2f}"
    return "—"


def _section_color(vehicles: list[dict]) -> int:
    """Pick embed color based on whether any prices dropped."""
    deltas = [v["delta"] for v in vehicles if v.get("delta") is not None]
    if not deltas:
        return _COLOR_BLUE
    if any(d < 0 for d in deltas):
        return _COLOR_GREEN
    if all(d >= 0 for d in deltas):
        return _COLOR_RED
    return _COLOR_BLUE


def build_success_embeds(sections: list[BookingSection], run_ts: str) -> list[dict]:
    """Build a list of Discord embed dicts for a successful scrape."""
    embeds = []
    for section in sections:
        booking = section.booking
        vehicles = section.vehicles
        holding = section.holding_summary

        color = _section_color(vehicles)

        # Build vehicle table as a code block
        lines = [f"{'Vehicle':<24} {'Price':>8}  {'$/day':>6}  {'Change':>10}"]
        lines.append("─" * 55)
        for v in vehicles:
            name = v["name"][:24]
            price = _fmt_price(v["total_price"])
            ppd = _fmt_price(v["price_per_day"])
            delta = _fmt_delta(v.get("delta"), v.get("is_new", False))
            lines.append(f"{name:<24} {price:>8}  {ppd:>6}  {delta:>10}")

        description = "```\n" + "\n".join(lines) + "\n```"

        # Holding summary field
        fields = []
        if holding:
            if holding["is_savings"]:
                holding_text = (
                    f"Current best: {_fmt_price(holding['best_price'])} vs "
                    f"your booking: {_fmt_price(holding['holding_price'])} "
                    f"— you'd save **{_fmt_price(holding['savings'])}** by rebooking!"
                )
            else:
                holding_text = (
                    f"Current best: {_fmt_price(holding['best_price'])} vs "
                    f"your booking: {_fmt_price(holding['holding_price'])} "
                    f"— keep your existing booking (saves {_fmt_price(holding['savings'])})."
                )
            fields.append({"name": "Holding Price", "value": holding_text, "inline": False})

        title = (
            f"🚗 {booking.pickup_location} · "
            f"{booking.pickup_date} → {booking.dropoff_date}"
        )

        embeds.append({
            "title": title,
            "description": description,
            "color": color,
            "fields": fields,
            "footer": {"text": f"Run at {run_ts} · {booking.name}"},
        })

    return embeds


def build_failure_embed(booking: BookingConfig, error_msg: str) -> dict:
    """Build a Discord embed dict for a scrape failure."""
    return {
        "title": f"❌ Scrape Failed — {booking.name}",
        "description": (
            f"**Location:** {booking.pickup_location}\n"
            f"**Dates:** {booking.pickup_date} → {booking.dropoff_date}\n\n"
            f"**Error:**\n```\n{error_msg[:1000]}\n```"
        ),
        "color": _COLOR_ORANGE,
    }


def send_webhook(webhook_url: str, embeds: list[dict]) -> None:
    """POST embeds to a Discord webhook URL."""
    payload = json.dumps({"embeds": embeds[:10]}).encode()  # Discord max 10 embeds
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status not in (200, 204):
            raise RuntimeError(f"Discord webhook returned HTTP {resp.status}")


def notify_success(sections: list[BookingSection], run_ts: str, webhook_url: str) -> None:
    """Send success embeds for all booking sections to Discord."""
    embeds = build_success_embeds(sections, run_ts)
    if embeds:
        send_webhook(webhook_url, embeds)


def notify_failure(booking: BookingConfig, error_msg: str, webhook_url: str) -> None:
    """Send a failure embed for a booking to Discord."""
    embed = build_failure_embed(booking, error_msg)
    send_webhook(webhook_url, [embed])

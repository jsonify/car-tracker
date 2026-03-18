from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass, field
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from car_tracker.config import BookingConfig
from car_tracker.database import VehicleRecord

_ENV_PATH = Path("/Users/jasonrueckert/code/car-tracker/.env")
_TEMPLATES_DIR = Path(__file__).parent / "templates"


@dataclass
class BookingSection:
    """Per-booking data bundle for email rendering."""
    booking: BookingConfig
    vehicles: list[dict]
    holding_summary: dict | None
    countdown_days: int = 0


@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    recipient_email: str


def days_until_booking(pickup_date: str, today: date) -> int:
    """Return the number of days until the pickup date.

    Args:
        pickup_date: ISO-format date string (YYYY-MM-DD).
        today:       The reference date (typically ``date.today()``).

    Returns:
        Positive int if pickup is in the future, 0 if today, negative if past.
    """
    return (date.fromisoformat(pickup_date) - today).days


def load_email_config() -> EmailConfig:
    """Load SMTP credentials from the shared .env file."""
    load_dotenv(_ENV_PATH)

    required = ["SMTP_SERVER", "SMTP_PORT", "SENDER_EMAIL", "SENDER_PASSWORD", "RECIPIENT_EMAIL"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise ValueError(f"Missing required email env vars: {', '.join(missing)}")

    return EmailConfig(
        smtp_server=os.environ["SMTP_SERVER"],
        smtp_port=int(os.environ["SMTP_PORT"]),
        sender_email=os.environ["SENDER_EMAIL"],
        sender_password=os.environ["SENDER_PASSWORD"],
        recipient_email=os.environ["RECIPIENT_EMAIL"],
    )


def extract_category(name: str) -> str:
    """Extract vehicle category from 'Category (Brand)' format.

    e.g. 'Economy Car (Alamo)' -> 'Economy Car'
    Names without a brand suffix are returned unchanged.
    """
    idx = name.find(" (")
    return name[:idx] if idx != -1 else name


def best_per_type(vehicles: list[dict]) -> list[dict]:
    """Collapse vehicles to one row per category, keeping the cheapest.

    Returns rows sorted by total_price ascending. The 'name' field is
    replaced with the extracted category (brand suffix stripped).
    """
    seen: dict[str, dict] = {}
    for v in vehicles:
        cat = extract_category(v["name"])
        if cat not in seen or v["total_price"] < seen[cat]["total_price"]:
            seen[cat] = {**v, "name": cat}
    return sorted(seen.values(), key=lambda r: r["total_price"])


def best_per_type_prices(vehicles: list[VehicleRecord]) -> dict[str, float]:
    """Return category → best (lowest) total_price mapping from a list of VehicleRecords."""
    result: dict[str, float] = {}
    for v in vehicles:
        cat = extract_category(v.name)
        if cat not in result or v.total_price < result[cat]:
            result[cat] = v.total_price
    return result


def build_delta(
    current: list[VehicleRecord],
    prior: dict[str, float],
) -> list[dict]:
    """Attach price delta information to each vehicle.

    Args:
        current: Vehicles from the current run.
        prior:   name → total_price mapping from the prior run.
                 Empty dict means no prior run exists.

    Returns:
        List of dicts with all VehicleRecord fields plus:
        - delta (float | None): current - prior price, or None
        - is_new (bool): True if prior run exists but this vehicle wasn't in it
    """
    has_prior = bool(prior)
    rows = []
    for v in current:
        if not has_prior:
            delta = None
            is_new = False
        elif v.name in prior:
            delta = round(v.total_price - prior[v.name], 2)
            is_new = False
        else:
            delta = None
            is_new = True

        rows.append({
            "position": v.position,
            "name": v.name,
            "total_price": v.total_price,
            "price_per_day": v.price_per_day,
            "delta": delta,
            "is_new": is_new,
        })
    return rows


def _jinja_env() -> Environment:
    return Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=True)


def build_holding_summary(
    vehicles: list[dict],
    holding_price: float | None,
    holding_vehicle_type: str | None = None,
) -> dict | None:
    """Compute holding price comparison summary.

    Both holding_price and holding_vehicle_type must be provided (pair rule).
    Returns None if either is missing, vehicles is empty, or no vehicles
    match the holding_vehicle_type.
    Returns a dict with holding_price, best_price, savings, is_savings.
    """
    if holding_price is None or holding_vehicle_type is None:
        return None
    matching = [v for v in vehicles if v["name"] == holding_vehicle_type]
    if not matching:
        return None
    best_price = round(min(v["total_price"] for v in matching), 2)
    savings = round(abs(holding_price - best_price), 2)
    return {
        "holding_price": holding_price,
        "best_price": best_price,
        "savings": savings,
        "is_savings": best_price < holding_price,
    }


def render_success(sections: list[BookingSection], run_ts: str) -> str:
    """Render the success HTML email body with one section per booking."""
    env = _jinja_env()
    tmpl = env.get_template("email_success.html")
    return tmpl.render(sections=sections, run_ts=run_ts)


def render_monitoring_paused() -> str:
    """Render the monitoring paused notification HTML email body."""
    env = _jinja_env()
    tmpl = env.get_template("email_monitoring_paused.html")
    return tmpl.render()


def render_failure(error_msg: str, booking: BookingConfig) -> str:
    """Render the failure HTML email body."""
    env = _jinja_env()
    tmpl = env.get_template("email_failure.html")
    return tmpl.render(error_msg=error_msg, booking=booking)


def send_email(subject: str, html_body: str, email_cfg: EmailConfig) -> None:  # pragma: no cover
    """Send an HTML email via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_cfg.sender_email
    msg["To"] = email_cfg.recipient_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(email_cfg.smtp_server, email_cfg.smtp_port) as server:
        server.starttls()
        server.login(email_cfg.sender_email, email_cfg.sender_password)
        server.sendmail(email_cfg.sender_email, email_cfg.recipient_email, msg.as_string())

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from car_tracker.config import load_config
from car_tracker.database import VehicleRecord, get_category_price_history, get_prior_run_vehicles, init_db, save_run, save_vehicles
from car_tracker.emailer import BookingSection, best_per_type, build_delta, build_holding_summary, build_subject, days_until_booking, load_email_config, render_failure, render_monitoring_paused, render_success, send_email
from car_tracker.lifecycle import remove_expired_bookings
from car_tracker.scraper import scrape
from car_tracker.state import read_app_state, write_app_state

_STATE_PATH = Path("data/imessage_state.json")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="car-tracker",
        description="Scrape Costco Travel rental car prices.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Run browser in headed (visible) mode for debugging.",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        metavar="PATH",
        help="Path to YAML config file (default: config.yaml).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = Path(args.config)
    today = date.today()

    # Expire bookings whose pickup_date has passed
    try:
        remove_expired_bookings(config_path, today)
    except FileNotFoundError:
        pass  # config doesn't exist — load_config below will surface the proper error

    # Load config (may now have fewer or zero bookings)
    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    # Handle empty bookings — monitoring paused
    if not config.bookings:
        state = read_app_state(_STATE_PATH)
        if not state.get("monitoring_paused_notified", False):
            try:
                email_cfg = load_email_config()
                html = render_monitoring_paused()
                send_email("Costco Travel — Monitoring Paused", html, email_cfg)
                print("Monitoring paused notification sent.")
            except Exception as exc:
                print(f"Failed to send monitoring paused email: {exc}", file=sys.stderr)
            state["monitoring_paused_notified"] = True
            write_app_state(_STATE_PATH, state)
        else:
            print("No active bookings. Monitoring paused (notification already sent).")
        return 0

    # Bookings exist — reset paused flag if it was previously set
    state = read_app_state(_STATE_PATH)
    if state.get("monitoring_paused_notified", False):
        state["monitoring_paused_notified"] = False
        write_app_state(_STATE_PATH, state)

    db_path = config.database.path
    init_db(db_path)

    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections: list[BookingSection] = []

    for booking in config.bookings:
        print(
            f"Scraping: {booking.name} | {booking.pickup_location} | "
            f"{booking.pickup_date} {booking.pickup_time} → "
            f"{booking.dropoff_date} {booking.dropoff_time}"
        )
        try:
            results = scrape(booking, debug=args.debug)
        except Exception as exc:
            print(f"Scrape failed for '{booking.name}': {exc}", file=sys.stderr)
            try:
                email_cfg = load_email_config()
                html = render_failure(str(exc), booking)
                subject = (
                    f"Costco Travel Scrape Failed — {booking.name} "
                    f"{booking.pickup_date} to {booking.dropoff_date}"
                )
                send_email(subject, html, email_cfg)
                print(f"Failure notification sent for '{booking.name}'.")
            except Exception as email_exc:
                print(
                    f"Also failed to send failure email for '{booking.name}': {email_exc}",
                    file=sys.stderr,
                )
            continue

        # Save run + vehicles
        run_id = save_run(
            db_path,
            pickup_location=booking.pickup_location,
            pickup_date=booking.pickup_date,
            pickup_time=booking.pickup_time,
            dropoff_date=booking.dropoff_date,
            dropoff_time=booking.dropoff_time,
            holding_price=booking.holding_price,
            holding_vehicle_type=booking.holding_vehicle_type,
            booking_name=booking.name,
        )
        vehicle_records = [
            VehicleRecord(
                position=v.position,
                name=f"{v.name} ({v.brand})",
                total_price=v.total_price,
                price_per_day=v.price_per_day,
            )
            for v in results
        ]
        save_vehicles(db_path, run_id, vehicle_records)

        prior = get_prior_run_vehicles(
            db_path, run_id,
            booking.pickup_location, booking.pickup_date, booking.dropoff_date,
            booking_name=booking.name,
        )

        type_rows = best_per_type(build_delta(vehicle_records, prior))
        holding_summary = build_holding_summary(
            type_rows, booking.holding_price, holding_vehicle_type=booking.holding_vehicle_type
        )
        countdown_days = days_until_booking(booking.pickup_date, today)
        price_history = get_category_price_history(db_path, booking.name)
        sections.append(BookingSection(
            booking=booking, vehicles=type_rows, holding_summary=holding_summary,
            countdown_days=countdown_days, price_history=price_history,
        ))
        print(f"Saved {len(results)} vehicles for '{booking.name}' (run_id={run_id})")

    if not sections:
        return 1

    # Send combined email for all successful bookings
    try:
        email_cfg = load_email_config()
        html = render_success(sections, run_ts)
        send_email(build_subject(sections), html, email_cfg)
        print(f"Email sent ({len(sections)} booking(s))")
    except Exception as email_exc:
        print(f"Failed to send email: {email_exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

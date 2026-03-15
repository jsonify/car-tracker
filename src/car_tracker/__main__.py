from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from car_tracker.config import load_config
from car_tracker.database import VehicleRecord, get_prior_run_vehicles, init_db, save_run, save_vehicles
from car_tracker.emailer import best_per_type, build_delta, build_holding_summary, extract_category, load_email_config, render_failure, render_success, send_email
from car_tracker.scraper import scrape


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

    # Load config
    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    db_path = config.database.path

    # Initialise DB (no-op if already exists)
    init_db(db_path)

    # Build email subject fragments
    s = config.search
    subject_base = f"{s.pickup_location} {s.pickup_date} to {s.dropoff_date}"

    # Run scraper
    print(
        f"Scraping: {s.pickup_location} | "
        f"{s.pickup_date} {s.pickup_time} → "
        f"{s.dropoff_date} {s.dropoff_time}"
    )
    try:
        results = scrape(config, debug=args.debug)
    except Exception as exc:
        print(f"Scrape failed: {exc}", file=sys.stderr)
        try:
            email_cfg = load_email_config()
            html = render_failure(str(exc), config)
            send_email(f"Costco Travel Scrape Failed — {subject_base}", html, email_cfg)
            print("Failure notification email sent.")
        except Exception as email_exc:
            print(f"Also failed to send failure email: {email_exc}", file=sys.stderr)
        return 1

    # Save run + vehicles
    run_id = save_run(
        db_path,
        pickup_location=s.pickup_location,
        pickup_date=s.pickup_date,
        pickup_time=s.pickup_time,
        dropoff_date=s.dropoff_date,
        dropoff_time=s.dropoff_time,
        holding_price=s.holding_price,
        holding_vehicle_type=s.holding_vehicle_type,
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

    # Collapse prior run vehicles to best-per-type (category → best price)
    prior_raw = get_prior_run_vehicles(db_path, run_id, s.pickup_location, s.pickup_date, s.dropoff_date)
    prior: dict[str, float] = {}
    for name, price in prior_raw.items():
        cat = extract_category(name)
        if cat not in prior or price < prior[cat]:
            prior[cat] = price

    # Collapse current vehicles to best-per-type before building delta and email
    type_rows = best_per_type(build_delta(vehicle_records, prior))
    holding_summary = build_holding_summary(type_rows, s.holding_price, holding_vehicle_type=s.holding_vehicle_type)
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        email_cfg = load_email_config()
        html = render_success(type_rows, config, run_ts, holding_summary=holding_summary)
        send_email(f"Costco Travel Rental Prices — {subject_base}", html, email_cfg)
        print(f"Email sent: {len(results)} vehicles (run_id={run_id})")
    except Exception as email_exc:
        print(f"Failed to send email: {email_exc}", file=sys.stderr)

    print(f"Saved {len(results)} vehicles to {db_path} (run_id={run_id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

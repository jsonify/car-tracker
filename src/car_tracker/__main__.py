from __future__ import annotations

import argparse
import sys

from car_tracker.config import load_config
from car_tracker.database import VehicleRecord, init_db, save_run, save_vehicles
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

    # Run scraper
    print(
        f"Scraping: {config.search.pickup_location} | "
        f"{config.search.pickup_date} {config.search.pickup_time} → "
        f"{config.search.dropoff_date} {config.search.dropoff_time}"
    )
    try:
        results = scrape(config, debug=args.debug)
    except Exception as exc:
        print(f"Scrape failed: {exc}", file=sys.stderr)
        return 1

    # Save run + vehicles
    run_id = save_run(
        db_path,
        pickup_location=config.search.pickup_location,
        pickup_date=config.search.pickup_date,
        pickup_time=config.search.pickup_time,
        dropoff_date=config.search.dropoff_date,
        dropoff_time=config.search.dropoff_time,
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

    print(f"Saved {len(results)} vehicles to {db_path} (run_id={run_id})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

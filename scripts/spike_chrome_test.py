#!/usr/bin/env python3
"""Diagnostic spike: verify the scraper can fetch real prices on this runner.

Usage: uv run python scripts/spike_chrome_test.py

No email, no database, no lifecycle calls.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Ensure the package is importable when run from repo root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from car_tracker.config import load_config
from car_tracker.scraper import scrape


def main() -> int:
    config = load_config("config.yaml")
    booking = config.bookings[0]
    print(f"Scraping booking: {booking.name!r}")

    try:
        results = scrape(booking, debug=False)
    except Exception as exc:
        print(f"\nSCRAPE FAILED: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1

    if not results:
        print("Scrape returned 0 results — possible bot-detection block.", file=sys.stderr)
        return 1

    print(f"\nSuccess: {len(results)} vehicle(s) returned.")
    for v in results[:3]:
        print(f"  [{v.position}] {v.name} — ${v.total_price:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

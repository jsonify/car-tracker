# Spec: Import Historical Price Data from CSV

## Overview
A one-time standalone script that reads `data/price_histories_rows.csv` and seeds the
SQLite database with historical scrape data for the `SAN_04022026_04082026_StandardCar`
booking, enabling price change comparison from day one of live runs.

## Functional Requirements
1. Read `data/price_histories_rows.csv`
2. Filter rows where `booking_id = "SAN_04022026_04082026_StandardCar"`
3. For each matching row:
   - Insert a `runs` record using `timestamp` as `run_at`, with:
     - `pickup_location = "SAN"`, `pickup_date = "2026-04-02"`, `pickup_time = "10:00"`
     - `dropoff_date = "2026-04-08"`, `dropoff_time = "10:00"`
     - `holding_price = None`, `holding_vehicle_type = None`
   - Parse the `prices` JSON column
   - Insert one `vehicles` record per category, with:
     - `name` = bare category name (e.g. `"Economy Car"`)
     - `total_price` = price value from JSON
     - `price_per_day` = `total_price / 6` (6-day rental: Apr 2–8)
     - `position` = rank by ascending `total_price` (1 = cheapest)
4. Script is idempotent — skip rows whose `timestamp` already exists as a `run_at` for matching search params
5. Print a summary: rows processed, runs inserted, runs skipped

## Non-Functional Requirements
- Script lives at `scripts/import_history.py`
- Reuses `database.py` functions where possible (`_connect`, `save_vehicles`, `init_db`)
- No new dependencies — uses only Python stdlib (`csv`, `json`) + existing project modules

## Acceptance Criteria
- Running the script populates `runs` and `vehicles` with historical StandardCar data
- Re-running the script produces no duplicate records
- Existing live runs are unaffected
- Summary output confirms counts

## Out of Scope
- Importing `FullsizeCar` records
- Integrating into the main app pipeline
- Any UI or config-driven behavior

# Plan: Import Historical Price Data from CSV

## Phase 1: Script Implementation

- [x] Task 1: Write tests for pure helper functions <!-- b8a6b03 -->
  - [x] Test `parse_prices(prices_json)` → sorted list of `(position, name, total_price, price_per_day)` with correct ranking and price_per_day = total/6
  - [x] Test idempotency check: `run_already_imported(db_path, run_at, pickup_location, pickup_date, dropoff_date)` returns True when duplicate exists, False otherwise

- [x] Task 2: Implement `scripts/import_history.py` <!-- b8a6b03 -->
  - [x] `parse_prices(prices_json: str) -> list[VehicleRecord]` — parse JSON, rank by ascending price, compute price_per_day
  - [x] `run_already_imported(db_path, run_at, pickup_location, pickup_date, dropoff_date) -> bool` — query runs table for matching record
  - [x] `import_csv(csv_path, db_path)` — main loop: filter by booking_id, call idempotency check, insert run + vehicles, accumulate counts
  - [x] `if __name__ == "__main__"` entrypoint with hardcoded paths (`data/price_histories_rows.csv`, `data/results.db`)
  - [x] Print summary: `Processed N rows → X runs inserted, Y skipped`

- [x] Task 3: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

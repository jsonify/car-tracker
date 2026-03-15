# spec.md — Vehicle Type Holding Price & Best-Per-Type Email Table

## Overview
Extend the holding price feature to associate a vehicle type with the booking,
so savings comparisons are made against the same vehicle category. Additionally,
collapse the email results table to show only the single best (cheapest) price
per vehicle type, reducing noise and improving scannability.

## Functional Requirements

### Config
- Add optional `holding_vehicle_type` field (string) to `config.yaml` under `search`:
  ```yaml
  search:
    holding_price: 396.63
    holding_vehicle_type: "Economy Car"
  ```
- `holding_price` and `holding_vehicle_type` are treated as a pair:
  - Both present → summary shown, compares against that vehicle type's best price
  - Either missing → no summary shown (config remains valid, no error)

### Vehicle Category Extraction
- Extract the category from a vehicle name using the existing "Category (Brand)" format.
  - e.g. `"Economy Car (Alamo)"` → category `"Economy Car"`
- New pure function: `extract_category(name: str) -> str`
- Edge case: name with no `(` returns name unchanged

### Best-Per-Type Reduction
- New pure function: `best_per_type(vehicles: list[dict]) -> list[dict]`
  - Groups vehicles by extracted category
  - Retains the single row with the lowest `total_price` per category
  - Result is sorted by `total_price` ascending (cheapest category first)
  - The `#` position column is dropped (position no longer meaningful at type level)

### Delta (Change Column)
- The `build_delta` function is applied AFTER `best_per_type` reduction.
- A new helper `best_per_type_prices(vehicles: list[VehicleRecord]) -> dict[str, float]`
  returns `category → best total_price` mapping, used as the prior-run lookup
  (keyed by category instead of full vehicle name).
- Delta = best price of that type this run − best price of that type from prior run.

### Database
- Add `holding_vehicle_type` column (TEXT, nullable) to the `runs` table via migration.
- Populated from config alongside `holding_price` in `save_run`.
- Keeps the historical record complete: price + vehicle type together per run.

### Holding Price Summary
- When both `holding_price` and `holding_vehicle_type` are configured:
  - `best_price` = lowest `total_price` among rows whose extracted category matches
    `holding_vehicle_type`
  - If no vehicles of that type are found in the current run, omit the summary
- When either is missing: no summary shown
- Display in email (unchanged wording):
  - Savings: `Your holding price: $X · Best current price: $Y · Savings: $Z`
  - No savings: `Your holding price: $X · Best current price: $Y · You're ahead by $Z — keep your booking`

### Email Table
- Table shows one row per vehicle type (post `best_per_type` reduction)
- Remove the `#` column; columns: Vehicle Type | Total | Per Day | Change
- "Vehicle Type" cell shows the category name only, e.g. "Economy Car" (brand dropped)

## Non-Functional Requirements
- All new pure functions are unit-tested (≥ 80% coverage maintained)
- Backward compatible: existing configs without holding fields continue to work

## Acceptance Criteria
- [ ] `config.yaml` accepts optional `holding_vehicle_type`
- [ ] `SearchConfig` stores `holding_vehicle_type: str | None`
- [ ] Both fields treated as a pair — one without the other → no summary
- [ ] `extract_category("Economy Car (Alamo)")` returns `"Economy Car"`
- [ ] `best_per_type` returns one row per category, cheapest wins, sorted by price
- [ ] `best_per_type_prices` returns category → best price mapping
- [ ] Email table shows one row per vehicle type, no `#` column
- [ ] Change column shows best-per-type delta vs. prior run's best-per-type
- [ ] Holding summary compares against the configured vehicle type's best price
- [ ] `holding_vehicle_type` stored in `runs` table via DB migration
- [ ] All new logic unit-tested

## Out of Scope
- Tracking multiple holding bookings
- Historical chart of holding price vs. market price over time
- Showing individual brand rows alongside the collapsed type row

# spec.md — Holding Price Comparison

## Overview
Add a "holding price" concept — the total price of the car rental booking already
made. On each run, compare the current best available price against the holding price
and surface the result prominently at the top of the email.

## Functional Requirements

### Config
- Add optional `holding_price` field to `config.yaml` under `search`:
  ```yaml
  search:
    pickup_location: "LAX"
    pickup_date: "2026-04-01"
    pickup_time: "10:00"
    dropoff_date: "2026-04-05"
    dropoff_time: "10:00"
    holding_price: 396.63   # total price of current booking
  ```
- Field is optional — if omitted, no holding price comparison is shown

### Database
- Add `holding_price` column (REAL, nullable) to the `runs` table
- Populated from config on each `save_run` call

### Email — Summary Line
Appears directly above the results table.

**When savings exist (current best < holding price):**
> Your holding price: $396.63 · Best current price: $371.00 · **Savings: $25.63**

**When no savings (current best ≥ holding price):**
> Your holding price: $396.63 · Best current price: $420.00 · You're ahead by $23.37 — keep your booking

**When no holding price configured:**
> (summary line omitted entirely)

### Best Current Price
- The lowest `total_price` among all scraped vehicles in the current run

## Non-Functional Requirements
- `holding_price` config field is optional with no default — existing configs remain valid
- All comparison logic is pure and unit-tested
- DB migration: `ALTER TABLE runs ADD COLUMN holding_price REAL` runs safely on
  existing databases (SQLite allows adding nullable columns)

## Acceptance Criteria
- [ ] `config.yaml` accepts optional `holding_price`
- [ ] `save_run` stores holding price (or NULL) in the runs table
- [ ] Email shows correct summary line when holding price is set
- [ ] Email shows "keep your booking" message when current best ≥ holding price
- [ ] Email omits summary line when no holding price configured
- [ ] All comparison logic unit-tested
- [ ] Existing DB upgraded cleanly via ALTER TABLE migration

## Out of Scope
- Tracking multiple bookings / multiple holding prices
- Alerting only when savings exceed a threshold
- Historical chart of holding price vs. market price over time

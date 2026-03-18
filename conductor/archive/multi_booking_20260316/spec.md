# Spec: Multiple Bookings Support

## Overview
Extend the car tracker to support multiple rental car bookings in a single run.
Each booking has its own search parameters (location, dates, times) and optional
holding price. Results are stored in a shared database and delivered in one
combined email with a section per booking.

## Functional Requirements

### Config
- `config.yaml` gains a top-level `bookings:` list replacing the single search
  parameter block
- Each booking entry includes:
  - `name` (string, unique label e.g. "hawaii", "vegas")
  - `location`, `pickup_date`, `pickup_time`, `dropoff_date`, `dropoff_time`
  - Optional `holding_price` + `holding_vehicle_type` pair
- Existing email/schedule settings remain at the top level (shared across bookings)

### Scraping
- The scraper iterates over all bookings in order, running a full search per booking
- Each booking's results are saved to the shared DB tagged with `booking_name`

### Database
- `runs` table gains a `booking_name` TEXT column (NOT NULL)
- `vehicles` table references `runs`, so booking context is inherited via the join
- Migration: add `booking_name` to `runs` (idempotent `ALTER TABLE` pattern)
- Prior-run lookups are scoped by `booking_name`

### Email
- Single combined HTML email per scheduled run
- One section per booking, in config list order
- Each section shows: booking name/label, best-per-type price table, price deltas,
  holding price comparison (if configured)

### iMessage Config Updates
- Command format supports both name and index:
  - By name: `update holding <booking_name> <price> <vehicle_type>`
    e.g. `update holding hawaii 450.00 Economy Car`
  - By index (1-based): `update holding <N> <price> <vehicle_type>`
    e.g. `update holding 1 450.00 Economy Car`
- Updates the correct booking entry's `holding_price` + `holding_vehicle_type`
  in `config.yaml`

## Non-Functional Requirements
- Backward compatibility: a config with no `bookings:` key (old format) should
  produce a clear `ConfigError` with a migration hint
- DB migration is idempotent and runs automatically on next scraper invocation

## Acceptance Criteria
- [ ] `config.yaml` supports a `bookings:` list with 2+ entries
- [ ] Scraper runs all bookings sequentially and saves results tagged by booking name
- [ ] DB migration adds `booking_name` to `runs` without breaking existing data
- [ ] Email contains one section per booking with correct data per booking
- [ ] iMessage `update holding` works by both name and 1-based index
- [ ] Old single-booking config format produces a clear error
- [ ] Tests cover: config loading, DB migration, per-booking delta, iMessage parsing

## Out of Scope
- Parallel scraping of multiple bookings simultaneously
- Per-booking email recipients or schedules
- Web UI for managing bookings

# Track Learnings: email_delivery_20260314

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- Vehicle name stored as "Category (Brand)" e.g. "Economy Car (Alamo)"
- Date format in config/DB: YYYY-MM-DD; form needs MM/DD/YYYY conversion
- Time format in config: HH:MM (24h); form needs 12h ("10:00 AM") conversion
- Chrome subprocess launched with `--remote-debugging-port=9222 --user-data-dir=...`
- Playwright connects via `connect_over_cdp("http://127.0.0.1:9222")`
- Pipeline: load_config → init_db → scrape → save_run → save_vehicles
- **Akamai bot detection:** Costco Travel blocks Playwright's bundled Chromium. Always use real Chrome via CDP.
- **`--remote-debugging-port` requires `--user-data-dir`** — Chrome will refuse to start without it.
- **jQuery datepicker blocks UI:** Set date fields via JS (`$(el).datepicker('setDate', val)`), never by clicking the field.
- **Autocomplete timing:** Type slowly (120-280ms/char), wait 2.5-3.5s before clicking suggestion.
- **SQLite FK enforcement:** Must run `PRAGMA foreign_keys = ON` per connection.
- Browser automation methods marked `# pragma: no cover` — they're integration-only
- Unit tests cover all pure logic: time conversion, date math, config validation, DB operations
- Mock `scrape()` in `__main__` tests to avoid live browser dependency

---

<!-- Learnings from implementation will be appended below -->

## [2026-03-14] - Phase 1 Task 1-2: get_prior_run_vehicles
- **Implemented:** DB function to find most recent prior run with matching pickup_location/pickup_date/dropoff_date
- **Files changed:** src/car_tracker/database.py, tests/test_database.py
- **Commit:** 82b9106
- **Learnings:**
  - Patterns: Use `id < current_run_id ORDER BY id DESC LIMIT 1` — simpler and correct since IDs are monotonically increasing
  - Gotchas: dropoff_time intentionally excluded from prior run lookup (we only care about same trip dates/location)
---

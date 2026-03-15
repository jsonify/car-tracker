# Codebase Patterns

Reusable patterns discovered during development. Read this before starting new work.

## Code Conventions
- Vehicle name stored as "Category (Brand)" e.g. "Economy Car (Alamo)"
- Date format in config/DB: YYYY-MM-DD; form needs MM/DD/YYYY conversion
- Time format in config: HH:MM (24h); form needs 12h ("10:00 AM") conversion

## Architecture
- Chrome subprocess launched with `--remote-debugging-port=9222 --user-data-dir=...`
- Playwright connects via `connect_over_cdp("http://127.0.0.1:9222")`
- Pipeline: load_config → init_db → scrape → save_run → save_vehicles

## Gotchas
- **Akamai bot detection:** Costco Travel blocks Playwright's bundled Chromium. Always use real Chrome via CDP.
- **`--remote-debugging-port` requires `--user-data-dir`** — Chrome will refuse to start without it.
- **jQuery datepicker blocks UI:** Set date fields via JS (`$(el).datepicker('setDate', val)`), never by clicking the field — the calendar popup covers other fields.
- **Autocomplete timing:** Type slowly (120-280ms/char), wait 2.5-3.5s before clicking suggestion.
- **SQLite FK enforcement:** Must run `PRAGMA foreign_keys = ON` per connection.

## Architecture
- Pipeline (full): load_config → init_db → scrape → save_run → save_vehicles → get_prior_run_vehicles → build_delta → render_success → send_email
- Email credentials loaded from `/Users/Jason/code/rental-car-pricer/.env` via `python-dotenv` — never stored in `config.yaml` or any tracked file (from: email_delivery_20260314)

## Testing
- Browser automation methods marked `# pragma: no cover` — they're integration-only
- I/O-only functions (e.g. `send_email`) also marked `# pragma: no cover` — same rationale (from: email_delivery_20260314)
- Unit tests cover all pure logic: time conversion, date math, config validation, DB operations
- Mock `scrape()` in `__main__` tests to avoid live browser dependency
- Mock `load_dotenv` in tests to prevent reads from the real `.env` file (from: email_delivery_20260314)

## Database Migrations
- SQLite `ALTER TABLE ... ADD COLUMN` wrapped in `try/except OperationalError` is idempotent — safe pattern for adding nullable columns to existing DBs (from: holding_price_20260315)
- `migrate_db()` is called from `init_db()` — existing DBs auto-upgrade on next run with no manual step required (from: holding_price_20260315)
- Comment each migration block with `# v2:`, `# v3:` etc. for traceability (from: type_holding_email_20260314)

## Config Patterns
- Pair validation: two optional fields that must both be present — if one is missing, set both to None in `load_config` before constructing the dataclass (from: type_holding_email_20260314)

## Email / Data Pipeline
- `extract_category(name)` uses `str.find(" (")` — returns -1 when no brand suffix present, cleanly handles both "Economy Car (Alamo)" and bare "Economy Car" formats (from: type_holding_email_20260314)
- `get_prior_run_vehicles` returns full names ("Economy Car (Alamo)") — collapse with `extract_category` before using as a category-keyed delta lookup; `best_per_type_prices` works on VehicleRecords, so inline collapse is simpler for the prior dict (from: type_holding_email_20260314)
- Pipeline (full): load_config → init_db → scrape → save_run → save_vehicles → get_prior_run_vehicles → collapse_prior_to_category → best_per_type(build_delta(...)) → build_holding_summary → render_success → send_email (from: type_holding_email_20260314)

---
Last refreshed: 2026-03-14 (from: type_holding_email_20260314)

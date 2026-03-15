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

---
Last refreshed: 2026-03-15 (from: email_delivery_20260314)

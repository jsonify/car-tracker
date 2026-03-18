# Codebase Patterns

Reusable patterns discovered during development. Read this before starting new work.

## Code Conventions
- Vehicle name stored as clean category only e.g. "Economy Car"; brand stored separately in `vehicles.brand` column (formerly "Category (Brand)" — fixed in db_brand_cleanup_20260318)
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

## Scripts / Standalone Tools
- Add `pythonpath = ["."]` to `[tool.pytest.ini_options]` in `pyproject.toml` to make `scripts/` importable in tests (from: import_history_20260315)
- `scripts/` directory needs `__init__.py` to be importable as a package in tests (from: import_history_20260315)
- Always import from `car_tracker.*` (installed package via uv), never `src.car_tracker.*` — the latter only works with pytest's pythonpath, not when running scripts directly (from: import_history_20260315)

## Shell Scripts / Cron
- **`timeout` is GNU coreutils — not on macOS.** Never use `timeout` in shell scripts intended for macOS; git fails fast on its own when the network is down. (from: remote_config_20260315)
- **Use `git pull --rebase` in cron wrappers**, not `--ff-only`. `--ff-only` aborts when local commits exist; `--rebase` handles diverged branches cleanly. (from: remote_config_20260315)
- **Push all local commits before the first cron run** when the cron job does a `git pull`. Otherwise local/remote diverge and the pull fails. In steady-state the scraper never commits, so future pulls always fast-forward. (from: remote_config_20260315)

## iMessage / Config Command Dispatch
- `parse_config_update` returns a dict; `apply_config_update` dispatches on its keys — the standard pattern for adding new iMessage command types: parse returns `{"action": "..."}`, apply branches on `action`. (from: imessage_booking_mgmt_20260316, archived 2026-03-17)
- Booking identifier resolved by name or 1-based index via `_resolve_booking()` — pass the second token from the command, try name match first, then `int(token) - 1` index. Raise `ValueError` with a clear message on no match. (from: multi_booking_20260316, archived 2026-03-17)

## iMessage Integration
- **`attributedBody` TypedStream fallback:** macOS Ventura+ stores message content in `attributedBody` when `text` is NULL. Extract with `re.findall(rb"[ -~]+", blob)`, skip known TypedStream metadata tokens (see `_STREAMTYPED_METADATA` frozenset in `scripts/check_imessage.py`). (from: imessage_config_20260315)
- **iMessage state tracking:** Use `data/imessage_state.json` with a `last_rowid` key to track the highest processed `rowid` from `chat.db`. Safe to reset to `0` to reprocess all messages. Connect read-only: `sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)`. (from: imessage_config_20260315)
- **osascript service lookup:** Use `of (first service whose service type is iMessage)` — NOT `of service "SMS"`. The hardcoded `"SMS"` service name returns `-10002 Invalid key form` on macOS. (from: imessage_booking_mgmt_20260316)
- **Phone number format:** osascript requires E.164 format with country code: `+15039990921`, not `5039990921`. (from: imessage_booking_mgmt_20260316)

## State Management
- **JSON state merging:** `{**DEFAULTS, **data}` in state readers safely adds new keys to an existing state file without overwriting prior values — new consumers get their defaults, existing keys are preserved. (from: booking_lifecycle_20260317)
- **Pre-step mutation before config load:** Call mutating operations (e.g. expiration, git ops) that modify the config file BEFORE calling `load_config`, so the loaded config reflects current reality. Wrap in `try/except FileNotFoundError: pass` — `load_config` surfaces the proper user-facing error for a truly missing file. (from: booking_lifecycle_20260317)
- **State file path:** `data/imessage_state.json` is shared between `scripts/check_imessage.py` (manages `last_rowid`) and `__main__.py` (manages `monitoring_paused_notified`) — both use `read_app_state`/`write_app_state` from `car_tracker.state` to merge-read and full-write so neither clobbers the other's key. (from: booking_lifecycle_20260317)

## Email / Jinja2
- **Expose Python functions to Jinja2 templates via `env.globals["fn_name"] = fn` in `_jinja_env()`** — avoids threading extra context through every render call; use `| safe` filter in the template when the function returns raw HTML/SVG. (from: email_enhancements_20260318)

## Circular Import Avoidance
- **Deferred import inside function body to break circular imports** — if `database.py` needs a helper from `emailer.py` (e.g. `extract_category`), import it inside the function rather than at module level to prevent circular import errors. (from: email_enhancements_20260318)

## Testing
- **Assert `<tr class="cls-name"` not `"cls-name" not in html`** — CSS class names defined in a `<style>` block appear in the full HTML string; asserting the class name is absent will always fail. Target actual element usage with the full attribute string. (from: email_enhancements_20260318)
- **New `__main__` DB functions need their own mock in `test_main.py`** — `init_db` is mocked in unit tests so no tables exist; any new DB function called in the booking loop must also be patched (e.g. `patch("car_tracker.__main__.get_category_price_history", return_value={})`). (from: email_enhancements_20260318)

## Database Migrations (continued)
- **Migration UPDATE idempotency via pattern match:** UPDATE rows WHERE name LIKE '% (%)' is self-limiting — once cleaned, rows no longer match the pattern on re-run. No explicit "already migrated" flag needed. (from: db_brand_cleanup_20260318)
- **`extract_category` in `get_category_price_history` is a safety net:** Now that names are stored clean, the call is redundant for new data but protects against any legacy rows that survived migration. Keep it. (from: db_brand_cleanup_20260318)

## Testing
- **Seed pre-migration data with raw SQL:** When testing DB migrations, bypass `save_vehicles` and insert dirty rows directly via `sqlite3.connect` to simulate data written before the migration existed. (from: db_brand_cleanup_20260318)

---
Last refreshed: 2026-03-18 (from: db_brand_cleanup_20260318)

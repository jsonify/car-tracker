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

## FastAPI / Backend Patterns
- **Shared uv venv for webapp backend:** Add `fastapi` and `uvicorn[standard]` to root `pyproject.toml`; the backend imports `car_tracker.*` directly without packaging complexity. (from: react_webapp_20260318)
- **FastAPI TestClient requires `httpx`:** Add `httpx>=0.28` to dev dependencies — it's a peer dep for `starlette.testclient`. (from: react_webapp_20260318)
- **Test isolation via env var:** Use a `CAR_TRACKER_CONFIG` env var (read via `os.getenv()`) in routers that read config files; set it in tests via `monkeypatch.setenv` to point to a tmp fixture file. (from: react_webapp_20260318)
- **SQL sort column whitelist:** Build a `_SORT_COLS: frozenset` and check before interpolating into f-string SQL — prevents injection without parameterized column names. (from: react_webapp_20260318)

## React / Frontend Patterns
- **Tailwind v4 setup:** `@import "tailwindcss"` in `index.css` + `@tailwindcss/vite` plugin in `vite.config.ts` — no `tailwind.config.js` needed. (from: react_webapp_20260318)
- **Loading/error/empty guard pattern:** All pages follow `if (loading) return <LoadingSpinner>; if (error) return <div className="text-red-400">; if (!data || data.length === 0) return <EmptyState>` before rendering content. (from: react_webapp_20260318)
- **NavLink active state:** Use `className={({ isActive }) => isActive ? 'active-class' : 'base-class'}` for sidebar nav links. (from: react_webapp_20260318)
- **Test selector specificity:** When multiple elements share the same text (nav link + page h1), use `getByRole('link', { name: /text/i })` or `getByRole('heading')` instead of `getByText`. (from: react_webapp_20260318)
- **Pure utility modules for testability:** Extract all business logic into side-effect-free utility modules (countdown, volatility, chartData, tableUtils) — they're easily unit-tested without DOM setup. (from: react_webapp_20260318)
- **Recharts responsive chart:** Wrap `<LineChart>` in `<ResponsiveContainer width="100%" height={300}>`. Use `<ReferenceLine y={holdingPrice}>` for horizontal threshold lines. (from: react_webapp_20260318)
- **Deterministic date formatting in tests:** Use `toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' })` — the `timeZone: 'UTC'` makes output identical in all CI/local environments regardless of host timezone. (from: history_charts_20260401)
- **Recharts floating range bar (stacked):** Create a min-to-max bar with two `<Bar stackId="r">`: first bar renders the invisible base (fill transparent), second bar renders the colored range (`max - min`). Tooltip: return `[null, null]` to suppress the base bar's tooltip entry. (from: history_charts_20260401)
- **Recharts per-bar conditional coloring:** Use `<Cell>` inside `<Bar>` to apply per-entry fill: `{data.map((entry, i) => <Cell key={i} fill={entry.delta < 0 ? green : red} />)}`. (from: history_charts_20260401)
- **Mock chart components in page tests:** In page-level tests, mock all Recharts chart components as simple `() => <div data-testid="..." />` — assertions become trivial and don't rely on Recharts internals or jsdom canvas limitations. (from: history_charts_20260401)
- **`getAllByText` for table cell duplicates:** When a value appears in both a data column and a summary/Latest column, `getByText` throws "found multiple elements". Use `getAllByText(val).length >= 1` or `getAllByText(val)[0]` instead. (from: history_charts_20260401)

## Startup Scripts
- **Parallel process startup with cleanup:** Use `trap cleanup EXIT INT TERM` + background `&` + store PIDs + `wait` for clean concurrent server launch in shell scripts. Run backend from project root via `uv run uvicorn webapp.backend.main:app`. (from: react_webapp_20260318)

## Jinja2 / Email Templates
- **Removing a Jinja2 global function: audit template tests too.** Stale test assertions on rendered output (e.g. `assert "Trend" in html`, sparkline SVG checks) won't fail on import but will fail at runtime or silently pass after the feature is gone — find and delete them when deleting the function. (from: fix_change_trend_20260321)
- **Unused `field` import after dataclass cleanup:** When removing the only `field(default_factory=...)` usage in a dataclass, also remove `field` from the `from dataclasses import dataclass, field` import line to avoid an unused-import warning. (from: fix_change_trend_20260321)

---
Last refreshed: 2026-04-01 (from: history_charts_20260401)

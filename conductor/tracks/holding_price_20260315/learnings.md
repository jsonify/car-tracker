# Track Learnings: holding_price_20260315

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- Vehicle name stored as "Category (Brand)" e.g. "Economy Car (Alamo)"
- Date format in config/DB: YYYY-MM-DD; form needs MM/DD/YYYY conversion
- Time format in config: HH:MM (24h); form needs 12h ("10:00 AM") conversion
- Chrome subprocess launched with `--remote-debugging-port=9222 --user-data-dir=...`
- Playwright connects via `connect_over_cdp("http://127.0.0.1:9222")`
- Pipeline (full): load_config → init_db → scrape → save_run → save_vehicles → get_prior_run_vehicles → build_delta → render_success → send_email
- **Akamai bot detection:** Costco Travel blocks Playwright's bundled Chromium. Always use real Chrome via CDP.
- **SQLite FK enforcement:** Must run `PRAGMA foreign_keys = ON` per connection.
- Email credentials loaded from `/Users/Jason/code/rental-car-pricer/.env` via `python-dotenv` — never stored in `config.yaml`
- I/O-only functions (e.g. `send_email`) marked `# pragma: no cover`
- Mock `load_dotenv` in tests to prevent reads from the real `.env` file

---

<!-- Learnings from implementation will be appended below -->

## [2026-03-15] - Phase 1-3: Holding Price Comparison
- **Implemented:** optional holding_price in config+DB, build_holding_summary, email summary banner, wired into pipeline
- **Files changed:** config.py, database.py, emailer.py, templates/email_success.html, __main__.py + all tests
- **Commit:** 534cab9
- **Learnings:**
  - Patterns: SQLite `ALTER TABLE ... ADD COLUMN` is idempotent via try/except OperationalError — safe migration pattern
  - Patterns: `migrate_db()` called from `init_db()` so existing DBs auto-upgrade on next run — no manual migration step needed
  - Gotchas: `build_holding_summary` returns None for empty vehicles list — guard against division/min errors
---

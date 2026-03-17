# Track Learnings: multi_booking_20260316

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- Vehicle name stored as "Category (Brand)" e.g. "Economy Car (Alamo)"
- Date format in config/DB: YYYY-MM-DD; form needs MM/DD/YYYY conversion
- Time format in config: HH:MM (24h); form needs 12h ("10:00 AM") conversion
- Chrome subprocess launched with `--remote-debugging-port=9222 --user-data-dir=...`
- Playwright connects via `connect_over_cdp("http://127.0.0.1:9222")`
- SQLite FK enforcement: must run `PRAGMA foreign_keys = ON` per connection
- SQLite `ALTER TABLE ... ADD COLUMN` wrapped in `try/except OperationalError` is idempotent — safe pattern for adding nullable columns to existing DBs
- `migrate_db()` is called from `init_db()` — existing DBs auto-upgrade on next run
- Comment each migration block with `# v2:`, `# v3:` etc. for traceability (next is `# v4:`)
- Pair validation: two optional fields that must both be present — if one is missing, set both to None in `load_config` before constructing the dataclass
- `extract_category(name)` uses `str.find(" (")` — handles both "Economy Car (Alamo)" and bare "Economy Car"
- Browser automation methods marked `# pragma: no cover`
- I/O-only functions (e.g. `send_email`) also marked `# pragma: no cover`
- Mock `scrape()` in `__main__` tests to avoid live browser dependency
- Always import from `car_tracker.*` (installed package via uv), never `src.car_tracker.*`

---

<!-- Learnings from implementation will be appended below -->

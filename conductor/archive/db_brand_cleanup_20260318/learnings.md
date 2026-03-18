# Track Learnings: db_brand_cleanup_20260318

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- SQLite `ALTER TABLE ... ADD COLUMN` wrapped in `try/except OperationalError` is idempotent — safe pattern for adding nullable columns to existing DBs.
- `migrate_db()` is called from `init_db()` — existing DBs auto-upgrade on next run with no manual step required.
- Comment each migration block with `# v2:`, `# v3:` etc. for traceability.
- Vehicle name stored as "Category (Brand)" e.g. "Economy Car (Alamo)" — this track removes that convention.
- `extract_category(name)` uses `str.find(" (")` — already handles both formats cleanly.

---

<!-- Learnings from implementation will be appended below -->

## [2026-03-18] - Phase 1 Task 1+2: Schema Migration + Tests
- **Implemented:** v5 migration — adds `brand TEXT` column to vehicles table, backfills by splitting "Category (Brand)" rows into separate name/brand values
- **Files changed:** src/car_tracker/database.py, tests/test_database.py
- **Commit:** 68c3a7b
- **Learnings:**
  - Patterns: Migration runs UPDATE for all rows LIKE '% (%)' — idempotent because cleaned rows no longer match the pattern on re-run
  - Gotchas: `init_db` must be called to trigger migration on an existing DB; running `python -c "from car_tracker.database import init_db; init_db('data/results.db')"` applies it manually
  - Context: Test helper `_seed_dirty_vehicle` needed to bypass `save_vehicles` for seeding pre-migration data in tests

---

## [2026-03-18] - Phase 2 Tasks 1-4: Write Layer Guard
- **Implemented:** VehicleRecord.brand field; save_vehicles inserts brand column; __main__ stores name/brand separately
- **Files changed:** src/car_tracker/database.py, src/car_tracker/__main__.py, tests/test_main.py
- **Commit:** b0402d4
- **Learnings:**
  - Patterns: Scraper already had name/brand as separate fields on VehicleResult — the bug was purely in the __main__ write call combining them
  - Gotchas: Existing test asserting `records[0].name == "Economy Car (Alamo)"` needed updating to assert clean name + brand separately
  - Context: `get_category_price_history` used `extract_category` to strip brands from names — now redundant for new data but still needed for any legacy rows missed by migration

---

# Track Learnings: import_history_20260315

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- Vehicle name stored as "Category (Brand)" e.g. "Economy Car (Alamo)" — but CSV has bare names; import uses bare names intentionally
- Date format in config/DB: YYYY-MM-DD
- Time format in config: HH:MM (24h)
- SQLite FK enforcement: Must run `PRAGMA foreign_keys = ON` per connection
- `migrate_db()` is called from `init_db()` — existing DBs auto-upgrade on next run
- Pipeline: load_config → init_db → scrape → save_run → save_vehicles

---

<!-- Learnings from implementation will be appended below -->

## [2026-03-15] - Phase 1 Tasks 1 & 2: Tests + Script Implementation
- **Implemented:** parse_prices(), run_already_imported(), import_csv() + 19 tests
- **Files changed:** scripts/__init__.py, scripts/import_history.py, tests/test_import_history.py, pyproject.toml
- **Commit:** b8a6b03
- **Learnings:**
  - Patterns: Add `pythonpath = ["."]` to `[tool.pytest.ini_options]` in pyproject.toml to import from `scripts/` package in tests
  - Patterns: `scripts/` directory needs `__init__.py` to be importable as a package
  - Patterns: Mark `if __name__ == "__main__"` blocks with `# pragma: no cover` — consistent with I/O-only pattern in codebase
  - Gotchas: CSV `prices` column uses escaped JSON double-quotes (`""`) from Postgres — Python's `json.loads()` handles this transparently when read via `csv.DictReader`
---

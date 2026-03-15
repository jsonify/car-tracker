# Track Learnings: mvp_scraper_20260314

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

<!-- No patterns yet - this is the first track -->

---

## [2026-03-15] - Phase 1: Project Scaffolding
- **Implemented:** uv project with src/car_tracker/ layout, dependencies, config.yaml, __main__.py CLI
- **Files changed:** pyproject.toml, src/car_tracker/__init__.py, src/car_tracker/__main__.py, tests/__init__.py, config.yaml, uv.lock
- **Commit:** feat(scaffold), feat(deps), feat(config), feat(cli)
- **Learnings:**
  - Patterns: uv init creates flat main.py — must manually restructure to src/ layout
  - Patterns: Use `[tool.hatch.build.targets.wheel] packages = ["src/car_tracker"]` for src layout
  - Patterns: Add pytest, pytest-cov, ruff as dev deps alongside runtime deps

---

## [2026-03-15] - Phase 2: Config Loader
- **Implemented:** config.py with dataclasses, YAML loading, date/time/string validation
- **Files changed:** src/car_tracker/config.py, tests/test_config.py
- **Commit:** feat(config)
- **Learnings:**
  - Patterns: Date validation regex `^\d{4}-\d{2}-\d{2}$`, time `^\d{2}:\d{2}$`
  - Gotchas: yaml.safe_load returns None for empty files — check isinstance(raw, dict)

---

## [2026-03-15] - Phase 3: SQLite Storage Layer
- **Implemented:** database.py with init_db, save_run, save_vehicles; auto-creates parent dirs
- **Files changed:** src/car_tracker/database.py, tests/test_database.py
- **Commit:** feat(database)
- **Learnings:**
  - Patterns: `conn.execute("PRAGMA foreign_keys = ON")` required for FK enforcement in SQLite
  - Patterns: `Path(db_path).parent.mkdir(parents=True, exist_ok=True)` before connecting

---

## [2026-03-15] - Phase 4: Playwright Scraper
- **Implemented:** scraper.py with ChromeManager (CDP), form fill, result extraction
- **Files changed:** src/car_tracker/scraper.py, tests/test_scraper.py
- **Commit:** feat(scraper)
- **Learnings:**
  - **CRITICAL GOTCHA:** Costco Travel uses Akamai Bot Manager — Playwright's bundled Chromium is blocked. Must use real Chrome via `--remote-debugging-port` + `connect_over_cdp`.
  - **CRITICAL GOTCHA:** `--remote-debugging-port` requires `--user-data-dir` on Chrome.
  - Patterns: Autocomplete suggestions are `<li data-value="LAX">` inside `ul.ui-list`; type slowly (120-280ms/char) and wait 2.5-3.5s before clicking
  - Patterns: Date fields use jQuery datepicker — set via JS: `$(el).datepicker('setDate', val)` + fire `change` event; do NOT click the field (calendar blocks drop-off field)
  - Patterns: Time fields are `<select>` with 12h format labels ("10:00 AM") — convert from 24h config values
  - Patterns: Result cards are `<a class="car-result-card">` with all data in attributes: `data-category-name`, `data-brand`, `data-price` (total as float string)
  - Patterns: Price per day must be calculated: `total / days_between(pickup, dropoff)`
  - Patterns: `pragma: no cover` on browser automation methods — they're integration-only

---

## [2026-03-15] - Phase 5: Integration & Wiring
- **Implemented:** Wired __main__.py pipeline; 42 tests passing; live E2E run produced 102 vehicles
- **Files changed:** src/car_tracker/__main__.py, tests/test_main.py
- **Commit:** feat(wiring), test(integration)
- **Learnings:**
  - Patterns: Vehicle name stored as "Category (Brand)" e.g. "Economy Car (Alamo)"
  - E2E result: LAX Apr 1–5, 2026 = 102 vehicles across multiple categories and vendors

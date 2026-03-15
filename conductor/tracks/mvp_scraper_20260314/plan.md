# Plan: MVP — Scraper, Config & Storage

## Phase 1: Project Scaffolding

- [ ] Task: Initialize uv project (`pyproject.toml`, `src/car_tracker/` layout)
- [ ] Task: Add dependencies (playwright, pyyaml, jinja2) to `pyproject.toml`
- [ ] Task: Create `config.yaml` with sample search parameters
- [ ] Task: Create `src/car_tracker/__main__.py` with CLI argument parsing (`--debug`, `--config`)
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Project Scaffolding' (Protocol in workflow.md)

## Phase 2: Config Loader

- [ ] Task: Implement `config.py` — load and validate `config.yaml` using dataclasses
- [ ] Task: Write tests for config loading (valid config, missing fields, bad types)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Config Loader' (Protocol in workflow.md)

## Phase 3: SQLite Storage Layer

- [ ] Task: Implement `database.py` — create `runs` and `vehicles` tables on first run
- [ ] Task: Implement `save_run()` — insert a run record and return `run_id`
- [ ] Task: Implement `save_vehicles()` — bulk insert vehicle records for a run
- [ ] Task: Write tests for database layer (schema creation, insert, foreign key)
- [ ] Task: Conductor - User Manual Verification 'Phase 3: SQLite Storage Layer' (Protocol in workflow.md)

## Phase 4: Playwright Scraper

- [ ] Task: Implement `scraper.py` — launch browser (headless/headed), navigate to Costco Travel
- [ ] Task: Implement form fill — populate pickup location, dates, and times
- [ ] Task: Implement results extraction — parse vehicle name, total price, price per day
- [ ] Task: Handle error states (timeout, no results, form errors)
- [ ] Task: Write tests for scraper (mock Playwright responses for unit tests)
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Playwright Scraper' (Protocol in workflow.md)

## Phase 5: Integration & Wiring

- [ ] Task: Wire `__main__.py` → load config → run scraper → save to DB
- [ ] Task: End-to-end integration test (live run with `--debug`, verify DB record created)
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Integration & Wiring' (Protocol in workflow.md)

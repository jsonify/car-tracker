# plan.md — Vehicle Type Holding Price & Best-Per-Type Email Table

## Phase 1: Config & Data Model

- [x] Task 1: Add `holding_vehicle_type` to `SearchConfig` and `load_config` <!-- commit: 4961558 -->
  - Add `holding_vehicle_type: str | None = None` to `SearchConfig` dataclass
  - Parse `holding_vehicle_type` from `config.yaml` in `load_config`
  - Treat as a pair: if one is present without the other, set both to None
  - Write unit tests for new config parsing (pair validation, both present, both absent, one missing)

- [x] Task 2: DB migration — add `holding_vehicle_type` to `runs` table <!-- commit: 143b88c -->
  - Add migration in `migrate_db`: `ALTER TABLE runs ADD COLUMN holding_vehicle_type TEXT`
  - Update `save_run` signature: add `holding_vehicle_type: str | None = None`
  - Write unit tests for `save_run` with and without vehicle type

- [x] Task 3: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Core Logic

- [x] Task 1: Add `extract_category` function to `emailer.py` <!-- commit: 46d4772 -->
  - `extract_category(name: str) -> str` — strips brand suffix, e.g. `"Economy Car (Alamo)"` → `"Economy Car"`
  - Handle edge case: name with no `(` returns name unchanged
  - Write unit tests

- [x] Task 2: Add `best_per_type` function to `emailer.py` <!-- commit: 46d4772 -->
  - `best_per_type(vehicles: list[dict]) -> list[dict]`
  - Groups by `extract_category(v["name"])`, retains lowest `total_price` row per category
  - Returns sorted by `total_price` ascending
  - Write unit tests (ties, single type, multiple types, empty input)

- [x] Task 3: Add `best_per_type_prices` helper to `emailer.py` <!-- commit: 46d4772 -->
  - `best_per_type_prices(vehicles: list[VehicleRecord]) -> dict[str, float]`
  - Returns `category → best total_price` for use as prior-run lookup in `build_delta`
  - Write unit tests

- [x] Task 4: Update `build_holding_summary` signature and logic <!-- commit: 46d4772 -->
  - Add `holding_vehicle_type: str | None = None` parameter
  - When both `holding_price` and `holding_vehicle_type` are provided:
    filter vehicles to matching category, use best of that subset
  - When either is None: return None (no summary)
  - Update existing unit tests; add tests for type-specific comparison

- [x] Task 5: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Email Template & Wiring

- [x] Task 1: Update `email_success.html` template <!-- commit: f41af43 -->
  - Remove `#` / position column from table header and rows
  - Rename "Vehicle" column to "Vehicle Type"
  - No other template changes needed (holding summary block unchanged)

- [x] Task 2: Wire everything together in `__main__.py` <!-- commit: 92db64c -->
  - Pass `holding_vehicle_type` to `save_run`
  - Apply `best_per_type` to `vehicle_records` before `build_delta`
  - Use `best_per_type_prices` to build prior lookup (keyed by category)
  - Pass `holding_vehicle_type` to `build_holding_summary`

- [x] Task 3: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

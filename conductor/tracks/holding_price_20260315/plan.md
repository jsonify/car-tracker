# plan.md — Holding Price Comparison

## Phase 1: Config + Database
<!-- execution: parallel -->

- [ ] Task 1: Add `holding_price` to `SearchConfig` in `config.py`
  <!-- files: src/car_tracker/config.py -->
  - Optional field, default `None`, type `float | None`
  - No validation required (any positive float is valid)
- [ ] Task 2: DB migration + update `save_run`
  <!-- files: src/car_tracker/database.py -->
  - Add `migrate_db(db_path)` function that runs:
    `ALTER TABLE runs ADD COLUMN holding_price REAL`
    safely (no-op if column already exists)
  - Call `migrate_db` from `init_db` so it's automatic
  - Add `holding_price: float | None = None` param to `save_run`
- [ ] Task 3: Unit tests for config and DB changes
  <!-- files: tests/test_config.py, tests/test_database.py -->
  <!-- depends: task1, task2 -->
  - Config: `holding_price` present → parsed as float; omitted → None
  - DB: `migrate_db` idempotent (safe to run twice)
  - `save_run` stores holding_price correctly (value and NULL)
  - `get_prior_run_vehicles` unaffected (regression check)
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Config + Database' (Protocol in workflow.md)

## Phase 2: Holding Price Summary Logic + Template
<!-- execution: parallel -->

- [ ] Task 1: Add `build_holding_summary` to `emailer.py`
  <!-- files: src/car_tracker/emailer.py -->
  - Pure function: `build_holding_summary(vehicles: list[dict], holding_price: float | None) -> dict | None`
  - Returns `None` if `holding_price` is None
  - Computes `best_price = min(v["total_price"] for v in vehicles)`
  - Returns dict: `{holding_price, best_price, savings, is_savings}`
    - `savings = abs(holding_price - best_price)`
    - `is_savings = best_price < holding_price`
- [ ] Task 2: Update `email_success.html` template
  <!-- files: src/car_tracker/templates/email_success.html -->
  - Add summary block above results table
  - Savings case: "Your holding price: $X · Best current price: $Y · Savings: $Z"
  - No-savings case: "Your holding price: $X · Best current price: $Y · You're ahead by $Z — keep your booking"
  - Hidden when `holding_summary` is None
- [ ] Task 3: Unit tests for `build_holding_summary` and template rendering
  <!-- files: tests/test_emailer.py -->
  <!-- depends: task1, task2 -->
  - Savings scenario
  - No-savings scenario (best > holding)
  - Break-even scenario (best == holding)
  - No holding price → returns None
  - Empty vehicles list with holding price set
  - Template renders summary when provided, omits when None
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Holding Price Summary Logic + Template' (Protocol in workflow.md)

## Phase 3: Wire Into `__main__.py`

- [ ] Task 1: Update `__main__.py` and `emailer.py`
  - Pass `holding_price=config.search.holding_price` to `save_run`
  - Call `build_holding_summary(rows, config.search.holding_price)` and pass
    result into `render_success`
  - Update `render_success` signature to accept `holding_summary`
- [ ] Task 2: Update tests
  - `test_main.py`: assert `save_run` called with holding_price kwarg
  - `test_emailer.py`: update `render_success` tests to pass holding_summary param
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Wire Into __main__.py' (Protocol in workflow.md)

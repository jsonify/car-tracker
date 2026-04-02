# Plan: Fix Change Delta Bug & Remove Trend Column

## Phase 1: Fix Change Column Delta Bug

- [x] Task 1: Write failing test for delta bug
  - In `test_database.py`, add a test where multiple brands exist for the same
    category in the prior run; assert `get_prior_run_vehicles` returns the minimum
    price per category (currently fails — last rowid price wins).

- [x] Task 2: Fix `get_prior_run_vehicles` in `database.py`
  - Change SQL to `SELECT name, MIN(total_price) FROM vehicles WHERE run_id = ?
    GROUP BY name` so the best (cheapest) prior price is used per category.
  - Verify Task 1 test now passes.

- [x] Task 3: Run tests, verify coverage ≥ 80%, commit <!-- 9b14064 -->
  - `fix(database): use MIN price per category in get_prior_run_vehicles`

- [x] Task 4: Conductor — User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Remove Trend Column & Dead Code
<!-- execution: parallel -->

- [x] Task 1: Remove Trend column from email template
  <!-- files: src/car_tracker/templates/email_success.html -->
  - Remove `<th>Trend</th>` and sparkline `<td>` from `email_success.html`.
  - Remove dead `.trend td` CSS rule.

- [x] Task 2: Remove sparkline code from `emailer.py`
  <!-- files: src/car_tracker/emailer.py -->
  - Delete `render_sparkline` function.
  - Remove `env.globals["render_sparkline"]` and `env.globals["extract_category"]`
    registrations from `_jinja_env()`.
  - Remove `price_history` field from `BookingSection` dataclass.

- [x] Task 3: Remove `get_category_price_history` from `database.py`
  <!-- files: src/car_tracker/database.py -->
  - Delete the function and its deferred circular import of `extract_category`.

- [x] Task 4: Clean up `__main__.py`
  <!-- files: src/car_tracker/__main__.py -->
  - Remove `get_category_price_history` from imports.
  - Remove `price_history = get_category_price_history(...)` call.
  - Remove `price_history=price_history` from `BookingSection(...)` constructor.

- [x] Task 5: Remove dead tests, verify suite, commit <!-- ea712d8 -->
  <!-- depends: task1, task2, task3, task4 -->
  - Delete `render_sparkline` tests from `test_emailer.py`.
  - Delete `get_category_price_history` tests from `test_database.py`.
  - Remove `get_category_price_history` mock patches from `test_main.py`.
  - Verify full suite passes with coverage ≥ 80%.
  - `fix(email): remove trend column and sparkline dead code`

- [x] Task 6: Conductor — User Manual Verification 'Phase 2' (Protocol in workflow.md)
  <!-- depends: task5 -->

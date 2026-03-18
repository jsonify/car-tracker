# Plan: Email Enhancements — Holding Row Highlight, Sparklines & Smart Subject Line

## Phase 1: Price History Data Layer
<!-- execution: sequential -->
<!-- depends: -->

- [x] Task 1: Write tests for `get_category_price_history` in `tests/test_database.py`
  <!-- files: tests/test_database.py -->
  - Returns `dict[str, list[float]]` — category → prices ordered oldest to newest
  - Covers: single booking, multiple runs, missing booking, multiple categories
- [x] Task 2: Implement `get_category_price_history(db_path, booking_name)` in `database.py`
  <!-- files: src/car_tracker/database.py -->
  - Query vehicles joined with runs, filter by booking_name, group by category, order by run_at ASC
  - Return best price per category per run

## Phase 2: SVG Sparkline Generator
<!-- execution: sequential -->
<!-- depends: phase1 -->

- [x] Task 1: Write tests for `render_sparkline` in `tests/test_emailer.py`
  <!-- files: tests/test_emailer.py -->
  - 1 data point → single SVG dot
  - 2+ data points → SVG polyline
  - Verify output is valid inline SVG string
- [x] Task 2: Implement `render_sparkline(prices: list[float]) -> str` in `emailer.py`
  <!-- files: src/car_tracker/emailer.py -->
  - Normalize prices to fixed viewport (60×20px)
  - 1 point: `<circle>` centered; 2+ points: `<polyline>` with mapped coordinates

## Phase 3: Smart Subject Line
<!-- execution: sequential -->
<!-- depends: -->

- [x] Task 1: Write tests for `build_subject` in `tests/test_emailer.py`
  <!-- files: tests/test_emailer.py -->
  - ✅ prefix when saving, ⚠️ when over, no prefix when no holding
  - Multi-booking joined with ` · `, booking name uppercased
- [x] Task 2: Implement `build_subject(sections: list[BookingSection]) -> str` in `emailer.py`
  <!-- files: src/car_tracker/emailer.py -->
- [x] Task 3: Wire `build_subject` into `__main__.py`, replacing hardcoded subject
  <!-- files: src/car_tracker/__main__.py -->

## Phase 4: Email Template Integration
<!-- execution: sequential -->
<!-- depends: phase2, phase3 -->

- [x] Task 1: Extend `BookingSection` with `price_history` field; wire `get_category_price_history` in `__main__.py`
  <!-- files: src/car_tracker/emailer.py, src/car_tracker/__main__.py -->
- [x] Task 2: Update `email_success.html` — Trend column + holding row highlight
  <!-- files: src/car_tracker/templates/email_success.html -->
- [x] Task 3: Update `render_success` tests for new Trend column and holding row markup
  <!-- files: tests/test_emailer.py -->

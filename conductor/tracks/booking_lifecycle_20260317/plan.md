# Plan: Booking Countdown & Expiration

## Phase 1: Countdown Logic & Email Template
<!-- execution: sequential -->
<!-- depends: -->

- [x] Task 1: Write tests for `days_until_booking` helper
  - `tests/test_emailer.py`: test `days_until_booking(pickup_date_str, today) -> int`
  - Cases: future date (n days), today (0), past date (negative)

- [x] Task 2: Implement `days_until_booking` in `emailer.py`
  - Pure function: `days_until_booking(pickup_date: str, today: date) -> int`
  - Parse `pickup_date` (YYYY-MM-DD), return `(pickup - today).days`
  - Add `countdown_days: int` field to `BookingSection` dataclass

- [x] Task 3: Update `email_success.html` countdown line
  - Below `.booking-header` div, add a second line:
    - If `section.countdown_days > 0`: `{{ section.countdown_days }} days until your booking`
    - If `section.countdown_days == 0`: `Today is your booking day!`
  - Add `.countdown` CSS class with appropriate styling

- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Booking Expiration & Config
<!-- execution: sequential -->
<!-- depends: -->

- [x] Task 1: Write tests for `remove_expired_bookings` and empty-bookings config
  - `tests/test_lifecycle.py`: test `remove_expired_bookings` filters expired, writes YAML, skips git (mocked), returns removed list
  - `tests/test_config.py`: test `load_config` accepts `bookings: []` without raising

- [x] Task 2: Relax `load_config` to allow empty bookings list
  - `src/car_tracker/config.py`: remove `len(bookings_raw) == 0` guard from validation
  - `AppConfig`: handle empty `bookings` gracefully (no `.search` property access when empty)

- [x] Task 3: Implement `remove_expired_bookings` in `src/car_tracker/lifecycle.py`
  - New module `lifecycle.py`
  - `remove_expired_bookings(config_path: Path, today: date) -> list[BookingConfig]`
    - Load raw YAML, filter out bookings where `today > pickup_date`
    - If any removed: write updated YAML back, git add + commit + push (pattern from `scripts/update_config.py`)
    - Return list of removed bookings (empty list = nothing expired)

- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Integration & Monitoring Paused Notification
<!-- execution: sequential -->
<!-- depends: phase1, phase2 -->

- [x] Task 1: Write tests for state flag and monitoring paused email
  - `tests/test_emailer.py`: test `render_monitoring_paused()` returns non-empty HTML
  - `tests/test_main.py`: test no-bookings path sends paused notification once, skips on second run

- [x] Task 2: Add `monitoring_paused_notified` to state management
  - New helpers: `read_app_state(state_path) -> dict` and `write_app_state(state_path, state: dict)`
  - Add `monitoring_paused_notified: bool` key (defaults to `False`)
  - Add tests in `tests/test_check_imessage.py` or new `tests/test_app_state.py`

- [x] Task 3: Add `render_monitoring_paused()` in `emailer.py` + template
  - New Jinja2 template `email_monitoring_paused.html`
  - Simple HTML: subject "Costco Travel — Monitoring Paused", body explains no active bookings
  - `render_monitoring_paused() -> str` function in `emailer.py`

- [x] Task 4: Update `__main__.py` — full integration
  - Compute `today = date.today()`
  - Call `remove_expired_bookings(config_path, today)` — modifies config if needed
  - Reload config after expiration (`load_config` again) to get fresh bookings list
  - **If `config.bookings` is empty:**
    - Load state; if `monitoring_paused_notified` is False: send monitoring paused email, set flag to True, write state
    - Exit 0 (clean exit — nothing to scrape)
  - **If `config.bookings` is non-empty:**
    - If `monitoring_paused_notified` is True: reset to False, write state
    - For each booking: compute `countdown_days = days_until_booking(booking.pickup_date, today)`, pass into `BookingSection`

- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

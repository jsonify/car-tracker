# plan.md — Email Delivery

## Phase 1: Database — Prior Run Query

- [x] Task 1: Add `get_prior_run_vehicles` function to `database.py`
  - Query the most recent `run_id` before the current one for matching
    `pickup_location`, `pickup_date`, `dropoff_date`
  - Return a `dict[str, float]` mapping `name` → `total_price` (keyed by
    vehicle name as stored, e.g. "Economy Car (Alamo)")
  - Return empty dict if no prior run exists
- [x] Task 2: Unit tests for `get_prior_run_vehicles`
  - No prior run → empty dict
  - One prior run → correct prices returned
  - Multiple prior runs → only most recent returned
  - Different search params → not returned
- [x] Task: Conductor - User Manual Verification 'Phase 1: Database — Prior Run Query' (Protocol in workflow.md)

## Phase 2: Email Module

- [x] Task 1: Create `src/car_tracker/emailer.py`
  - `load_email_config()` — loads `.env` from
    `/Users/Jason/code/rental-car-pricer/.env` via `python-dotenv`; returns
    dataclass with smtp_server, smtp_port, sender_email, sender_password,
    recipient_email
  - `build_delta(current: list[VehicleRecord], prior: dict[str, float]) -> list[dict]`
    — pure function; returns list of dicts adding `delta: float | None` and
    `is_new: bool` to each vehicle
  - `render_success(vehicles_with_delta, config, run_ts) -> str` — Jinja2 HTML
  - `render_failure(error_msg, config) -> str` — Jinja2 HTML
  - `send_email(subject, html_body, email_cfg)` — smtplib SMTP; marked
    `# pragma: no cover` for SMTP I/O
- [x] Task 2: Create Jinja2 templates
  - `src/car_tracker/templates/email_success.html`
  - `src/car_tracker/templates/email_failure.html`
- [x] Task 3: Unit tests for `emailer.py`
  - `build_delta`: price increase, decrease, new vehicle, no prior run
  - `render_success`: renders table with correct delta markup (▲/▼/New/—)
  - `render_failure`: renders error message and search params
  - `load_email_config`: mock `load_dotenv`; missing required field raises
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Email Module' (Protocol in workflow.md)

## Phase 3: Wire Into `__main__.py`

- [ ] Task 1: Update `__main__.py` to send email after save
  - On success: call `get_prior_run_vehicles`, `build_delta`, `render_success`,
    `send_email`
  - On scrape failure (existing except block): call `render_failure`,
    `send_email`
  - Subject strings match spec
- [ ] Task 2: Update `test_main.py`
  - Mock `send_email` in success path; assert called with correct subject
  - Mock `send_email` in failure path; assert failure subject used
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Wire Into __main__.py' (Protocol in workflow.md)

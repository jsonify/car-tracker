# Plan: Multiple Bookings Support

## Phase 1: Config Layer

- [ ] Task 1: Write tests for multi-booking config loading
  - Test `bookings:` list parses into a list of booking dataclasses
  - Test each booking carries its own search params + optional holding pair
  - Test 1-based index and name lookup helpers
  - Test old single-`search:` format raises a clear `ConfigError`

- [ ] Task 2: Implement multi-booking config
  - Add `BookingConfig` dataclass with fields: `name`, `location`, dates/times, optional holding pair
  - Update `AppConfig` to replace `search` field with `bookings: list[BookingConfig]`
  - Add `get_booking_by_name(name)` and `get_booking_by_index(n)` helpers to `AppConfig`
  - Detect old single-`search:` format and raise `ConfigError` with migration hint
  - Update `config.yaml` example to use `bookings:` list (2 sample bookings)

- [ ] Task: Conductor - User Manual Verification 'Config Layer' (Protocol in workflow.md)

## Phase 2: Database Migration

- [ ] Task 1: Write tests for DB migration
  - Test `booking_name` column is added to `runs` idempotently
  - Test saving a run with `booking_name` and retrieving it scoped by `booking_name`
  - Test `get_prior_run_vehicles` filters by `booking_name`

- [ ] Task 2: Implement DB migration
  - Add `# v4:` migration block: `ALTER TABLE runs ADD COLUMN booking_name TEXT NOT NULL DEFAULT ''`
  - Update `save_run()` to accept and store `booking_name`
  - Update `get_prior_run_vehicles()` to filter by `booking_name`

- [ ] Task: Conductor - User Manual Verification 'Database Migration' (Protocol in workflow.md)

## Phase 3: Scraper Pipeline

- [ ] Task 1: Write tests for multi-booking pipeline orchestration
  - Test main pipeline iterates over all bookings
  - Test each booking's results are saved with correct `booking_name`
  - Mock `scrape()` per booking

- [ ] Task 2: Update pipeline to iterate bookings
  - Update `__main__.py` to loop over `config.bookings`
  - Pass `booking.name` through to `save_run()` and downstream calls
  - Collect per-booking results for email rendering

- [ ] Task: Conductor - User Manual Verification 'Scraper Pipeline' (Protocol in workflow.md)

## Phase 4: Email Rendering

- [ ] Task 1: Write tests for multi-booking email rendering
  - Test combined email contains one section per booking
  - Test each section shows correct booking label, price table, deltas, holding summary

- [ ] Task 2: Update email template and renderer
  - Update Jinja2 template to accept a list of booking result objects
  - Render one section per booking (label header + existing price table + holding banner)
  - Update `render_success()` signature to accept list of per-booking results

- [ ] Task: Conductor - User Manual Verification 'Email Rendering' (Protocol in workflow.md)

## Phase 5: iMessage Config Updates

- [ ] Task 1: Write tests for multi-booking iMessage parsing
  - Test `update holding <name> <price> <type>` resolves correct booking by name
  - Test `update holding <N> <price> <type>` resolves correct booking by 1-based index
  - Test unknown name and out-of-range index produce clear error responses

- [ ] Task 2: Update iMessage handler
  - Update command parser to accept name-or-index as second token
  - Use `get_booking_by_name()` / `get_booking_by_index()` to resolve target booking
  - Write updated holding pair back to correct entry in `config.yaml`

- [ ] Task: Conductor - User Manual Verification 'iMessage Config Updates' (Protocol in workflow.md)

## Phase 6: Documentation

- [ ] Task 1: Update README.md
  - Replace single-booking `config.yaml` example with multi-booking `bookings:` list example
  - Document iMessage `update holding` command with name and index examples
  - Update "How It Works" section to reflect multi-booking run behavior
  - Update email output description to mention per-booking sections

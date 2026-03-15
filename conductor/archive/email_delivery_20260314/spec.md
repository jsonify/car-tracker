# spec.md — Email Delivery

## Overview
Format scrape results as an HTML email and send it after each run. Credentials are
loaded from an external `.env` file. The email includes a price-delta column comparing
each vehicle's total price to the previous run's data. On scrape failure, a failure
notice email is sent instead.

## Functional Requirements

### Email Sending
- Load SMTP credentials from `/Users/Jason/code/rental-car-pricer/.env` via
  `python-dotenv` (fields: `SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`,
  `SENDER_PASSWORD`, `RECIPIENT_EMAIL`)
- Send via `smtplib` + `email.mime` (standard library, no yagmail)
- Subject format: `Costco Travel Rental Prices — {pickup_location} {pickup_date} to {dropoff_date}`

### Success Email Body (HTML)
- Rendered via Jinja2 template
- Header section: search params (location, pickup date/time, dropoff date/time, run timestamp)
- Results table columns: Position | Vehicle | Brand | Total Price | Per Day | Change
- "Change" column: delta vs same vehicle (matched by name+brand) from the prior run
  - Up: ▲ $X.XX (red)
  - Down: ▼ $X.XX (green)
  - New (no prior match): "New"
  - No prior run: "—"
- Vehicles in the order they appear on the site (position order)

### Failure Email
- Subject: `Costco Travel Scrape Failed — {pickup_location} {pickup_date} to {dropoff_date}`
- Body: plain description of the error, search params shown

### Database Query for Deltas
- Look up the most recent prior `run_id` for the same `pickup_location`,
  `pickup_date`, and `dropoff_date` from the `runs` table
- Join `vehicles` to get prior prices
- Return mapping of vehicle name → total_price

## Non-Functional Requirements
- `send_email` function is unit-testable with a mocked SMTP connection
- Jinja2 template renders correctly with zero, one, or many vehicles
- Delta logic is pure and fully unit-tested

## Acceptance Criteria
- [ ] Running `python -m car_tracker` sends an HTML email after a successful scrape
- [ ] Email subject matches specified format
- [ ] Results table shows all vehicles in position order with correct delta values
- [ ] First run (no prior data) shows "—" in Change column
- [ ] Scrape failure triggers a failure-notice email
- [ ] All unit-testable code covered by tests; SMTP calls mocked

## Out of Scope
- Scheduling (cron setup is a separate track)
- Unsubscribe / HTML email client compatibility testing
- Multiple recipients

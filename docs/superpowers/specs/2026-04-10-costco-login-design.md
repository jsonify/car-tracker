# Costco Login for Member Pricing

**Date:** 2026-04-10
**Status:** Approved

## Problem

The scraper reads `data-price` from `.car-result-card` elements using an unauthenticated Chrome session. Costco Travel serves the rack rate to unauthenticated sessions and member pricing to logged-in sessions. The rack rate ($357.22) is ~14% higher than the member price ($307.32), making the holding price comparison in the email inaccurate.

The scraper runs unattended overnight (~6:45 AM) with no active browser session available, so cookie injection from a live browser is not viable. The solution is to log into Costco Travel before each search run using stored credentials.

## Approach

Log in on every run. The 10–15 second overhead is irrelevant for an overnight cron job. This is simpler than session persistence strategies and has no stale-state failure modes.

## What Changes

Only `scraper.py` and `.env` are modified. All other components (config, database, emailer, lifecycle, templates) are unchanged.

### Call sequence (updated)

```
ChromeManager.start()
  → navigate to Costco Travel
  → _login(page, username, password)      ← new
  → _fill_search_form(page, booking)
  → _extract_results(page, booking)
ChromeManager.stop()
```

## Components

### `.env` additions

```
COSTCO_USERNAME=your@email.com
COSTCO_PASSWORD=yourpassword
```

Both are required. If either is missing, the scraper exits before launching Chrome with a clear `ValueError`.

### `load_costco_config()` — new function in `scraper.py`

Reads `COSTCO_USERNAME` and `COSTCO_PASSWORD` from `.env` via `python-dotenv` (already a dependency). Raises `ValueError` with a descriptive message if either var is absent. Called once at the top of `scrape()` before Chrome starts.

Follows the same pattern as `load_email_config()` in `emailer.py`.

### `_login(page, username, password)` — new async function in `scraper.py`

1. Clicks the Sign In link on the already-loaded Costco Travel page
2. Waits for the login form to appear
3. Fills the email field with `username`
4. Fills the password field with `password`
5. Submits the form
6. Waits for a success signal (Sign In link disappears or account indicator appears in header)
7. Raises `LoginError` if the success signal doesn't appear within timeout

Uses `_slow_pause()` between interactions, consistent with the rest of the scraper.

Called in `_run_scrape()` after the page loads and before `_fill_search_form()`.

### Member pricing verification in `_extract_results()`

After results load, checks for the presence of the Costco member savings banner. If the banner is absent, raises `LoginError("Login succeeded but member pricing not detected")`. This triggers the existing retry loop rather than saving rack-rate data silently.

### `LoginError` — new exception class in `scraper.py`

A simple subclass of `RuntimeError`. Raised by `_login()` on timeout and by `_extract_results()` on missing member banner. Caught by the existing retry loop in `scrape()` — no changes to retry logic needed.

## Error Handling

| Scenario | Behavior |
|---|---|
| Credentials missing from `.env` | `ValueError` before Chrome starts; failure email sent |
| Login form doesn't appear | `LoginError` after timeout; retried up to 3× |
| Login form appears but success signal absent | `LoginError` after timeout; retried up to 3× |
| All 3 retries fail | Existing failure email with message "Login failed — check COSTCO_USERNAME / COSTCO_PASSWORD in .env" |
| Login succeeds but member banner absent | `LoginError("Login succeeded but member pricing not detected")`; retried up to 3× |

## Constraints

- Exact login form selectors (field IDs, button selector) must be confirmed with a headed debug run during implementation — this is expected, not a risk.
- No new dependencies required.
- `.env` is already in `.gitignore`; credentials will not be committed.

## Out of Scope

- Session persistence / cookie caching between runs
- MFA handling (Costco account uses email + password only)
- Changes to config.yaml, database schema, email templates, or any module other than `scraper.py`

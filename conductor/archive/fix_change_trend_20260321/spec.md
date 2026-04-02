# Spec: Fix Change Delta Bug & Remove Trend Column

## Overview
Two bugs in the email report:
1. The **Change column** shows incorrect price deltas because `get_prior_run_vehicles`
   keeps the last (arbitrary) price per vehicle category instead of the best (cheapest),
   causing inflated/misleading deltas.
2. The **Trend column** renders inline SVG sparklines that are stripped by email clients,
   leaving the column permanently blank. The column and all supporting code will be removed.

## Functional Requirements

### Bug 1 — Change Column Delta Fix
- `get_prior_run_vehicles` must return the **minimum (best) price per vehicle category**
  from the prior run, consistent with how `best_per_type` selects the current run's prices.
- Fix: use `SELECT name, MIN(total_price) ... GROUP BY name` in the SQL query.
- The `build_delta` comparison becomes correct: best current price vs. best prior price.

### Bug 2 — Trend Column Removal
- Remove the `<th>Trend</th>` header and sparkline `<td>` from `email_success.html`.
- Remove the `render_sparkline` function from `emailer.py`.
- Remove `render_sparkline` and `extract_category` global registrations from `_jinja_env()`.
- Remove `get_category_price_history` from `database.py`.
- Remove the `price_history` field from the `BookingSection` dataclass in `emailer.py`.
- Remove the `price_history` assignment and `get_category_price_history` import in `__main__.py`.
- Remove the dead `.trend td` CSS rule from `email_success.html`.

## Non-Functional Requirements
- All existing tests must continue to pass.
- Test coverage must remain ≥ 80%.
- Tests covering `render_sparkline` and `get_category_price_history` must be deleted
  along with the functions.

## Acceptance Criteria
- [ ] Change column deltas reflect best-vs-best price comparison across runs.
- [ ] Trend column and header are gone from the email output.
- [ ] No dead code remains for sparkline or price history functionality.
- [ ] All tests pass with ≥ 80% coverage.

## Out of Scope
- Adding any alternative visualization for price trends (e.g., Unicode sparklines).
- Changes to the scraper, config, or iMessage integration.

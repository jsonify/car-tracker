# Track Learnings: fix_change_trend_20260321

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `get_prior_run_vehicles` returns full names ("Economy Car (Alamo)") — collapse with
  `extract_category` before using as a category-keyed delta lookup; `best_per_type_prices`
  works on VehicleRecords, so inline collapse is simpler for the prior dict.
  (from: type_holding_email_20260314)
- **Expose Python functions to Jinja2 templates via `env.globals["fn_name"] = fn`** —
  use `| safe` filter in the template when function returns raw HTML/SVG.
  (from: email_enhancements_20260318)
- **Deferred import inside function body to break circular imports** — `database.py`
  imports `extract_category` from `emailer.py` inside `get_category_price_history`;
  removing that function eliminates the circular import.
  (from: email_enhancements_20260318)
- **New `__main__` DB functions need their own mock in `test_main.py`** — any DB
  function called in the booking loop must be patched since `init_db` is mocked.
  (from: email_enhancements_20260318)
- **Assert `<tr class="cls-name"` not `"cls-name" not in html`** — CSS class names
  in `<style>` blocks appear in the full HTML string; target actual element usage.
  (from: email_enhancements_20260318)

---

## [2026-03-21 16:15] - Phase 2 Tasks 1-5: Remove Trend Column & Dead Code
- **Implemented:** Removed Trend column from template, deleted render_sparkline and get_category_price_history, cleaned up BookingSection, _jinja_env globals, imports, and all related tests
- **Files changed:** `email_success.html`, `emailer.py`, `database.py`, `__main__.py`, `test_emailer.py`, `test_database.py`, `test_main.py`
- **Commit:** ea712d8
- **Learnings:**
  - Patterns: When removing a Jinja2 global function, also check template tests that assert on rendered output (e.g., `assert "Trend" in html`, sparkline SVG assertions) — they won't fail on import but will fail at runtime or be stale
  - Gotchas: `from dataclasses import dataclass, field` — remove `field` import when removing the only field that used `field(default_factory=...)`, otherwise unused import warning
  - Context: `tech-stack.md` still lists "SVG Sparklines" — update that in doc sync
---

<!-- Learnings from implementation will be appended below -->

## [2026-03-21 15:36] - Phase 1 Tasks 1-3: Fix Change Column Delta Bug
- **Implemented:** Added failing test for multi-brand category MIN price, then fixed `get_prior_run_vehicles` SQL to use `GROUP BY name` with `MIN(total_price)`
- **Files changed:** `tests/test_database.py`, `src/car_tracker/database.py`
- **Commit:** 9b14064
- **Learnings:**
  - Patterns: `GROUP BY name` with `MIN()` is the correct SQL pattern when multiple rows share a category name and you need the best value
  - Gotchas: Pre-existing 5 failures in `test_check_imessage.py` (attributedBody schema) — unrelated to this track, do not investigate
  - Context: `get_prior_run_vehicles` now matches `best_per_type` logic — both select cheapest per category
---

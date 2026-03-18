# Track Learnings: react_webapp_20260318

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

### Data Conventions
- Vehicle name stored as clean category only e.g. "Economy Car"; brand stored separately in `vehicles.brand`
- Date format in DB: YYYY-MM-DD; UI should display MM/DD/YYYY
- Time format in DB/config: HH:MM (24h); UI should display 12h ("10:00 AM")
- `extract_category(name)` uses `str.find(" (")` for legacy brand-suffix handling

### Database
- SQLite FK enforcement: must run `PRAGMA foreign_keys = ON` per connection
- `get_category_price_history` lives in `car_tracker.database` — use it for price history queries
- Migration pattern: `ALTER TABLE ... ADD COLUMN` wrapped in `try/except OperationalError` is idempotent

### Config / Bookings
- Bookings stored in `config.yaml` — the FastAPI backend must read/write this file, not the DB
- Pair validation: `holding_price` + `holding_vehicle_type` must both be present or both None
- Booking identifier resolved by name or 1-based index via `_resolve_booking()`

### iMessage / State
- `data/imessage_state.json` is shared state — any new writer must use merge-read pattern
- `read_app_state`/`write_app_state` from `car_tracker.state` to avoid clobbering keys

### Testing
- Browser automation and I/O functions marked `# pragma: no cover`
- Mock `load_dotenv` in tests to prevent reads from real `.env`
- Assert `<tr class="cls-name"` not just the class name string (appears in `<style>` blocks too)
- Seed pre-migration data with raw SQL when testing migrations

### Email / Jinja2
- Expose Python functions to Jinja2 via `env.globals["fn_name"] = fn` in `_jinja_env()`

---

<!-- Learnings from implementation will be appended below -->

## [2026-03-18] - Phase 1-9: React Web App — Car Tracker Dashboard

### Phase 1: Project Setup
- **Implemented:** FastAPI backend + React/Vite/TypeScript frontend with Tailwind v4 and Vitest
- **Files changed:** pyproject.toml, webapp/backend/main.py, webapp/backend/database.py, webapp/frontend/ (scaffold)
- **Learnings:**
  - Patterns: Share root uv venv for backend — add fastapi/uvicorn to root pyproject.toml; avoids import packaging complexity
  - Patterns: Tailwind v4 uses `@import "tailwindcss"` in CSS + `@tailwindcss/vite` plugin; no tailwind.config.js needed
  - Gotchas: FastAPI TestClient requires `httpx` as a peer dep — add to dev dependencies explicitly
  - Gotchas: Run `npm run test` from `webapp/frontend/` not project root

### Phase 2: Backend API
- **Implemented:** All 4 routers — bookings CRUD, runs, vehicles (paginated/sorted), analytics (price history + dashboard summary)
- **Files changed:** webapp/backend/routers/, webapp/backend/models/, webapp/backend/tests/
- **Learnings:**
  - Patterns: Use `CAR_TRACKER_CONFIG` env var for test isolation in bookings router; pytest monkeypatch.setenv to point to tmp config
  - Patterns: SQL injection prevention via sort column whitelist set (`_SORT_COLS`) before f-string interpolation
  - Patterns: `_extract_category(name)` strips brand suffixes via `str.find(" (")` for legacy data compatibility
  - Gotchas: Pydantic pair validation — use `model_post_init` to clear both fields if only one is set

### Phase 3: React Shell & Shared Components
- **Implemented:** React Router v6 shell, Sidebar, Card, Badge, LoadingSpinner, EmptyState, typed axios API client
- **Files changed:** webapp/frontend/src/App.tsx, Sidebar.tsx, shared components, api/client.ts
- **Learnings:**
  - Gotchas: `getByText('Dashboard')` fails in tests if both sidebar nav link AND page h1 say "Dashboard" — use `getByRole('link', { name: /dashboard/i })` instead
  - Patterns: NavLink `className` prop accepts a function `({ isActive }) =>` for active state styling

### Phases 4-8: Feature Pages
- **Implemented:** Dashboard, Bookings (full CRUD with modal), PriceHistory (Recharts chart + insights), Vehicles (paginated table), Runs (expandable rows)
- **Files changed:** All 5 pages + 7 utility modules + PriceChart component + BookingModal
- **Learnings:**
  - Patterns: All pages use `loading/error/empty` state guards before rendering content (LoadingSpinner → error div → EmptyState → content)
  - Patterns: Pure utility modules (countdown, volatility, chartData, insights, tableUtils, runUtils) enable easy unit testing without DOM
  - Patterns: Recharts `ReferenceLine` for holding price horizontal line; `LineChart` with `ResponsiveContainer` for responsive layout
  - Patterns: Sortable table columns use `toggleSort(sort, col, order)` helper that returns `{sort, order}` and resets offset to 0

### Phase 9: Integration & Polish
- **Implemented:** Verified error/loading/empty states across all pages; wrote webapp/start.sh and webapp/README.md
- **Files changed:** webapp/start.sh, webapp/README.md
- **Learnings:**
  - Patterns: `start.sh` uses `trap cleanup EXIT INT TERM` with `wait` for clean parallel process management
  - Context: Backend runs from project root via `uv run uvicorn webapp.backend.main:app` to use shared venv

---

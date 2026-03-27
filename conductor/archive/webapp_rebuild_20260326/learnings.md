# Track Learnings: webapp_rebuild_20260326

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

### Tailwind v4
- `@import "tailwindcss"` in `index.css` + `@tailwindcss/vite` plugin in `vite.config.ts` — no `tailwind.config.js` needed (from: react_webapp_20260318)

### FastAPI / Backend
- Shared uv venv for webapp backend — add deps to root `pyproject.toml`
- `CAR_TRACKER_CONFIG` env var for test isolation; `monkeypatch.setenv` in pytest
- SQL sort column whitelist (`_SORT_COLS` frozenset) before f-string interpolation
- Bookings stored in `config.yaml` — backend reads/writes this file, not the DB
- Pydantic pair validation: `model_post_init` to clear both fields if only one set

### React / Frontend
- Loading/error/empty guard pattern on all pages
- NavLink active state via `className={({ isActive }) => ...}`
- Test selector: use `getByRole('link', { name })` when text appears in both nav and heading
- Pure utility modules for testability (countdown, volatility, chartData, etc.)
- Recharts: `ResponsiveContainer` wrapper, `ReferenceLine` for holding price

### Database
- SQLite FK: `PRAGMA foreign_keys = ON` per connection
- Migration: `ALTER TABLE ... ADD COLUMN` in `try/except OperationalError` is idempotent

---

<!-- Learnings from implementation will be appended below -->

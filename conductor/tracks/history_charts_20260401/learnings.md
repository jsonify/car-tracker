# Track Learnings: history_charts_20260401

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- **Recharts responsive chart:** Wrap `<LineChart>` in `<ResponsiveContainer width="100%" height={300}>`. Use `<ReferenceLine y={holdingPrice}>` for horizontal threshold lines.
- **Pure utility modules for testability:** Extract all business logic into side-effect-free utility modules (countdown, volatility, chartData, tableUtils) — they're easily unit-tested without DOM setup.
- **Loading/error/empty guard pattern:** All pages follow `if (loading) return <LoadingSpinner>; if (error) return <div className="text-red-400">; if (!data || data.length === 0) return <EmptyState>` before rendering content.
- **Tailwind v4 setup:** `@import "tailwindcss"` in `index.css` + `@tailwindcss/vite` plugin in `vite.config.ts` — no `tailwind.config.js` needed.
- **Test selector specificity:** When multiple elements share the same text, use `getByRole('link', { name: /text/i })` or `getByRole('heading')` instead of `getByText`.

---

## [2026-04-01 19:13] - Phase 1 Tasks 1-3: Bug Fixes
- **Implemented:** formatRunDate utility (ISO → "Mar 27"), applied to XAxis/Tooltip/card; fixed tooltip formatter to return category name; widened LineChart margin + moved ReferenceLine label to insideTopRight
- **Files changed:** `utils/dateUtils.ts`, `utils/dateUtils.test.ts`, `PriceChart.tsx`, `PriceChart.test.tsx`, `PriceHistory.tsx`
- **Commits:** dccbb3b, 745a20c, 48e5b59
- **Learnings:**
  - Patterns: `toLocaleDateString('en-US', { timeZone: 'UTC' })` gives deterministic output in tests regardless of CI timezone — always set timeZone for date formatting utilities
  - Gotchas: Recharts `<Tooltip formatter>` second return value must be the category `name` string (not undefined) — returning undefined suppresses the label entirely
  - Gotchas: ReferenceLine `position: 'right'` renders outside the SVG viewport and gets clipped by the container; use `position: 'insideTopRight'` and widen the chart margin instead
  - Patterns: `npx vitest run` must be executed from `webapp/frontend/` (the directory with vite.config.ts), not the repo root — jsdom environment not loaded otherwise
---

## [2026-04-01 19:15] - Phase 2 Tasks 1-4: Chart Data Utilities
- **Implemented:** buildPriceRangeData, buildLatestPricesData, buildPriceChangeData, buildHoldingComparisonData in chartData.ts; 26 new unit tests
- **Files changed:** `utils/chartData.ts`, `utils/chartData.test.ts`
- **Commit:** 836bc1f
- **Learnings:**
  - Patterns: Phase marked `<!-- execution: parallel -->` but all 4 tasks claimed same files — detected conflict, made sequential, committed as one batch
  - Patterns: Pure utility functions with no side effects are trivial to test exhaustively; keep all chart transforms in chartData.ts
---

## [2026-04-01 19:17] - Phase 3 Tasks 1-4: New Chart Components
- **Implemented:** PriceRangeChart (stacked floating bar), LatestPricesChart (horizontal), PriceChangeChart (Cell conditional color), HoldingComparisonChart (side-by-side); all with empty states and test files
- **Files changed:** `PriceRangeChart.tsx/test.tsx`, `LatestPricesChart.tsx/test.tsx`, `PriceChangeChart.tsx/test.tsx`, `HoldingComparisonChart.tsx/test.tsx`
- **Commit:** bffeca6
- **Learnings:**
  - Patterns: Stacked BarChart floating range bar — invisible base bar + colored range bar with same `stackId`; Tooltip suppresses base bar value with `[null, null]` return
  - Patterns: Recharts `<Cell>` component enables per-bar conditional coloring inside a `<Bar>` — map data index to color based on value sign
  - Gotchas: Parallel sub-agents ran independently and all passed; monitor `parallel_state.json` for completion before aggregating
---

## [2026-04-01 19:19] - Phase 4 Task 1: AllCategoriesTable
- **Implemented:** Scrollable sortable HTML table — all categories × all run dates; sort by Latest column via useState toggle; formatRunDate for date headers
- **Files changed:** `AllCategoriesTable.tsx`, `AllCategoriesTable.test.tsx`
- **Commit:** bffeca6
- **Learnings:**
  - Gotchas: When a value appears in both a run-date cell and the Latest cell, `getByText` fails with "found multiple elements" — use `getAllByText(...).length >= 1` instead
---

## [2026-04-01 19:22] - Phase 5 Tasks 1-2: Page Integration
- **Implemented:** Rewrote PriceHistory.tsx to integrate all 5 new components; wrote PriceHistory.test.tsx with 9 tests
- **Files changed:** `src/pages/PriceHistory.tsx`, `src/pages/PriceHistory.test.tsx`
- **Commit:** df0a39b
- **Learnings:**
  - Gotchas: `page-price-history` testid only renders after async data loads — first test used synchronous query and failed; must wrap even initial render assertions in `waitFor` when component shows a loading spinner first
  - Patterns: Mock all chart sub-components in page tests with simple `data-testid` divs — tests assertions become trivial and don't rely on Recharts internals
---

<!-- Learnings from implementation will be appended below -->

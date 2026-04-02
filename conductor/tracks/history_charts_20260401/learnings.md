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

<!-- Learnings from implementation will be appended below -->

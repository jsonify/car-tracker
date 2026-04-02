# Plan: Price History Page — Bug Fixes & Chart Enhancements

## Phase 1: Bug Fixes

- [x] Task 1: Date formatting utility & application <!-- dccbb3b -->
  - [ ] Write `formatRunDate(isoString: string): string` in `utils/dateUtils.ts`
  - [ ] Unit tests for `formatRunDate` (valid ISO, null/undefined guard, timezone)
  - [ ] Apply `formatRunDate` to `PriceChart` X-axis `tickFormatter`
  - [ ] Apply `formatRunDate` to `PriceChart` Tooltip `labelFormatter`
  - [ ] Apply `formatRunDate` to "Best Time to Book" card in `PriceHistoryPage`

- [x] Task 2: Fix tooltip category names <!-- 745a20c -->
  - [ ] Update `PriceChart` Tooltip `formatter` to return `[$X.XX, category_name]`
        instead of `[$X.XX, undefined]`
  - [ ] Update PriceChart tests to assert names appear

- [x] Task 3: Fix ReferenceLine label clipping <!-- 48e5b59 -->
  - [ ] Increase LineChart right margin to fit full "Holding $X.XX" label
  - [ ] Update PriceChart tests

## Phase 2: Chart Data Utilities
<!-- execution: parallel -->
<!-- depends: -->

- [x] Task 1: `buildPriceRangeData` utility + tests <!-- 836bc1f -->
  <!-- files: src/utils/chartData.ts, src/utils/chartData.test.ts -->
  - [x] Returns `{ category, min, max, range }[]` for visible categories

- [x] Task 2: `buildLatestPricesData` utility + tests <!-- 836bc1f -->
  <!-- files: src/utils/chartData.ts, src/utils/chartData.test.ts -->
  - [x] Returns `{ category, price }[]` sorted cheapest-first

- [x] Task 3: `buildPriceChangeData` utility + tests <!-- 836bc1f -->
  <!-- files: src/utils/chartData.ts, src/utils/chartData.test.ts -->
  - [x] Returns `{ category, delta, pctChange }[]` (first → latest price)

- [x] Task 4: `buildHoldingComparisonData` utility + tests <!-- 836bc1f -->
  <!-- files: src/utils/chartData.ts, src/utils/chartData.test.ts -->
  - [x] Returns `{ holdingPrice, currentBest }` or null when not configured

## Phase 3: New Chart Components
<!-- execution: parallel -->
<!-- depends: phase2 -->

- [x] Task 1: `PriceRangeChart` component + tests <!-- bffeca6 -->
  <!-- files: src/components/PriceRangeChart.tsx, src/components/PriceRangeChart.test.tsx -->
  - [x] BarChart with min/max bars per category

- [x] Task 2: `LatestPricesChart` component + tests <!-- bffeca6 -->
  <!-- files: src/components/LatestPricesChart.tsx, src/components/LatestPricesChart.test.tsx -->
  - [x] Horizontal BarChart sorted cheapest → most expensive

- [x] Task 3: `PriceChangeChart` component + tests <!-- bffeca6 -->
  <!-- files: src/components/PriceChangeChart.tsx, src/components/PriceChangeChart.test.tsx -->
  - [x] BarChart with conditional fill: green for drop, red for increase

- [x] Task 4: `HoldingComparisonChart` component + tests <!-- bffeca6 -->
  <!-- files: src/components/HoldingComparisonChart.tsx, src/components/HoldingComparisonChart.test.tsx -->
  - [x] Side-by-side bars: holding price vs. current best; fallback when unset

## Phase 4: All Categories Overview Table
<!-- depends: -->

- [x] Task 1: `AllCategoriesTable` component + tests <!-- bffeca6 -->
  <!-- files: src/components/AllCategoriesTable.tsx, src/components/AllCategoriesTable.test.tsx -->
  - [x] Scrollable table: all categories × all run dates
  - [x] Sortable by latest price column

## Phase 5: Page Integration
<!-- depends: phase1, phase2, phase3, phase4 -->

- [x] Task 1: Wire all new charts into `PriceHistoryPage` <!-- commit TBD -->
  <!-- files: src/pages/PriceHistory.tsx -->
  - [x] Keep existing insight cards (Best Time to Book, Savings Summary)
  - [x] Add 2-column chart grid: PriceRange, LatestPrices, PriceChange,
        HoldingComparison
  - [x] Add AllCategoriesTable below the grid

- [x] Task 2: Update `PriceHistoryPage` tests <!-- commit TBD -->
  <!-- files: src/pages/PriceHistory.test.tsx -->
  - [x] Assert new chart sections render; existing tests still pass

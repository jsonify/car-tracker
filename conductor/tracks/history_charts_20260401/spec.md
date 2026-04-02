# Spec: Price History Page — Bug Fixes & Chart Enhancements

## Overview
The Price History page has several display bugs and needs richer visualizations
to better tell the story of price data over time. This track fixes the broken
tooltip and date formatting issues, and adds five new chart types arranged in a
2-column grid below the existing "Price Trends" line chart.

## Functional Requirements

### Bug Fixes
1. **X-axis date formatting**: Format `run_at` ISO timestamps to a readable
   short form (e.g. "Mar 27") on the Price Trends X-axis.
2. **Tooltip label formatting**: Tooltip hover label must show the formatted
   date, not the raw ISO string.
3. **Tooltip entry names**: Each tooltip row must display the category name
   alongside its price (e.g. "Economy Car — $433.15"). Currently the name is
   `undefined` because the `formatter` returns `undefined` as the second element.
4. **Holding price label clipping**: The ReferenceLine label ("Holding $X.XX")
   is cut off at the right edge. Fix via chart margin or label position
   adjustment.
5. **"Best Time to Book" date formatting**: The card shows raw ISO timestamp;
   format to a readable date string (same formatter as the chart).

### New Charts (2-column grid below Price Trends)
6. **Price Range Bar Chart**: Ranged bar (or grouped min/max bars) per visible
   category across all tracked runs — reveals which categories fluctuate most.
7. **Latest Prices Snapshot**: Horizontal bar chart of the most recent price per
   visible category, sorted cheapest → most expensive. Instant "where things
   stand now" view.
8. **Price Change Summary**: Bar chart showing delta (first tracked price →
   latest) per visible category. Positive = up, negative = down; color-coded
   green/red.
9. **Holding Price Comparison**: Side-by-side bar comparing holding price vs.
   current best price for the holding vehicle type. Shows fallback message
   when no holding price is configured.
10. **All Categories Overview**: Compact data table showing price at each run
    date for all categories (not just visible ones). Sortable by latest price.

## Non-Functional Requirements
- All chart components follow existing Recharts + Tailwind v4 + design token
  patterns.
- No new npm dependencies.
- New utility functions must be pure and unit-tested (≥ 80% coverage per
  workflow.md).

## Acceptance Criteria
- [ ] X-axis on Price Trends shows short readable dates (not ISO strings)
- [ ] Tooltip label shows readable date
- [ ] Tooltip rows show "Category Name — $X.XX"
- [ ] Holding price ReferenceLine label is fully visible (not clipped)
- [ ] "Best Time to Book" card shows readable date
- [ ] Price Range chart renders for selected categories
- [ ] Latest Prices Snapshot renders sorted cheapest-first
- [ ] Price Change Summary shows deltas, green for drop, red for increase
- [ ] Holding Price Comparison renders when holding data exists; shows
      fallback otherwise
- [ ] All Categories Overview table renders all categories × all run dates
- [ ] All new utility functions have ≥ 80% test coverage

## Out of Scope
- Backend API changes (all data needed is in the existing `PriceHistory`
  response)
- Drill-down / click-through from charts to run detail
- Chart export or download
- Persisting chart preferences across sessions

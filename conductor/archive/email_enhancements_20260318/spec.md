# Spec: Email Enhancements — Holding Row Highlight, Sparklines & Smart Subject Line

## Overview

Enhance the HTML success email with three visual/UX improvements:
1. Background color highlight on the holding vehicle type row in each booking's table
2. Inline SVG sparkline charts in a new "Trend" column showing price history per vehicle category
3. A smart subject line showing each booking's holding vehicle price and holding comparison

## Functional Requirements

### 1. Holding Vehicle Row Highlight
- The row matching `booking.holding_vehicle_type` is tinted with a background color
- Tint color matches the existing holding banner palette:
  - Green tint if current best price < holding price (saving)
  - Amber tint if current best price ≥ holding price (over holding)
- If no holding vehicle type is configured, no rows are highlighted

### 2. Sparkline Trend Column
- A new "Trend" column is added to the right of the existing "Change" column
- Each row contains an inline SVG sparkline showing price history for that
  vehicle category across all prior runs for the same booking
- Price history is fetched from the SQLite database (best-per-category price per run)
- Sparkline behavior:
  - 1 data point: render a single dot (first reading)
  - 2+ data points: render a connected line chart
- SVG is generated server-side in Python and embedded in the Jinja2 template
- No external dependencies — pure Python math/string generation

### 3. Smart Email Subject Line
- Subject line reflects the holding vehicle comparison for each booking:
  - Saving: `✅ SAN_APRIL $393.07 (saving $24.98 vs holding)`
  - Over holding: `⚠️ SAN_APRIL $417.05 (over holding +$23.98)`
  - No holding configured: `SAN_APRIL` (no price detail)
- Multiple bookings are joined with ` · ` separator:
  `⚠️ SAN_APRIL $417.05 (+$23.98) · ✅ HAWAII_JULY $312.00 (-$45.00)`
- Booking name is uppercased in the subject for readability
- The price shown is the best current price for the holding vehicle type

## Non-Functional Requirements
- Sparkline SVGs must render in Gmail (inline SVG in HTML email)
- No JavaScript in the email
- Subject line stays under ~100 characters for single-booking case;
  multi-booking subject may be longer (acceptable)

## Acceptance Criteria
- [ ] Holding vehicle row is visually distinct with a background tint
- [ ] Tint color matches the holding banner (green = saving, amber = over)
- [ ] All vehicle category rows have a sparkline in the Trend column
- [ ] Single dot shown when only one historical price exists
- [ ] Sparklines accurately reflect price history from the database
- [ ] Change column is preserved alongside the new Trend column
- [ ] Subject shows ✅/⚠️ prefix, holding vehicle price, and delta for bookings with holdings
- [ ] Subject falls back gracefully for bookings without a holding price
- [ ] Multi-booking subject uses · separator
- [ ] Existing tests continue to pass; new logic has ≥ 80% test coverage

## Out of Scope
- Interactive or animated sparklines
- Sparklines in failure or monitoring-paused emails
- Per-brand (non-collapsed) sparklines
- Configurable sparkline dimensions or colors via config.yaml
- Subject line truncation logic for very long multi-booking names

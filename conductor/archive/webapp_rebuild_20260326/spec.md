# Spec: Webapp Rebuild — Velocity Dark Design System

## Overview

Rebuild the existing car-tracker webapp (React 19 + TypeScript + Vite frontend, FastAPI backend) to adopt the "Velocity Dark" premium design system from the incoming `web-app/` mockups. This is a visual redesign with page restructuring and backend enhancements — not a ground-up rewrite. The app remains a single-user personal tool.

The rebuild replaces the current 5-page layout with a 6-page structure, applies the full Velocity Dark design language, enriches the Booking Manager with per-booking city/location context, and extends the backend API to support new data points (volatility, savings tracking, alert configuration).

## Design System: Velocity Dark

All pages adopt the Velocity Dark design system in full:

- **Color Palette**: Amber primary (#fe9821), violet secondary (#a68cff), cyan tertiary (#81ecff), deep obsidian surfaces (#0e0d14), surface containers (#1a1921, #201e28, #26252f), error (#ff7351), on-surface (#f4eff9), on-surface-variant (#ada9b3)
- **Typography**: Manrope (headlines, font-weight 900) + Inter (body, font-weight 500). Prices always display-sm/headline-lg.
- **No-Line Rule**: Boundaries defined through tonal shifts, never borders
- **Glassmorphism**: Floating elements use backdrop-blur (20px) + 70% opacity backgrounds
- **Signature Texture**: Linear gradient from primary → primary-container on CTAs and accents
- **Elevation**: Tonal layer stacking instead of drop shadows
- **Ghost Border Fallback**: outline-variant at 15% opacity only where accessibility requires it
- **Icons**: Google Material Symbols Outlined (replacing any existing icon set)

## Page Structure

### 1. Dashboard (`/`)
Redesigned from `main_dashboard` mockup.
- Sidebar navigation (fixed, 256px) with app logo, nav links, "New Search" CTA, user profile card
- Top app bar with search input and filter controls
- Hero stats grid: aggregate market trend chart (Recharts, restyled), total saved, active price drops
- Active price alerts section (card-based)
- Upcoming bookings rail with countdown badges (days until pickup, urgency color coding)
- Recent runs summary

### 2. Booking Manager (`/bookings`)
Redesigned from `booking_manager` mockup. Replaces current Bookings page.
- Reservations table: rental company, dates, city/location, booked price, current price, savings delta
- Color-coded savings (tertiary) vs. hikes (error)
- CRUD operations (create, edit, delete bookings)
- Expanded detail view per booking: city/location context, price history mini-chart, holding comparison
- Sidebar contextual cards: savings summary, category volatility breakdown
- Status filter tabs: Active, Expired

### 3. Price History (`/price-history`)
Existing page, restyled with Velocity Dark.
- Booking selector dropdown
- Recharts line chart (restyled: Velocity Dark palette, Manrope/Inter typography)
- Best-time-to-book insight card
- Savings summary vs. holding price

### 4. Vehicles (`/vehicles`)
Existing page, restyled with Velocity Dark.
- Sortable, filterable, paginated table
- Filter by booking name and category
- Velocity Dark table styling (tonal row alternation, no borders)

### 5. Runs Log (`/runs`)
Existing page, restyled with Velocity Dark.
- Expandable run rows with nested vehicle table
- Holding vehicle type highlighted
- Velocity Dark card/table styling

### 6. Settings & Alerts (`/settings`)
New page inspired by `price_alert_settings` mockup.
- Per-booking alert configuration: holding price, target price thresholds
- Toggle switches: email notifications per booking
- System stats footer (sync frequency, alerts dispatched, server status)
- Email preferences (price drop alerts, market summaries, product updates)

## Backend Enhancements

### New/Extended Endpoints
- **Savings tracking**: Endpoint to compute per-booking savings (current best price vs. booked/holding price)
- **Volatility calculation**: Endpoint returning price volatility per vehicle category (price range, trend direction)
- **Alert/settings CRUD**: Endpoints to read/write per-booking alert configuration (holding price, thresholds, notification preferences)
- **Dashboard summary enhancement**: Extend existing `/dashboard/summary` with savings totals, active alert counts, volatility data

### Data Model Changes
- Booking model extended with: city/location field, alert preferences (notification toggles, target price)
- Settings storage: alert configuration persisted in config.yaml (consistent with existing pattern)

## Non-Functional Requirements

- **Responsiveness**: All pages responsive (mobile-friendly sidebar collapse, responsive grids)
- **Performance**: Sub-3s load on WiFi, lazy-load non-critical components
- **Accessibility**: Semantic HTML, WCAG 2.1 AA contrast ratios, keyboard navigation, sr-only labels
- **Test Coverage**: >=80% unit test coverage (Vitest) per workflow.md
- **Charting**: Recharts retained and restyled to Velocity Dark palette (no custom SVG charts)
- **Fonts**: Manrope + Inter loaded via Google Fonts (or local assets for performance)
- **Icons**: Material Symbols Outlined via Google Fonts CDN

## Acceptance Criteria

- [ ] All 6 pages render with Velocity Dark design system (colors, typography, no-line rule, glassmorphism, icons)
- [ ] Sidebar navigation with working routing across all pages
- [ ] Dashboard shows aggregate stats, upcoming bookings with countdown, recent runs
- [ ] Booking Manager supports full CRUD with expanded city/location detail per booking
- [ ] Price History chart uses Recharts restyled to Velocity Dark
- [ ] Vehicles table sortable/filterable with Velocity Dark styling
- [ ] Runs Log expandable rows with holding vehicle highlight
- [ ] Settings page allows per-booking alert config with notification toggles
- [ ] Backend endpoints support savings, volatility, and alert data
- [ ] All existing tests pass; new features have >=80% coverage
- [ ] Responsive layout on mobile viewports
- [ ] Accessibility: keyboard navigable, proper contrast, semantic markup

## Out of Scope

- Multi-user authentication / user accounts (remains single-user)
- User Profile & Billing page (no billing in a personal tool)
- City Tracking as a standalone page (city context embedded in Booking Manager instead)
- Market Comparison Matrix page (no multi-market data source exists)
- Real-time WebSocket price updates (stays polling/cron-based)
- Payment processing or subscription management

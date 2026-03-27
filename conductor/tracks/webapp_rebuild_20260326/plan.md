# Plan: Webapp Rebuild — Velocity Dark Design System

## Phase 1: Design System Foundation
<!-- execution: parallel -->
<!-- depends: -->

- [x] Task 1: Configure Velocity Dark Tailwind theme
  <!-- files: webapp/frontend/tailwind.config.ts, webapp/frontend/src/index.css -->
  - [x] Extend Tailwind config with Velocity Dark color palette (primary, secondary, tertiary, surface tiers, error, on-surface, on-surface-variant)
  - [x] Add Manrope + Inter font families to Tailwind config
  - [x] Write tests verifying theme token exports
  - [x] Replace existing CSS custom properties and base styles in index.css
  - [x] Add glassmorphism utility classes (backdrop-blur-[20px], bg-opacity-70)
  - [x] Add signature gradient utility (bg-gradient-to-r from-primary to-primary-container)

- [x] Task 2: Add Material Symbols and font loading
  <!-- files: webapp/frontend/index.html, webapp/frontend/src/main.tsx -->
  - [x] Add Google Fonts links for Manrope, Inter, Material Symbols Outlined
  - [x] Remove any existing icon library imports
  - [x] Create Icon component wrapper for Material Symbols
  - [x] Write tests for Icon component

- [x] Task 3: Create design system token reference
  <!-- files: webapp/frontend/src/styles/tokens.ts -->
  - [x] Export color, typography, spacing, and elevation constants
  - [x] Document ghost-border-fallback and no-line-rule patterns as reusable classes
  - [x] Write tests for token value correctness

## Phase 2: Backend Enhancements
<!-- execution: parallel -->
<!-- depends: -->

- [x] Task 1: Extend booking model with city/location and alert fields
  <!-- files: webapp/backend/models/booking.py, webapp/backend/tests/test_bookings.py -->
  - [x] Write tests for new Booking fields (city, alert_enabled, target_price, notification_prefs)
  - [x] Add fields to Pydantic Booking model
  - [x] Update config.yaml read/write to handle new fields
  - [x] Verify backward compatibility with existing bookings

- [x] Task 2: Add savings tracking endpoint
  <!-- files: webapp/backend/routers/analytics.py, webapp/backend/tests/test_analytics.py -->
  - [x] Write tests for savings calculation (current best vs. holding price per booking)
  - [x] Implement GET /bookings/{booking_name}/savings endpoint
  - [x] Return: booked_price, current_best, delta, percentage_change

- [x] Task 3: Add volatility calculation endpoint
  <!-- files: webapp/backend/routers/analytics.py, webapp/backend/tests/test_analytics.py -->
  <!-- depends: task2 -->
  - [x] Write tests for volatility computation (price range, std dev, trend direction per category)
  - [x] Implement GET /analytics/volatility endpoint
  - [x] Return: per-category volatility index, trend direction, price range

- [x] Task 4: Add settings/alerts CRUD endpoints
  <!-- files: webapp/backend/routers/settings.py, webapp/backend/tests/test_settings.py -->
  - [x] Write tests for alert config CRUD
  - [x] Create settings router with GET/PUT /settings/alerts
  - [x] Persist alert preferences to config.yaml
  - [x] Register router in main.py

- [x] Task 5: Enhance dashboard summary endpoint
  <!-- files: webapp/backend/routers/analytics.py, webapp/backend/tests/test_analytics.py -->
  <!-- depends: task2, task3 -->
  - [x] Write tests for enhanced summary (savings totals, alert counts, volatility)
  - [x] Extend GET /dashboard/summary response with new fields
  - [x] Ensure backward-compatible JSON structure

## Phase 3: Shared UI Components
<!-- execution: parallel -->
<!-- depends: phase1 -->

- [x] Task 1: Rebuild Sidebar component
  <!-- files: webapp/frontend/src/components/Sidebar.tsx, webapp/frontend/src/components/Sidebar.test.tsx -->
  - [x] Write tests for new sidebar (nav links for 6 pages, active state, user card, "New Search" CTA)
  - [x] Implement fixed 256px sidebar with Velocity Dark styling
  - [x] Tonal active state (bg + border-right-4), no borders elsewhere
  - [x] Collapsible on mobile viewports

- [x] Task 2: Rebuild Card component with glassmorphism variant
  <!-- files: webapp/frontend/src/components/Card.tsx, webapp/frontend/src/components/Card.test.tsx -->
  - [x] Write tests for Card variants (standard, glass, gradient-accent)
  - [x] Implement rounded-xl, surface-container bg, hover to surface-container-high
  - [x] Glass variant: backdrop-blur + semi-transparent bg

- [x] Task 3: Rebuild Badge component with Velocity Dark variants
  <!-- files: webapp/frontend/src/components/Badge.tsx, webapp/frontend/src/components/Badge.test.tsx -->
  - [x] Write tests for new color variants (primary, secondary, tertiary, error, on-surface-variant)
  - [x] Implement pill-style badges with tonal backgrounds

- [x] Task 4: Rebuild LoadingSpinner and EmptyState
  <!-- files: webapp/frontend/src/components/LoadingSpinner.tsx, webapp/frontend/src/components/EmptyState.tsx -->
  - [x] Restyle with Velocity Dark palette and Manrope/Inter typography
  - [x] Write/update tests

- [x] Task 5: Create TopAppBar component
  <!-- files: webapp/frontend/src/components/TopAppBar.tsx, webapp/frontend/src/components/TopAppBar.test.tsx -->
  - [x] Write tests for top bar (search input, filter button, responsive width)
  - [x] Implement with backdrop-blur, semi-transparent bg, calc(100% - 16rem) width
  - [x] Search input with primary focus ring

- [x] Task 6: Create StatsCard component
  <!-- files: webapp/frontend/src/components/StatsCard.tsx, webapp/frontend/src/components/StatsCard.test.tsx -->
  - [x] Write tests for stat display (value, label, trend indicator, icon)
  - [x] Implement with Velocity Dark tonal layering
  - [x] Support positive (tertiary) and negative (error) trend colors

- [x] Task 7: Create ToggleSwitch component
  <!-- files: webapp/frontend/src/components/ToggleSwitch.tsx, webapp/frontend/src/components/ToggleSwitch.test.tsx -->
  - [x] Write tests for toggle (checked/unchecked, onChange, disabled state)
  - [x] Implement styled toggle matching price_alert_settings mockup

- [x] Task 8: Rebuild BookingModal with Velocity Dark styling
  <!-- files: webapp/frontend/src/components/BookingModal.tsx, webapp/frontend/src/components/BookingModal.test.tsx -->
  - [x] Write tests for modal (create/edit modes, new fields: city, target_price, alert toggle)
  - [x] Restyle form inputs with Velocity Dark theme
  - [x] Glassmorphism overlay background

- [x] Task 9: Restyle PriceChart for Velocity Dark
  <!-- files: webapp/frontend/src/components/PriceChart.tsx, webapp/frontend/src/components/PriceChart.test.tsx -->
  - [x] Write tests for chart theming (Velocity Dark colors in series, tooltips, legend)
  - [x] Update Recharts color mapping to use Velocity Dark palette
  - [x] Manrope for chart labels, Inter for axis text

## Phase 4: Update API Client & Types
<!-- execution: sequential -->
<!-- depends: phase2 -->

- [x] Task 1: Extend API client with new types and endpoints
  <!-- files: webapp/frontend/src/api/client.ts, webapp/frontend/src/api/client.test.ts -->
  - [x] Write tests for new API functions
  - [x] Add TypeScript types: SavingsData, VolatilityData, AlertConfig, EnhancedDashboardSummary
  - [x] Add functions: getSavings, getVolatility, getAlertSettings, updateAlertSettings
  - [x] Extend existing Booking type with city, alert fields

## Phase 5: Page Rebuilds
<!-- execution: parallel -->
<!-- depends: phase3, phase4 -->

- [x] Task 1: Rebuild Dashboard page
  <!-- files: webapp/frontend/src/pages/Dashboard.tsx, webapp/frontend/src/pages/Dashboard.test.tsx -->
  - [x] Write tests for dashboard sections (stats grid, alerts, upcoming bookings, recent runs)
  - [x] Implement hero stats grid (bento layout, 8/4 split) with Recharts aggregate trend
  - [x] Active price alerts section with dismiss/action CTAs
  - [x] Upcoming bookings rail with countdown badges and urgency colors
  - [x] Recent runs summary list

- [x] Task 2: Rebuild Booking Manager page
  <!-- files: webapp/frontend/src/pages/Bookings.tsx, webapp/frontend/src/pages/Bookings.test.tsx -->
  - [x] Write tests for reservations table, CRUD, expanded detail, sidebar cards
  - [x] Implement reservations table (city, booked vs. current price, savings delta)
  - [x] Color-coded savings (tertiary) vs. hikes (error)
  - [x] Expandable detail view per booking with city context and mini price chart
  - [x] Sidebar contextual cards: savings summary, volatility breakdown
  - [x] Status filter tabs: Active, Expired

- [x] Task 3: Restyle Price History page
  <!-- files: webapp/frontend/src/pages/PriceHistory.tsx, webapp/frontend/src/pages/PriceHistory.test.tsx -->
  - [x] Write tests for restyled layout
  - [x] Apply Velocity Dark styling to booking selector, chart container, insight cards
  - [x] Ensure Recharts uses Velocity Dark theme via restyled PriceChart component

- [x] Task 4: Restyle Vehicles page
  <!-- files: webapp/frontend/src/pages/Vehicles.tsx, webapp/frontend/src/pages/Vehicles.test.tsx -->
  - [x] Write tests for restyled table
  - [x] Apply Velocity Dark table styling (tonal row alternation, no borders)
  - [x] Restyle filter controls and pagination

- [x] Task 5: Restyle Runs Log page
  <!-- files: webapp/frontend/src/pages/Runs.tsx, webapp/frontend/src/pages/Runs.test.tsx -->
  - [x] Write tests for restyled expandable rows
  - [x] Apply Velocity Dark styling to run rows and nested vehicle table
  - [x] Holding vehicle highlight with primary accent

- [x] Task 6: Build Settings & Alerts page
  <!-- files: webapp/frontend/src/pages/Settings.tsx, webapp/frontend/src/pages/Settings.test.tsx -->
  - [x] Write tests for alert form, active monitors, toggle switches, system stats
  - [x] Implement new alert form (sticky left column): city, dates, target price
  - [x] Active monitors list (right column) with per-booking toggles
  - [x] System stats footer
  - [x] Email preferences section with save button

## Phase 6: App Shell & Routing
<!-- execution: sequential -->
<!-- depends: phase5 -->

- [x] Task 1: Update App.tsx with new layout and routes
  <!-- files: webapp/frontend/src/App.tsx, webapp/frontend/src/App.test.tsx, webapp/frontend/src/App.css -->
  - [x] Write tests for routing (6 routes) and layout structure
  - [x] Integrate rebuilt Sidebar + TopAppBar into app shell
  - [x] Add /settings route for Settings & Alerts page
  - [x] Replace App.css with Velocity Dark base styles (or remove if index.css covers it)
  - [x] Verify all routes render correct pages

## Phase 7: Integration Testing & Polish
<!-- execution: sequential -->
<!-- depends: phase6 -->

- [ ] Task 1: End-to-end integration verification
  - [ ] Run full backend test suite, verify all pass
  - [ ] Run full frontend test suite, verify >=80% coverage
  - [ ] Verify API client <-> backend contract (types match responses)
  - [ ] Test responsive layout on mobile viewports
  - [ ] Verify keyboard navigation and accessibility (semantic HTML, contrast, sr-only labels)

- [ ] Task 2: Visual polish and consistency audit
  - [ ] Audit all pages against Velocity Dark mockup screenshots
  - [ ] Verify no-line-rule compliance (no stray borders)
  - [ ] Verify glassmorphism on all floating/modal elements
  - [ ] Verify Material Symbols icons render correctly across pages
  - [ ] Verify Recharts styling consistency across Dashboard and Price History

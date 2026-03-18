# Implementation Plan: React Web App — Car Tracker Dashboard

## Phase 1: Project Setup & Foundation
<!-- execution: parallel -->
<!-- depends: -->

- [x] Task 1: Initialize FastAPI backend
  <!-- files: webapp/backend/main.py, webapp/backend/database.py, webapp/backend/pyproject.toml, webapp/backend/tests/test_database.py -->
  - [ ] Create `webapp/backend/` directory structure
  - [ ] Add FastAPI, uvicorn dependencies (via uv)
  - [ ] Create `main.py` with app init and CORS config for localhost
  - [ ] Create `database.py` with SQLite connection helper pointing to existing DB
  - [ ] Write tests for DB connection helper
  - [ ] Verify 80% coverage, commit

- [x] Task 2: Initialize React/Vite frontend
  <!-- files: webapp/frontend/package.json, webapp/frontend/vite.config.ts, webapp/frontend/tailwind.config.ts, webapp/frontend/src/App.tsx, webapp/frontend/src/App.test.tsx -->
  - [ ] Scaffold `webapp/frontend/` with Vite + React + TypeScript
  - [ ] Install and configure Tailwind CSS (dark mode: class strategy)
  - [ ] Install React Router, Recharts, axios
  - [ ] Set up Vitest + React Testing Library
  - [ ] Write smoke test for App component render
  - [ ] Verify tests pass, commit

## Phase 2: FastAPI Backend — Core API Endpoints
<!-- execution: parallel -->

- [x] Task 1: Bookings CRUD endpoints
  <!-- files: webapp/backend/routers/bookings.py, webapp/backend/models/booking.py, webapp/backend/tests/test_bookings.py -->
  - [x] Write tests for GET /bookings, POST /bookings, PUT /bookings/{id}, DELETE /bookings/{id}
  - [x] Implement Pydantic models for Booking
  - [x] Implement CRUD endpoints reading/writing config.yaml bookings array
  - [x] Handle date/time format conversion (MM/DD/YYYY ↔ YYYY-MM-DD, 12h ↔ 24h)
  - [x] Verify tests pass, 80% coverage, commit

- [x] Task 2: Runs & vehicles endpoints
  <!-- files: webapp/backend/routers/runs.py, webapp/backend/routers/vehicles.py, webapp/backend/tests/test_runs.py, webapp/backend/tests/test_vehicles.py -->
  - [x] Write tests for GET /runs, GET /runs/{id}/vehicles
  - [x] Write tests for GET /vehicles (with pagination, sort, filter params)
  - [x] Implement endpoints reading from SQLite runs and vehicles tables
  - [x] Verify tests pass, 80% coverage, commit

- [x] Task 3: Price history & analytics endpoints
  <!-- files: webapp/backend/routers/analytics.py, webapp/backend/tests/test_analytics.py -->
  - [x] Write tests for GET /bookings/{id}/price-history
  - [x] Write tests for GET /dashboard/summary
  - [x] Implement price history endpoint (category → run → price time series)
  - [x] Implement dashboard summary (savings, volatility, countdowns)
  - [x] Verify tests pass, 80% coverage, commit

## Phase 3: React — Navigation Shell & Shared Components
<!-- execution: parallel -->
<!-- depends: -->

- [x] Task 1: App shell and routing
  <!-- files: webapp/frontend/src/App.tsx, webapp/frontend/src/components/Sidebar.tsx, webapp/frontend/src/pages/Dashboard.tsx, webapp/frontend/src/pages/Bookings.tsx, webapp/frontend/src/pages/PriceHistory.tsx, webapp/frontend/src/pages/Vehicles.tsx, webapp/frontend/src/pages/Runs.tsx, webapp/frontend/src/components/Sidebar.test.tsx -->
  - [x] Implement React Router with routes for all 5 sections
  - [x] Build sidebar nav with active state indicators and icons
  - [x] Create page stub components for each route
  - [x] Write tests for nav rendering and active route state
  - [x] Verify tests pass, commit

- [x] Task 2: Shared UI components & API client
  <!-- files: webapp/frontend/src/components/Card.tsx, webapp/frontend/src/components/Table.tsx, webapp/frontend/src/components/Badge.tsx, webapp/frontend/src/components/LoadingSpinner.tsx, webapp/frontend/src/components/EmptyState.tsx, webapp/frontend/src/api/client.ts, webapp/frontend/src/components/Card.test.tsx, webapp/frontend/src/components/Badge.test.tsx -->
  - [x] Build reusable components: Card, Table, Badge, LoadingSpinner, EmptyState
  - [x] Create typed API client (axios wrapper for all endpoints)
  - [x] Write tests for reusable components
  - [x] Verify tests pass, commit

## Phase 4: Dashboard Page
<!-- execution: parallel -->
<!-- depends: phase2, phase3 -->

- [x] Task 1: Summary cards and booking countdown widget
  <!-- files: webapp/frontend/src/pages/Dashboard.tsx, webapp/frontend/src/utils/countdown.ts, webapp/frontend/src/utils/countdown.test.ts -->
  - [x] Write tests for countdown logic and savings calculation utilities
  - [x] Implement summary cards (active bookings count, total runs, total savings)
  - [x] Implement booking timeline widget with days-remaining and urgency colors
  - [x] Wire to /dashboard/summary API endpoint
  - [x] Verify tests pass, commit

- [x] Task 2: Volatility highlight and recent activity
  <!-- files: webapp/frontend/src/pages/Dashboard.tsx, webapp/frontend/src/utils/volatility.ts, webapp/frontend/src/utils/volatility.test.ts -->
  - [x] Write tests for volatility ranking utility
  - [x] Implement price volatility highlight panel (top 2-3 volatile categories)
  - [x] Implement recent runs activity feed
  - [x] Verify tests pass, commit

## Phase 5: Bookings Manager Page
<!-- execution: sequential -->
<!-- depends: phase2, phase3 -->

- [x] Task 1: Bookings table with full CRUD
  <!-- files: webapp/frontend/src/pages/Bookings.tsx, webapp/frontend/src/components/BookingModal.tsx, webapp/frontend/src/utils/dateTime.ts, webapp/frontend/src/utils/dateTime.test.ts -->
  - [x] Write tests for BookingForm date/time validation and format conversion
  - [x] Implement bookings table with status column (active/expired)
  - [x] Implement Add/Edit modal with all booking fields
  - [x] Implement delete with confirmation dialog
  - [x] Wire all actions to bookings API endpoints
  - [x] Verify tests pass, commit

## Phase 6: Price History / Trends Page
<!-- execution: sequential -->
<!-- depends: phase2, phase3 -->

- [x] Task 1: Interactive price chart
  <!-- files: webapp/frontend/src/pages/PriceHistory.tsx, webapp/frontend/src/components/PriceChart.tsx, webapp/frontend/src/utils/chartData.ts, webapp/frontend/src/utils/chartData.test.ts -->
  - [x] Write tests for chart data transformation utilities
  - [x] Implement booking selector dropdown
  - [x] Implement Recharts multi-line chart with per-category overlays
  - [x] Add holding price horizontal reference line
  - [x] Add hover tooltips showing price, date, and delta
  - [x] Verify tests pass, commit

- [x] Task 2: Insights panel
  <!-- files: webapp/frontend/src/pages/PriceHistory.tsx, webapp/frontend/src/utils/insights.ts, webapp/frontend/src/utils/insights.test.ts -->
  <!-- depends: task1 -->
  - [x] Write tests for best-price-run detection logic
  - [x] Implement "Best time to book" annotation on chart
  - [x] Implement savings tracker summary (total saved vs. holding over time)
  - [x] Verify tests pass, commit

## Phase 7: Vehicles Table Page
<!-- execution: sequential -->
<!-- depends: phase2, phase3 -->

- [x] Task 1: Paginated, sortable, filterable vehicles table
  <!-- files: webapp/frontend/src/pages/Vehicles.tsx, webapp/frontend/src/utils/tableUtils.ts, webapp/frontend/src/utils/tableUtils.test.ts -->
  - [x] Write tests for filter/sort/pagination logic
  - [x] Implement vehicles table with all columns (run date, booking, name, brand, price, price/day, delta)
  - [x] Add filters: booking selector, category text search, date range
  - [x] Add sortable column headers (asc/desc toggle)
  - [x] Add pagination controls
  - [x] Verify tests pass, commit

## Phase 8: Runs Log Page
<!-- execution: sequential -->
<!-- depends: phase2, phase3 -->

- [x] Task 1: Runs table and run detail drill-down
  <!-- files: webapp/frontend/src/pages/Runs.tsx, webapp/frontend/src/utils/runUtils.ts, webapp/frontend/src/utils/runUtils.test.ts -->
  - [x] Write tests for holding-beat detection per run
  - [x] Implement runs table with holding-beat row highlight
  - [x] Implement click-to-expand run detail showing all vehicles for that run
  - [x] Verify tests pass, commit

## Phase 9: Integration & Polish
<!-- execution: sequential -->
<!-- depends: phase4, phase5, phase6, phase7, phase8 -->

- [x] Task 1: Error states, loading states, empty states
  - [x] Add loading spinners and error boundaries to all pages
  - [x] Add empty state components for pages with no data
  - [x] Verify all pages handle API errors gracefully
  - [x] Commit

- [x] Task 2: Startup scripts and documentation
  - [x] Write `webapp/start.sh` to launch uvicorn + vite dev in parallel
  - [x] Add `webapp/README.md` with setup and run instructions
  - [x] Commit

# Spec: React Web App — Car Tracker Dashboard

## Overview

A locally-hosted React web application paired with a FastAPI backend that provides
a beautiful, dark-mode interface for managing bookings, exploring price history,
and surfacing meaningful insights from the data collected by the Costco Travel
Car Tracker scraper.

The FastAPI server reads from (and writes to) the existing local SQLite database.
The React frontend communicates with this API and is run locally on demand.

## Functional Requirements

### FR1: Navigation & Layout
- Single-page application with sidebar or top-nav linking to all five sections
- Dark mode as the default (and only) theme
- Persistent layout shell with app name/branding

### FR2: Dashboard / Overview
- Summary cards showing: total active bookings, total scrape runs, overall
  savings vs. holding across all bookings
- Booking timeline widget: each booking shown with days-remaining countdown
  and urgency color coding (green → yellow → red as pick-up approaches)
- Price volatility highlight: top 2-3 most volatile vehicle categories
  across all bookings
- Recent activity feed: last N scrape runs with timestamps

### FR3: Bookings Manager
- Table of all bookings with columns: name, location, dates, vehicle type,
  holding price, status (active/expired)
- Add booking form: all fields required by config schema
  (location, pick-up date/time, drop-off date/time, vehicle type, holding price)
- Edit booking inline or via modal
- Delete booking with confirmation
- Date inputs handle MM/DD/YYYY display, stored as YYYY-MM-DD
- Time inputs handle 12h display, stored as HH:MM (24h)

### FR4: Price History / Trends
- Per-booking view: select a booking, see a rich interactive line chart of
  price history per vehicle category across all runs
- Category comparison: overlay multiple vehicle types on one chart for
  side-by-side comparison
- "Best time to book" insight panel: annotate chart with lowest-price run
  and surface the day-of-week / time pattern if detectable
- Savings tracker: show holding price as a horizontal reference line;
  highlight runs where best price was below holding

### FR5: Vehicles Table
- Paginated, sortable, filterable table of all vehicle records
- Columns: run date, booking, vehicle name, brand, total price, price/day,
  delta vs prior run
- Filter by booking, vehicle category, date range

### FR6: Runs Log
- Table of all scrape runs: ID, timestamp, booking name, vehicle count
- Click a run to see all vehicles captured in that run
- Highlight runs where any category beat the holding price

## Non-Functional Requirements

- **Local only**: no authentication required; binds to localhost
- **Dark mode UI**: consistent dark palette, high contrast text, colored
  accents for status indicators
- **Data-dense**: compact table rows, no wasted whitespace in tabular views
- **Card-based overview**: dashboard uses cards for summary stats and widgets
- **Rich charts**: interactive (hover tooltips, zoom/pan) via a charting library
  (e.g. Recharts or Chart.js)
- **FastAPI backend**: Python, reads/writes the existing SQLite DB; CORS
  configured for localhost React dev server
- **React frontend**: bootstrapped with Vite; Tailwind CSS for styling
- **No build/deploy complexity**: `uvicorn` for API, `vite dev` for frontend —
  both run locally

## Acceptance Criteria

- [ ] Dashboard loads with live data from the SQLite DB and shows all summary cards
- [ ] Bookings can be created, edited, and deleted via the UI; changes persist to DB
- [ ] Price history chart renders for any selected booking with category overlay support
- [ ] Holding price reference line visible on price history chart
- [ ] Vehicles table is paginated, sortable, and filterable by booking and date range
- [ ] Runs log shows all scrape runs; clicking a run shows its vehicle records
- [ ] All date/time inputs convert correctly between display format and storage format
- [ ] App runs fully offline with `uvicorn` + `vite dev` on localhost

## Out of Scope

- User authentication or multi-user support
- Deployment to any remote server or cloud
- Triggering scraper runs from the UI (scraper remains cron-driven)
- Editing raw config YAML directly in the UI (bookings only, not scraper config)
- Mobile / responsive design (desktop-only for now)

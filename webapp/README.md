# Car Tracker Dashboard

A local React web app for exploring Costco Travel car booking price data collected by the `car_tracker` scraper.

## Features

- **Dashboard** — Summary stats, booking countdowns with urgency colors, price volatility highlights, recent runs feed
- **Bookings** — Add, edit, and delete bookings with holding price and vehicle type tracking
- **Price History** — Interactive Recharts multi-line chart per vehicle category, with holding price reference line and best-time-to-book insights
- **Vehicles** — Sortable, filterable, paginated table of all scraped vehicle prices
- **Runs Log** — Expandable run rows showing all vehicles scraped per run, with holding-beat highlights

## Prerequisites

- Python ≥ 3.11 with [uv](https://docs.astral.sh/uv/) installed
- Node.js ≥ 18 with npm

## Setup

```bash
# From the project root — install Python dependencies (first time only)
uv sync

# Install frontend Node dependencies (first time only)
cd webapp/frontend
npm install
cd ../..
```

## Running

```bash
# From the project root
./webapp/start.sh
```

This starts both servers concurrently:

| Server   | URL                       |
|----------|---------------------------|
| Backend  | http://127.0.0.1:8000     |
| Frontend | http://localhost:5173     |

Open http://localhost:5173 in your browser. Press `Ctrl+C` to stop both servers.

## API Docs

FastAPI auto-generates interactive docs at http://127.0.0.1:8000/docs.

## Testing

```bash
# Backend tests (from project root)
uv run pytest webapp/backend/tests/ -v

# Frontend tests
cd webapp/frontend
npm test
```

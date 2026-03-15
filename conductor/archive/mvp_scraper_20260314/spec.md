# Spec: MVP — Scraper, Config & Storage

## Overview
Build the core pipeline for the Costco Travel Car Tracker:
YAML config → Playwright scraper → SQLite storage.

## Goals
- Read search parameters from a YAML config file
- Scrape https://www.costcotravel.com/rental-cars using Playwright
- Extract all listed vehicles with name/category, total price, and price per day
- Save results to a local SQLite database
- Run headless by default; `--debug` flag enables headed browser for development

## Out of Scope (future tracks)
- Email delivery
- Scheduling / cron
- HTML report generation

---

## Config File (`config.yaml`)

```yaml
search:
  pickup_location: "LAX"        # Airport code or city name
  pickup_date: "2026-04-01"     # YYYY-MM-DD
  pickup_time: "10:00"          # HH:MM (24hr)
  dropoff_date: "2026-04-05"    # YYYY-MM-DD
  dropoff_time: "10:00"         # HH:MM (24hr)

database:
  path: "data/results.db"       # Relative path to SQLite file
```

---

## Scraper Behavior
- Launch real Chrome (not Playwright's Chromium) via subprocess with `--remote-debugging-port`
  - Required: Costco Travel uses Akamai bot detection that blocks Playwright's bundled Chromium
  - `--debug` flag launches Chrome in headed mode; default is `--headless=new`
- Connect Playwright to Chrome via CDP (`connect_over_cdp`)
- Navigate to Costco Travel rental cars URL
- Fill in search form with config parameters
- Submit search and wait for results to load
- Extract for each vehicle:
  - Vehicle name / category (e.g. "Economy", "Full-Size SUV")
  - Total price for the rental period
  - Price per day
- Return results in the order they appear on the page

---

## SQLite Schema

### Table: `runs`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| run_at | DATETIME | UTC timestamp of scrape |
| pickup_location | TEXT | |
| pickup_date | TEXT | |
| pickup_time | TEXT | |
| dropoff_date | TEXT | |
| dropoff_time | TEXT | |

### Table: `vehicles`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| run_id | INTEGER | Foreign key → runs.id |
| position | INTEGER | Order on page (1-based) |
| name | TEXT | Vehicle name / category |
| total_price | REAL | Total rental price (USD) |
| price_per_day | REAL | Daily rate (USD) |

---

## CLI Interface

```bash
# Normal run (headless)
python -m car_tracker

# Debug run (headed browser)
python -m car_tracker --debug

# Specify alternate config
python -m car_tracker --config path/to/config.yaml
```

---

## Acceptance Criteria
- [ ] `config.yaml` is loaded and validated at startup
- [ ] Playwright navigates to Costco Travel and submits the search form
- [ ] At least one vehicle is extracted per successful run
- [ ] All extracted vehicles are saved to SQLite with correct run association
- [ ] `--debug` flag shows the browser window
- [ ] Graceful error message if scrape fails (no crash)

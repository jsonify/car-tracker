# Costco Travel Car Tracker

A scheduled scraping tool that monitors Costco Travel rental car prices and delivers results via email. Runs on a configurable schedule and tracks price changes over time, with optional holding price comparison.

## How It Works

1. Launches a real Chrome browser via CDP (to bypass bot detection)
2. Scrapes [costcotravel.com/rental-cars](https://www.costcotravel.com/rental-cars) with your configured search parameters
3. Saves results to a local SQLite database
4. Collapses results to the best (cheapest) price per vehicle category
5. Compares against the previous run to show price deltas
6. Optionally compares against a holding price for a specific vehicle type
7. Sends an HTML-formatted email summary

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (package manager)
- Google Chrome installed at the default macOS path
- A Gmail account (or other SMTP provider) for sending email

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Install Playwright browsers (for fallback/testing)

```bash
uv run playwright install chromium
```

### 3. Configure credentials

Create a `.env` file at `/Users/<you>/code/rental-car-pricer/.env` with your SMTP credentials:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=you@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=you@gmail.com
```

> For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your account password.

### 4. Configure search parameters

Edit `config.yaml`:

```yaml
search:
  pickup_location: "LAX"        # Airport code or city name
  pickup_date: "2026-04-01"     # YYYY-MM-DD
  pickup_time: "10:00"          # HH:MM (24hr)
  dropoff_date: "2026-04-05"    # YYYY-MM-DD
  dropoff_time: "10:00"         # HH:MM (24hr)

  # Optional: track savings vs. a price you've already locked in.
  # Both fields must be present together, or both omitted.
  holding_price: 396.63         # Price of your current reservation
  holding_vehicle_type: "Economy Car"  # Vehicle category to compare against

database:
  path: "data/results.db"       # Relative path to SQLite file
```

The `data/` directory is created automatically on first run.

## Running

```bash
uv run python -m car_tracker
```

Or with a custom config path:

```bash
uv run python -m car_tracker --config /path/to/config.yaml
```

For debugging (opens a visible browser window):

```bash
uv run python -m car_tracker --debug
```

## Email Output

Each run sends an HTML email with:

- A table of all vehicle categories and their best (cheapest) price
- Price change vs. the previous run (up/down arrows with delta)
- A holding price summary banner (if configured) showing how much you'd save vs. your current reservation

On scrape failure, a failure notification email is sent instead.

## Scheduling with cron

To run automatically twice a week (e.g. Monday and Thursday at 8 AM):

```bash
crontab -e
```

Add:

```
0 8 * * 1,4 cd /Users/<you>/code/car-tracker && /Users/<you>/code/car-tracker/.venv/bin/python -m car_tracker >> /tmp/car-tracker.log 2>&1
```

## Project Structure

```
car-tracker/
├── config.yaml              # Search parameters and database path
├── src/car_tracker/
│   ├── __main__.py          # Entry point and main pipeline
│   ├── config.py            # Config loading and validation
│   ├── scraper.py           # Playwright browser automation
│   ├── database.py          # SQLite storage
│   ├── emailer.py           # Email rendering and delivery
│   └── templates/           # Jinja2 HTML email templates
├── tests/                   # Unit tests
├── data/                    # SQLite database (created on first run, git-ignored)
└── pyproject.toml
```

## Development

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=car_tracker --cov-report=term-missing
```

Lint:

```bash
uv run ruff check src tests
```

## Notes

- Costco Travel uses Akamai bot detection — the scraper always uses a real Chrome installation via CDP, not Playwright's bundled Chromium.
- The `.env` credentials file is loaded from a fixed path and is never committed to the repo.
- `config.yaml` contains no secrets and is committed.
- The SQLite database file is git-ignored.

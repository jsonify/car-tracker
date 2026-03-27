# Costco Travel Car Tracker

A scheduled scraping tool that monitors Costco Travel rental car prices across multiple bookings and delivers results via email. Runs on a configurable schedule and tracks price changes over time, with optional holding price comparison per booking. Bookings are automatically removed when their pick-up date passes, and monitoring pauses with a one-time notification when no bookings remain.

## How It Works

1. Removes any bookings whose pick-up date has already passed from `config.yaml` and pushes the change to git
2. If no bookings remain, sends a one-time "monitoring paused" notification email and exits — no further emails until a new booking is added
3. Launches a real Chrome browser via CDP (to bypass bot detection)
4. Iterates over all active bookings in order, scraping each independently
5. Saves results to a local SQLite database tagged by booking name
6. Collapses results to the best (cheapest) price per vehicle category
7. Compares against the previous run to show price deltas
8. Optionally compares against a holding price for a specific vehicle type
9. Sends a single HTML email with one section per booking, including a countdown to each booking's pick-up date

## Adding a New Booking

When you sign up for a new Costco Travel reservation and want to start tracking it:

### 1. Add it to `config.yaml` (or via iMessage)

**Direct edit** (takes effect immediately on the next run):
```yaml
bookings:
  - name: vegas_june
    pickup_location: "LAS"
    pickup_date: "2026-06-10"
    pickup_time: "12:00"
    dropoff_date: "2026-06-15"
    dropoff_time: "12:00"
    holding_price: 350.00          # Optional: your current locked-in price
    holding_vehicle_type: "Standard Car"
```

**Via iMessage** (if you're away from your machine):
```
add booking vegas_june LAS 2026-06-10 12:00 2026-06-15 12:00
```

### 2. Does adding a booking trigger a run?

**No.** Adding a booking — whether via config edit or iMessage — does not automatically trigger a scrape. The system is schedule-driven, not event-driven.

To run immediately after adding:

```bash
uv run python -m scripts.check_imessage && uv run python -m car_tracker
```

Or skip the iMessage check if you edited `config.yaml` directly:

```bash
uv run python -m car_tracker
```

### 3. What happens on the next scheduled run

1. `check_imessage.py` fires first — picks up any pending iMessage commands and applies them to `config.yaml`
2. `car_tracker` scrapes prices for all active bookings and emails results
3. Your new booking appears as a section in the email with current prices, deltas vs. the prior run, and a countdown to pick-up

After that, every scheduled run monitors your booking automatically until its pick-up date passes, at which point it's removed from `config.yaml` and monitoring pauses if no bookings remain.

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

Create a `.env` file in the project root with your SMTP credentials:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=you@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=you@gmail.com
```

> For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your account password.

### 4. Configure bookings

Edit `config.yaml` with a `bookings:` list — one entry per trip you want to track:

```yaml
bookings:
  - name: hawaii_may           # Unique label used in emails and iMessage commands
    pickup_location: "HNL"     # Airport code or city name
    pickup_date: "2026-05-01"  # YYYY-MM-DD
    pickup_time: "10:00"       # HH:MM (24hr)
    dropoff_date: "2026-05-08"
    dropoff_time: "10:00"

    # Optional: track savings vs. a price you've already locked in.
    # Both fields must be present together, or both omitted.
    holding_price: 420.00
    holding_vehicle_type: "Economy Car"

  - name: vegas_june
    pickup_location: "LAS"
    pickup_date: "2026-06-10"
    pickup_time: "12:00"
    dropoff_date: "2026-06-15"
    dropoff_time: "12:00"
    holding_price: 199.00
    holding_vehicle_type: "Standard Car"

database:
  path: "data/results.db"      # Relative path to SQLite file

imessage:
  phone_number: "+15551234567" # Phone number to watch for remote config commands
```

The `data/` directory is created automatically on first run. You can track as many bookings as you like — each is scraped and reported independently in the same run.

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

Each run sends a single HTML email containing one section per booking. Each section shows:

- The booking name and search parameters (location, dates)
- A countdown line: **"X days until your booking"** (or **"Today is your booking day!"** on pick-up day)
- A table of all vehicle categories and their best (cheapest) price
- Price change vs. the previous run (up/down arrows with delta)
- A holding price summary banner (if configured) showing how much you'd save vs. your current reservation

On scrape failure for a booking, a failure notification email is sent for that booking individually and the run continues with remaining bookings.

### Booking expiration and monitoring pause

After a booking's pick-up date passes, it is automatically removed from `config.yaml` on the next run and the change is committed and pushed to git. If the last booking expires (or the bookings list is otherwise empty), a single **"Monitoring Paused"** notification email is sent — subsequent runs are silent until a new booking is added, at which point monitoring resumes automatically.

## Remote Config Updates via iMessage

You can update a booking's holding price and vehicle type by sending an iMessage from your configured phone number. The `check_imessage` script is designed to run before each scrape (e.g. via cron).

All commands are case-insensitive. Any matching command updates `config.yaml`, commits, and pushes automatically.

> **Ambiguity rule:** Natural-language commands that don't specify a booking name are only applied when there is exactly one booking configured. With multiple bookings and no name, the command is ignored to avoid updating the wrong entry.

### Update holding price and type together (structured)

```
update holding <name_or_index> <price> <vehicle_type>
```

```
update holding hawaii_may 380.00 Economy Car
update holding las_june 175.00 Compact Car
update holding 1 420.00 Standard Car
update holding 2 199.00 Economy Car
```

### Update holding price only

```
update holding price to 350 for san_april
set san_april holding price to 350
update holding price to $299.99 for las_june
```

Single-booking shorthand (only works when exactly one booking is configured):
```
update holding price to 375
set holding price to $400.50
```

### Update holding vehicle type only

```
update holding type to Standard Car for san_april
update holding vehicle type to Economy Car for las_june
set san_april holding type to Standard Car
set las_june holding vehicle type to SUV
```

Single-booking shorthand:
```
set holding type to SUV
update holding type to Economy Car
```

### Add a new booking

```
add booking <name> <location> <pickup_date> <pickup_time> <dropoff_date> <dropoff_time>
```

```
add booking hawaii_may HNL 2026-05-01 10:00 2026-05-08 10:00
add booking portland PDX 2026-07-01 09:00 2026-07-05 09:00
```

Dates must be `YYYY-MM-DD` and times `HH:MM` (24hr). The new booking has no holding price until you set one.

### List bookings

```
list bookings
```

Returns a numbered list of active bookings with their current holding price and vehicle type.

### Running the iMessage checker

```bash
uv run python -m scripts.check_imessage
```

See `docs/imessage_shortcut_setup.md` for macOS Full Disk Access setup and automation options (manual, macOS Shortcuts, or cron).

## Scheduling with cron

To run automatically twice a week (e.g. Monday and Thursday at 8 AM):

```bash
crontab -e
```

Add:

```
0 8 * * 1,4 cd /Users/<you>/code/car-tracker && /usr/sbin/lsof -ti tcp:9222 | xargs kill -9 2>/dev/null; /Users/<you>/code/car-tracker/.venv/bin/python -m scripts.check_imessage >> /tmp/car-tracker.log 2>&1 && /Users/<you>/code/car-tracker/.venv/bin/python -m car_tracker >> /tmp/car-tracker.log 2>&1
```

## Project Structure

```
car-tracker/
├── config.yaml              # Bookings list and database path
├── src/car_tracker/
│   ├── __main__.py          # Entry point: expires bookings, iterates active ones, sends email
│   ├── config.py            # Config loading and validation (AppConfig, BookingConfig)
│   ├── lifecycle.py         # Booking expiration: removes past bookings from config.yaml + git push
│   ├── state.py             # App state helpers: read/write data/imessage_state.json
│   ├── scraper.py           # Playwright browser automation
│   ├── database.py          # SQLite storage (booking_name-scoped)
│   ├── emailer.py           # Email rendering and delivery (incl. countdown + monitoring paused)
│   └── templates/           # Jinja2 HTML email templates
├── scripts/
│   ├── check_imessage.py    # Poll iMessage for remote config update commands
│   └── update_config.py     # Parse and apply config updates from iMessage text
├── docs/
│   └── imessage_shortcut_setup.md
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
- Old single-booking configs using a top-level `search:` key are no longer supported and will raise a `ConfigError` with a migration hint.

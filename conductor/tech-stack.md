# Tech Stack: Costco Travel Car Tracker

## Language
- Python 3.11+

## Scraping
- Playwright (handles JavaScript-rendered content on Costco Travel)
- playwright-python (async browser automation)

## Data Storage
- SQLite (via Python built-in `sqlite3`)

## Email Delivery
- smtplib + email.mime (Python standard library)
- OR yagmail (simplified Gmail integration)

## Scheduling
- cron (system-level, twice-weekly via crontab)
- run.sh (bash) — cron wrapper: git pull to sync remote config changes, then exec scraper

## Configuration
- YAML config file (via PyYAML)

## HTML Generation
- Jinja2 (templating for HTML email)

## Dependency Management
- uv (fast Python package manager + project tool)

## Environment
- Runs locally on macOS

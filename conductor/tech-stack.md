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

## Remote Config Updates
- `scripts/check_imessage.py` — reads `~/Library/Messages/chat.db`, parses natural-language
  holding price commands, patches `config.yaml`, commits and pushes via subprocess
- Triggered via macOS Shortcut, cron, or automatically by `run.sh` before each scraper run

## SVG Sparklines
- Pure Python inline SVG generation (no external library) — embedded in Jinja2 HTML email templates

## Environment
- Runs locally on macOS

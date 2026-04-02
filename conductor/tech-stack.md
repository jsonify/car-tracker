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

## Web Dashboard (webapp/)
- FastAPI (Python async REST API framework)
- uvicorn (ASGI server)
- React 19 + Vite + TypeScript (frontend)
- Tailwind CSS v4 (dark-mode styling)
- React Router v6 (client-side routing)
- Recharts (interactive price charts)
- axios (typed HTTP client)
- Vitest + React Testing Library (frontend unit tests)
- httpx (FastAPI TestClient peer dep)

## Environment
- Runs locally on macOS

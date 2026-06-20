#!/usr/bin/env bash
# run.sh — cron wrapper for car-tracker
#
# 1. git pull to pick up any config changes made on GitHub.com
# 2. Activate the project virtualenv and run the scraper
#
# If git pull fails for any reason, a warning is logged and the scraper runs
# with the existing local config — the run is never aborted due to a pull failure.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$REPO_DIR/car-tracker.log"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
LOCKFILE="$REPO_DIR/.run.lock"

# ---------------------------------------------------------------------------
# 0. Acquire lock — prevent concurrent runs (e.g. launchd + Shortcuts overlap)
# ---------------------------------------------------------------------------
if [ -f "$LOCKFILE" ] && kill -0 "$(cat "$LOCKFILE" 2>/dev/null)" 2>/dev/null; then
    echo "[$TIMESTAMP] run.sh: another instance is already running (pid $(cat "$LOCKFILE")); exiting" >> "$LOG"
    exit 0
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

# ---------------------------------------------------------------------------
# 1. git pull (best-effort, non-fatal)
# ---------------------------------------------------------------------------
echo "[$TIMESTAMP] run.sh: starting git pull" >> "$LOG"

if git -C "$REPO_DIR" pull --rebase --autostash >> "$LOG" 2>&1; then
    echo "[$TIMESTAMP] run.sh: git pull succeeded" >> "$LOG"
else
    echo "[$TIMESTAMP] run.sh: WARNING — git pull failed; proceeding with local config" >> "$LOG"
fi

# ---------------------------------------------------------------------------
# 2. Run scraper
# ---------------------------------------------------------------------------
cd "$REPO_DIR"
source "$REPO_DIR/.venv/bin/activate"
exec python -m car_tracker --config "$REPO_DIR/config.yaml"

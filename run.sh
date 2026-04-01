#!/usr/bin/env bash
# run.sh — cron wrapper for car-tracker
#
# 1. git pull to pick up any config changes made on GitHub.com
# 2. check_imessage — apply any pending iMessage config commands, commit & push
# 3. Activate the project virtualenv
# 4. Run the scraper
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
exec 9>"$LOCKFILE"
if ! flock -n 9; then
    echo "[$TIMESTAMP] run.sh: another instance is already running; exiting" >> "$LOG"
    exit 0
fi

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
# 2. check_imessage — apply any pending iMessage config commands (best-effort)
# ---------------------------------------------------------------------------
cd "$REPO_DIR"
source "$REPO_DIR/.venv/bin/activate"

echo "[$TIMESTAMP] run.sh: checking iMessage for config updates" >> "$LOG"
IMESSAGE_EXIT=0
python -m scripts.check_imessage --config "$REPO_DIR/config.yaml" >> "$LOG" 2>&1 || IMESSAGE_EXIT=$?

if [ "$IMESSAGE_EXIT" -eq 2 ]; then
    echo "[$TIMESTAMP] run.sh: car_tracker already ran on-demand via iMessage; skipping scheduled run" >> "$LOG"
    exit 0
elif [ "$IMESSAGE_EXIT" -ne 0 ]; then
    echo "[$TIMESTAMP] run.sh: WARNING — iMessage check failed; proceeding with existing config" >> "$LOG"
else
    echo "[$TIMESTAMP] run.sh: iMessage check complete" >> "$LOG"
fi

# ---------------------------------------------------------------------------
# 3. Run scraper
# ---------------------------------------------------------------------------
exec python -m car_tracker --config "$REPO_DIR/config.yaml"

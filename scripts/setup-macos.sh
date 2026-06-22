#!/usr/bin/env bash
#
# setup-macos.sh — one-command setup for scheduled, headless car-tracker runs.
#
# Installs Python deps, ensures a .env exists, optionally seeds Costco cookies,
# then installs and loads a LaunchAgent that runs the scraper headless every
# Monday and Thursday at 04:00. Safe to re-run (idempotent).
#
# Usage:
#   ./scripts/setup-macos.sh
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_LABEL="com.cartracker"
PLIST_DEST="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
PLIST_TEMPLATE="$REPO_DIR/deploy/${PLIST_LABEL}.plist.template"
CHROME_PATH="${CAR_TRACKER_CHROME_PATH:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m!! \033[0m %s\n' "$1"; }
die()  { printf '\033[1;31mxx \033[0m %s\n' "$1" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 1. Prerequisites
# ---------------------------------------------------------------------------
say "Checking prerequisites"
command -v uv  >/dev/null 2>&1 || die "uv not found. Install: brew install uv"
command -v git >/dev/null 2>&1 || die "git not found. Install: brew install git"
[ -x "$CHROME_PATH" ] || die "Google Chrome not found at: $CHROME_PATH
  Install Chrome, or set CAR_TRACKER_CHROME_PATH and re-run."

# ---------------------------------------------------------------------------
# 2. Python dependencies
# ---------------------------------------------------------------------------
say "Installing Python dependencies (uv sync)"
( cd "$REPO_DIR" && uv sync )

# ---------------------------------------------------------------------------
# 3. .env credentials
# ---------------------------------------------------------------------------
if [ ! -f "$REPO_DIR/.env" ]; then
    say "Creating .env template (fill in your credentials)"
    cat > "$REPO_DIR/.env" <<'EOF'
# SMTP (for result emails). For Gmail use an App Password, not your login.
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=you@gmail.com
SENDER_PASSWORD=your-gmail-app-password
RECIPIENT_EMAIL=you@gmail.com

# Costco login — used only as a fallback to refresh cookies when the cached
# session expires. Headless runs rely on cached cookies (data/cookies.json).
COSTCO_USERNAME=your-costco-login-email
COSTCO_PASSWORD=your-costco-password
EOF
    warn ".env created at $REPO_DIR/.env — edit it with real values, then re-run this script."
    exit 0
else
    say ".env already present — leaving it untouched"
fi

# ---------------------------------------------------------------------------
# 4. Seed cookies (one headed login so headless runs have a valid session)
# ---------------------------------------------------------------------------
if [ ! -f "$REPO_DIR/data/cookies.json" ]; then
    warn "No cached cookies yet (data/cookies.json missing)."
    printf "    Run a one-time headed seed login now? A visible Chrome will open. [y/N] "
    read -r reply
    if [[ "$reply" =~ ^[Yy]$ ]]; then
        say "Seeding cookies — log in if prompted, then let it finish"
        ( cd "$REPO_DIR" && uv run python -m car_tracker --debug ) || \
            warn "Seed run did not complete cleanly — you can retry: uv run python -m car_tracker --debug"
    else
        warn "Skipping seed. Headless runs will fail until cookies exist."
        warn "Seed later with: uv run python -m car_tracker --debug"
    fi
else
    say "Cached cookies already present — skipping seed"
fi

# ---------------------------------------------------------------------------
# 5. Install + load the LaunchAgent
# ---------------------------------------------------------------------------
say "Installing LaunchAgent at $PLIST_DEST"
[ -f "$PLIST_TEMPLATE" ] || die "Missing template: $PLIST_TEMPLATE"
mkdir -p "$HOME/Library/LaunchAgents"
sed "s#__REPO_DIR__#${REPO_DIR}#g" "$PLIST_TEMPLATE" > "$PLIST_DEST"

# Reload cleanly if already loaded.
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load -w "$PLIST_DEST"
say "LaunchAgent loaded — runs Mon & Thu at 04:00, headless"

# ---------------------------------------------------------------------------
# 6. Wake schedule (so a sleeping Mac runs on time)
# ---------------------------------------------------------------------------
cat <<EOF

$(say "Almost done — one manual step")
To wake the Mac ~2 min before each run (it needs sudo), run:

    sudo pmset repeat wake MR 03:58:00

Notes:
  • A user must stay logged in (screen may be locked).
  • Logs: $REPO_DIR/car-tracker.log  and  $REPO_DIR/launchd.*.log
  • Test the job now without waiting:  launchctl start ${PLIST_LABEL}
  • Remove later:  launchctl unload "$PLIST_DEST" && sudo pmset repeat cancel
EOF

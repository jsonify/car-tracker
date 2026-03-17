"""Entry point for the car-tracker Discord bot.

Usage:
    python scripts/run_discord_bot.py
    python scripts/run_discord_bot.py --config /path/to/config.yaml

The bot token is read from DISCORD_BOT_TOKEN in the .env file.

Setup:
    1. Create a Discord application at https://discord.com/developers/applications
    2. Add a bot to the application and copy the token
    3. Add DISCORD_BOT_TOKEN=<token> to your .env file
    4. Add DISCORD_WEBHOOK_URL=<url> to your .env file (for cron notifications)
    5. Invite the bot to your server with the applications.commands scope
    6. Run this script to start the bot
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the project root is on sys.path when run directly
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from car_tracker.discord_bot import run_bot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run_discord_bot",
        description="Run the car-tracker Discord bot.",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        metavar="PATH",
        help="Path to YAML config file (default: config.yaml).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        run_bot(args.config)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

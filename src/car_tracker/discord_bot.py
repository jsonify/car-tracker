"""Discord bot for car-tracker slash commands.

Run with: python scripts/run_discord_bot.py

Required env vars:
    DISCORD_BOT_TOKEN   — bot token from Discord Developer Portal
    DISCORD_CHANNEL_ID  — channel ID where the bot operates (optional; restricts commands)

Optional env vars:
    DISCORD_WEBHOOK_URL — if set, scrape results are also posted as embeds

Slash commands:
    /scrape [booking]             — trigger an immediate scrape
    /prices [booking]             — show latest prices from the database
    /history <booking> <vehicle>  — show price history for a vehicle category
    /holding <booking> <price> <vehicle> — update the holding price for a booking
    /bookings                     — list all configured bookings
    /status                       — show last run info for all bookings
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

import discord
from discord import app_commands
from dotenv import load_dotenv

from car_tracker.config import BookingConfig, load_config
from car_tracker.database import (
    VehicleRecord,
    get_latest_run_vehicles,
    get_price_history,
    get_prior_run_vehicles,
    init_db,
    save_run,
    save_vehicles,
)
from car_tracker.emailer import (
    BookingSection,
    best_per_type,
    build_delta,
    build_holding_summary,
    extract_category,
)

_ENV_PATH = Path("/Users/jasonrueckert/code/car-tracker/.env")

# Discord embed colors
_COLOR_GREEN = 0x2ECC71
_COLOR_RED = 0xE74C3C
_COLOR_BLUE = 0x3498DB
_COLOR_ORANGE = 0xE67E22


def _fmt_price(price: float) -> str:
    return f"${price:,.2f}"


def _fmt_delta(delta: float | None, is_new: bool) -> str:
    if is_new:
        return "🆕 New"
    if delta is None:
        return "—"
    if delta < 0:
        return f"▼ ${abs(delta):.2f}"
    if delta > 0:
        return f"▲ ${delta:.2f}"
    return "—"


def _prices_embed(run_at: str, vehicles: list[VehicleRecord], booking: BookingConfig) -> discord.Embed:
    """Build a Discord embed showing current prices for a booking."""
    lines = [f"{'Vehicle':<24} {'Price':>8}  {'$/day':>6}"]
    lines.append("─" * 42)
    for v in vehicles:
        name = v.name[:24] if len(v.name) > 24 else v.name
        # Strip brand suffix for display
        cat = extract_category(v.name)
        cat = cat[:24] if len(cat) > 24 else cat
        lines.append(f"{cat:<24} {_fmt_price(v.total_price):>8}  {_fmt_price(v.price_per_day):>6}")

    ts_display = run_at[:16].replace("T", " ") if "T" in run_at else run_at[:16]

    embed = discord.Embed(
        title=f"🚗 {booking.pickup_location} · {booking.pickup_date} → {booking.dropoff_date}",
        description="```\n" + "\n".join(lines) + "\n```",
        color=_COLOR_BLUE,
    )
    embed.set_footer(text=f"Last run: {ts_display} UTC · {booking.name}")
    return embed


class CarTrackerBot(discord.Client):
    def __init__(self, config_path: str) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.config_path = config_path
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()
        print("Slash commands synced.")

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (id={self.user.id})")

    def _load_config(self):
        return load_config(self.config_path)

    def _booking_names(self) -> list[str]:
        try:
            return [b.name for b in self._load_config().bookings]
        except Exception:
            return []

    def _db_path(self) -> str:
        return self._load_config().database.path


def _booking_autocomplete(choices_fn):
    """Decorator factory for booking name autocomplete."""
    async def autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        names = choices_fn(interaction)
        return [
            app_commands.Choice(name=n, value=n)
            for n in names
            if current.lower() in n.lower()
        ][:25]
    return autocomplete


def setup_commands(bot: CarTrackerBot, config_path: str) -> None:
    """Register all slash commands on the bot's command tree."""

    @bot.tree.command(name="bookings", description="List all configured bookings.")
    async def bookings_cmd(interaction: discord.Interaction) -> None:
        try:
            config = load_config(config_path)
        except Exception as exc:
            await interaction.response.send_message(f"❌ Failed to load config: {exc}", ephemeral=True)
            return

        lines = []
        for b in config.bookings:
            holding = (
                f"  Holding: {_fmt_price(b.holding_price)} ({b.holding_vehicle_type})"
                if b.holding_price and b.holding_vehicle_type
                else ""
            )
            lines.append(
                f"**{b.name}**\n"
                f"  {b.pickup_location} · {b.pickup_date} {b.pickup_time} → "
                f"{b.dropoff_date} {b.dropoff_time}"
                + (f"\n{holding}" if holding else "")
            )

        embed = discord.Embed(
            title="📋 Configured Bookings",
            description="\n\n".join(lines) if lines else "No bookings configured.",
            color=_COLOR_BLUE,
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="status", description="Show last run info for all bookings.")
    async def status_cmd(interaction: discord.Interaction) -> None:
        try:
            config = load_config(config_path)
        except Exception as exc:
            await interaction.response.send_message(f"❌ Failed to load config: {exc}", ephemeral=True)
            return

        db_path = config.database.path
        lines = []
        for b in config.bookings:
            run_at, vehicles = get_latest_run_vehicles(db_path, b.name)
            if run_at:
                ts = run_at[:16].replace("T", " ")
                best = min((v.total_price for v in vehicles), default=None)
                best_str = f" · best price: {_fmt_price(best)}" if best else ""
                lines.append(f"**{b.name}**: last run {ts} UTC{best_str}")
            else:
                lines.append(f"**{b.name}**: no runs yet")

        embed = discord.Embed(
            title="📊 Bot Status",
            description="\n".join(lines) if lines else "No bookings configured.",
            color=_COLOR_BLUE,
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="prices", description="Show latest prices from the database.")
    @app_commands.describe(booking="Booking name (defaults to first booking)")
    async def prices_cmd(interaction: discord.Interaction, booking: str | None = None) -> None:
        try:
            config = load_config(config_path)
        except Exception as exc:
            await interaction.response.send_message(f"❌ Failed to load config: {exc}", ephemeral=True)
            return

        if booking is None:
            b = config.bookings[0]
        else:
            try:
                b = config.get_booking_by_name(booking)
            except KeyError:
                names = ", ".join(x.name for x in config.bookings)
                await interaction.response.send_message(
                    f"❌ Unknown booking `{booking}`. Available: {names}", ephemeral=True
                )
                return

        run_at, vehicles = get_latest_run_vehicles(config.database.path, b.name)
        if not run_at:
            await interaction.response.send_message(
                f"No data yet for booking `{b.name}`. Run `/scrape` first.", ephemeral=True
            )
            return

        # Collapse to best per category
        best: dict[str, VehicleRecord] = {}
        for v in vehicles:
            cat = extract_category(v.name)
            if cat not in best or v.total_price < best[cat].total_price:
                best[cat] = v
        sorted_vehicles = sorted(best.values(), key=lambda v: v.total_price)

        embed = _prices_embed(run_at, sorted_vehicles, b)
        await interaction.response.send_message(embed=embed)

    @prices_cmd.autocomplete("booking")
    async def prices_autocomplete(
        interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        try:
            names = [b.name for b in load_config(config_path).bookings]
        except Exception:
            names = []
        return [app_commands.Choice(name=n, value=n) for n in names if current.lower() in n.lower()][:25]

    @bot.tree.command(name="history", description="Show price history for a vehicle category.")
    @app_commands.describe(
        booking="Booking name",
        vehicle="Vehicle category (e.g. 'Economy Car', 'Standard Car')",
        limit="Number of past runs to show (default 8, max 20)",
    )
    async def history_cmd(
        interaction: discord.Interaction,
        booking: str,
        vehicle: str,
        limit: int = 8,
    ) -> None:
        try:
            config = load_config(config_path)
        except Exception as exc:
            await interaction.response.send_message(f"❌ Failed to load config: {exc}", ephemeral=True)
            return

        try:
            b = config.get_booking_by_name(booking)
        except KeyError:
            names = ", ".join(x.name for x in config.bookings)
            await interaction.response.send_message(
                f"❌ Unknown booking `{booking}`. Available: {names}", ephemeral=True
            )
            return

        limit = max(1, min(limit, 20))
        rows = get_price_history(config.database.path, b.name, vehicle, limit=limit)

        if not rows:
            await interaction.response.send_message(
                f"No history for `{vehicle}` in booking `{b.name}`.\n"
                "Check that the vehicle category name is exact (e.g. `Economy Car`).",
                ephemeral=True,
            )
            return

        lines = []
        for run_at, price in rows:
            ts = run_at[:10]  # YYYY-MM-DD
            lines.append(f"`{ts}`  {_fmt_price(price)}")

        # Trend indicator
        if len(rows) >= 2:
            diff = rows[0][1] - rows[-1][1]
            if diff < 0:
                trend = f"📈 Up {_fmt_price(abs(diff))} over this period"
            elif diff > 0:
                trend = f"📉 Down {_fmt_price(diff)} over this period"
            else:
                trend = "➡️ No change over this period"
        else:
            trend = ""

        embed = discord.Embed(
            title=f"📈 Price History — {vehicle}",
            description="\n".join(lines),
            color=_COLOR_BLUE,
        )
        if trend:
            embed.set_footer(text=f"{trend} · {b.name}")
        else:
            embed.set_footer(text=b.name)

        await interaction.response.send_message(embed=embed)

    @history_cmd.autocomplete("booking")
    async def history_booking_autocomplete(
        interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        try:
            names = [b.name for b in load_config(config_path).bookings]
        except Exception:
            names = []
        return [app_commands.Choice(name=n, value=n) for n in names if current.lower() in n.lower()][:25]

    @bot.tree.command(name="holding", description="Update the holding (locked-in) price for a booking.")
    @app_commands.describe(
        booking="Booking name",
        price="Your locked-in price (e.g. 375.00)",
        vehicle="Vehicle category to compare against (e.g. 'Standard Car')",
    )
    async def holding_cmd(
        interaction: discord.Interaction,
        booking: str,
        price: float,
        vehicle: str,
    ) -> None:
        try:
            config = load_config(config_path)
        except Exception as exc:
            await interaction.response.send_message(f"❌ Failed to load config: {exc}", ephemeral=True)
            return

        try:
            config.get_booking_by_name(booking)
        except KeyError:
            names = ", ".join(x.name for x in config.bookings)
            await interaction.response.send_message(
                f"❌ Unknown booking `{booking}`. Available: {names}", ephemeral=True
            )
            return

        if price <= 0:
            await interaction.response.send_message("❌ Price must be positive.", ephemeral=True)
            return

        # Defer while we run the blocking git operations
        await interaction.response.defer(thinking=True)

        def _apply() -> str:
            from scripts.update_config import apply_config_update
            apply_config_update(
                config_path=config_path,
                booking_identifier=booking,
                holding_price=price,
                holding_vehicle_type=vehicle,
            )
            return f"✅ Holding price for **{booking}** updated to {_fmt_price(price)} ({vehicle})."

        try:
            msg = await asyncio.get_event_loop().run_in_executor(None, _apply)
            await interaction.followup.send(msg)
        except Exception as exc:
            await interaction.followup.send(f"❌ Failed to update holding price: {exc}")

    @holding_cmd.autocomplete("booking")
    async def holding_booking_autocomplete(
        interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        try:
            names = [b.name for b in load_config(config_path).bookings]
        except Exception:
            names = []
        return [app_commands.Choice(name=n, value=n) for n in names if current.lower() in n.lower()][:25]

    @bot.tree.command(name="scrape", description="Trigger an immediate scrape for a booking.")
    @app_commands.describe(booking="Booking name (defaults to first booking)")
    async def scrape_cmd(interaction: discord.Interaction, booking: str | None = None) -> None:
        try:
            config = load_config(config_path)
        except Exception as exc:
            await interaction.response.send_message(f"❌ Failed to load config: {exc}", ephemeral=True)
            return

        if booking is None:
            b = config.bookings[0]
        else:
            try:
                b = config.get_booking_by_name(booking)
            except KeyError:
                names = ", ".join(x.name for x in config.bookings)
                await interaction.response.send_message(
                    f"❌ Unknown booking `{booking}`. Available: {names}", ephemeral=True
                )
                return

        await interaction.response.send_message(
            f"🔍 Starting scrape for **{b.name}** ({b.pickup_location} "
            f"{b.pickup_date} → {b.dropoff_date})…"
        )

        def _run_scrape():
            from car_tracker.scraper import scrape as do_scrape
            return do_scrape(b, debug=False)

        try:
            results = await asyncio.get_event_loop().run_in_executor(None, _run_scrape)
        except Exception as exc:
            await interaction.followup.send(f"❌ Scrape failed for **{b.name}**: {exc}")
            return

        db_path = config.database.path
        init_db(db_path)
        run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        run_id = save_run(
            db_path,
            pickup_location=b.pickup_location,
            pickup_date=b.pickup_date,
            pickup_time=b.pickup_time,
            dropoff_date=b.dropoff_date,
            dropoff_time=b.dropoff_time,
            holding_price=b.holding_price,
            holding_vehicle_type=b.holding_vehicle_type,
            booking_name=b.name,
        )
        vehicle_records = [
            VehicleRecord(
                position=v.position,
                name=f"{v.name} ({v.brand})",
                total_price=v.total_price,
                price_per_day=v.price_per_day,
            )
            for v in results
        ]
        save_vehicles(db_path, run_id, vehicle_records)

        prior_raw = get_prior_run_vehicles(
            db_path, run_id,
            b.pickup_location, b.pickup_date, b.dropoff_date,
            booking_name=b.name,
        )
        prior: dict[str, float] = {}
        for name, price in prior_raw.items():
            cat = extract_category(name)
            if cat not in prior or price < prior[cat]:
                prior[cat] = price

        type_rows = best_per_type(build_delta(vehicle_records, prior))
        holding_summary = build_holding_summary(
            type_rows, b.holding_price, holding_vehicle_type=b.holding_vehicle_type
        )
        section = BookingSection(booking=b, vehicles=type_rows, holding_summary=holding_summary)

        # Send results embed
        from car_tracker.discord_notifier import build_success_embeds
        embeds = build_success_embeds([section], run_ts)
        if embeds:
            e = embeds[0]
            discord_embed = discord.Embed(
                title=e.get("title", "Results"),
                description=e.get("description", ""),
                color=e.get("color", _COLOR_BLUE),
            )
            for field in e.get("fields", []):
                discord_embed.add_field(
                    name=field["name"], value=field["value"], inline=field.get("inline", False)
                )
            if "footer" in e:
                discord_embed.set_footer(text=e["footer"].get("text", ""))
            await interaction.followup.send(
                f"✅ Scraped {len(results)} vehicles for **{b.name}**.", embed=discord_embed
            )
        else:
            await interaction.followup.send(f"✅ Scraped {len(results)} vehicles for **{b.name}**.")

    @scrape_cmd.autocomplete("booking")
    async def scrape_autocomplete(
        interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        try:
            names = [b.name for b in load_config(config_path).bookings]
        except Exception:
            names = []
        return [app_commands.Choice(name=n, value=n) for n in names if current.lower() in n.lower()][:25]


def create_bot(config_path: str) -> CarTrackerBot:
    """Create and configure the bot with all slash commands registered."""
    load_dotenv(_ENV_PATH)
    bot = CarTrackerBot(config_path=config_path)
    setup_commands(bot, config_path)
    return bot


def run_bot(config_path: str) -> None:
    """Load token from env and run the bot (blocking)."""
    load_dotenv(_ENV_PATH)
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN not set in environment or .env file.")
    bot = create_bot(config_path)
    bot.run(token)

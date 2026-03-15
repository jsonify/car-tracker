from __future__ import annotations

import asyncio
import random
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import date, datetime

from playwright.async_api import Page, async_playwright

from car_tracker.config import Config

COSTCO_RENTAL_URL = "https://www.costcotravel.com/rental-cars"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CDP_PORT = 9222
USER_DATA_DIR = "/tmp/car-tracker-chrome"


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------


@dataclass
class VehicleResult:
    position: int
    name: str
    brand: str
    total_price: float
    price_per_day: float


# ---------------------------------------------------------------------------
# Time conversion: "10:00" (24h) → "10:00 AM" (12h)
# ---------------------------------------------------------------------------


def to_12h(time_str: str) -> str:
    """Convert HH:MM (24h) to H:MM AM/PM for Costco Travel select options."""
    t = datetime.strptime(time_str, "%H:%M")
    # Costco uses format like "10:00 AM", "12:00 PM", "01:00 PM"
    hour = t.hour
    minute = t.minute
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour:02d}:{minute:02d} {period}"


# ---------------------------------------------------------------------------
# Days between two date strings
# ---------------------------------------------------------------------------


def days_between(start: str, end: str) -> float:
    """Return number of days between two YYYY-MM-DD date strings."""
    d1 = date.fromisoformat(start)
    d2 = date.fromisoformat(end)
    delta = (d2 - d1).days
    return max(delta, 1)  # avoid division by zero


# ---------------------------------------------------------------------------
# Chrome launcher
# ---------------------------------------------------------------------------


class ChromeManager:  # pragma: no cover
    """Launch Chrome with remote debugging and tear it down cleanly."""

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug
        self._proc: subprocess.Popen | None = None

    def start(self) -> None:
        args = [
            CHROME_PATH,
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={USER_DATA_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
        ]
        if not self.debug:
            args.extend([
                "--headless=new",
                "--window-size=1920,1080",
                "--disable-gpu",
                "--hide-scrollbars",
                "--mute-audio",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
            ])

        self._proc = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Wait for Chrome to be ready
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                import urllib.request
                urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=1)
                return
            except Exception:
                time.sleep(0.3)
        raise RuntimeError("Chrome did not start in time.")

    def stop(self) -> None:
        if self._proc:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------


async def _slow_pause(lo: float = 0.8, hi: float = 1.8) -> None:  # pragma: no cover
    await asyncio.sleep(random.uniform(lo, hi))


async def _set_date_field(page: Page, field_id: str, value: str) -> None:  # pragma: no cover
    """Set a jQuery datepicker field value via JavaScript."""
    await page.evaluate(
        """([id, val]) => {
            const el = document.getElementById(id);
            el.value = val;
            if (window.$) {
                window.$(el).trigger('change');
                try { window.$(el).datepicker('setDate', val); } catch(e) {}
            }
            el.dispatchEvent(new Event('change', {bubbles: true}));
        }""",
        [field_id, value],
    )


def _to_mmddyyyy(iso_date: str) -> str:
    """Convert YYYY-MM-DD to MM/DD/YYYY for Costco form fields."""
    d = date.fromisoformat(iso_date)
    return d.strftime("%m/%d/%Y")


async def _fill_search_form(page: Page, config: Config) -> None:  # pragma: no cover
    """Fill and submit the Costco Travel rental car search form."""
    s = config.search

    # Location autocomplete
    await page.click("#pickupLocationTextWidget")
    await _slow_pause()
    location = s.pickup_location
    for ch in location:
        await page.type(
            "#pickupLocationTextWidget",
            ch,
            delay=random.randint(120, 280),
        )
    await _slow_pause(2.5, 3.5)

    # Click first matching autocomplete suggestion
    suggestion = page.locator("ul.ui-list li").first
    await suggestion.wait_for(state="visible", timeout=10000)
    # Try exact airport match first
    airport_item = page.locator(f'li[data-value="{location}"]').first
    try:
        await airport_item.wait_for(state="visible", timeout=3000)
        await airport_item.click()
    except Exception:
        await suggestion.click()
    await _slow_pause()

    # Dates (MM/DD/YYYY format for form)
    await _set_date_field(page, "pickUpDateWidget", _to_mmddyyyy(s.pickup_date))
    await _slow_pause(0.5, 1.0)
    await _set_date_field(page, "dropOffDateWidget", _to_mmddyyyy(s.dropoff_date))
    await _slow_pause(0.5, 1.0)

    # Times
    await page.select_option("#pickupTimeWidget", label=to_12h(s.pickup_time))
    await _slow_pause(0.3, 0.7)
    await page.select_option("#dropoffTimeWidget", label=to_12h(s.dropoff_time))
    await _slow_pause()

    # Submit
    await page.locator("#findMyCarButton").click()


async def _extract_results(page: Page, config: Config) -> list[VehicleResult]:  # pragma: no cover
    """Wait for results then extract vehicle cards."""
    # Wait for at least one result card
    await page.locator(".car-result-card").first.wait_for(state="attached", timeout=30000)
    await _slow_pause(2.0, 3.0)

    cards = await page.locator(".car-result-card").all()
    num_days = days_between(config.search.pickup_date, config.search.dropoff_date)

    results: list[VehicleResult] = []
    for i, card in enumerate(cards, start=1):
        try:
            category = await card.get_attribute("data-category-name") or ""
            brand = await card.get_attribute("data-brand") or ""
            price_str = await card.get_attribute("data-price") or "0"
            total_price = float(price_str)
            price_per_day = round(total_price / num_days, 2)

            results.append(
                VehicleResult(
                    position=i,
                    name=category,
                    brand=brand,
                    total_price=round(total_price, 2),
                    price_per_day=price_per_day,
                )
            )
        except Exception:
            continue

    return results


async def _run_scrape(config: Config) -> list[VehicleResult]:  # pragma: no cover
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        await page.goto(COSTCO_RENTAL_URL, timeout=60000, wait_until="domcontentloaded")
        await _slow_pause(3, 5)

        await _fill_search_form(page, config)

        results = await _extract_results(page, config)
        await browser.close()
        return results


def scrape(config: Config, debug: bool = False) -> list[VehicleResult]:  # pragma: no cover
    """
    Launch Chrome, scrape Costco Travel rental cars, and return results.

    Args:
        config: Loaded and validated Config object.
        debug:  If True, Chrome launches in headed (visible) mode.

    Returns:
        List of VehicleResult in the order they appear on the page.

    Raises:
        RuntimeError: If Chrome fails to start or results cannot be scraped.
    """
    chrome = ChromeManager(debug=debug)
    chrome.start()
    try:
        results = asyncio.run(_run_scrape(config))
    finally:
        chrome.stop()

    if not results:
        raise RuntimeError("Scrape completed but returned no vehicle results.")

    return results

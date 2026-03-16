from __future__ import annotations

import asyncio
import os
import random
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import date, datetime

# Suppress Playwright's Node.js DEP0169 deprecation warning (url.parse)
os.environ.setdefault("NODE_OPTIONS", "--no-deprecation")

from playwright.async_api import Page, async_playwright

from car_tracker.config import Config

COSTCO_RENTAL_URL = "https://www.costcotravel.com/rental-cars"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CDP_PORT = 9222
USER_DATA_DIR = "/tmp/car-tracker-chrome"
_CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/146.0.0.0 Safari/537.36"
)


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
        self._tmp_dir: str | None = None

    def _kill_stale(self) -> None:
        """Kill any leftover Chrome process listening on CDP_PORT."""
        try:
            out = subprocess.check_output(
                ["/usr/sbin/lsof", "-ti", f"tcp:{CDP_PORT}"],
                stderr=subprocess.DEVNULL,
            )
            for pid in out.decode().split():
                subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
            time.sleep(0.5)
        except subprocess.CalledProcessError:
            pass  # nothing on that port

    def _build_args(self) -> list[str]:
        self._tmp_dir = tempfile.mkdtemp(prefix="car-tracker-chrome-")
        args = [
            CHROME_PATH,
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={self._tmp_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=AutomationControlled",
        ]
        if not self.debug:
            args.extend([
                "--headless=new",
                "--window-size=1920,1080",
                f"--user-agent={_CHROME_UA}",
                "--disable-gpu",
                "--hide-scrollbars",
                "--mute-audio",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
            ])
        return args

    def is_alive(self) -> bool:
        """Check if the Chrome process is still running."""
        if self._proc is None:
            return False
        return self._proc.poll() is None

    def start(self) -> None:
        self._kill_stale()
        mode = "headed (debug)" if self.debug else "headless"
        print(f"  Starting Chrome ({mode})...", end=" ", flush=True)
        self._chrome_log = open("/tmp/car-tracker-chrome-stderr.log", "a")
        self._proc = subprocess.Popen(
            self._build_args(),
            stdout=subprocess.DEVNULL,
            stderr=self._chrome_log,
        )
        # Wait for Chrome to be ready
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                import urllib.request
                urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=1)
                print("ready")
                return
            except Exception:
                time.sleep(0.3)
        raise RuntimeError("Chrome did not start in time.")

    def restart(self) -> None:
        """Stop (if running) and start a fresh Chrome instance."""
        self.stop()
        self.start()

    def stop(self) -> None:
        if self._proc:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            self._proc = None
        if self._tmp_dir:
            shutil.rmtree(self._tmp_dir, ignore_errors=True)
            self._tmp_dir = None


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

        print("  Loading Costco Travel...", end=" ", flush=True)
        await page.goto(COSTCO_RENTAL_URL, timeout=60000, wait_until="domcontentloaded")
        await _slow_pause(3, 5)
        print("done")

        print("  Filling search form...", end=" ", flush=True)
        await _fill_search_form(page, config)
        print("submitted")

        print("  Waiting for results...", end=" ", flush=True)
        results = await _extract_results(page, config)
        print(f"{len(results)} vehicles found")

        await page.close()
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
        last_err: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                results = asyncio.run(_run_scrape(config))
                break
            except Exception as exc:
                last_err = exc
                if attempt < MAX_RETRIES:
                    print(f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}")
                    if not chrome.is_alive():
                        print("Chrome crashed — restarting...")
                        chrome.restart()
                    else:
                        print(f"Retrying in {RETRY_DELAY}s...")
                        time.sleep(RETRY_DELAY)
        else:
            raise RuntimeError(
                f"All {MAX_RETRIES} scrape attempts failed. Last error: {last_err}"
            )
    finally:
        chrome.stop()

    if not results:
        raise RuntimeError("Scrape completed but returned no vehicle results.")

    return results

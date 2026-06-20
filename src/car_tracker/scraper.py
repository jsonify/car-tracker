from __future__ import annotations

import asyncio
import os
import random
import re
import shutil
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

# Suppress Playwright's Node.js DEP0169 deprecation warning (url.parse)
os.environ.setdefault("NODE_OPTIONS", "--no-deprecation")

from dotenv import load_dotenv
from playwright.async_api import Page, async_playwright

from car_tracker.config import BookingConfig

COSTCO_RENTAL_URL = "https://www.costcotravel.com/rental-cars"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries
CHROME_PATH = os.environ.get(
    "CAR_TRACKER_CHROME_PATH",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)
CDP_PORT = 9222
USER_DATA_DIR = "/tmp/car-tracker-chrome"
_CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/146.0.0.0 Safari/537.36"
)
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"

# Costco login selectors — verified via debug_login.py
_LOGIN_LINK_SELECTOR = "a[data-hook='top_link_login']:visible"
_LOGIN_EMAIL_SELECTOR = "input#signInName"
_LOGIN_PASSWORD_SELECTOR = "input#password"
_LOGIN_SUBMIT_SELECTOR = "button#next"


class LoginError(RuntimeError):
    """Raised when Costco login fails or member pricing is not detected."""


def load_costco_config() -> tuple[str, str]:
    """Load Costco credentials from .env. Returns (username, password).

    Raises:
        ValueError: If COSTCO_USERNAME or COSTCO_PASSWORD is missing.
    """
    load_dotenv(_ENV_PATH)
    username = os.environ.get("COSTCO_USERNAME", "")
    password = os.environ.get("COSTCO_PASSWORD", "")
    missing = [k for k, v in [("COSTCO_USERNAME", username), ("COSTCO_PASSWORD", password)] if not v]
    if missing:
        raise ValueError(f"Missing required Costco env vars: {', '.join(missing)}")
    return username, password


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
        lsof = shutil.which("lsof")
        if not lsof:
            return
        try:
            out = subprocess.check_output(
                [lsof, "-ti", f"tcp:{CDP_PORT}"],
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
            # Run headed but off-screen: Costco's Azure AD B2C blocks headless Chrome
            # logins ("We are having trouble signing you in"). Headed mode with the
            # window positioned off-screen passes their bot detection identically to a
            # real browser session.
            args.extend([
                "--window-size=1920,1080",
                "--window-position=-9999,0",
                "--start-minimized",
                f"--user-agent={_CHROME_UA}",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
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
                if not self.debug:
                    self._start_hider_thread()
                return
            except Exception:
                time.sleep(0.3)
        raise RuntimeError("Chrome did not start in time.")

    def _start_hider_thread(self) -> None:
        """Background thread that repeatedly hides Chrome's window on macOS.

        Chrome opens new windows during page navigation, so a one-shot hide
        is not enough. We tell the Chrome application to hide itself every
        300 ms until stop() is called. Uses Chrome's own AppleScript interface
        (no Accessibility permissions required).
        """
        self._hider_stop = threading.Event()

        def _run(stop: threading.Event) -> None:
            script = 'tell application "Google Chrome" to hide'
            while not stop.is_set():
                try:
                    subprocess.run(
                        ["osascript", "-e", script],
                        capture_output=True,
                        timeout=5,
                    )
                except Exception:
                    pass  # Non-fatal
                stop.wait(1.0)

        t = threading.Thread(target=_run, args=(self._hider_stop,), daemon=True)
        t.start()

    def restart(self) -> None:
        """Stop (if running) and start a fresh Chrome instance."""
        self.stop()
        self.start()

    def stop(self) -> None:
        if hasattr(self, "_hider_stop"):
            self._hider_stop.set()
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


async def _login(page: Page, username: str, password: str) -> None:  # pragma: no cover
    """Log into Costco Travel using stored credentials.

    Clicks the login link (which performs a full-page redirect to signin.costco.com),
    fills credentials, submits, and waits for the redirect back to costcotravel.com.

    Raises:
        LoginError: If the login form does not appear, or the redirect back
                    to costcotravel.com does not occur within timeout.
    """
    login_link = page.locator(_LOGIN_LINK_SELECTOR).first
    try:
        await login_link.wait_for(state="visible", timeout=10000)
    except Exception as exc:
        raise LoginError("Login link not found — check _LOGIN_LINK_SELECTOR") from exc
    await login_link.click()

    # Full-page redirect to signin.costco.com — wait for it to load
    try:
        await page.wait_for_url(re.compile(r"signin\.costco\.com"), timeout=15000)
    except Exception as exc:
        raise LoginError("Did not reach Costco sign-in page — check _LOGIN_LINK_SELECTOR") from exc

    await _slow_pause(1.5, 2.5)

    email_field = page.locator(_LOGIN_EMAIL_SELECTOR).first
    try:
        await email_field.wait_for(state="visible", timeout=15000)
    except Exception as exc:
        raise LoginError("Login email field not found — check _LOGIN_EMAIL_SELECTOR") from exc

    await email_field.fill(username)
    await _slow_pause(0.5, 1.0)
    await page.locator(_LOGIN_PASSWORD_SELECTOR).first.fill(password)
    await _slow_pause(0.5, 1.0)
    await page.locator(_LOGIN_SUBMIT_SELECTOR).first.click()

    # Wait for redirect back to costcotravel.com as success indicator.
    # Using a regex because the glob pattern **/costcotravel.com/** fails to match
    # www.costcotravel.com (minimatch treats the subdomain as its own path segment).
    try:
        await page.wait_for_url(
            re.compile(r"^https?://(?:www\.)?costcotravel\.com/"),
            timeout=30000,
        )
    except Exception as exc:
        try:
            await page.screenshot(path="/tmp/car-tracker-login-failure.png", full_page=True)
        except Exception:
            pass
        raise LoginError(
            "Costco login failed — check COSTCO_USERNAME / COSTCO_PASSWORD in .env"
        ) from exc

    await _slow_pause(1.0, 2.0)


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


async def _fill_search_form(page: Page, booking: BookingConfig) -> None:  # pragma: no cover
    """Fill and submit the Costco Travel rental car search form."""
    # Location autocomplete
    await page.click("#pickupLocationTextWidget")
    await _slow_pause()
    location = booking.pickup_location
    for ch in location:
        await page.type(
            "#pickupLocationTextWidget",
            ch,
            delay=random.randint(120, 280),
        )
    await _slow_pause(2.5, 3.5)

    # Click first matching autocomplete suggestion.
    # Use :visible to skip the hidden pre-selected airport item (class="airport selected")
    # which Playwright resolves first but can never become visible.
    suggestion = page.locator("ul.ui-list li:visible").first
    await suggestion.wait_for(state="visible", timeout=10000)
    # Try exact airport match first (visible items only)
    airport_item = page.locator(f'ul.ui-list li[data-value="{location}"]:visible').first
    try:
        await airport_item.wait_for(state="visible", timeout=3000)
        await airport_item.click()
    except Exception:
        await suggestion.click()
    await _slow_pause()

    # Dates (MM/DD/YYYY format for form)
    await _set_date_field(page, "pickUpDateWidget", _to_mmddyyyy(booking.pickup_date))
    await _slow_pause(0.5, 1.0)
    await _set_date_field(page, "dropOffDateWidget", _to_mmddyyyy(booking.dropoff_date))
    await _slow_pause(0.5, 1.0)

    # Times
    await page.select_option("#pickupTimeWidget", label=to_12h(booking.pickup_time))
    await _slow_pause(0.3, 0.7)
    await page.select_option("#dropoffTimeWidget", label=to_12h(booking.dropoff_time))
    await _slow_pause()

    # Submit
    await page.locator("#findMyCarButton").click()


async def _extract_results(page: Page, booking: BookingConfig) -> list[VehicleResult]:  # pragma: no cover
    """Wait for results then extract vehicle cards."""
    # Wait for at least one result card
    await page.locator(".car-result-card").first.wait_for(state="attached", timeout=30000)
    await _slow_pause(2.0, 3.0)

    # Verify member pricing is active — if absent, login did not produce a member session
    member_banner = page.locator("text=The price includes your Costco member savings").first
    try:
        await member_banner.wait_for(state="visible", timeout=5000)
    except Exception as exc:
        raise LoginError(
            "Login succeeded but member pricing not detected — retrying"
        ) from exc

    cards = await page.locator(".car-result-card").all()
    num_days = days_between(booking.pickup_date, booking.dropoff_date)

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


async def _run_scrape(booking: BookingConfig, username: str, password: str) -> list[VehicleResult]:  # pragma: no cover
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        print("  Loading Costco Travel...", end=" ", flush=True)
        await page.goto(COSTCO_RENTAL_URL, timeout=60000, wait_until="domcontentloaded")
        await _slow_pause(3, 5)
        print("done")

        print("  Logging in...", end=" ", flush=True)
        await _login(page, username, password)
        print("done")

        # After login, Costco redirects to /memberBookings. Navigate back to
        # the rental car search page before filling the form.
        print("  Navigating to rental cars...", end=" ", flush=True)
        await page.goto(COSTCO_RENTAL_URL, timeout=60000, wait_until="domcontentloaded")
        await _slow_pause(2, 3)
        print("done")

        print("  Filling search form...", end=" ", flush=True)
        await _fill_search_form(page, booking)
        print("submitted")

        print("  Waiting for results...", end=" ", flush=True)
        results = await _extract_results(page, booking)
        print(f"{len(results)} vehicles found")

        await page.close()
        return results


def scrape(booking: BookingConfig, debug: bool = False) -> list[VehicleResult]:  # pragma: no cover
    """
    Launch Chrome, log into Costco Travel, scrape rental car prices, and return results.

    Args:
        booking: The BookingConfig to scrape.
        debug:   If True, Chrome launches in headed (visible) mode.

    Returns:
        List of VehicleResult in the order they appear on the page.

    Raises:
        ValueError:   If COSTCO_USERNAME or COSTCO_PASSWORD is missing from .env.
        LoginError:   If login fails or member pricing is not detected.
        RuntimeError: If Chrome fails to start or results cannot be scraped.
    """
    username, password = load_costco_config()
    chrome = ChromeManager(debug=debug)
    chrome.start()
    try:
        last_err: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                results = asyncio.run(_run_scrape(booking, username, password))
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

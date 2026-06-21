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
_COOKIE_CACHE_PATH = Path("data/cookies.json")

# Costco login selectors — updated for 2026 unified login (costco.com + costcotravel.com merged)
_LOGIN_LINK_SELECTOR = "a[data-hook='top_link_login']:visible"
# New unified login uses input[type="email"]; old Azure B2C page used input#signInName
_LOGIN_EMAIL_SELECTOR = "input[type='email'], input#signInName, input#email"
_LOGIN_PASSWORD_SELECTOR = "input[type='password'], input#password"
# Use text-based selector for the Sign In button — more robust than id/type across login page versions
_LOGIN_SUBMIT_SELECTOR = "button:has-text('Sign In'), button#next, button[type='submit']"


class LoginError(RuntimeError):
    """Raised when Costco login fails or member pricing is not detected."""


async def _load_cookies(ctx) -> bool:  # pragma: no cover
    """Load cookies from disk cache or COSTCO_COOKIES env var into browser context.

    Disk cache takes precedence over the env var so that fresh cookies saved
    after a login are reused on the next run without any manual secret update.
    Returns True if cookies were loaded.
    """
    import json as _json

    source: list | None = None

    if _COOKIE_CACHE_PATH.exists():
        try:
            source = _json.loads(_COOKIE_CACHE_PATH.read_text())
        except Exception:
            pass

    if source is None:
        raw = os.environ.get("COSTCO_COOKIES", "").strip()
        if raw:
            try:
                source = _json.loads(raw)
            except Exception:
                pass

    if not source:
        return False

    await ctx.add_cookies([
        {
            "name": c["name"],
            "value": c["value"],
            "domain": c.get("domain", ".costcotravel.com"),
            "path": c.get("path", "/"),
            "httpOnly": bool(c.get("httpOnly", False)),
            "secure": bool(c.get("secure", True)),
            "sameSite": c.get("sameSite", "Lax"),
        }
        for c in source
    ])
    return True


async def _save_cookies(ctx) -> None:  # pragma: no cover
    """Save current browser cookies to disk so the next run can skip login."""
    import json as _json

    cookies = await ctx.cookies(["https://www.costcotravel.com", "https://signin.costco.com"])
    if not cookies:
        return
    _COOKIE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _COOKIE_CACHE_PATH.write_text(_json.dumps(cookies))
    print(f"  Saved {len(cookies)} cookie(s) to cache.", flush=True)


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
                "--window-position=0,0",
                f"--user-agent={_CHROME_UA}",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                # Force HTTP/1.1 — GitHub Actions runners can trigger ERR_HTTP2_PROTOCOL_ERROR
                # from Costco's CDN when negotiating HTTP/2, but HTTP/1.1 passes through fine.
                "--disable-http2",
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

    # Use type() instead of fill() so React's onChange synthetic events fire and
    # the form's internal state actually receives the credentials.
    await email_field.click()
    await email_field.type(username, delay=50)
    await _slow_pause(0.5, 1.0)
    password_field = page.locator(_LOGIN_PASSWORD_SELECTOR).first
    try:
        await password_field.wait_for(state="visible", timeout=10000)
    except Exception as exc:
        raise LoginError("Login password field not found — check _LOGIN_PASSWORD_SELECTOR") from exc
    await password_field.click()
    await password_field.type(password, delay=50)
    await _slow_pause(0.5, 1.0)
    submit_btn = page.locator(_LOGIN_SUBMIT_SELECTOR).first
    try:
        await submit_btn.wait_for(state="visible", timeout=10000)
    except Exception as exc:
        await page.screenshot(path="/tmp/car-tracker-login-failure.png", full_page=True)
        raise LoginError("Login submit button not found — check _LOGIN_SUBMIT_SELECTOR") from exc

    btn_text = await submit_btn.text_content()
    print(f"\n  [login-debug] Submitting '{btn_text}' via JS click, url={page.url}", flush=True)

    # Use JS .click() on the button — this calls the DOM method directly and
    # bypasses Playwright's event dispatch, which bot detection often hooks.
    await page.evaluate(
        "btn => btn.click()",
        await submit_btn.element_handle(),
    )
    await _slow_pause(1.0, 1.5)
    print(f"  [login-debug] Post-submit url={page.url}", flush=True)

    # Wait for redirect away from signin.costco.com as the success indicator.
    try:
        await page.wait_for_url(
            re.compile(r"^https?://(?:www\.)?(?:costcotravel|costco)\.com/"),
            timeout=30000,
        )
        print(f"  [login-debug] Redirect success: {page.url}", flush=True)
    except Exception as exc:
        await page.screenshot(path="/tmp/car-tracker-login-failure.png", full_page=True)
        print(f"\n  [login-debug] URL at failure: {page.url}", flush=True)
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

    # Age checkbox — "Yes, I am at least 25 years old" must be checked or the
    # Search button does nothing (form validation silently blocks submission).
    age_checkbox = page.locator("input[type='checkbox']").first
    try:
        if not await age_checkbox.is_checked():
            await age_checkbox.check()
    except Exception:
        pass
    await _slow_pause(0.3, 0.7)

    await page.locator("#findMyCarButton").click()


async def _extract_results(page: Page, booking: BookingConfig) -> list[VehicleResult]:  # pragma: no cover
    """Wait for results then extract vehicle cards."""
    # Wait for at least one result card
    try:
        await page.locator(".car-result-card").first.wait_for(state="attached", timeout=30000)
    except Exception as exc:
        await page.screenshot(path="/tmp/car-tracker-results-failure.png", full_page=True)
        raise exc
    await _slow_pause(2.0, 3.0)

    # Check whether member pricing is active; log a warning if absent but continue.
    member_banner = page.locator("text=The price includes your Costco member savings").first
    try:
        await member_banner.wait_for(state="visible", timeout=5000)
        print("  [member pricing active]", flush=True)
    except Exception:
        print("  [warning] member pricing banner not found — prices may not include member discount", flush=True)

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


async def _login_and_navigate(page: Page, ctx) -> None:  # pragma: no cover
    """Log in to Costco Travel, save fresh cookies, then navigate to the rental cars page."""
    username, password = load_costco_config()
    print("  Logging in...", end=" ", flush=True)
    await page.goto(COSTCO_RENTAL_URL, timeout=60000, wait_until="domcontentloaded")
    await _slow_pause(3, 5)
    await _login(page, username, password)
    print("done")
    await _save_cookies(ctx)
    print("  Navigating to rental cars...", end=" ", flush=True)
    await page.goto(COSTCO_RENTAL_URL, timeout=60000, wait_until="domcontentloaded")
    await _slow_pause(2, 3)
    print("done")


async def _run_scrape(booking: BookingConfig) -> list[VehicleResult]:  # pragma: no cover
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Mask navigator.webdriver on the context so it applies to ALL pages/origins including
        # the signin.costco.com cross-origin redirect. Page-level init scripts don't survive
        # cross-origin navigations reliably when connecting via CDP.
        await ctx.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            window.chrome = { runtime: {} };
        """)

        # Try cached cookies first (disk cache, then COSTCO_COOKIES env var).
        # Only fall back to login when the cache is cold or cookies have expired.
        # After login, cookies are saved to disk so the next run skips login entirely.
        if await _load_cookies(ctx):
            print("  Loaded cached cookies.", flush=True)
            print("  Navigating to rental cars...", end=" ", flush=True)
            try:
                await page.goto(COSTCO_RENTAL_URL, timeout=60000, wait_until="domcontentloaded")
                if "signin" in page.url:
                    raise RuntimeError("cookies expired — redirected to login")
                await _slow_pause(2, 3)
                print("done")
            except Exception as exc:
                print(f"stale ({exc!s:.80}), logging in...", flush=True)
                await ctx.clear_cookies()
                await _login_and_navigate(page, ctx)
        else:
            await _login_and_navigate(page, ctx)

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
        RuntimeError: If all retries are exhausted without a successful scrape.
    """
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        chrome = ChromeManager(debug=debug)
        chrome.start()
        try:
            results = asyncio.run(_run_scrape(booking))
            if not results:
                raise RuntimeError("Scrape completed but returned no vehicle results.")
            return results
        except Exception as exc:
            last_exc = exc
        finally:
            chrome.stop()

        if attempt < MAX_RETRIES:
            print(f"  Attempt {attempt}/{MAX_RETRIES} failed: {last_exc}. Retrying in {RETRY_DELAY}s...", flush=True)
            time.sleep(RETRY_DELAY)

    raise RuntimeError(f"All {MAX_RETRIES} scrape attempts failed") from last_exc

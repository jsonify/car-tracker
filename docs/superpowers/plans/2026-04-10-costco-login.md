# Costco Login for Member Pricing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Log into Costco Travel before each scrape so the scraper sees member pricing instead of the rack rate.

**Architecture:** Add `LoginError`, `load_costco_config()`, and `_login()` to `scraper.py`. Call `_login()` in `_run_scrape()` after page load. Add member-savings banner verification in `_extract_results()` to catch silent auth failures. Credentials are loaded from `.env` before Chrome starts.

**Tech Stack:** Playwright async API (already in use), python-dotenv (already a dependency), pytest + monkeypatch for unit tests.

---

## File Map

| File | Change |
|---|---|
| `src/car_tracker/scraper.py` | Add imports, `LoginError`, `load_costco_config()`, `_login()`, update `_extract_results()`, `_run_scrape()`, `scrape()` |
| `tests/test_scraper.py` | Add tests for `load_costco_config()` |
| `.env` | Add `COSTCO_USERNAME` and `COSTCO_PASSWORD` (user action, Task 5) |

Pre-existing failures in `tests/test_main.py` (13 failing): these are unrelated to this feature. Do not fix them; do not break any currently-passing tests.

---

## Task 1: Discover login form selectors

**Files:**
- Create (temp): `debug_login.py` — deleted after this task

- [ ] **Step 1: Write the selector discovery script**

Create `debug_login.py` at the repo root:

```python
"""Discover Costco Travel login form selectors. Delete after use."""
import asyncio
import os
import sys

os.environ.setdefault("NODE_OPTIONS", "--no-deprecation")
sys.path.insert(0, "src")

from car_tracker.scraper import CDP_PORT, COSTCO_RENTAL_URL, ChromeManager, _slow_pause
from playwright.async_api import async_playwright


async def run() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        await page.goto(COSTCO_RENTAL_URL, timeout=60000, wait_until="domcontentloaded")
        await _slow_pause(3, 4)

        # Find the login link/button in the header
        print("=== Login link candidates ===")
        for el in await page.locator("a, button").all():
            text = (await el.inner_text()).strip().lower()
            if any(word in text for word in ("login", "sign in", "log in")):
                attrs = await el.evaluate(
                    "el => Object.fromEntries([...el.attributes].map(a => [a.name, a.value]))"
                )
                print(f"  text={text!r}  attrs={attrs}")

        # Click whichever login element is visible
        login_el = page.locator("a:visible, button:visible").filter(has_text="Login").first
        await login_el.click()
        print("\nClicked login element")
        await _slow_pause(2, 3)

        # Print all visible inputs
        print("\n=== Visible input fields after click ===")
        for inp in await page.locator("input:visible").all():
            attrs = await inp.evaluate(
                "el => Object.fromEntries([...el.attributes].map(a => [a.name, a.value]))"
            )
            print(f"  {attrs}")

        # Print visible submit buttons
        print("\n=== Visible submit buttons ===")
        for btn in await page.locator("button:visible").all():
            text = (await btn.inner_text()).strip()
            attrs = await btn.evaluate(
                "el => Object.fromEntries([...el.attributes].map(a => [a.name, a.value]))"
            )
            if attrs.get("type") == "submit" or "submit" in text.lower() or "sign" in text.lower():
                print(f"  text={text!r}  attrs={attrs}")

        await page.close()


chrome = ChromeManager(debug=False)
chrome.start()
try:
    asyncio.run(run())
finally:
    chrome.stop()
```

- [ ] **Step 2: Run the discovery script**

```bash
source .venv/bin/activate && python debug_login.py
```

Read the output carefully. Record:
- The selector for the Login link (likely `a:has-text("Login")` or a `data-test` attribute)
- The `id` or `name` of the email input field (e.g., `#logonId`)
- The `id` or `name` of the password input field (e.g., `#currentPassword`)
- The `id` or `type` of the submit button (e.g., `#logon-submit-btn` or `button[type="submit"]`)

These values are used as `LOGIN_*` constants in Task 3.

- [ ] **Step 3: Delete the discovery script**

```bash
rm debug_login.py
```

---

## Task 2: Add LoginError and load_costco_config() with tests

**Files:**
- Modify: `src/car_tracker/scraper.py`
- Modify: `tests/test_scraper.py`

- [ ] **Step 1: Write failing tests for load_costco_config()**

Add to the bottom of `tests/test_scraper.py`:

```python
# ---------------------------------------------------------------------------
# load_costco_config
# ---------------------------------------------------------------------------

from unittest.mock import patch


def test_load_costco_config_success(monkeypatch):
    monkeypatch.setenv("COSTCO_USERNAME", "user@example.com")
    monkeypatch.setenv("COSTCO_PASSWORD", "secret123")
    with patch("car_tracker.scraper.load_dotenv"):
        from car_tracker.scraper import load_costco_config
        username, password = load_costco_config()
    assert username == "user@example.com"
    assert password == "secret123"


def test_load_costco_config_missing_username(monkeypatch):
    monkeypatch.delenv("COSTCO_USERNAME", raising=False)
    monkeypatch.setenv("COSTCO_PASSWORD", "secret123")
    with patch("car_tracker.scraper.load_dotenv"):
        from car_tracker.scraper import load_costco_config
        with pytest.raises(ValueError, match="COSTCO_USERNAME"):
            load_costco_config()


def test_load_costco_config_missing_password(monkeypatch):
    monkeypatch.setenv("COSTCO_USERNAME", "user@example.com")
    monkeypatch.delenv("COSTCO_PASSWORD", raising=False)
    with patch("car_tracker.scraper.load_dotenv"):
        from car_tracker.scraper import load_costco_config
        with pytest.raises(ValueError, match="COSTCO_PASSWORD"):
            load_costco_config()


def test_load_costco_config_missing_both(monkeypatch):
    monkeypatch.delenv("COSTCO_USERNAME", raising=False)
    monkeypatch.delenv("COSTCO_PASSWORD", raising=False)
    with patch("car_tracker.scraper.load_dotenv"):
        from car_tracker.scraper import load_costco_config
        with pytest.raises(ValueError, match="COSTCO_USERNAME"):
            load_costco_config()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
source .venv/bin/activate && python -m pytest tests/test_scraper.py::test_load_costco_config_success tests/test_scraper.py::test_load_costco_config_missing_username tests/test_scraper.py::test_load_costco_config_missing_password tests/test_scraper.py::test_load_costco_config_missing_both -v
```

Expected: 4 FAILED with `ImportError` or `cannot import name 'load_costco_config'`

- [ ] **Step 3: Add imports, LoginError, _ENV_PATH, and load_costco_config() to scraper.py**

At the top of `src/car_tracker/scraper.py`, update the imports block. Add `from pathlib import Path` and `from dotenv import load_dotenv` after the existing standard-library imports, before the Playwright import:

```python
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
from pathlib import Path

# Suppress Playwright's Node.js DEP0169 deprecation warning (url.parse)
os.environ.setdefault("NODE_OPTIONS", "--no-deprecation")

from dotenv import load_dotenv
from playwright.async_api import Page, async_playwright

from car_tracker.config import BookingConfig
```

Then, after the existing constants block (`COSTCO_RENTAL_URL`, `MAX_RETRIES`, etc.) and before `_CHROME_UA`, add:

```python
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"


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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
source .venv/bin/activate && python -m pytest tests/test_scraper.py::test_load_costco_config_success tests/test_scraper.py::test_load_costco_config_missing_username tests/test_scraper.py::test_load_costco_config_missing_password tests/test_scraper.py::test_load_costco_config_missing_both -v
```

Expected: 4 PASSED

- [ ] **Step 5: Run full test suite to confirm no regressions**

```bash
source .venv/bin/activate && python -m pytest tests/test_scraper.py -v
```

Expected: all previously-passing scraper tests still pass.

- [ ] **Step 6: Commit**

```bash
git add src/car_tracker/scraper.py tests/test_scraper.py
git commit -m "feat(scraper): add LoginError and load_costco_config()"
```

---

## Task 3: Implement _login()

**Files:**
- Modify: `src/car_tracker/scraper.py`

`_login()` is browser-dependent and marked `# pragma: no cover`. The selectors below use the values discovered in Task 1. If Task 1 produced different values, substitute them here.

- [ ] **Step 1: Add LOGIN_* selector constants after the existing constants**

Add these after `_CHROME_UA` in `scraper.py`. Replace the selector strings with what Task 1 discovered if they differ:

```python
# Costco login selectors — verified via debug_login.py
_LOGIN_LINK_SELECTOR = "a:visible:has-text('Login')"
_LOGIN_EMAIL_SELECTOR = "#logonId"
_LOGIN_PASSWORD_SELECTOR = "#currentPassword"
_LOGIN_SUBMIT_SELECTOR = "#logon-submit-btn"
_LOGIN_SUCCESS_SELECTOR = "#header-account-name, [data-test='link-account'], a:has-text('Hi,')"
```

- [ ] **Step 2: Add _login() after the existing _slow_pause() function**

```python
async def _login(page: Page, username: str, password: str) -> None:  # pragma: no cover
    """Log into Costco Travel using stored credentials.

    Raises:
        LoginError: If the login form does not appear, or if the success
                    indicator is not detected within timeout.
    """
    await page.locator(_LOGIN_LINK_SELECTOR).first.click()
    await _slow_pause(1.5, 2.5)

    email_field = page.locator(_LOGIN_EMAIL_SELECTOR).first
    try:
        await email_field.wait_for(state="visible", timeout=15000)
    except Exception as exc:
        raise LoginError("Login form did not appear — check _LOGIN_EMAIL_SELECTOR") from exc

    await email_field.fill(username)
    await _slow_pause(0.5, 1.0)
    await page.locator(_LOGIN_PASSWORD_SELECTOR).first.fill(password)
    await _slow_pause(0.5, 1.0)
    await page.locator(_LOGIN_SUBMIT_SELECTOR).first.click()
    await _slow_pause(2.0, 3.0)

    try:
        await page.locator(_LOGIN_SUCCESS_SELECTOR).first.wait_for(
            state="visible", timeout=15000
        )
    except Exception as exc:
        raise LoginError(
            "Costco login failed — check COSTCO_USERNAME / COSTCO_PASSWORD in .env"
        ) from exc
```

- [ ] **Step 3: Commit**

```bash
git add src/car_tracker/scraper.py
git commit -m "feat(scraper): add _login() with Costco Travel login flow"
```

---

## Task 4: Add member pricing verification to _extract_results()

**Files:**
- Modify: `src/car_tracker/scraper.py`

- [ ] **Step 1: Update _extract_results() to check for the member savings banner**

In `_extract_results()`, add the banner check immediately after the `_slow_pause(2.0, 3.0)` call and before extracting cards. The full updated function:

```python
async def _extract_results(page: Page, booking: BookingConfig) -> list[VehicleResult]:  # pragma: no cover
    """Wait for results then extract vehicle cards."""
    # Wait for at least one result card
    await page.locator(".car-result-card").first.wait_for(state="attached", timeout=30000)
    await _slow_pause(2.0, 3.0)

    # Verify member pricing is active — if absent, login did not produce a member session
    member_banner = page.locator("text=The price includes your Costco member savings")
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
```

- [ ] **Step 2: Run full test suite to confirm no regressions**

```bash
source .venv/bin/activate && python -m pytest tests/test_scraper.py -v
```

Expected: all scraper tests still pass (no new tests needed — `_extract_results` is `# pragma: no cover`).

- [ ] **Step 3: Commit**

```bash
git add src/car_tracker/scraper.py
git commit -m "feat(scraper): verify member pricing banner after login in _extract_results()"
```

---

## Task 5: Wire credentials into _run_scrape() and scrape()

**Files:**
- Modify: `src/car_tracker/scraper.py`

- [ ] **Step 1: Update _run_scrape() to accept and use credentials**

Replace the existing `_run_scrape` signature and add the login step:

```python
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

        print("  Filling search form...", end=" ", flush=True)
        await _fill_search_form(page, booking)
        print("submitted")

        print("  Waiting for results...", end=" ", flush=True)
        results = await _extract_results(page, booking)
        print(f"{len(results)} vehicles found")

        await page.close()
        return results
```

- [ ] **Step 2: Update scrape() to load credentials and pass them to _run_scrape()**

Replace the existing `scrape()` function:

```python
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
```

- [ ] **Step 3: Run full test suite**

```bash
source .venv/bin/activate && python -m pytest tests/test_scraper.py -v
```

Expected: all scraper tests still pass.

- [ ] **Step 4: Commit**

```bash
git add src/car_tracker/scraper.py
git commit -m "feat(scraper): wire Costco login into scrape() and _run_scrape()"
```

---

## Task 6: Add credentials and run integration test

**Files:**
- Modify: `.env`

- [ ] **Step 1: Add Costco credentials to .env**

Open `.env` and add:

```
COSTCO_USERNAME=<your Costco email>
COSTCO_PASSWORD=<your Costco password>
```

- [ ] **Step 2: Run in debug mode to verify login works**

```bash
source .venv/bin/activate && python -m car_tracker --config config.yaml --debug
```

Watch the headed Chrome window. Verify:
1. The login form appears and fills automatically
2. Login succeeds (header updates, Login link disappears)
3. Search form fills and submits
4. Results load with the member savings banner visible

If any `_LOGIN_*` selector is wrong, the error message will name which one. Update the constant in `scraper.py` and re-run.

- [ ] **Step 3: Confirm member pricing in the database**

```bash
sqlite3 data/results.db "
SELECT v.name, v.brand, v.total_price
FROM vehicles v
JOIN runs r ON v.run_id = r.id
WHERE r.id = (SELECT MAX(id) FROM runs)
AND v.name = 'Fullsize Car' AND v.brand = 'Budget';
"
```

Expected: `Fullsize Car|Budget|307.32` (or close to it — prices fluctuate).

- [ ] **Step 4: Run headless to confirm cron-mode works**

```bash
source .venv/bin/activate && python -m car_tracker --config config.yaml
```

Expected output includes `Logging in... done` and the sent email shows member pricing.

- [ ] **Step 5: Verify .env is not tracked**

`.env` is in `.gitignore` and must never be committed. Confirm:

```bash
git status
```

Expected: `.env` does not appear in the output. If it does, run `git rm --cached .env` immediately.

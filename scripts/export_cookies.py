#!/usr/bin/env python3
"""Export costcotravel.com cookies from Chrome for use as COSTCO_COOKIES secret.

Usage:
    uv run --with browser-cookie3 python scripts/export_cookies.py | pbcopy

Prints a JSON array to stdout. Pipe it to pbcopy or redirect to a file,
then paste as the COSTCO_COOKIES GitHub secret value.
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        import browser_cookie3
    except ImportError:
        print("browser-cookie3 not found. Run with: uv run --with browser-cookie3 python scripts/export_cookies.py", file=sys.stderr)
        return 1

    domains = (".costcotravel.com", "www.costcotravel.com", "costcotravel.com")

    print("Reading Chrome cookies (you may see a macOS keychain prompt)...", file=sys.stderr)
    jar = browser_cookie3.chrome(domain_name="costcotravel.com")

    cookies = []
    for c in jar:
        if any(d in c.domain for d in ("costcotravel",)):
            cookies.append({
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "secure": c.secure,
                "httpOnly": bool(getattr(c, "_rest", {}).get("HttpOnly", False)),
                "sameSite": "Lax",
            })

    if not cookies:
        print("No costcotravel.com cookies found — make sure you're logged in to costcotravel.com in Chrome.", file=sys.stderr)
        return 1

    print(f"Found {len(cookies)} cookie(s).", file=sys.stderr)
    print(json.dumps(cookies, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import logging
import time

import requests

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; jobradar/0.1; personal job monitor)",
    "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
}


def fetch_static(url: str, retries: int = 3, timeout: int = 20) -> str:
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            resp.raise_for_status()
            resp.encoding = resp.encoding or resp.apparent_encoding
            return resp.text
        except requests.RequestException as exc:
            last = exc
            log.warning("fetch %s failed (%d/%d): %s", url, attempt, retries, exc)
            time.sleep(2 * attempt)
    raise RuntimeError(f"could not fetch {url}") from last


def fetch_dynamic(url: str, wait_selector: str | None = None, timeout_ms: int = 30000) -> str:
    """Render with Playwright. Imported lazily so it is only needed when used."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(extra_http_headers={"Accept-Language": HEADERS["Accept-Language"]})
            page.goto(url, timeout=timeout_ms, wait_until="networkidle")
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=timeout_ms)
            return page.content()
        finally:
            browser.close()


def fetch(source: dict) -> str:
    if source.get("render") == "playwright":
        return fetch_dynamic(source["url"], source.get("selectors", {}).get("item"))
    return fetch_static(source["url"])

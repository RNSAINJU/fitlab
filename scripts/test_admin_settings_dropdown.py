#!/usr/bin/env python3
"""Test admin Settings sidebar dropdown on desktop and short mobile viewports."""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
USERNAME = sys.argv[2] if len(sys.argv) > 2 else "admintest"
PASSWORD = sys.argv[3] if len(sys.argv) > 3 else "TestAdminPass123!"


def login(page):
    page.goto(f"{BASE}/accounts/login/", wait_until="networkidle")
    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


def test_viewport(page, width, height):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(f"{BASE}/admin-portal/", wait_until="networkidle")

    if width < 961:
        page.click("[data-sidebar-toggle]")
        page.wait_for_timeout(250)

    toggle = page.locator("[data-sidebar-group-toggle]")
    group = page.locator("[data-sidebar-group]")
    subnav = page.locator("#admin-settings-subnav")
    general = page.locator('#admin-settings-subnav a[href*="settings"]')

    sidebar = page.locator(".admin-sidebar")
    overflow_y = sidebar.evaluate("el => getComputedStyle(el).overflowY")

    toggle.click()
    page.wait_for_timeout(250)

    is_open = group.evaluate("el => el.classList.contains('is-open')")
    subnav_display = subnav.evaluate("el => getComputedStyle(el).display")
    general_visible = general.first.is_visible() if general.count() else False

    return {
        "viewport": f"{width}x{height}",
        "overflow_y": overflow_y,
        "is_open": is_open,
        "subnav_display": subnav_display,
        "general_visible": general_visible,
        "ok": is_open and subnav_display == "flex" and general_visible,
    }


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        login(page)

        results = [
            test_viewport(page, 1280, 800),
            test_viewport(page, 390, 844),
            test_viewport(page, 390, 568),
        ]

        browser.close()

    for row in results:
        print(row)
    print("js_errors:", errors)
    ok = all(r["ok"] for r in results)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())

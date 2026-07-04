#!/usr/bin/env python3
"""Test home page mobile menu toggle."""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(URL, wait_until="networkidle", timeout=30000)

        toggle = page.locator("#home-menu-toggle")
        nav = page.locator("#home-mobile-nav")

        toggle_visible = toggle.is_visible()
        toggle_display = toggle.evaluate(
            "el => window.getComputedStyle(el).display"
        )
        toggle_pe = toggle.evaluate(
            "el => window.getComputedStyle(el).pointerEvents"
        )
        toggle_z = toggle.evaluate(
            "el => window.getComputedStyle(el).zIndex"
        )
        nav_open_before = nav.evaluate("el => el.classList.contains('is-open')")

        # Check what element is at center of toggle button
        box = toggle.bounding_box()
        top_el = None
        if box:
            cx = box["x"] + box["width"] / 2
            cy = box["y"] + box["height"] / 2
            top_el = page.evaluate(
                """([x, y]) => {
                    const el = document.elementFromPoint(x, y);
                    return el ? el.id || el.className || el.tagName : null;
                }""",
                [cx, cy],
            )

        toggle.click(timeout=5000)
        page.wait_for_timeout(300)

        nav_open_after = nav.evaluate("el => el.classList.contains('is-open')")
        nav_display = nav.evaluate("el => window.getComputedStyle(el).display")
        nav_visibility = nav.evaluate("el => window.getComputedStyle(el).visibility")

        print("URL:", URL)
        print("toggle_visible:", toggle_visible)
        print("toggle_display:", toggle_display)
        print("toggle_pointer_events:", toggle_pe)
        print("toggle_z_index:", toggle_z)
        print("element_at_toggle_center:", top_el)
        print("nav_open_before:", nav_open_before)
        print("nav_open_after_click:", nav_open_after)
        print("nav_display_after:", nav_display)
        print("nav_visibility_after:", nav_visibility)
        print("js_errors:", errors)

        ok = nav_open_after and nav_display == "flex"
        print("RESULT:", "PASS" if ok else "FAIL")
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())

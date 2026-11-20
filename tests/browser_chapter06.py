"""Chromium responsive, semantic and live-filter QA for CAN Chapter 06."""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "chapter06"
VIEWPORTS = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def run():
    REPORTS.mkdir(parents=True, exist_ok=True)
    findings = []
    with sync_playwright() as engine:
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        assert chrome, "Chromium/Google Chrome executable not available"
        browser = engine.chromium.launch(headless=True, executable_path=chrome)
        for width, height in VIEWPORTS:
            page = browser.new_page(
                viewport={"width": width, "height": height},
                device_scale_factor=1,
            )
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto((ROOT / "06.html").as_uri(), wait_until="load")
            assert page.locator("main article h1").count() == 1
            assert page.locator("figure").count() == 3
            assert page.locator("figure figcaption").count() == 3
            for img in page.locator("figure img").all():
                img.scroll_into_view_if_needed()
                img.evaluate("(element) => element.decode()")
            assert page.locator("figure img").evaluate_all(
                "(imgs) => imgs.every(i => i.complete && i.naturalWidth > 0)"
            ), "one or more standalone diagrams did not load"
            status = page.locator("#filter-result")
            assert status.get_attribute("data-match") == "true"
            assert "SIDH=0x24" in status.inner_text()
            change = page.locator("#test-other")
            change.focus()
            assert change.evaluate("(button) => document.activeElement === button")
            change.press("Enter")
            assert status.get_attribute("data-match") == "false"
            page.locator("#ignore-low").click()
            assert status.get_attribute("data-match") == "true"
            assert "0x7F0" in status.inner_text()
            page.locator("#device").select_option("sja1000")
            assert status.get_attribute("data-match") == "false"
            assert "掩码 0x000" in status.inner_text()
            page.locator("#ignore-low").click()
            assert status.get_attribute("data-match") == "true"
            assert "掩码 0x00F" in status.inner_text()
            page.locator("#received").fill("0x800")
            assert status.get_attribute("data-match") == "invalid"
            page.locator("#reset-demo").click()
            assert status.get_attribute("data-match") == "true"
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth - window.innerWidth"
            )
            assert overflow <= 1, f"document overflows at {width}px by {overflow}px"
            assert not errors, f"JavaScript errors at {width}px: {errors}"
            if width <= 390:
                assert page.locator(".figure-scroll").first.evaluate(
                    "(el) => el.scrollWidth > el.clientWidth"
                ), "expected diagram-local horizontal scroll on narrow mobile"
            page.screenshot(
                path=str(REPORTS / f"chapter06-{width}.png"), full_page=True
            )
            findings.append({
                "width": width, "height": height,
                "overflow_px": overflow, "figures": 3,
                "interaction": "passed", "pageerrors": errors,
            })
            page.close()
        print_page = browser.new_page(viewport={"width": 1440, "height": 900})
        print_page.goto((ROOT / "06.html").as_uri(), wait_until="load")
        print_page.emulate_media(media="print")
        assert print_page.locator("main article").is_visible()
        assert print_page.locator("figure").count() == 3
        print_page.close()
        browser.close()
    (REPORTS / "report.json").write_text(
        json.dumps({
            "status": "passed", "viewports": findings,
            "print_smoke": "passed",
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Chapter 06 browser QA passed:", [r["width"] for r in findings])


if __name__ == "__main__":
    run()

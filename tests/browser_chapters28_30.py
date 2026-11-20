"""Responsive browser QA for CAN chapters 28–30.

Requires Playwright Python package and a local Chromium or Google Chrome.
Run: python tests/browser_chapters28_30.py
"""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "chapters28-30"
VIEWPORTS = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def exercise(page, chapter):
    assert page.locator("main article h1").count() == 1
    assert page.locator("figure").count() == 2
    assert page.locator("figure figcaption").count() == 2
    assert page.locator("figure svg[role='img']").count() == 2
    assert page.locator("figure svg title").count() == 2
    assert page.locator("figure svg desc").count() == 2
    assert page.locator(".chapter-footer a").count() >= 2
    rendered = page.locator("figure svg").evaluate_all(
        "(svgs) => svgs.every(s => s.getBoundingClientRect().width > 0 && s.getBoundingClientRect().height > 0)"
    )
    assert rendered, f"chapter {chapter}: diagram failed to render"
    if chapter == 28:
        status = page.locator("#load-result")
        assert "10.40%" in status.inner_text()
        field = page.locator("#period")
        field.fill("10")
        assert "20.80%" in status.inner_text()
        field.fill("20")
    elif chapter == 29:
        power = page.locator("#power-result")
        assert "249.5" in power.inner_text()
        page.locator("#wake-other").focus()
        assert page.locator("#wake-other").evaluate(
            "(el) => document.activeElement === el"
        )
        page.locator("#wake-other").press("Enter")
        assert "保持休眠" in page.locator("#wake-result").inner_text()
        page.locator("#wake-mode").select_option("normal")
        assert "唤醒 MCU" in page.locator("#wake-result").inner_text()
        page.locator("#duty").fill("0")
        assert "50.0" in power.inner_text()
    elif chapter == 30:
        packet = page.locator("#packet-result")
        assert "2E FB C4 09 AA 05 07 01" in packet.inner_text()
        page.locator("#temp").fill("0")
        assert "00 00 C4 09 AA 05 07 01" in packet.inner_text()


def run():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    assert chrome, "Chrome/Chromium is required for browser QA"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=chrome)
        for chapter in (28, 29, 30):
            for width, height in VIEWPORTS:
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                )
                errors = []
                page.on("pageerror", lambda err, errors=errors: errors.append(str(err)))
                page.goto((ROOT / f"{chapter}.html").as_uri(), wait_until="load")
                exercise(page, chapter)
                overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth - innerWidth"
                )
                assert overflow <= 1, (
                    f"chapter {chapter} at {width}px has document overflow {overflow}px"
                )
                assert not errors, f"chapter {chapter} JS errors: {errors}"
                path = REPORT_DIR / f"chapter{chapter}-{width}.png"
                page.screenshot(path=str(path), full_page=True)
                records.append({
                    "chapter": chapter, "width": width, "overflow_px": overflow,
                    "figures": 2, "interaction": "passed", "errors": errors
                })
                page.close()
            print_page = browser.new_page(viewport={"width": 1440, "height": 900})
            print_page.goto((ROOT / f"{chapter}.html").as_uri())
            print_page.emulate_media(media="print")
            assert print_page.locator("main article h1").is_visible()
            print_page.close()
            for figure in (1, 2):
                svg_page = browser.new_page()
                svg_page.goto(
                    (ROOT / f"assets/chapter{chapter}-figure{figure}.svg").as_uri()
                )
                assert svg_page.locator("svg").count() == 1
                assert svg_page.locator("svg title").count() == 1
                assert svg_page.locator("svg desc").count() == 1
                svg_page.close()
        browser.close()
    output = {
        "result": "passed",
        "viewports": records,
        "standalone_svg": "6 inspected",
        "print_smoke": "passed for 3 articles",
    }
    (REPORT_DIR / "report.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("CAN chapters 28–30 browser QA passed", len(records), "viewports")


if __name__ == "__main__":
    run()

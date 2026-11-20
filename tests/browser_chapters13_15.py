"""Actual Chromium checks for the CAN long-form articles (chapters 13–15)."""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "chapters13-15"
VIEWPORTS = [(1440, 900), (768, 1024), (390, 844), (360, 800)]
DEMO_TESTS = {
    13: ('[data-demo="filter"] [data-id="528"]', "未匹配",
         '[data-demo="filter"] [data-id="512"]', "通过过滤器"),
    14: ('[data-demo="length"] [data-length="100"]', "1000 ns",
         '[data-demo="length"] [data-rate="1000"]', "100.0%"),
    15: ('[data-demo="termination"] [data-count="3"]', "40 Ω",
         '[data-demo="termination"] [data-count="0"]', "∞ Ω"),
}


def run():
    REPORTS.mkdir(parents=True, exist_ok=True)
    records = []
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    assert chrome, "Chrome/Chromium is unavailable: browser QA cannot be claimed"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=chrome)
        for chapter in [13, 14, 15]:
            for width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height},
                                        device_scale_factor=1)
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto((ROOT / f"{chapter:02d}.html").as_uri(), wait_until="load")
                assert page.locator("main article h1").count() == 1
                assert page.locator("figure").count() == 1
                assert page.locator("figure figcaption").count() == 1
                for img in page.locator("figure img").all():
                    img.scroll_into_view_if_needed()
                    img.evaluate("(element) => element.decode()")
                assert page.locator("figure img").evaluate_all(
                    "(images) => images.every(img => img.complete && img.naturalWidth > 0)"
                ), f"Chapter {chapter}: SVG failed to render"
                first, expected1, second, expected2 = DEMO_TESTS[chapter]
                button = page.locator(first)
                button.focus()
                assert button.evaluate("(node) => document.activeElement === node")
                button.press("Enter")
                result = page.locator("[data-demo] [data-output]")
                assert expected1 in result.inner_text(), (
                    f"Chapter {chapter}: primary interaction did not update content")
                page.locator(second).click()
                assert expected2 in result.inner_text(), (
                    f"Chapter {chapter}: secondary interaction did not update content")
                assert page.locator("[data-demo] button[aria-pressed='true']").count() >= 1
                overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth - window.innerWidth")
                assert overflow <= 1, (
                    f"Chapter {chapter} document overflow at {width}px: {overflow}px")
                assert not errors, f"Chapter {chapter} JS errors at {width}px: {errors}"
                page.screenshot(
                    path=str(REPORTS / f"chapter{chapter:02d}-{width}.png"),
                    full_page=True,
                )
                records.append({"chapter": chapter, "width": width, "height": height,
                                "document_overflow_px": overflow,
                                "svg_loaded": True, "keyboard_and_click": "passed",
                                "pageerrors": errors})
                page.close()
            print_page = browser.new_page(viewport={"width": 1440, "height": 900})
            print_page.goto((ROOT / f"{chapter:02d}.html").as_uri(), wait_until="load")
            print_page.emulate_media(media="print")
            assert print_page.locator("main article h1").is_visible()
            assert print_page.locator("figure img").is_visible()
            print_page.close()
        browser.close()
    (REPORTS / "report.json").write_text(
        json.dumps({"status": "passed", "viewports": records,
                    "print_smoke": [13, 14, 15]}, ensure_ascii=False, indent=2)+"\n",
        encoding="utf-8",
    )
    print("Browser QA passed for chapters 13, 14, 15 at", [w for w, _ in VIEWPORTS])


if __name__ == "__main__":
    run()

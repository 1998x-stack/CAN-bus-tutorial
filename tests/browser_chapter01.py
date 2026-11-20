"""Playwright smoke QA for the interactive Chapter 01 CAN overview."""
from pathlib import Path
import json

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "chapter01"
REPORTS.mkdir(parents=True, exist_ok=True)

SIZES = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def run():
    results = []
    with sync_playwright() as engine:
        browser = engine.chromium.launch(headless=True)
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((ROOT / "01.html").as_uri(), wait_until="load")
            page.locator("main article h1").wait_for(state="visible")
            assert page.locator("main article h1").count() == 1
            assert page.locator("figure").count() == 3
            assert page.locator("figure figcaption").count() == 3
            assert page.locator("svg#signal-svg title").count() == 1
            assert page.locator("figure img").evaluate_all(
                "(images) => images.every(img => img.complete && img.naturalWidth > 0)"
            ), "Diagram asset failed to load"
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth - window.innerWidth"
            )
            assert overflow <= 1, f"Unexpected horizontal overflow at {width}px: {overflow}px"
            assert page.locator('button[data-bit="dominant"]').get_attribute("aria-pressed") == "true"
            page.locator('button[data-bit="recessive"]').click()
            assert "差分 ≈ 0 V" in page.locator("#demo-status").inner_text()
            assert page.locator("#signal-svg").get_attribute("data-selected") == "recessive"
            assert page.locator('button[data-bit="recessive"]').get_attribute("aria-pressed") == "true"
            page.locator('button[data-bit="dominant"]').click()
            assert "差分 ≈ 2 V" in page.locator("#demo-status").inner_text()
            assert page.locator('button[data-bit="recessive"]').get_attribute("aria-pressed") == "false"
            assert not errors, f"JavaScript errors at {width}px: {errors}"
            page.screenshot(path=str(REPORTS / f"chapter01-{width}.png"), full_page=True)
            results.append({"width": width, "height": height, "overflow_px": overflow,
                            "figures": 3, "interaction": "passed", "pageerrors": errors})
            page.close()
        print_page = browser.new_page(viewport={"width": 1440, "height": 900})
        print_page.goto((ROOT / "01.html").as_uri())
        print_page.emulate_media(media="print")
        assert print_page.locator("figure").count() == 3
        assert print_page.locator("main article").is_visible()
        print_page.close()
        browser.close()
    (REPORTS / "report.json").write_text(
        json.dumps({"status": "passed", "viewports": results, "print_smoke": "passed"},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print("Chapter 01 Playwright QA passed:", [r["width"] for r in results])


if __name__ == "__main__":
    run()


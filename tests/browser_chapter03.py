"""Playwright acceptance checks for chapter 03 progressive arbitration."""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "chapter03"
SIZES = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as engine:
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        assert chrome, "Missing Chrome/Chromium on GitHub Actions runner"
        browser = engine.chromium.launch(headless=True, executable_path=chrome)
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((ROOT / "03.html").as_uri(), wait_until="load")
            assert page.locator("main article h1").count() == 1
            assert page.locator("figure").count() == 3
            assert page.locator("figure figcaption").count() == 3
            assert page.locator("[data-scenario]").count() == 4
            for img in page.locator("figure img").all():
                img.scroll_into_view_if_needed()
                img.evaluate("(image) => image.decode()")
            assert page.locator("figure img").evaluate_all(
                "(images) => images.every(img => img.complete && img.naturalWidth > 0)"
            ), "A standalone SVG could not be loaded"
            assert page.locator("#bit-position").inner_text() == "第 1 / 12 位"
            page.locator("#step-next").click()
            assert "A=0，B=1，总线=0" in page.locator("#arbitration-status").inner_text()
            assert "获胜" in page.locator("#arbitration-status").inner_text()
            page.locator('button[data-scenario="remote"]').click()
            assert page.locator('button[data-scenario="remote"]').get_attribute("aria-pressed") == "true"
            for _ in range(11):
                page.locator("#step-next").click()
            assert "RTR" in page.locator("#arbitration-status").inner_text()
            assert "获胜" in page.locator("#arbitration-status").inner_text()
            # Keyboard scenario activation.
            ext = page.locator('button[data-scenario="extended"]')
            ext.focus()
            assert ext.evaluate("(element) => document.activeElement === element")
            ext.press("Enter")
            assert page.locator("#bit-position").inner_text() == "第 1 / 13 位"
            for _ in range(12):
                page.locator("#step-next").click()
            assert "IDE" in page.locator("#arbitration-status").inner_text()
            assert "获胜" in page.locator("#arbitration-status").inner_text()
            page.locator('button[data-scenario="same"]').click()
            for _ in range(11):
                page.locator("#step-next").click()
            assert "没有选出唯一发送者" in page.locator("#arbitration-status").inner_text()
            page.locator('button[data-scenario="different"]').click()
            assert page.locator("#bit-position").inner_text() == "第 1 / 12 位"
            assert page.locator("#step-prev").is_disabled()
            overflow = page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
            assert overflow <= 1, f"Unexpected document overflow at {width}px: {overflow}px"
            assert not errors, f"JavaScript errors at {width}px: {errors}"
            page.screenshot(path=str(OUT / f"chapter03-{width}.png"), full_page=True)
            results.append({"width":width, "height":height, "overflow_px":overflow,
                            "figures":3, "interactions":"passed", "js_errors":errors})
            page.close()
        printed = browser.new_page(viewport={"width": 1440, "height": 900})
        printed.goto((ROOT / "03.html").as_uri())
        printed.emulate_media(media="print")
        assert printed.locator("main article").is_visible()
        assert printed.locator("figure").count() == 3
        printed.close()
        browser.close()
    (OUT / "report.json").write_text(json.dumps(
        {"result":"passed","viewports":results,"print_smoke":"passed"},
        ensure_ascii=False, indent=2
    ) + "\n", encoding="utf-8")
    print("Chapter 03 browser QA passed:", [r["width"] for r in results])


if __name__ == "__main__":
    main()


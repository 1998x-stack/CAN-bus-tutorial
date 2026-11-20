"""Browser QA for chapters 25–27, including interactive calculations.
Run: python tests/browser_chapters_25_27.py
Requires: pip install playwright; python -m playwright install chromium
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "chapter25-27"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    for chapter in (25, 26, 27):
        for width in (1440, 390, 360):
            page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto((ROOT / f"{chapter}.html").as_uri())
            page.locator("h1").wait_for()
            assert page.locator("h1").count() == 1, (chapter, width, "h1")
            assert page.locator('img[src^="assets/olah-ch"]').evaluate("(img) => img.complete && img.naturalWidth > 0"), (chapter, width, "svg")
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), (chapter, width, "overflow")
            page.keyboard.press("Tab")
            assert page.evaluate("document.activeElement !== document.body"), (chapter, width, "keyboard focus")
            if chapter == 25:
                assert "22.2%" in page.locator("#out25").inner_text(), (chapter, width, "default load")
                page.locator("#fps25").fill("2000")
                assert "44.4%" in page.locator("#out25").inner_text(), (chapter, width, "changed load")
            elif chapter == 26:
                assert "60.0" in page.locator("#r26").inner_text(), (chapter, width, "default resistance")
                page.locator("#n26").select_option("3")
                assert "40.0" in page.locator("#r26").inner_text(), (chapter, width, "three terminations")
            else:
                for _ in range(5):
                    page.locator("#add27").click()
                assert "溢出 1" in page.locator("#out27").inner_text(), (chapter, width, "queue overflow")
                page.locator("#reset27").click()
                assert "溢出 0" in page.locator("#out27").inner_text(), (chapter, width, "queue reset")
            assert not errors, (chapter, width, errors)
            page.screenshot(path=str(OUT / f"chapter-{chapter}-{width}.png"), full_page=True)
            print(f"chapter {chapter}, {width}px: OK")
            page.close()
    browser.close()

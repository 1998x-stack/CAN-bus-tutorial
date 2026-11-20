"""Browser acceptance check for interactive CAN Chapter 04 at 4 screen sizes."""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "chapter04"
SIZES = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def run():
    REPORT.mkdir(parents=True, exist_ok=True)
    runs = []
    with sync_playwright() as engine:
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        assert chrome, "Chrome/Chromium executable not found"
        browser = engine.chromium.launch(headless=True, executable_path=chrome)
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((ROOT / "04.html").as_uri(), wait_until="load")
            assert page.locator("main article h1").count() == 1
            assert page.locator("figure").count() == 3
            assert page.locator("figure figcaption").count() == 3
            assert page.locator("button[data-error]").count() == 5
            assert page.locator("button[data-preset]").count() == 6
            for img in page.locator("figure img").all():
                img.scroll_into_view_if_needed()
                img.evaluate("(img) => img.decode()")
            assert page.locator("figure img").evaluate_all(
                "(images) => images.every(img => img.complete && img.naturalWidth > 0)"
            ), "One of the standalone SVG figures was not rendered"
            # All relative HTML navigation targets should exist in this checkout.
            hrefs = page.locator("a[href]").evaluate_all(
                "(elements) => elements.map(element => element.getAttribute('href'))"
            )
            for href in hrefs:
                if href.endswith(".html") and not href.startswith(("http://", "https://")):
                    assert (ROOT / href).is_file(), "Broken chapter link: " + href
            assert "Error Active" in page.locator("#state-status").inner_text()
            assert page.locator("#state-result").get_attribute("data-state") == "active"
            page.locator('button[data-error="stuff"]').click()
            assert "Stuff Error" in page.locator("#error-result").inner_text()
            assert "SOF 到 CRC" in page.locator("#error-result").inner_text()
            assert page.locator('button[data-error="stuff"]').get_attribute("aria-pressed") == "true"
            # Native button must be usable from keyboard.
            button = page.locator('button[data-error="bit"]')
            button.focus()
            assert button.evaluate("(element) => document.activeElement === element")
            button.press("Enter")
            assert "Bit Error" in page.locator("#error-result").inner_text()
            page.locator('button[data-preset="passive"]').click()
            assert "Error Passive" in page.locator("#state-status").inner_text()
            assert page.locator("#rec-input").input_value() == "128"
            page.locator('button[data-preset="rx-high"]').click()
            assert page.locator("#state-result").get_attribute("data-state") == "passive"
            assert page.locator("#rec-input").input_value() == "255"
            page.locator('button[data-preset="off"]').click()
            assert "Bus-Off" in page.locator("#state-status").inner_text()
            assert page.locator("#state-result").get_attribute("data-state") == "off"
            page.locator('button[data-preset="warning"]').click()
            assert "Error Active" in page.locator("#state-status").inner_text()
            assert "Error Warning" in page.locator("#state-reason").inner_text()
            page.locator("#tec-input").fill("-1")
            assert "请输入有效的整数" in page.locator("#state-status").inner_text()
            page.locator('button[data-preset="normal"]').click()
            assert page.locator("#state-result").get_attribute("data-state") == "active"
            assert page.locator('button[data-preset="normal"]').get_attribute("aria-pressed") == "true"
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth - window.innerWidth"
            )
            assert overflow <= 1, f"Unexpected horizontal overflow at {width}px: {overflow}px"
            assert not errors, f"JavaScript errors at {width}px: {errors}"
            page.screenshot(path=str(REPORT / f"chapter04-{width}.png"), full_page=True)
            runs.append({"width": width, "height": height, "overflow_px": overflow,
                         "figures": 3, "interaction": "passed", "javascript_errors": errors})
            page.close()
        printed = browser.new_page(viewport={"width": 1440, "height": 900})
        printed.goto((ROOT / "04.html").as_uri())
        printed.emulate_media(media="print")
        assert printed.locator("main article").is_visible()
        assert printed.locator("figure").count() == 3
        printed.close()
        browser.close()
    (REPORT / "report.json").write_text(json.dumps(
        {"result": "passed", "viewports": runs, "print_smoke": "passed"},
        ensure_ascii=False, indent=2
    ) + "\n", encoding="utf-8")
    print("Chapter 04 browser QA passed at widths:", [r["width"] for r in runs])


if __name__ == "__main__":
    run()


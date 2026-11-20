"""Playwright visual/interactive QA for the rebuilt CAN Chapter 05."""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "chapter05"
SIZES = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def run():
    REPORTS.mkdir(parents=True, exist_ok=True)
    outcomes = []
    with sync_playwright() as engine:
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        assert chrome, "Chrome/Chromium is unavailable on the test runner"
        browser = engine.chromium.launch(headless=True, executable_path=chrome)
        for width, height in SIZES:
            page = browser.new_page(
                viewport={"width": width, "height": height}, device_scale_factor=1
            )
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto((ROOT / "05.html").as_uri(), wait_until="load")
            assert page.locator("main article h1").count() == 1
            assert page.locator("figure").count() == 3
            assert page.locator("figure figcaption").count() == 3
            for img in page.locator("figure img").all():
                img.scroll_into_view_if_needed()
                img.evaluate("(element) => element.decode()")
            assert page.locator("figure img").evaluate_all(
                "(imgs) => imgs.every(img => img.complete && img.naturalWidth > 0)"
            ), "Diagram could not render"
            status = page.locator("#calc-result")
            assert "500.000 kbit/s" in status.inner_text()
            assert "87.50%" in status.inner_text()
            button = page.locator("#preset-b")
            button.focus()
            assert button.evaluate("(node) => document.activeElement === node")
            button.press("Enter")
            assert "500.000 kbit/s" in status.inner_text()
            assert "83.33%" in status.inner_text()
            page.locator("#sjw").fill("4")
            assert "SJW 不能大于 BS2" in status.inner_text()
            page.locator("#sjw").fill("2")
            assert "500.000 kbit/s" in status.inner_text()
            button.click()
            assert "87.50%" in status.inner_text()
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth - window.innerWidth"
            )
            assert overflow <= 1, f"document overflow at {width}px: {overflow}px"
            assert not errors, f"JavaScript errors at {width}px: {errors}"
            page.screenshot(path=str(REPORTS / f"chapter05-{width}.png"), full_page=True)
            outcomes.append({
                "width": width, "height": height, "overflow_px": overflow,
                "figures": 3, "interaction": "passed", "pageerrors": errors
            })
            page.close()
        print_page = browser.new_page(viewport={"width": 1440, "height": 900})
        print_page.goto((ROOT / "05.html").as_uri())
        print_page.emulate_media(media="print")
        assert print_page.locator("main article").is_visible()
        assert print_page.locator("figure").count() == 3
        print_page.close()
        browser.close()
    (REPORTS / "report.json").write_text(
        json.dumps(
            {"status": "passed", "viewports": outcomes, "print_smoke": "passed"},
            ensure_ascii=False, indent=2
        ) + "\n",
        encoding="utf-8",
    )
    print("Chapter 05 browser QA passed:", [x["width"] for x in outcomes])


if __name__ == "__main__":
    run()

"""Chromium responsive and interactive QA of CAN Chapter 02 (Playwright)."""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "chapter02"
SIZES = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def run():
    REPORTS.mkdir(parents=True, exist_ok=True)
    findings = []
    with sync_playwright() as engine:
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        assert chrome, "Chrome/Chromium not found on GitHub runner"
        browser = engine.chromium.launch(headless=True, executable_path=chrome)
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((ROOT / "02.html").as_uri(), wait_until="load")
            assert page.locator("main article h1").count() == 1
            assert page.locator("figure").count() == 3
            assert page.locator("figure figcaption").count() == 3
            assert page.locator("button[data-format]").count() == 3
            for img in page.locator("figure img").all():
                img.scroll_into_view_if_needed()
                img.evaluate("(img) => img.decode()")
            assert page.locator("figure img").evaluate_all(
                "(images) => images.every(img => img.complete && img.naturalWidth > 0)"
            ), "standalone SVG failed to render"
            assert "108 bit" in page.locator("#frame-formula").inner_text()
            assert page.locator('button[data-format="base"]').get_attribute("aria-pressed") == "true"
            # Interaction from mouse.
            page.locator('button[data-format="extended"]').click()
            assert "128 bit" in page.locator("#frame-formula").inner_text()
            assert "29 位 ID" in page.locator("#frame-status").inner_text()
            assert page.locator('button[data-format="extended"]').get_attribute("aria-pressed") == "true"
            # Keyboard interaction from focusable native control.
            remote = page.locator('button[data-format="remote"]')
            remote.focus()
            assert remote.evaluate("(button) => document.activeElement === button")
            remote.press("Enter")
            assert "44 bit" in page.locator("#frame-formula").inner_text()
            assert page.locator("#frame-strip .frame-block").count() == 6
            assert "没有数据场" in page.locator("#frame-status").inner_text()
            assert remote.get_attribute("aria-pressed") == "true"
            page.locator('button[data-format="base"]').click()
            assert "108 bit" in page.locator("#frame-formula").inner_text()
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth - window.innerWidth"
            )
            assert overflow <= 1, f"document overflows at {width}px by {overflow}px"
            assert not errors, f"JavaScript errors at {width}px: {errors}"
            page.screenshot(path=str(REPORTS / f"chapter02-{width}.png"), full_page=True)
            findings.append({"viewport": width, "height": height, "overflow_px": overflow,
                             "figures": 3, "interaction": "passed", "pageerrors": errors})
            page.close()
        print_page = browser.new_page(viewport={"width": 1440, "height": 900})
        print_page.goto((ROOT / "02.html").as_uri())
        print_page.emulate_media(media="print")
        assert print_page.locator("main article").is_visible()
        assert print_page.locator("figure").count() == 3
        print_page.close()
        browser.close()
    (REPORTS / "report.json").write_text(json.dumps(
        {"status": "passed", "viewports": findings, "print_smoke": "passed"},
        ensure_ascii=False, indent=2
    ) + "\n", encoding="utf-8")
    print("Chapter 02 Chrome QA passed:", [r["viewport"] for r in findings])


if __name__ == "__main__":
    run()


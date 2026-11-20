"""Visual, interaction and responsive QA for CAN chapters 16-18.

Run: python tests/browser_chapters16_18.py
Requires playwright==1.56.0 and a local Chrome/Chromium executable.
"""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "chapters16-18"
SIZES = [(1440, 900), (390, 844), (360, 800)]
FIGURES = {16: 1, 17: 2, 18: 3}
SVG_FILES = [
    "chapter16-differential-wave.svg",
    "chapter17-propagation-path.svg",
    "chapter17-bit-segments.svg",
    "chapter18-canopen-layers.svg",
    "chapter18-pdo-mapping.svg",
    "chapter18-sdo-exchange.svg",
]


def check_interaction(page, chapter):
    if chapter == 16:
        result = page.locator("#c16-result")
        assert "Vdiff = 2.00 V" in result.inner_text()
        page.locator("#c16-noise").evaluate(
            "(el) => { el.value = '1'; el.dispatchEvent(new Event('input', {bubbles:true})); }"
        )
        assert "CAN_H = 4.50 V" in result.inner_text()
        assert "Vdiff = 2.00 V" in result.inner_text()
        assert "Vcm = 3.50 V" in result.inner_text()
    elif chapter == 17:
        status = page.locator("#c17-result")
        assert "500.000 kbit/s" in status.inner_text()
        assert "83.33%" in status.inner_text()
        btn = page.locator("#c17-calc")
        btn.focus()
        assert btn.evaluate("(x) => document.activeElement === x")
        page.locator("#c17-sjw").fill("4")
        btn.press("Enter")
        assert "参数无效" in status.inner_text()
        page.locator("#c17-sjw").fill("1")
        btn.click()
        assert "500.000 kbit/s" in status.inner_text()
    elif chapter == 18:
        status = page.locator("#c18-result")
        assert "0x601" in status.inner_text()
        btn = page.locator("#c18-generate")
        btn.focus()
        assert btn.evaluate("(x) => document.activeElement === x")
        page.locator("#c18-node").fill("2")
        btn.press("Enter")
        assert "0x602" in status.inner_text()
        assert "0x582" in status.inner_text()
        page.locator("#c18-node").fill("128")
        btn.click()
        assert "必须为" in status.inner_text()


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    assert chrome, "Chrome/Chromium unavailable; browser QA not verified"
    with sync_playwright() as engine:
        browser = engine.chromium.launch(headless=True, executable_path=chrome)
        for number, figure_count in FIGURES.items():
            for width, height in SIZES:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                page.goto((ROOT / f"{number:02d}.html").as_uri(), wait_until="load")
                assert page.locator("main article h1").count() == 1
                assert page.locator("figure").count() == figure_count
                assert page.locator("svg[role='img']").count() == figure_count
                assert page.locator("figure figcaption").count() == figure_count
                for item in page.locator("svg[role='img']").all():
                    assert item.locator("title").count() == 1
                    assert item.locator("desc").count() == 1
                    dims = item.bounding_box()
                    assert dims and dims["width"] > 100 and dims["height"] > 40
                for math in page.locator("math").all():
                    assert math.evaluate("(el) => el.namespaceURI === 'http://www.w3.org/1998/Math/MathML'")
                    assert math.bounding_box()["height"] > 0
                check_interaction(page, number)
                overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth - window.innerWidth"
                )
                assert overflow <= 1, f"{number:02d}.html overflow at {width}px: {overflow}px"
                assert not errors, f"{number:02d}.html JS errors at {width}px: {errors}"
                page.screenshot(path=str(OUT / f"chapter{number:02d}-{width}.png"), full_page=True)
                report.append({"chapter": number, "width": width, "overflow_px": overflow,
                               "figures": figure_count, "javascript_errors": errors,
                               "interaction": "passed"})
                page.close()
            print_page = browser.new_page(viewport={"width": 1440, "height": 900})
            print_page.goto((ROOT / f"{number:02d}.html").as_uri())
            print_page.emulate_media(media="print")
            assert print_page.locator("main article").is_visible()
            assert print_page.locator("figure").count() == figure_count
            print_page.close()
        for name in SVG_FILES:
            page = browser.new_page()
            page.goto((ROOT / "assets" / name).as_uri())
            svg = page.locator("svg").first
            assert svg.count() == 1
            assert svg.locator("title").count() == 1
            assert svg.locator("desc").count() == 1
            box = svg.bounding_box()
            assert box and box["width"] > 100 and box["height"] > 40
            page.close()
        browser.close()
    (OUT / "report.json").write_text(
        json.dumps({"status": "passed", "viewports": report,
                    "standalone_svgs": SVG_FILES, "print": "passed"},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Browser QA passed for chapters 16-18:", len(report), "viewports")


if __name__ == "__main__":
    run()

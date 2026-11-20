"""Playwright smoke checks for the revised CANopen chapters 19–21.

Run with: python tests/browser_chapters19_21.py
Requires playwright and Chromium/Chrome on the runner.
"""
from pathlib import Path
import json
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "canopen-19-21"
SIZES = [(1440, 900), (390, 844), (360, 800)]


def check_interaction(page, chapter: int):
    status = page.locator("#result")
    if chapter == 19:
        assert "DATA 01 05" in status.inner_text()
        page.locator("#node").fill("3")
        assert "DATA 01 03" in status.inner_text()
        page.locator("#timeout").fill("600")
        assert "0x00030258" in status.inner_text()
        page.locator("#node").fill("128")
        assert "输入越界" in status.inner_text()
    elif chapter == 20:
        assert "4660" in status.inner_text()
        page.locator("#cmd").select_option("80")
        page.locator("#payload").fill("00 00 02 06")
        assert "0x06020000" in status.inner_text()
        page.locator("#cmd").select_option("42")
        assert "未指示有效字节数" in status.inner_text()
    elif chapter == 21:
        assert "0x185" in status.inner_text()
        assert "E8 03 00 00 30 F8 FF FF" in status.inner_text()
        page.locator("#speed").fill("-1")
        assert "FF FF FF FF" in status.inner_text()
        page.locator("#pos").fill("2147483648")
        assert "输入无效" in status.inner_text()
    else:
        raise AssertionError(chapter)


def run():
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = []
    with sync_playwright() as engine:
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        assert chrome, "Chrome/Chromium not found"
        browser = engine.chromium.launch(headless=True, executable_path=chrome)
        for chapter in (19, 20, 21):
            for width, height in SIZES:
                page = browser.new_page(
                    viewport={"width": width, "height": height}, device_scale_factor=1
                )
                errors = []
                page.on("pageerror", lambda err: errors.append(str(err)))
                page.goto((ROOT / f"{chapter:02}.html").as_uri(), wait_until="load")
                assert page.locator("main article h1").count() == 1
                assert page.locator("figure").count() == 2
                assert page.locator("figure figcaption").count() == 2
                for img in page.locator("figure img").all():
                    img.scroll_into_view_if_needed()
                    img.evaluate("(el) => el.decode()")
                assert page.locator("figure img").evaluate_all(
                    "(imgs) => imgs.every(img => img.complete && img.naturalWidth > 0)"
                ), "SVG image missing or broken"
                assert page.locator("nav.course-nav a[aria-current='page']").count() == 1
                for element in page.locator("math").all():
                    assert element.evaluate(
                        "(el) => el.namespaceURI === 'http://www.w3.org/1998/Math/MathML'"
                    )
                    assert element.evaluate("(el) => el.getBoundingClientRect().width > 0")
                first_input = page.locator(".lab input").first
                first_input.focus()
                assert first_input.evaluate("(el) => el === document.activeElement")
                check_interaction(page, chapter)
                overflow = page.evaluate(
                    "() => document.documentElement.scrollWidth - innerWidth"
                )
                assert overflow <= 1, (
                    f"chapter {chapter} overflows {width}px viewport by {overflow}px"
                )
                assert not errors, f"chapter {chapter} JS errors: {errors}"
                page.screenshot(
                    path=str(REPORTS / f"chapter{chapter}-{width}.png"),
                    full_page=True,
                )
                output.append({
                    "chapter": chapter, "width": width, "overflow_px": overflow,
                    "figures": 2, "interaction": "passed", "pageerrors": errors,
                })
                page.close()
            print_page = browser.new_page(viewport={"width": 1440, "height": 900})
            print_page.goto((ROOT / f"{chapter:02}.html").as_uri())
            print_page.emulate_media(media="print")
            assert print_page.locator("main article").is_visible()
            assert print_page.locator("figure img").count() == 2
            print_page.close()
        browser.close()
    (REPORTS / "report.json").write_text(
        json.dumps({"status": "passed", "checks": output, "print_smoke": "passed"},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("CANopen chapters 19–21 visual QA passed")


if __name__ == "__main__":
    run()

"""Browser smoke QA: 1440 / 768 / 390 / 360 px, real details interaction and screenshots."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "chapter10-12"
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for chapter in ("10", "11", "12"):
        for width in (1440, 768, 390, 360):
            page = browser.new_page(viewport={"width": width, "height": 850},
                                    device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.goto((ROOT / f"{chapter}.html").as_uri(), wait_until="load")
            assert page.locator("main article h1").count() == 1, chapter
            assert page.locator("article figure svg").count() == 1, chapter
            assert page.locator("article svg title").count() == 1, chapter
            assert page.locator("article figcaption").count() == 1, chapter
            assert page.locator("article details").count() == 1, chapter
            page.locator("article details summary").click()
            assert page.locator("article details").evaluate("(el) => el.open"), chapter
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), (
                chapter, width, "horizontal page overflow"
            )
            css = page.locator('link[href="reading.css"]').evaluate(
                "(el) => el.sheet !== null"
            )
            assert css, (chapter, width, "missing local reading.css")
            svg_resource = page.locator('figure a[href$=".svg"]').get_attribute("href")
            assert (ROOT / svg_resource).is_file(), (chapter, svg_resource)
            assert not errors, (chapter, width, errors)
            if width in (1440, 390, 360):
                page.screenshot(path=str(OUT / f"{chapter}-{width}.png"), full_page=True)
            page.close()
    browser.close()
print("Chapters 10–12 browser checks passed at 1440/768/390/360.")

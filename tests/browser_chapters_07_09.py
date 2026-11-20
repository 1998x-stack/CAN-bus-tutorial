"""Run with: python -m pip install playwright && python -m playwright install chromium
Then: python tests/browser_chapters_07_09.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for chapter in ("07","08","09"):
        for width in (1440,768,390,360):
            page = browser.new_page(viewport={"width":width,"height":850})
            errors = []
            page.on("pageerror",lambda exc: errors.append(str(exc)))
            page.goto((ROOT / f"{chapter}.html").as_uri())
            assert page.locator("main h1").count()==1
            assert page.locator("figure img").count()==2
            assert page.locator("figure img").evaluate_all(
                "(images)=>images.every(img=>img.complete && img.naturalWidth>0)"
            ), f"{chapter}: missing SVG"
            if chapter=="07":
                page.locator("#recessive").click()
                assert "差分 0.0 V" in page.locator("#voltage-readout").inner_text()
                page.locator("#dominant").click()
                page.locator("#noise").evaluate(
                    "(el)=>{el.value='1';el.dispatchEvent(new Event('input',{bubbles:true}));}"
                )
                assert "差分 2.0 V" in page.locator("#voltage-readout").inner_text()
            elif chapter=="08":
                assert "500.000 kbit/s" in page.locator("#timing-result").inner_text()
                page.locator("#sjw").fill("4")
                assert "SJW 不能大于 BS2" in page.locator("#timing-result").inner_text()
            else:
                page.locator("#frame-type").select_option("rtr")
                assert "拒绝" in page.locator("#filter-result").inner_text()
                page.locator("#filter-mode").select_option("all")
                assert "通过" in page.locator("#filter-result").inner_text()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1"), (chapter,width)
            assert not errors, (chapter,width,errors)
            page.close()
    browser.close()
print("Chapters 07–09 browser smoke checks passed at 1440/768/390/360.")

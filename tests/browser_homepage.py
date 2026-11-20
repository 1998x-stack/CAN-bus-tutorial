"""Smoke-test the static homepage in Chrome/Chromium, including small screens."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from contextlib import contextmanager

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "homepage"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@contextmanager
def serve():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_port) + "/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def main():
    REPORT.mkdir(parents=True, exist_ok=True)
    with serve() as address, sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True, channel="chrome", args=["--no-sandbox"])
        except Exception:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(address, wait_until="networkidle")
            page.locator(".chapter-card").first.wait_for()
            assert page.title().startswith("CAN 总线教程")
            assert page.locator("h1").count() == 1
            assert page.locator(".chapter-card").count() == 30
            assert page.locator(".stage-card").count() == 6

            page.locator('button[data-filter="canopen"]').click()
            assert page.locator(".chapter-card").count() == 4
            page.locator('button[data-filter="all"]').click()
            page.locator("#chapterSearch").fill("仲裁")
            assert 0 < page.locator(".chapter-card").count() < 30
            page.locator("#chapterSearch").fill("impossible-search-text-999")
            assert page.locator(".chapter-card").count() == 0
            assert page.locator("#emptyState").is_visible()
            page.locator("#resetFilters").click()
            assert page.locator(".chapter-card").count() == 30

            first = page.locator(".chapter-card").first
            first.locator(".mark-button").click()
            assert page.locator("#progressText").inner_text().startswith("1 / 30")
            page.reload(wait_until="networkidle")
            page.locator(".chapter-card").first.wait_for()
            assert page.locator('.chapter-card .mark-button[aria-pressed="true"]').count() == 1
            page.locator(".chapter-card").first.locator(".chapter-read").click()
            page.wait_for_url("**/01.html")
            page.goto(address, wait_until="networkidle")
            page.locator(".chapter-card").first.wait_for()
            assert page.locator("#continueLink").is_visible()
            assert page.locator("#continueLink").get_attribute("href") == "01.html"

            for width in (1440, 768, 390, 360):
                page.set_viewport_size({"width": width, "height": 900})
                page.wait_for_timeout(80)
                overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                assert overflow <= 1, "Horizontal overflow at " + str(width) + "px: " + str(overflow)
                assert page.locator(".chapter-card").first.is_visible()
                if width in (1440, 390):
                    page.screenshot(path=str(REPORT / ("home-" + str(width) + ".png")), full_page=True)
            assert not errors, "Browser errors: " + "; ".join(errors)
            print("Homepage browser QA passed: catalog, stages, search, progress and responsive widths.")
        finally:
            browser.close()


if __name__ == "__main__":
    main()

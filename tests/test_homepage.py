"""Homepage and repository metadata regression tests (Python standard library only)."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = set()
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag in ("a", "link"):
            self.refs.append(attrs.get("href", ""))
        if tag in ("img", "script"):
            self.refs.append(attrs.get("src", ""))


class HomePageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets/js/home.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets/css/home.css").read_text(encoding="utf-8")

    def test_catalog_is_complete_and_links_are_stable(self):
        chapters = self.catalog["chapters"]
        self.assertEqual(self.catalog["chapterCount"], 30)
        self.assertEqual(len(chapters), 30)
        self.assertEqual([c["num"] for c in chapters], [f"{n:02d}" for n in range(1, 31)])
        for c in chapters:
            with self.subTest(chapter=c["num"]):
                self.assertEqual(c["file"], c["num"] + ".html")
                self.assertTrue((ROOT / c["file"]).is_file())
                self.assertTrue(c["title"].strip())
                self.assertTrue(c["topics"])

    def test_stages_are_contiguous_and_cover_all_chapters(self):
        stages = self.catalog["stages"]
        self.assertEqual(len(stages), 6)
        self.assertEqual(len(set(s["id"] for s in stages)), len(stages))
        cursor = 1
        for s in stages:
            with self.subTest(stage=s["id"]):
                self.assertEqual(s["start"], cursor)
                self.assertGreaterEqual(s["end"], s["start"])
                self.assertTrue(s["title"].strip())
                self.assertTrue(s["description"].strip())
                cursor = s["end"] + 1
        self.assertEqual(cursor, len(self.catalog["chapters"]) + 1)

    def test_html_semantics_and_relative_assets(self):
        parser = AssetParser()
        parser.feed(self.html)
        self.assertEqual(parser.h1_count, 1)
        for element_id in ("main", "roadmap", "chapters", "stageGrid", "chapterGrid", "chapterSearch",
                           "filterBar", "progressTrack", "emptyState", "continueLink"):
            self.assertIn(element_id, parser.ids)
        self.assertIn("assets/css/home.css", parser.refs)
        self.assertIn("assets/js/home.js", parser.refs)
        self.assertIn("assets/chapter01-network.svg", parser.refs)
        for ref in parser.refs:
            if not ref or ref.startswith(("#", "https://", "http://", "data:", "mailto:")):
                continue
            with self.subTest(ref=ref):
                self.assertFalse(ref.startswith("/"), "URLs must work under the Pages project prefix")
                self.assertTrue((ROOT / ref).exists(), "Missing local resource: " + ref)

    def test_homepage_has_accessible_interactions(self):
        self.assertIn('type="search"', self.html)
        self.assertIn('role="status"', self.html)
        self.assertIn('role="progressbar"', self.html)
        self.assertIn("aria-pressed", self.js)
        self.assertIn("localStorage", self.js)
        self.assertIn("textContent", self.js)
        self.assertNotIn("innerHTML", self.js)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn("max-width:620px", self.css)
        self.assertIn("max-width:850px", self.css)
        self.assertTrue(re.search(r"<a[^>]+class=\"skip-link\"[^>]+href=\"#main\"|<a[^>]+href=\"#main\"[^>]+class=\"skip-link\"", self.html))

    def test_readme_links_all_chapters(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for number in range(1, 31):
            self.assertIn(f"({number:02d}.html)", readme)
        self.assertTrue((ROOT / "docs/PROJECT_STRUCTURE.md").exists())
        self.assertTrue((ROOT / "CONTRIBUTING.md").exists())


if __name__ == "__main__":
    unittest.main()

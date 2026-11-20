"""Chapters 16–18: deterministic technical checks and semantic-HTML smoke tests."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = (16, 17, 18)
LINKS = {16: ("15.html", "17.html"), 17: ("16.html", "18.html"), 18: ("17.html", "19.html")}


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.names = []
        self.ids = []
        self.links = []
        self.has_aria_live = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        self.names.append(tag)
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "a":
            self.links.append(data.get("href", ""))
        if data.get("aria-live") == "polite":
            self.has_aria_live = True


class Chapters1618Tests(unittest.TestCase):
    def test_html_semantics_and_responsive_stylesheet(self):
        css = (ROOT / "assets" / "olah-can-16-18.css").read_text(encoding="utf8")
        self.assertIn("@media (max-width:480px)", css)
        self.assertIn("@media print", css)
        self.assertIn("prefers-reduced-motion", css)
        for n in CHAPTERS:
            with self.subTest(chapter=n):
                html = (ROOT / f"{n:02d}.html").read_text(encoding="utf8")
                tags = Tags()
                tags.feed(html)
                self.assertEqual(tags.names.count("h1"), 1)
                self.assertEqual(tags.names.count("main"), 1)
                self.assertEqual(tags.names.count("article"), 1)
                self.assertGreaterEqual(tags.names.count("figure"), 1)
                self.assertEqual(tags.names.count("figure"), tags.names.count("figcaption"))
                self.assertEqual(tags.names.count("svg"), tags.names.count("title"))
                self.assertEqual(tags.names.count("svg"), tags.names.count("desc"))
                self.assertEqual(len(tags.ids), len(set(tags.ids)))
                self.assertTrue(tags.has_aria_live)
                self.assertIn("assets/olah-can-16-18.css", html)
                self.assertLess(html.find("</style>"), html.find('href="assets/olah-can-16-18.css"'))
                for link in (*LINKS[n], "index.html"):
                    self.assertIn(link, tags.links)
                self.assertTrue(any(x.startswith("https://") for x in tags.links))

    def test_formula_and_protocol_regressions(self):
        h16 = (ROOT / "16.html").read_text(encoding="utf8")
        h17 = (ROOT / "17.html").read_text(encoding="utf8")
        h18 = (ROOT / "18.html").read_text(encoding="utf8")
        self.assertIn("<math", h16)
        self.assertIn("<math", h17)
        self.assertIn("Vdiff", h16)
        self.assertIn("id=\"c16-noise\"", h16)
        self.assertIn("id=\"c17-calc\"", h17)
        self.assertIn("id=\"c18-generate\"", h18)
        self.assertIn("0x1000:00", h18)
        self.assertIn("0x1001:00", h18)
        self.assertIn("0x4B", h18)
        self.assertIn("0x60410010", h18)
        self.assertIn("0x606C0020", h18)
        self.assertNotIn("0x0000 表示设备类型ID", h18)
        self.assertNotIn("能用500kbps就别用250kbps", h17)

    def test_exact_numeric_invariants(self):
        def differential(noise):
            h, l = 3.5 + noise, 1.5 + noise
            return h-l, (h+l)/2
        for n in [-1, -0.25, 0, 0.75, 1]:
            self.assertAlmostEqual(differential(n)[0], 2)
            self.assertAlmostEqual(differential(n)[1], 2.5+n)
        pclk, brp, bs1, bs2 = 36_000_000, 4, 14, 3
        total = 1 + bs1 + bs2
        self.assertEqual(pclk // (brp * total), 500_000)
        self.assertAlmostEqual(100 * (1+bs1) / total, 83.33333333333)
        req = (0x600 + 1, bytes.fromhex("40 17 10 00 00 00 00 00"))
        rsp = bytes.fromhex("4B 17 10 00 64 00 00 00")
        self.assertEqual(req[0], 0x601)
        self.assertEqual(len(req[1]), 8)
        self.assertEqual(int.from_bytes(rsp[4:6], "little"), 100)
        self.assertEqual((0x6041 << 16) | 16, 0x60410010)
        self.assertEqual((0x606C << 16) | 32, 0x606C0020)

    def test_evidence_ledgers(self):
        for n in CHAPTERS:
            with self.subTest(chapter=n):
                p = ROOT / "docs" / "evidence" / f"{n}.json"
                data = json.loads(p.read_text(encoding="utf8"))
                self.assertEqual(data["chapter"], n)
                self.assertGreaterEqual(len(data["claims"]), 4)
                ids = [c["id"] for c in data["claims"]]
                self.assertEqual(len(ids), len(set(ids)))
                for c in data["claims"]:
                    self.assertIn(c["status"], {"verified", "derived", "illustrative", "unverified"})
                    self.assertTrue(c["claim"] and c["locator"])
                    if c["status"] == "verified":
                        self.assertTrue(c["source_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()

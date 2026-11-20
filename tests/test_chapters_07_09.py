"""Chapters 07–09: technical invariants, accessible assets and source provenance."""
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []
    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

class Chapters0709(unittest.TestCase):
    def test_bit_timing_exact(self):
        tq = 1 + 14 + 3
        self.assertEqual(tq, 18)
        self.assertEqual(36_000_000 // (4 * tq), 500_000)
        self.assertAlmostEqual((1 + 14) / tq, 0.8333333333333334)

    def test_standard_filter_mask(self):
        mask = 0xFFE00006
        target = 0x123 << 21
        def accepts(ident, extended=False, remote=False):
            key = (ident << (3 if extended else 21))
            if extended:
                key |= 4
            if remote:
                key |= 2
            return (key & mask) == (target & mask)
        self.assertTrue(accepts(0x123))
        for args in [(0x124, False, False),(0x123, False, True),(0x123, True, False)]:
            self.assertFalse(accepts(*args))

    def test_semantics(self):
        for n in (7, 8, 9):
            with self.subTest(chapter=n):
                html = (ROOT / f"{n:02d}.html").read_text(encoding="utf8")
                p = Markup(); p.feed(html)
                tags = [tag for tag,_ in p.nodes]
                self.assertEqual(tags.count("h1"), 1)
                self.assertEqual(tags.count("article"), 1)
                self.assertEqual(tags.count("main"), 1)
                self.assertEqual(tags.count("figure"), 2 if n != 9 else 2)
                self.assertEqual(tags.count("figcaption"), tags.count("figure"))
                self.assertTrue(any(tag=="a" and attr.get("href")==f"{n+1:02d}.html" for tag,attr in p.nodes))
                self.assertTrue(any(tag=="link" and attr.get("href")=="assets/olah-chapters.css" for tag,attr in p.nodes))
                self.assertIn('aria-live="polite"', html)
                self.assertNotIn("CAN_Start(", html)
                self.assertNotIn("CAN_Cmd(", html)

    def test_svg_resources(self):
        names = ["chapter07-transceiver-path","chapter07-differential",
                 "chapter08-bxcan-flow","chapter08-timing",
                 "chapter09-setup","chapter09-filter"]
        for name in names:
            with self.subTest(name=name):
                root = ET.parse(ROOT / "assets" / f"{name}.svg").getroot()
                tags = {child.tag.rsplit("}",1)[-1] for child in root.iter()}
                self.assertIn("title", tags)
                self.assertIn("desc", tags)
                self.assertTrue(root.attrib.get("viewBox"))
                ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
                self.assertEqual(len(ids),len(set(ids)))
                chapter = name.split("-")[0][-2:]
                self.assertIn(f"assets/{name}.svg",
                              (ROOT / f"{chapter}.html").read_text(encoding="utf8"))

    def test_claims_are_located(self):
        for n in (7, 8, 9):
            obj = json.loads((ROOT / "docs" / f"chapter{n:02d}-evidence.json").read_text(encoding="utf8"))
            self.assertGreaterEqual(len(obj["claims"]), 5)
            for claim in obj["claims"]:
                self.assertTrue(claim["locator"])
                self.assertTrue(claim["source_url"].startswith("https://"))
                self.assertIn(claim["status"], {"verified","derived","illustrative","unverified"})
if __name__ == "__main__":
    unittest.main()

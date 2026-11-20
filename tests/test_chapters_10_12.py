"""Chapters 10–12: semantic HTML, bxCAN invariants, independent SVG and evidence ledger."""
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    10: "chapter10-tx-flow.svg",
    11: "chapter11-rx-flow.svg",
    12: "chapter12-irq-timeline.svg",
}

class Nodes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []
    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

class Chapters1012(unittest.TestCase):
    def test_semantic_structure_and_navigation(self):
        for n in ASSETS:
            with self.subTest(chapter=n):
                html = (ROOT / f"{n:02d}.html").read_text(encoding="utf-8")
                parser = Nodes()
                parser.feed(html)
                tags = [t for t, _ in parser.nodes]
                self.assertEqual(tags.count("main"), 1)
                self.assertEqual(tags.count("article"), 1)
                self.assertEqual(tags.count("h1"), 1)
                self.assertEqual(tags.count("figure"), 1)
                self.assertEqual(tags.count("figcaption"), 1)
                self.assertEqual(tags.count("svg"), 1)
                self.assertGreaterEqual(tags.count("section"), 4)
                self.assertEqual(tags.count("details"), 1)
                links = {attrs.get("href") for tag, attrs in parser.nodes if tag in ("a", "link")}
                for target in (
                    "reading.css", f"{n-1:02d}.html", f"{n+1:02d}.html",
                    f"assets/{ASSETS[n]}"
                ):
                    self.assertIn(target, links)
                self.assertIn("name=\"viewport\"", html)
                self.assertIn("id=\"content\"", html)
                self.assertEqual(html.count("<h1>"), 1)
                self.assertNotIn("CAN_Cmd(", html)

    def test_standalone_diagrams(self):
        ns = "{http://www.w3.org/2000/svg}"
        for n, path in ASSETS.items():
            with self.subTest(chapter=n):
                root = ET.parse(ROOT / "assets" / path).getroot()
                self.assertEqual(root.tag, ns + "svg")
                self.assertTrue(root.attrib.get("viewBox"))
                self.assertIsNotNone(root.find(ns + "title"))
                self.assertIsNotNone(root.find(ns + "desc"))
                ids = [e.attrib["id"] for e in root.iter() if "id" in e.attrib]
                self.assertEqual(len(ids), len(set(ids)))

    def test_evidence_ledgers(self):
        for n in ASSETS:
            with self.subTest(chapter=n):
                ledger = json.loads(
                    (ROOT / "docs" / f"chapter{n}-evidence.json").read_text(encoding="utf-8")
                )
                self.assertEqual(ledger["chapter"], n)
                self.assertGreaterEqual(len(ledger["claims"]), 5)
                for row in ledger["claims"]:
                    self.assertTrue(row["claim"])
                    self.assertTrue(row["locator"])
                    self.assertTrue(row["source_url"].startswith("https://"))
                    self.assertIn(row["status"], ("verified", "derived", "illustrative", "unverified"))

    def test_rx_mask_0x100_to_0x10f_standard_data_only(self):
        mask = (0x7F0 << 21) | 0x6
        target = (0x100 << 21)
        def accepted(identifier, extended=False, remote=False):
            candidate = identifier << (3 if extended else 21)
            if extended:
                candidate |= 0x4
            if remote:
                candidate |= 0x2
            return (candidate & mask) == (target & mask)
        for identifier in (0x100, 0x107, 0x10F):
            self.assertTrue(accepted(identifier))
        for identifier in (0x0FF, 0x110, 0x200):
            self.assertFalse(accepted(identifier))
        self.assertFalse(accepted(0x100, remote=True))
        self.assertFalse(accepted(0x100, extended=True))

    def test_teaching_calculations(self):
        ids = [(0, 0x300), (1, 0x100), (2, 0x200)]
        self.assertEqual([m for m, _ in sorted(ids, key=lambda p: p[1])], [1, 2, 0])
        self.assertEqual(720 / 72_000_000 * 1_000_000, 10.0)
        self.assertEqual((0x100 & 0x7F0), (0x10F & 0x7F0))
        self.assertNotEqual((0x100 & 0x7F0), (0x110 & 0x7F0))

if __name__ == "__main__":
    unittest.main()

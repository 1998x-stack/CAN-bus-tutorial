"""Chapter 13–15 reference arithmetic, HTML invariants and SVG/evidence checks."""
from html.parser import HTMLParser
from pathlib import Path
import json
import math
import unittest
import xml.etree.ElementTree as ET

from examples.can_chapters13_15_checks import (
    bxcan_std_data_matches, cable_round_trip_ns, bit_time_ns,
    equivalent_termination_ohms, reflection_coefficient, termination_power_w,
)

ROOT = Path(__file__).resolve().parents[1]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.elements.append((tag, d))
        if tag in {"a", "img", "link", "script"}:
            self.links.append(d.get("href", d.get("src", "")))


class Chapter1315Tests(unittest.TestCase):
    def test_filter_boundary_and_frame_type(self):
        self.assertEqual(
            [bxcan_std_data_matches(i) for i in [0x1FF, 0x200, 0x20F, 0x210]],
            [False, True, True, False],
        )
        self.assertTrue(bxcan_std_data_matches(0x3FF, target=0x200, mask=0))
        self.assertFalse(bxcan_std_data_matches(0x200, is_extended=True))
        self.assertFalse(bxcan_std_data_matches(0x200, is_remote=True))
        with self.assertRaises(ValueError):
            bxcan_std_data_matches(0x800)

    def test_cable_only_delay_and_bit_time(self):
        self.assertEqual(cable_round_trip_ns(40), 400)
        self.assertEqual(bit_time_ns(500), 2000)
        self.assertEqual(bit_time_ns(1000), 1000)
        self.assertAlmostEqual(100*cable_round_trip_ns(40)/bit_time_ns(500), 20.0)
        for meters, expected in [(20, 200), (40, 400), (100, 1000)]:
            self.assertEqual(cable_round_trip_ns(meters), expected)
        with self.assertRaises(ValueError):
            cable_round_trip_ns(-1)

    def test_termination_parallel_reflection_and_power(self):
        self.assertTrue(math.isinf(equivalent_termination_ohms(0)))
        for n, expected in [(1, 120), (2, 60), (3, 40)]:
            self.assertEqual(equivalent_termination_ohms(n), expected)
        self.assertAlmostEqual(reflection_coefficient(120), 0)
        self.assertAlmostEqual(reflection_coefficient(0), -1)
        self.assertAlmostEqual(reflection_coefficient(float("inf")), 1)
        self.assertAlmostEqual(termination_power_w(2), 1/30)

    def test_semantic_chapter_pages(self):
        for chapter, prev, nxt in [(13,12,14), (14,13,15), (15,14,16)]:
            with self.subTest(chapter=chapter):
                html = (ROOT / f"{chapter:02d}.html").read_text(encoding="utf-8")
                p = Markup()
                p.feed(html)
                tags = [name for name, attrs in p.elements]
                for name in ("h1", "main", "article", "figure", "figcaption"):
                    self.assertEqual(tags.count(name), 1, name)
                self.assertIn(f"{prev:02d}.html", p.links)
                self.assertIn(f"{nxt:02d}.html", p.links)
                self.assertIn("index.html", p.links)
                self.assertIn(f"assets/ch{chapter}-" + {13:"filter",14:"topology",15:"termination"}[chapter] + ".svg", p.links)
                self.assertIn("assets/olah-chapters-13-15.css", p.links)
                self.assertIn("assets/olah-chapters-13-15.js", p.links)
                self.assertIn('aria-live="polite"', html)
                self.assertIn('href="#content"', html)
                self.assertIn('xmlns="http://www.w3.org/1998/Math/MathML"', html)

    def test_svg_structure_and_figure_labels(self):
        for name in ["ch13-filter", "ch14-topology", "ch15-termination"]:
            with self.subTest(name=name):
                root = ET.parse(ROOT / "assets" / f"{name}.svg").getroot()
                self.assertTrue(root.attrib.get("viewBox"))
                tags = [el.tag.split("}")[-1] for el in root.iter()]
                self.assertIn("title", tags)
                self.assertIn("desc", tags)
                ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
                self.assertEqual(len(ids), len(set(ids)))

    def test_evidence_ledgers_have_sources(self):
        for chapter in [13, 14, 15]:
            with self.subTest(chapter=chapter):
                ledger = json.loads(
                    (ROOT / "docs" / f"chapter{chapter:02d}-evidence.json").read_text(encoding="utf-8")
                )
                self.assertGreaterEqual(len(ledger["claims"]), 4)
                for claim in ledger["claims"]:
                    self.assertTrue(claim["id"] and claim["claim"] and claim["locator"])
                    self.assertTrue(claim["source_url"].startswith("https://"))
                    self.assertIn(claim["status"], {"verified", "derived", "illustrative", "unverified"})


if __name__ == "__main__":
    unittest.main()

"""Chapter 05: source/diagram regressions and exact timing arithmetic."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

from reference.can_p0 import BxCanTiming
from examples.can_chapter05_checks import examples

ROOT = Path(__file__).resolve().parents[1]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.tags.append((tag, d))
        if tag in {"a", "img"}:
            self.links.append(d.get("href", d.get("src", "")))


class Chapter05Tests(unittest.TestCase):
    def test_two_exact_500k_examples(self):
        case = examples()
        self.assertEqual(set(case), {"A_16MHz", "B_36MHz"})
        a, b = case["A_16MHz"], case["B_36MHz"]
        self.assertEqual(a.tq_per_bit, 16)
        self.assertEqual(b.tq_per_bit, 18)
        self.assertEqual(a.bitrate_hz, 500_000)
        self.assertEqual(b.bitrate_hz, 500_000)
        self.assertEqual(a.sample_point, 0.875)
        self.assertAlmostEqual(b.sample_point, 15 / 18, places=12)
        self.assertEqual(1e9 * a.prescaler / a.can_clock_hz, 125)

    def test_bxcan_rejects_incompatible_settings(self):
        base = dict(can_clock_hz=16_000_000, prescaler=2, bs1=13, bs2=2, sjw=2)
        for k, v in [
            ("can_clock_hz", 0), ("prescaler", 0), ("prescaler", 1025),
            ("bs1", 0), ("bs1", 17), ("bs2", 0), ("bs2", 9),
            ("sjw", 0), ("sjw", 5), ("sjw", 3)
        ]:
            with self.subTest(field=k, value=v):
                args = dict(base)
                args[k] = v
                with self.assertRaises(ValueError):
                    BxCanTiming(**args)

    def test_html_semantics_and_interaction_contract(self):
        page = (ROOT / "05.html").read_text(encoding="utf-8")
        doc = Markup()
        doc.feed(page)
        counts = [x[0] for x in doc.tags]
        self.assertEqual(counts.count("h1"), 1)
        self.assertEqual(counts.count("main"), 1)
        self.assertEqual(counts.count("article"), 1)
        self.assertEqual(counts.count("figure"), 3)
        self.assertEqual(counts.count("figcaption"), 3)
        self.assertIn("04.html", doc.links)
        self.assertIn("06.html", doc.links)
        self.assertIn("index.html", doc.links)
        self.assertIn("examples/can_chapter05_checks.py", doc.links)
        for name in ["chapter05-bit-timing.svg", "chapter05-resynchronization.svg",
                     "chapter05-propagation.svg"]:
            self.assertIn("assets/" + name, doc.links)
        self.assertIn('role="status"', page)
        self.assertIn('aria-live="polite"', page)
        self.assertIn('id="preset-b"', page)
        self.assertIn("SJW 不能大于 BS2", page)
        self.assertIn("PHASE_SEG1", page)
        self.assertIn("PHASE_SEG2", page)

    def test_standalone_svg_is_accessible_and_well_formed(self):
        for name in ["bit-timing", "resynchronization", "propagation"]:
            with self.subTest(name=name):
                root = ET.parse(ROOT / "assets" / f"chapter05-{name}.svg").getroot()
                self.assertEqual(root.tag.split("}")[-1], "svg")
                self.assertTrue(root.attrib.get("viewBox"))
                tags = {el.tag.split("}")[-1] for el in root.iter()}
                self.assertIn("title", tags)
                self.assertIn("desc", tags)
                ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
                self.assertEqual(len(ids), len(set(ids)))

    def test_claims_have_verifiable_sources(self):
        doc = json.loads((ROOT / "docs" / "chapter05-evidence.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(doc["claims"]), 12)
        for claim in doc["claims"]:
            self.assertTrue(claim["id"])
            self.assertTrue(claim["locator"])
            self.assertTrue(claim["source_url"].startswith("https://"))
            self.assertIn(claim["status"], {"verified", "derived", "illustrative", "unverified"})


if __name__ == "__main__":
    unittest.main()

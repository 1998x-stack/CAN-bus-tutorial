"""Chapter 03 checks: accurate arbitration keys, article structure and SVG."""
from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def load_model():
    spec = importlib.util.spec_from_file_location("can_chapter03",
        ROOT / "examples" / "can_chapter03_arbitration.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SemanticParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.tags.append((tag, values))
        if tag == "a":
            self.links.append(values.get("href", ""))


class Chapter03Tests(unittest.TestCase):
    def test_arbitration_examples(self):
        m = load_model()
        self.assertEqual(m.compare_frames(m.base(0x100), m.base(0x200)),
                         {"winner": "A", "bit_index": 2, "field": "ID9", "observed": 0})
        self.assertEqual(m.compare_frames(m.base(0x123), m.base(0x123, remote=True))["field"], "RTR")
        self.assertEqual(m.compare_frames(m.base(0x123, remote=True),
            m.extended((0x123 << 18) | 0x12))["field"], "IDE")
        self.assertEqual(m.compare_frames(m.base(0x123, remote=True),
            m.extended((0x123 << 18) | 0x12))["winner"], "A")
        self.assertEqual(m.compare_frames(m.base(0x123),
            m.extended((0x123 << 18) | 0x12))["bit_index"], 12)
        self.assertEqual(m.compare_frames(m.base(0x123), m.base(0x123))["winner"], None)
        self.assertEqual(m.compare_frames(m.extended(0x1234567),
                                           m.extended(0x1234567))["winner"], None)
        for a in range(64):
            for b in range(64):
                result = m.compare_frames(m.base(a), m.base(b))
                self.assertEqual(result["winner"], "A" if a < b else "B" if a > b else None)

    def test_keys_and_bounds(self):
        m = load_model()
        self.assertEqual(len(m.arbitration_bits(0x100)), 13)
        self.assertEqual(len(m.arbitration_bits(0x100, extended=True)), 32)
        self.assertEqual(m.arbitration_bits(0x100)[0], ("ID10", 0))
        self.assertEqual([v for _, v in m.arbitration_bits(0x100)][:11],
                         [int(v) for v in "00100000000"])
        for bad in (-1, 0x800, 2.5, "7", True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    m.arbitration_bits(bad)
        for bad in (-1, 0x20000000):
            with self.assertRaises(ValueError):
                m.arbitration_bits(bad, extended=True)
        with self.assertRaises(ValueError):
            m.arbitration_bits(0, remote=1)

    def test_article_semantics_and_navigation(self):
        source = (ROOT / "03.html").read_text(encoding="utf-8")
        parsed = SemanticParser()
        parsed.feed(source)
        self.assertEqual(sum(t == "h1" for t, _ in parsed.tags), 1)
        self.assertEqual(sum(t == "main" for t, _ in parsed.tags), 1)
        self.assertEqual(sum(t == "article" for t, _ in parsed.tags), 1)
        self.assertEqual(sum(t == "figure" for t, _ in parsed.tags), 3)
        self.assertEqual(sum(t == "figcaption" for t, _ in parsed.tags), 3)
        self.assertEqual(sum(t == "button" and "data-scenario" in a for t, a in parsed.tags), 4)
        self.assertTrue(any("aria-live" in a for _, a in parsed.tags))
        self.assertIn("02.html", parsed.links)
        self.assertIn("04.html", parsed.links)
        self.assertIn("index.html", parsed.links)
        for name in ("dominance", "bitwise", "format-priority"):
            self.assertIn("assets/chapter03-" + name + ".svg", source)
        self.assertNotIn("不丢数据", source)
        self.assertIn("Bus-Off", source)

    def test_svg_xml_and_accessible_titles(self):
        for name in ("dominance", "bitwise", "format-priority"):
            root = ET.parse(ROOT / "assets" / ("chapter03-" + name + ".svg")).getroot()
            self.assertTrue(root.get("viewBox"))
            self.assertEqual(root.get("role"), "img")
            tags = [x.tag.split("}")[-1] for x in root.iter()]
            self.assertIn("title", tags)
            self.assertIn("desc", tags)

    def test_evidence_ledger(self):
        ledger = json.loads((ROOT / "docs" / "chapter03-evidence.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(ledger["claims"]), 7)
        for claim in ledger["claims"]:
            self.assertTrue(claim["id"])
            self.assertTrue(claim["locator"])
            self.assertIn(claim["status"], {"verified", "derived", "illustrative", "unverified"})
            if claim["status"] == "verified":
                self.assertTrue(claim["source_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()


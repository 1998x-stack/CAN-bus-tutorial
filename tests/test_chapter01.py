"""Regression checks for Chapter 01 content and ideal termination example."""
from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "a":
            self.links.append(attrs.get("href", ""))


class Chapter01Tests(unittest.TestCase):
    def test_article_structure_and_links(self):
        text = (ROOT / "01.html").read_text(encoding="utf-8")
        parser = ArticleParser()
        parser.feed(text)
        self.assertEqual(sum(tag == "h1" for tag, _ in parser.tags), 1)
        self.assertTrue(any(tag == "main" for tag, _ in parser.tags))
        self.assertTrue(any(tag == "article" for tag, _ in parser.tags))
        self.assertTrue(any(tag == "button" and "data-bit" in attrs for tag, attrs in parser.tags))
        self.assertTrue(any("aria-live" in attrs for _, attrs in parser.tags))
        self.assertIn("02.html", parser.links)
        self.assertIn("assets/chapter01-network.svg", text)
        self.assertIn("assets/chapter01-topology.svg", text)
        self.assertNotIn("标准CAN总线最多支持110个节点", text)
        self.assertIn('aria-pressed', text)

    def test_svg_exports_are_valid_and_accessible(self):
        for name in ("network", "topology", "signal"):
            path = ROOT / "assets" / f"chapter01-{name}.svg"
            root = ET.parse(path).getroot()
            self.assertTrue(root.attrib.get("viewBox"))
            tags = [child.tag.split("}")[-1] for child in root.iter()]
            self.assertIn("title", tags)
            self.assertIn("desc", tags)

    def test_evidence_ledger_has_sources(self):
        claims = json.loads((ROOT / "docs" / "chapter01-evidence.json").read_text(encoding="utf-8"))["claims"]
        self.assertGreaterEqual(len(claims), 6)
        for claim in claims:
            self.assertIn(claim["status"], {"verified", "derived", "illustrative", "unverified"})
            if claim["status"] == "verified":
                self.assertTrue(claim["source_url"].startswith("https://"))

    def test_ideal_parallel_resistors(self):
        path = ROOT / "examples" / "can_chapter01_checks.py"
        spec = importlib.util.spec_from_file_location("can_checks", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertAlmostEqual(module.parallel_ohms(120, 120), 60)
        self.assertAlmostEqual(module.parallel_ohms(120), 120)
        self.assertAlmostEqual(module.parallel_ohms(120, 120, 120), 40)
        for invalid in ((), (0,), (-120, 120), (float("inf"),)):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    module.parallel_ohms(*invalid)


if __name__ == "__main__":
    unittest.main()


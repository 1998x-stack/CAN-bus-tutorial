"""Chapter 02 verifiable framing, illustration, and text regression tests."""
from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "a":
            self.links.append(attrs.get("href", ""))


def import_reference():
    spec = importlib.util.spec_from_file_location(
        "can_chapter02_checks", ROOT / "examples" / "can_chapter02_checks.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Chapter02Tests(unittest.TestCase):
    def test_semantic_html_and_navigation(self):
        text = (ROOT / "02.html").read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(text)
        self.assertEqual(sum(tag == "h1" for tag, _ in parser.tags), 1)
        self.assertEqual(sum(tag == "main" for tag, _ in parser.tags), 1)
        self.assertEqual(sum(tag == "article" for tag, _ in parser.tags), 1)
        self.assertEqual(sum(tag == "figure" for tag, _ in parser.tags), 3)
        self.assertEqual(sum(tag == "figcaption" for tag, _ in parser.tags), 3)
        self.assertEqual(
            len([tag for tag, attrs in parser.tags if tag == "button" and "data-format" in attrs]), 3
        )
        self.assertTrue(any("aria-live" in attrs for _, attrs in parser.tags))
        self.assertIn("01.html", parser.links)
        self.assertIn("03.html", parser.links)
        self.assertIn("index.html", parser.links)
        for name in ("standard-frame", "standard-extended", "stuffing"):
            self.assertIn("assets/chapter02-" + name + ".svg", text)
        self.assertIn("Bus-Off", text)
        self.assertIn("TEC", text)
        self.assertNotIn("主动复位节点，而不是等它自己关闭", text)

    def test_standalone_svg_integrity(self):
        for name in ("standard-frame", "standard-extended", "stuffing"):
            root = ET.parse(ROOT / "assets" / ("chapter02-" + name + ".svg")).getroot()
            self.assertTrue(root.attrib.get("viewBox"), name)
            tags = [element.tag.split("}")[-1] for element in root.iter()]
            self.assertIn("title", tags, name)
            self.assertIn("desc", tags, name)

    def test_evidence_quality(self):
        records = json.loads((ROOT / "docs" / "chapter02-evidence.json").read_text(
            encoding="utf-8"
        ))["claims"]
        self.assertGreaterEqual(len(records), 10)
        for record in records:
            self.assertTrue(record["id"])
            self.assertTrue(record["locator"])
            self.assertIn(record["status"], {"verified", "derived", "illustrative", "unverified"})
            if record["status"] == "verified":
                self.assertTrue(record["source_url"].startswith("https://"))

    def test_frame_bit_counts(self):
        model = import_reference()
        self.assertEqual(model.frame_bits(), 108)
        self.assertEqual(model.frame_bits(intermission=True), 111)
        self.assertEqual(model.frame_bits(extended=True), 128)
        self.assertEqual(model.frame_bits(extended=True, intermission=True), 131)
        self.assertEqual(model.frame_bits(remote=True), 44)
        self.assertEqual(model.frame_bits(remote=True, intermission=True), 47)
        self.assertEqual(model.frame_bits(extended=True, remote=True), 64)
        self.assertEqual(model.frame_bits(data_bytes=0), 44)
        for bad in (-1, 9, 100, "8", 8.0, True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    model.frame_bits(data_bytes=bad)

    def test_bit_stuffing_examples_and_roundtrip(self):
        model = import_reference()
        self.assertEqual(model.stuff_bits("0000001"), "00000101")
        self.assertEqual(model.destuff_bits("00000101"), "0000001")
        self.assertEqual(model.stuff_bits("1010"), "1010")
        # Exhaustive short sequences, catches counter reset mistakes around stuff bits.
        for length in range(12):
            for value in range(1 << length):
                bits = format(value, "0" + str(length) + "b") if length else ""
                # Leading zeros in the str format are intentional; value 0 and length 0 => "".
                self.assertEqual(model.destuff_bits(model.stuff_bits(bits)), bits)
        for bad in ("000000", "01102", "11111"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    model.destuff_bits(bad)
        with self.assertRaises(ValueError):
            model.stuff_bits("a01")


if __name__ == "__main__":
    unittest.main()


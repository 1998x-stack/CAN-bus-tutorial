"""Chapter 04 regression tests for CRC-15, CAN error states and semantic article."""
from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def load_model():
    spec = importlib.util.spec_from_file_location(
        "can_chapter04_checks", ROOT / "examples" / "can_chapter04_checks.py"
    )
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


class Chapter04Tests(unittest.TestCase):
    def test_crc15_reference_and_exhaustive_short_strings(self):
        model = load_model()
        self.assertEqual(model.GENERATOR, 0xC599)
        self.assertEqual(model.crc15_can(""), 0)
        self.assertEqual(model.crc15_can("00000"), 0)
        self.assertEqual(model.crc15_can("1"), 0x4599)
        for length in range(11):
            for value in range(1 << length):
                sequence = f"{value:0{length}b}" if length else ""
                with self.subTest(bits=sequence):
                    self.assertEqual(
                        model.crc15_can(sequence),
                        model.crc15_polynomial_division(sequence),
                    )
        for invalid in ("0102", "abcd", 12, None, [0, 1]):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    model.crc15_can(invalid)

    def test_state_boundaries_and_invalid_inputs(self):
        model = load_model()
        examples = (
            (0, 0, "error-active"),
            (96, 0, "error-active"),
            (127, 127, "error-active"),
            (128, 0, "error-passive"),
            (0, 128, "error-passive"),
            (255, 0, "error-passive"),
            (0, 255, "error-passive"),
            (255, 255, "error-passive"),
            (256, 0, "bus-off"),
            (256, 255, "bus-off"),
        )
        for tec, rec, expected in examples:
            with self.subTest(tec=tec, rec=rec):
                self.assertEqual(model.classify_error_state(tec, rec), expected)
        for bad in ((-1, 0), (257, 0), (0, -1), (0, 256),
                    (128.0, 0), (True, 0), ("128", 0), (0, None)):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    model.classify_error_state(*bad)

    def test_nominal_error_flags(self):
        model = load_model()
        self.assertEqual(model.nominal_error_flag_bits("error-active"), "00000011111111")
        self.assertEqual(model.nominal_error_flag_bits("error-passive"), "11111111111111")
        with self.assertRaises(ValueError):
            model.nominal_error_flag_bits("bus-off")

    def test_html_semantics_accessibility_and_scope(self):
        source = (ROOT / "04.html").read_text(encoding="utf-8")
        parsed = SemanticParser()
        parsed.feed(source)
        self.assertEqual(sum(t == "h1" for t, _ in parsed.tags), 1)
        self.assertEqual(sum(t == "main" for t, _ in parsed.tags), 1)
        self.assertEqual(sum(t == "article" for t, _ in parsed.tags), 1)
        self.assertEqual(sum(t == "figure" for t, _ in parsed.tags), 3)
        self.assertEqual(sum(t == "figcaption" for t, _ in parsed.tags), 3)
        self.assertEqual(sum(t == "button" and "data-error" in a for t, a in parsed.tags), 5)
        self.assertEqual(sum(t == "button" and "data-preset" in a for t, a in parsed.tags), 6)
        self.assertEqual(sum(t == "input" and a.get("type") == "number" for t, a in parsed.tags), 2)
        self.assertTrue(any("aria-live" in attrs for _, attrs in parsed.tags))
        self.assertTrue(any(a.get("aria-current") == "page" and a.get("href") == "04.html"
                            for t, a in parsed.tags if t == "a"))
        self.assertIn("03.html", parsed.links)
        self.assertIn("05.html", parsed.links)
        self.assertIn("index.html", parsed.links)
        for name in ("detection-map", "error-flags", "state-machine"):
            self.assertIn("assets/chapter04-" + name + ".svg", source)
        for crucial in ("TEC", "REC", "128", "256", "ACK", "Bus-Off", "0x4599", "128 次"):
            self.assertIn(crucial, source)
        self.assertNotIn("错误计数器超过255，就会进入总线关闭", source)

    def test_standalone_svg_parses_and_has_accessible_title(self):
        for name in ("detection-map", "error-flags", "state-machine"):
            root = ET.parse(ROOT / "assets" / ("chapter04-" + name + ".svg")).getroot()
            self.assertTrue(root.get("viewBox"))
            self.assertEqual(root.get("role"), "img")
            names = [element.tag.split("}")[-1] for element in root.iter()]
            self.assertIn("title", names)
            self.assertIn("desc", names)

    def test_evidence_has_source_locators(self):
        claims = json.loads(
            (ROOT / "docs" / "chapter04-evidence.json").read_text(encoding="utf-8")
        )["claims"]
        self.assertGreaterEqual(len(claims), 10)
        for claim in claims:
            self.assertTrue(claim["id"])
            self.assertTrue(claim["locator"])
            self.assertIn(claim["status"], {"verified", "derived", "illustrative", "unverified"})
            if claim["status"] == "verified":
                self.assertTrue(claim["source_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()


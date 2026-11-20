"""Regression tests for the revised J1939 and CAN-tools chapters (stdlib only)."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

FIGURES = {
    22: ["j1939-id-fields.svg", "j1939-engine-speed.svg"],
    23: ["j1939-tp-flows.svg"],
    24: ["can-debug-three-layers.svg", "can-differential-waveform.svg"],
}


class ChapterParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.hrefs = []
        self.codes = []
        self._in_pre = False
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "a":
            self.hrefs.append(attrs.get("href", ""))
        if tag == "pre":
            self._in_pre = True
            self._buffer = []

    def handle_data(self, data):
        if self._in_pre:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "pre":
            self.codes.append("".join(self._buffer))
            self._in_pre = False


class J1939ChaptersTests(unittest.TestCase):
    def read_page(self, number):
        data = (ROOT / f"{number:02d}.html").read_text(encoding="utf-8")
        parser = ChapterParser()
        parser.feed(data)
        return data, parser

    def test_semantic_structure_and_navigation(self):
        for number in FIGURES:
            with self.subTest(chapter=number):
                html, parsed = self.read_page(number)
                tags = [tag for tag, _ in parsed.tags]
                self.assertEqual(tags.count("h1"), 1)
                self.assertEqual(tags.count("main"), 1)
                self.assertEqual(tags.count("article"), 1)
                self.assertEqual(tags.count("nav"), 1)
                self.assertEqual(tags.count("figure"), len(FIGURES[number]))
                self.assertEqual(tags.count("figcaption"), len(FIGURES[number]))
                self.assertIn("index.html", parsed.hrefs)
                self.assertIn(f"{number - 1:02d}.html", parsed.hrefs)
                self.assertIn(f"{number + 1:02d}.html", parsed.hrefs)
                self.assertIn('aria-live="polite"', html)
                self.assertNotIn("我曾经", html)
                self.assertNotIn("原创图解 · 单文件离线 HTML", html)

    def test_figures_are_standalone_accessible_svg(self):
        for number, figures in FIGURES.items():
            page, _ = self.read_page(number)
            for filename in figures:
                with self.subTest(figure=filename):
                    root = ET.parse(ROOT / "assets" / filename).getroot()
                    self.assertEqual(root.tag.rsplit("}", 1)[-1], "svg")
                    self.assertIn("viewBox", root.attrib)
                    self.assertEqual(root.attrib.get("role"), "img")
                    tags = [el.tag.rsplit("}", 1)[-1] for el in root.iter()]
                    self.assertIn("title", tags)
                    self.assertIn("desc", tags)
                    ids = [el.attrib["id"] for el in root.iter() if "id" in el.attrib]
                    self.assertEqual(len(ids), len(set(ids)))
                    self.assertIn(f'data-export="{filename}"', page)

    def test_claims_have_source_and_scope(self):
        for number in FIGURES:
            with self.subTest(chapter=number):
                ledger = json.loads((ROOT / "docs" / f"chapter{number}-evidence.json").read_text(encoding="utf-8"))
                self.assertGreaterEqual(len(ledger["claims"]), 5)
                for claim in ledger["claims"]:
                    self.assertTrue(claim["id"])
                    self.assertTrue(claim["locator"])
                    self.assertTrue(claim["source_url"].startswith("https://"))
                    self.assertIn(claim["status"], {"verified", "derived", "illustrative", "unverified"})

    def test_chapter_22_executable_example(self):
        page, parsed = self.read_page(22)
        self.assertIn("id22-input", page)
        self.assertIn("PF &lt; 240", page)
        ns = {}
        exec(parsed.codes[0], ns)
        decoder = ns["decode_j1939"]
        self.assertEqual(decoder(0x0CF00401, bytes.fromhex("00 7D 82 E0 2E FF FF FF")), (61444, 1, 1500.0))
        self.assertEqual(decoder(0x18EAFF80, bytes(8)), (59904, 128, None))
        self.assertIsNone(decoder(0x0CF00401, bytes.fromhex("00 7D 82 FF FF FF FF FF"))[2])

    def test_chapter_23_executable_example(self):
        page, parsed = self.read_page(23)
        ns = {}
        exec(parsed.codes[0], ns)
        split_tp, join_tp = ns["split_tp"], ns["join_tp"]
        for length in (9, 49, 50, 1785):
            with self.subTest(length=length):
                data = bytes(i % 256 for i in range(length))
                packets = split_tp(data)
                self.assertEqual(len(packets), (length + 6) // 7)
                self.assertEqual([packet[0] for packet in packets], list(range(1, len(packets) + 1)))
                self.assertEqual(join_tp(packets, length), data)
        broken = split_tp(bytes(range(50)))
        broken[1], broken[2] = broken[2], broken[1]
        with self.assertRaises(AssertionError):
            join_tp(broken, 50)
        with self.assertRaises(AssertionError):
            split_tp(bytes(8))
        with self.assertRaises(AssertionError):
            split_tp(bytes(1786))
        self.assertIn("EOM ACK", page)
        self.assertNotIn("发送方发一个End of Message", page)

    def test_chapter_24_diagnosis_and_vendor_limits(self):
        page, parsed = self.read_page(24)
        self.assertIn("TJA1040", page)
        self.assertIn("不能把某一款设备", page)
        self.assertIn("tool24-symptom", page)
        self.assertIn("candump -L", parsed.codes[0])
        self.assertIn("listen-only", parsed.codes[0])
        self.assertNotIn("自动切换到单线模式", page)


if __name__ == "__main__":
    unittest.main()

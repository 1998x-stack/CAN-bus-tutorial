"""Chapter 06: deterministic register maths and article/source regressions."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

from examples.can_chapter06_checks import (
    MCP2515_REQOP,
    mcp2515_request_mode_transaction,
    mcp2515_standard_id_registers,
    mcp2515_standard_id_from_registers,
    standard_id_filter_accepts,
    sja1000_bit_timing,
)

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "img":
            self.links.append(attrs.get("src", ""))


class Chapter06Tests(unittest.TestCase):
    def test_mcp2515_standard_id_roundtrip(self):
        self.assertEqual(mcp2515_standard_id_registers(0x123), (0x24, 0x60))
        self.assertEqual(mcp2515_standard_id_registers(0x7FF), (0xFF, 0xE0))
        self.assertEqual(mcp2515_standard_id_registers(0), (0, 0))
        for id_ in range(0x800):
            self.assertEqual(
                mcp2515_standard_id_from_registers(
                    *mcp2515_standard_id_registers(id_)
                ), id_
            )
        for invalid in (-1, 0x800, 1.5, "0x123", True):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                mcp2515_standard_id_registers(invalid)
        with self.assertRaises(ValueError):
            mcp2515_standard_id_from_registers(0x24, 0x68)

    def test_filter_polarity_and_device_rejection(self):
        for target in (0, 0x123, 0x7FF):
            for candidate in (0, 0x12A, target):
                for mask in (0, 0xF, 0x7F0, 0x7FF):
                    self.assertEqual(
                        standard_id_filter_accepts(
                            candidate, target, mask, device="mcp2515"
                        ),
                        standard_id_filter_accepts(
                            candidate, target, ~mask & 0x7FF,
                            device="sja1000"
                        ),
                    )
        self.assertFalse(standard_id_filter_accepts(0x12A, 0x123, 0x7FF))
        self.assertTrue(standard_id_filter_accepts(0x12A, 0x123, 0x7F0))
        self.assertFalse(standard_id_filter_accepts(
            0x12A, 0x123, 0x000, device="sja1000"
        ))
        self.assertTrue(standard_id_filter_accepts(
            0x12A, 0x123, 0x00F, device="sja1000"
        ))
        for invalid in ("bxcan", "", "MCP2515"):
            with self.assertRaises(ValueError):
                standard_id_filter_accepts(0x123, 0x123, 0, device=invalid)
        with self.assertRaises(ValueError):
            standard_id_filter_accepts(0x800, 0x123, 0x7FF)

    def test_sja1000_bit_timing_encoding(self):
        btr0, btr1, bitrate, sample = sja1000_bit_timing(
            16_000_000, 1, 13, 2
        )
        self.assertEqual((btr0, btr1), (0x00, 0x1C))
        self.assertEqual(bitrate, 500_000)
        self.assertEqual(sample, 0.875)
        self.assertEqual(
            sja1000_bit_timing(16_000_000, 4, 13, 2)[2], 125_000
        )
        self.assertEqual(
            sja1000_bit_timing(16_000_000, 1, 13, 2, triple_sample=True)[1],
            0x9C
        )
        for patch in [
            {"oscillator_hz": 0}, {"brp": 0}, {"brp": 65},
            {"tseg1": 0}, {"tseg1": 17}, {"tseg2": 0},
            {"tseg2": 9}, {"sjw": 0}, {"sjw": 5},
        ]:
            args = {
                "oscillator_hz": 16_000_000, "brp": 1,
                "tseg1": 13, "tseg2": 2, "sjw": 1
            }
            args.update(patch)
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                sja1000_bit_timing(**args)

    def test_mcp2515_mode_commands(self):
        self.assertEqual(MCP2515_REQOP["configuration"], 0x80)
        self.assertEqual(MCP2515_REQOP["listen_only"], 0x60)
        self.assertEqual(MCP2515_REQOP["loopback"], 0x40)
        self.assertEqual(MCP2515_REQOP["sleep"], 0x20)
        self.assertEqual(MCP2515_REQOP["normal"], 0x00)
        self.assertEqual(
            mcp2515_request_mode_transaction("configuration"),
            bytes((0x05, 0x0F, 0xE0, 0x80))
        )
        for mode in MCP2515_REQOP:
            cmd = mcp2515_request_mode_transaction(mode)
            self.assertEqual(cmd[:3], bytes((0x05, 0x0F, 0xE0)))
            self.assertEqual(cmd[3], MCP2515_REQOP[mode])
        with self.assertRaises(ValueError):
            mcp2515_request_mode_transaction("invalid")

    def test_page_semantics(self):
        html = (ROOT / "06.html").read_text(encoding="utf-8")
        parser = Page()
        parser.feed(html)
        names = [tag for tag, _ in parser.tags]
        self.assertEqual(names.count("h1"), 1)
        self.assertEqual(names.count("main"), 1)
        self.assertEqual(names.count("article"), 1)
        self.assertEqual(names.count("figure"), 3)
        self.assertEqual(names.count("figcaption"), 3)
        for name in ("05.html", "07.html", "index.html",
                     "examples/can_chapter06_checks.py"):
            self.assertIn(name, parser.links)
        self.assertIn('href="06.html" aria-current="page"', html)
        for name in ("system-boundary", "sja1000-map", "mcp2515-path"):
            self.assertIn(f"assets/chapter06-{name}.svg", parser.links)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('id="ignore-low"', html)
        self.assertIn("0xC0", html)
        self.assertIn("SIDH=0x24", html)
        self.assertIn("BTR1 = 0x1C", html)

    def test_illustrations(self):
        for name in ("system-boundary", "sja1000-map", "mcp2515-path"):
            with self.subTest(name=name):
                svg = ET.parse(ROOT / "assets" / f"chapter06-{name}.svg").getroot()
                self.assertEqual(svg.tag.split("}")[-1], "svg")
                self.assertTrue(svg.attrib.get("viewBox"))
                labels = [e.tag.split("}")[-1] for e in svg.iter()]
                self.assertIn("title", labels)
                self.assertIn("desc", labels)
                ids = [e.attrib["id"] for e in svg.iter() if "id" in e.attrib]
                self.assertEqual(len(ids), len(set(ids)))

    def test_evidence_ledger(self):
        evidence = json.loads(
            (ROOT / "docs/chapter06-evidence.json").read_text(encoding="utf-8")
        )
        self.assertGreaterEqual(len(evidence["claims"]), 16)
        ids = [c["id"] for c in evidence["claims"]]
        self.assertEqual(len(ids), len(set(ids)))
        for item in evidence["claims"]:
            self.assertTrue(item["locator"])
            self.assertTrue(item["kind"])
            self.assertIn(item["status"], {
                "verified", "derived", "illustrative", "unverified"
            })
            self.assertTrue(item["source_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()

"""Regression tests for the CAN chapters 28–30 reference contracts and article assets."""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from examples.can_chapters28_30_reference import (
    average_current_ua, counter_gap, decode_sample, estimated_bus_load_pct,
    illustrative_wake, pack_four_temperatures, pack_sample,
    standard_frame_unstuffed_bits,
)

ROOT = Path(__file__).resolve().parents[1]


class CAN28to30ModelTests(unittest.TestCase):
    def test_standard_frame_length_excludes_stuff(self):
        self.assertEqual(standard_frame_unstuffed_bits(8), 111)
        self.assertEqual(standard_frame_unstuffed_bits(0), 47)
        with self.assertRaises(ValueError):
            standard_frame_unstuffed_bits(9)

    def test_bus_budget(self):
        self.assertAlmostEqual(estimated_bus_load_pct(8, 20, 130, 500), 10.4)
        self.assertAlmostEqual(estimated_bus_load_pct(8, 10, 130, 500), 20.8)
        with self.assertRaises(ValueError):
            estimated_bus_load_pct(8, 0, 130, 500)

    def test_temp_payload_is_explicit_little_endian(self):
        p = pack_four_temperatures([-1234, 0, 2500, 32767])
        self.assertEqual(p.hex(" "), "2e fb 00 00 c4 09 ff 7f")
        with self.assertRaises(ValueError):
            pack_four_temperatures([1, 2, 3])

    def test_wake_is_hardware_wuf_not_software_filter(self):
        self.assertTrue(illustrative_wake("pn", 0x321))
        self.assertFalse(illustrative_wake("pn", 0x120))
        self.assertTrue(illustrative_wake("normal", 0x120))
        self.assertFalse(illustrative_wake("normal", 0x120, valid=False))

    def test_power_budget(self):
        self.assertAlmostEqual(average_current_ua(50, 20, 1), 249.5)
        self.assertAlmostEqual(average_current_ua(50, 20, 0), 50)
        with self.assertRaises(ValueError):
            average_current_ua(50, 20, 101)

    def test_golden_vector(self):
        raw = pack_sample(-1234, 2500, 1450, 7, 1)
        self.assertEqual(raw.hex(" ").upper(), "2E FB C4 09 AA 05 07 01")
        self.assertEqual(decode_sample(raw), (-1234, 2500, 1450, 7, 1))
        with self.assertRaises(ValueError):
            pack_sample(-1234, 2500, 1450, 7, 2)
        with self.assertRaises(ValueError):
            decode_sample(raw[:7])

    def test_sequence_rollover(self):
        self.assertFalse(counter_gap(255, 0))
        self.assertTrue(counter_gap(255, 2))
        self.assertFalse(counter_gap(None, 7))


class ArticleStructureTests(unittest.TestCase):
    def test_three_articles_and_standalone_svg(self):
        for n in (28, 29, 30):
            with self.subTest(chapter=n):
                html = (ROOT / f"{n}.html").read_text(encoding="utf-8")
                self.assertEqual(len(re.findall(r"<h1\b", html)), 1)
                self.assertEqual(len(re.findall(r"<figure\b", html)), 2)
                self.assertIn('<main class="reader" id="content">', html)
                self.assertIn('aria-live="polite"', html)
                self.assertIn('assets/chapters28-30.css', html)
                code_blocks = "\n".join(re.findall(r"<pre><code>[\\s\\S]*?</code></pre>", html))
                self.assertNotIn("HAL_Delay(rand()", code_blocks)
                self.assertNotIn("原创图解 · 单文件离线 HTML", html)
                for i in (1, 2):
                    path = ROOT / f"assets/chapter{n}-figure{i}.svg"
                    svg = path.read_text(encoding="utf-8")
                    root = ET.fromstring(svg)
                    self.assertTrue(root.tag.endswith("svg"))
                    self.assertTrue(root.attrib.get("viewBox"))
                    self.assertIn("<title", svg)
                    self.assertIn("<desc", svg)

    def test_fixed_reference_assumptions_present(self):
        self.assertIn("10.40%", (ROOT / "28.html").read_text(encoding="utf-8"))
        self.assertIn("249.5 μA", (ROOT / "29.html").read_text(encoding="utf-8"))
        self.assertIn("2E FB C4 09 AA 05 07 01", (ROOT / "30.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

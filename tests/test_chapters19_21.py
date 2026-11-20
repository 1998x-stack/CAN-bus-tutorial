"""Regression and artifact checks for CANopen lessons 19, 20 and 21."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

from reference.canopen_ch19_21 import (
    nmt_frame, heartbeat_can_id, consumer_heartbeat_entry,
    decode_initiate_upload, upload_segment_reply, block_ack,
    speed_position_mapping, speed_position_payload, example_load, examples,
)

ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.refs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if tag == "img":
            self.refs.append(a.get("src", ""))
        if tag == "link":
            self.refs.append(a.get("href", ""))


class CANopenChapterTests(unittest.TestCase):
    def test_nmt_and_heartbeat(self):
        self.assertEqual(nmt_frame(1, 5), (0, b"\x01\x05"))
        self.assertEqual(nmt_frame(0x80, 0), (0, b"\x80\x00"))
        self.assertEqual(heartbeat_can_id(5), 0x705)
        self.assertEqual(consumer_heartbeat_entry(5, 600), 0x00050258)
        for bad_cmd, node in [(0x03, 5), (1, -1), (1, 128)]:
            with self.subTest(command=bad_cmd, node=node):
                with self.assertRaises(ValueError):
                    nmt_frame(bad_cmd, node)
        with self.assertRaises(ValueError):
            consumer_heartbeat_entry(0, 600)
        with self.assertRaises(ValueError):
            consumer_heartbeat_entry(5, 65536)

    def test_sdo_upload_is_not_abort(self):
        replies = {
            "4F 00 20 01 7A 00 00 00": ("success", 0x7A),
            "4B 00 20 01 34 12 00 00": ("success", 0x1234),
            "47 00 20 01 01 02 03 00": ("success", 0x030201),
            "43 00 20 01 01 02 03 04": ("success", 0x04030201),
            "42 00 20 01 34 12 00 00": ("success", None),
            "80 00 20 01 00 00 02 06": ("abort", 0x06020000),
        }
        for wire, expected in replies.items():
            with self.subTest(wire=wire):
                self.assertEqual(decode_initiate_upload(bytes.fromhex(wire)), expected)
        with self.assertRaises(ValueError):
            decode_initiate_upload(bytes.fromhex("00 00 00 00"))

    def test_segment_control_and_block_ack(self):
        self.assertEqual(upload_segment_reply(0x00, 0), (7, False))
        self.assertEqual(upload_segment_reply(0x19, 1), (3, True))
        with self.assertRaises(ValueError):
            upload_segment_reply(0x19, 0)
        with self.assertRaises(ValueError):
            upload_segment_reply(0xA2, 0)
        self.assertEqual(block_ack(7, 16).hex(" "), "a2 07 10 00 00 00 00 00")
        for a, b in [(-1, 10), (128, 10), (3, 0), (3, 128)]:
            with self.assertRaises(ValueError):
                block_ack(a, b)

    def test_pdo_mapping_payload_and_bandwidth(self):
        self.assertEqual(speed_position_mapping(), (0x606C0020, 0x60640020))
        self.assertEqual(speed_position_payload(1000, -2000).hex(" "), "e8 03 00 00 30 f8 ff ff")
        self.assertAlmostEqual(example_load(), 1.11, places=12)
        with self.assertRaises(ValueError):
            speed_position_payload(2**31, 0)
        self.assertIn("tpdo_payload", examples())

    def test_chapters_are_semantic_and_linked(self):
        for n in (19, 20, 21):
            with self.subTest(chapter=n):
                page = (ROOT / f"{n:02}.html").read_text(encoding="utf-8")
                parser = Tags()
                parser.feed(page)
                self.assertEqual(parser.tags.count("h1"), 1)
                self.assertEqual(parser.tags.count("main"), 1)
                self.assertEqual(parser.tags.count("article"), 1)
                self.assertEqual(parser.tags.count("figure"), 2)
                self.assertEqual(parser.tags.count("figcaption"), 2)
                self.assertIn('role="status"', page)
                self.assertIn('aria-live="polite"', page)
                self.assertIn("index.html", page)
                for local in parser.refs:
                    if not local.startswith(("https://", "data:")):
                        self.assertTrue((ROOT / local).is_file(), local)
                self.assertIn(f"assets/chapter{n}-", page)
                self.assertIn('aria-current="page"', page)
                self.assertEqual(parser.tags.count("math"), 1 if n in (20, 21) else 0)

    def test_svg_title_desc_and_evidence(self):
        names = {
            19: ("nmt", "heartbeat"),
            20: ("expedited", "segments"),
            21: ("mapping", "sync"),
        }
        for n, concepts in names.items():
            for concept in concepts:
                path = ROOT / "assets" / f"chapter{n}-{concept}.svg"
                with self.subTest(path=str(path)):
                    root = ET.parse(path).getroot()
                    self.assertTrue(root.attrib.get("viewBox"))
                    types = [el.tag.rsplit("}", 1)[-1] for el in root.iter()]
                    self.assertIn("title", types)
                    self.assertIn("desc", types)
                    ids = [x.attrib["id"] for x in root.iter() if "id" in x.attrib]
                    self.assertEqual(len(ids), len(set(ids)))
            claims = json.loads(
                (ROOT / "docs" / f"chapter{n}-evidence.json").read_text(encoding="utf-8")
            )["claims"]
            self.assertGreaterEqual(len(claims), 5)
            for claim in claims:
                self.assertIn(claim["status"], {"verified", "derived", "illustrative", "unverified"})
                self.assertTrue(claim["source_url"].startswith("https://"))
                self.assertTrue(claim["locator"])


if __name__ == "__main__":
    unittest.main()

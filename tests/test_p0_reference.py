"""Run with: python3 -m unittest discover -s tests -v"""
import unittest
from pathlib import Path

from reference.can_p0 import (
    BxCanTiming, arbitration_winner, error_state, can_crc15_bits,
    sdo_upload_reply, pdo_mapping, little_endian_speed,
    classical_can_frame_bits, nominal_bus_load,
)

ROOT = Path(__file__).resolve().parents[1]


class TestTiming(unittest.TestCase):
    def test_16tq_875_percent(self):
        t = BxCanTiming(16_000_000, 2, 13, 2)
        self.assertEqual(t.tq_per_bit, 16)
        self.assertEqual(t.bitrate_hz, 500_000)
        self.assertEqual(t.sample_point, 0.875)

    def test_36mhz_500k(self):
        t = BxCanTiming(36_000_000, 4, 14, 3)
        self.assertEqual(t.bitrate_hz, 500_000)
        self.assertAlmostEqual(t.sample_point, 15 / 18)

    def test_old_wrong_setting_is_562k5(self):
        self.assertEqual(BxCanTiming(36_000_000, 4, 8, 7).bitrate_hz, 562_500)

    def test_invalid_segments(self):
        for params in [(36_000_000, 4, 17, 2), (36_000_000, 4, 14, 0)]:
            with self.subTest(params=params), self.assertRaises(ValueError):
                BxCanTiming(*params)

    def test_sjw_constraint(self):
        with self.assertRaises(ValueError):
            BxCanTiming(36_000_000, 4, 14, 1, sjw=2)


class TestArbitrationAndErrors(unittest.TestCase):
    def test_lower_id_wins(self):
        self.assertEqual(arbitration_winner(0x100, 0x200), "A")

    def test_same_id_is_a_tie(self):
        self.assertIsNone(arbitration_winner(0x123, 0x123))

    def test_standard_beats_extended_for_same_base_id(self):
        ext_id = (0x123 << 18) | 0x1
        self.assertEqual(
            arbitration_winner(0x123, ext_id, extended_b=True), "A"
        )

    def test_29bit_extended_arbitration(self):
        self.assertEqual(
            arbitration_winner(0x18F00401, 0x18F00501,
                               extended_a=True, extended_b=True),
            "A",
        )

    def test_id_bounds(self):
        with self.assertRaises(ValueError):
            arbitration_winner(0x800, 0x100)

    def test_error_state_boundaries(self):
        self.assertEqual(error_state(0, 0), "error-active")
        self.assertEqual(error_state(127, 127), "error-active")
        self.assertEqual(error_state(128, 0), "error-passive")
        self.assertEqual(error_state(0, 128), "error-passive")
        self.assertEqual(error_state(255, 0), "error-passive")
        self.assertEqual(error_state(256, 0), "bus-off")

    def test_crc15_known_single_bit(self):
        self.assertEqual(can_crc15_bits([]), 0)
        self.assertEqual(can_crc15_bits([0] * 12), 0)
        self.assertEqual(can_crc15_bits([1]), 0x4599)

    def test_crc_rejects_non_bits(self):
        with self.assertRaises(ValueError):
            can_crc15_bits([0, 2, 1])


class TestApplicationEncodings(unittest.TestCase):
    def test_sdo_one_byte_is_success(self):
        self.assertEqual(sdo_upload_reply(0x4F), ("success", 1))

    def test_sdo_other_upload_sizes(self):
        self.assertEqual(sdo_upload_reply(0x4B), ("success", 2))
        self.assertEqual(sdo_upload_reply(0x47), ("success", 3))
        self.assertEqual(sdo_upload_reply(0x43), ("success", 4))
        self.assertEqual(sdo_upload_reply(0x42), ("success", None))

    def test_sdo_abort(self):
        self.assertEqual(sdo_upload_reply(0x80), ("abort", None))
        with self.assertRaises(ValueError):
            sdo_upload_reply(0x40)

    def test_cia402_mapping_entries(self):
        self.assertEqual(pdo_mapping(0x606C, 0, 32), 0x606C0020)
        self.assertEqual(pdo_mapping(0x6064, 0, 32), 0x60640020)
        self.assertEqual(pdo_mapping(0x6041, 0, 16), 0x60410010)
        self.assertEqual(32 + 32, 64)

    def test_mapping_rejects_oversize(self):
        with self.assertRaises(ValueError):
            pdo_mapping(0x606C, 0, 65)

    def test_little_endian_speed(self):
        self.assertEqual(
            little_endian_speed(bytes.fromhex("00 B8 0B 00")), 30.0
        )
        with self.assertRaises(ValueError):
            little_endian_speed(b"\x00")


class TestLoadAndRegressions(unittest.TestCase):
    def test_classic_can_frame_lengths(self):
        self.assertEqual(classical_can_frame_bits(8), 111)
        self.assertEqual(classical_can_frame_bits(8, extended=True), 131)
        self.assertEqual(classical_can_frame_bits(0), 47)

    def test_nominal_load_excludes_stuffing(self):
        self.assertAlmostEqual(
            nominal_bus_load(500_000, [(8, 1000, False)]), 0.222
        )

    def test_negative_frame_rate(self):
        with self.assertRaises(ValueError):
            nominal_bus_load(500_000, [(8, -1, False)])

    def test_repaired_chapter_pitfalls(self):
        pages = {n: (ROOT / (n + ".html")).read_text(encoding="utf-8")
                 for n in ("03", "04", "05", "08", "09",
                           "10", "20", "21", "27", "30")}
        self.assertNotIn("每次仲裁都输，输多了计数器就超限", pages["03"])
        self.assertNotIn("至少需要20个Tq以上", pages["05"])
        # Accept both the legacy SPL enumerator and the newer calculation-first
        # Chapter 08, while still guarding the exact 500-kbit/s configuration.
        self.assertTrue(
            "CAN_BS1_14tq" in pages["08"] or (
                "BS1 = 14" in pages["08"] and "500 kbit/s" in pages["08"]
            ),
            "Chapter 08 should teach the correct 14-tq BS1 configuration",
        )
        self.assertIn("GPIO_PinRemapConfig(GPIO_Remap1_CAN1", pages["09"])
        self.assertNotIn("CAN_TIxR_IDE;  // 标准帧", pages["10"])
        self.assertNotIn("0x4F表示读响应失败", pages["20"])
        self.assertIn("0x606C0020", pages["21"])
        self.assertIn("Protocol_GetVehicleSpeed", pages["27"])
        self.assertNotIn("HAL_CAN_Reset(&amp;hcan)", pages["30"])
        # Chapter 30 now explains the same correct bxCAN timing numerically,
        # instead of spelling out a legacy CAN_BS1_14TQ macro. Accept both
        # representations while preserving the 500-kbit/s arithmetic guard.
        self.assertTrue(
            "CAN_BS1_14TQ" in pages["30"] or (
                "BS1 = 14 TQ" in pages["30"] and
                "BS2 = 3 TQ" in pages["30"] and
                "BRP = 4" in pages["30"]
            )
        )
        self.assertTrue(
            "36MHz/[4*(1+14+3)] = 500kbps" in pages["30"] or (
                "36 MHz / [4 × (1+14+3)] = 500 kbit/s" in pages["30"]
            )
        )


if __name__ == "__main__":
    unittest.main()

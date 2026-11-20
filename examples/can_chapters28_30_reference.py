"""Deterministic reference models for CAN tutorial chapters 28–30.

These models operate on *application bytes* and a deliberately estimated bus budget.
They do not emulate bit stuffing, arbitration latency, electrical wake detection
or a live STM32 / CAN controller.
"""
from __future__ import annotations

import struct
from typing import Sequence


def standard_frame_unstuffed_bits(dlc: int) -> int:
    """11-bit classical CAN data frame incl. 3-bit intermission; no stuff bits."""
    if not isinstance(dlc, int) or not 0 <= dlc <= 8:
        raise ValueError("DLC must be an integer 0..8")
    return 47 + 8 * dlc


def estimated_bus_load_pct(
    nodes: int, period_ms: float, bits_per_frame: float, bitrate_kbps: float
) -> float:
    """Steady periodic frames only; ignores other traffic/retries and burst latency."""
    if not isinstance(nodes, int) or nodes <= 0:
        raise ValueError("nodes must be a positive integer")
    if not all(v > 0 for v in (period_ms, bits_per_frame, bitrate_kbps)):
        raise ValueError("period, frame bits, bitrate must be positive")
    return nodes * (1000.0 / period_ms) * bits_per_frame / (
        bitrate_kbps * 1000.0
    ) * 100.0


def average_current_ua(
    sleep_ua: float, active_ma: float, active_duty_pct: float
) -> float:
    if sleep_ua < 0 or active_ma < 0 or not 0 <= active_duty_pct <= 100:
        raise ValueError("invalid current or duty cycle")
    duty = active_duty_pct / 100.0
    return sleep_ua * (1.0 - duty) + (active_ma * 1000.0) * duty


def illustrative_wake(
    mode: str, frame_id: int, *, configured_id: int = 0x321, valid: bool = True
) -> bool:
    """Teaching-only result. 'valid' represents valid WUP/WUF, not one dominant bit."""
    if mode not in {"normal", "pn"}:
        raise ValueError("unknown mode")
    if not 0 <= frame_id <= 0x7FF:
        raise ValueError("11-bit frame ID required")
    return bool(valid and (mode == "normal" or frame_id == configured_id))


def pack_four_temperatures(values: Sequence[int]) -> bytes:
    if len(values) != 4 or any(not -32768 <= v <= 32767 for v in values):
        raise ValueError("four signed 16-bit centi-degree values required")
    return struct.pack("<hhhh", *values)


def pack_sample(
    temp_centi: int, pressure_decikpa: int, rpm: int, seq: int, status: int
) -> bytes:
    ranges = [
        (-32768, 32767, temp_centi),
        (0, 65535, pressure_decikpa),
        (0, 65535, rpm),
        (0, 255, seq),
        (0, 1, status),
    ]
    if any(not isinstance(v, int) or not lo <= v <= hi for lo, hi, v in ranges):
        raise ValueError("sample field outside chapter-30 wire contract")
    return struct.pack("<hHHBB", temp_centi, pressure_decikpa, rpm, seq, status)


def decode_sample(payload: bytes) -> tuple[int, int, int, int, int]:
    if len(payload) != 8:
        raise ValueError("chapter-30 sample must be 8 bytes")
    temp, pressure, rpm, seq, flags = struct.unpack("<hHHBB", payload)
    if flags & ~1:
        raise ValueError("reserved status flag bits must be zero")
    return temp, pressure, rpm, seq, flags


def counter_gap(previous: int | None, current: int) -> bool:
    if not 0 <= current <= 255:
        raise ValueError("invalid sequence")
    if previous is None:
        return False
    if not 0 <= previous <= 255:
        raise ValueError("invalid previous sequence")
    return current != ((previous + 1) % 256)

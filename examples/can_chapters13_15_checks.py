"""Minimal, deterministic teaching models for CAN tutorial chapters 13–15.

These models are not a hardware driver, cable simulator, or ISO certification test.
"""
from __future__ import annotations


def bxcan_std_data_matches(rx_id: int, target: int = 0x200, mask: int = 0x7F0,
                           *, is_extended: bool = False, is_remote: bool = False) -> bool:
    """Matches the chapter-13 STM32 bxCAN ID + IDE + RTR mask example."""
    if not (0 <= rx_id <= 0x7FF and 0 <= target <= 0x7FF and 0 <= mask <= 0x7FF):
        raise ValueError("Standard CAN IDs and mask must be 11-bit values")
    return not is_extended and not is_remote and (rx_id & mask) == (target & mask)


def cable_round_trip_ns(length_m: float, ns_per_m: float = 5.0) -> float:
    """Cable-only two-way propagation delay; excludes transceiver and controller."""
    if length_m < 0 or ns_per_m <= 0:
        raise ValueError("Length must be nonnegative; delay per meter positive")
    return 2.0 * length_m * ns_per_m


def bit_time_ns(rate_kbps: float) -> float:
    if rate_kbps <= 0:
        raise ValueError("Bitrate must be positive")
    return 1_000_000.0 / rate_kbps


def equivalent_termination_ohms(count: int, each_ohms: float = 120.0) -> float:
    """Parallel ideal identical terminators; zero returns open circuit."""
    if count < 0 or each_ohms <= 0:
        raise ValueError("Invalid terminator count or resistance")
    return float("inf") if count == 0 else each_ohms / count


def reflection_coefficient(load_ohms: float, z0_ohms: float = 120.0) -> float:
    """Ideal transmission-line endpoint reflection (not a complete CAN topology)."""
    if load_ohms < 0 or z0_ohms <= 0:
        raise ValueError("Nonnegative load and positive characteristic impedance needed")
    if load_ohms == float("inf"):
        return 1.0
    return (load_ohms - z0_ohms) / (load_ohms + z0_ohms)


def termination_power_w(differential_v: float, resistor_ohms: float = 120.0) -> float:
    """Power in one resistor when its differential voltage is given."""
    if resistor_ohms <= 0:
        raise ValueError("Resistance must be positive")
    return differential_v ** 2 / resistor_ohms

"""Reproducible Chapter 06 register arithmetic (not a hardware driver).

Run: python -m examples.can_chapter06_checks
No external dependencies or simulated CAN bus acknowledgements.
"""


def _check_u11(value: int, label: str) -> None:
    if type(value) is not int or not 0 <= value <= 0x7FF:
        raise ValueError(f"{label} must be an 11-bit integer")


def mcp2515_standard_id_registers(identifier: int) -> tuple[int, int]:
    """SIDH/SIDL for a standard ID (EXIDE=0, EID fields zero)."""
    _check_u11(identifier, "identifier")
    return identifier >> 3, (identifier & 0x07) << 5


def mcp2515_standard_id_from_registers(sidh: int, sidl: int) -> int:
    """Decode the SID fields; reject EXIDE/EID bits for this standard-only demo."""
    if any(type(x) is not int or not 0 <= x <= 0xFF for x in (sidh, sidl)):
        raise ValueError("registers must be bytes")
    if sidl & 0x1F:
        raise ValueError("not a standard-only SID field encoding")
    return (sidh << 3) | (sidl >> 5)


def standard_id_filter_accepts(
    received: int, target: int, mask: int, *, device: str = "mcp2515"
) -> bool:
    """11-bit teaching model: omits frame type/data-byte filtering and routing."""
    for label, number in (
        ("received", received), ("target", target), ("mask", mask)
    ):
        _check_u11(number, label)
    if device == "mcp2515":
        compared = mask  # 1 = compare
    elif device == "sja1000":
        compared = ~mask & 0x7FF  # 0 = compare
    else:
        raise ValueError("device must be mcp2515 or sja1000")
    return ((received ^ target) & compared) == 0


def sja1000_bit_timing(
    oscillator_hz: int, brp: int, tseg1: int, tseg2: int, sjw: int = 1,
    triple_sample: bool = False,
) -> tuple[int, int, float, float]:
    """Return encoded BTR0/BTR1, bitrate, sample point for SJA1000.

    One TQ = 2 * BRP / oscillator_hz. BRP and TSEG are *physical* counts,
    while BTR0/BTR1 store count-minus-one fields.
    """
    if type(oscillator_hz) is not int or oscillator_hz <= 0:
        raise ValueError("oscillator_hz must be a positive integer")
    for value, low, high, label in (
        (brp, 1, 64, "brp"), (tseg1, 1, 16, "tseg1"),
        (tseg2, 1, 8, "tseg2"), (sjw, 1, 4, "sjw"),
    ):
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f"{label} out of encoded field range")
    if type(triple_sample) is not bool:
        raise ValueError("triple_sample must be bool")
    total = 1 + tseg1 + tseg2
    btr0 = ((sjw - 1) << 6) | (brp - 1)
    btr1 = (int(triple_sample) << 7) | ((tseg2 - 1) << 4) | (tseg1 - 1)
    bitrate = oscillator_hz / (2 * brp * total)
    sample = (1 + tseg1) / total
    return btr0, btr1, bitrate, sample


MCP2515_REQOP = {
    "normal": 0x00,
    "sleep": 0x20,
    "loopback": 0x40,
    "listen_only": 0x60,
    "configuration": 0x80,
}


def mcp2515_request_mode_transaction(mode: str) -> bytes:
    """SPI BIT MODIFY command for CANCTRL.REQOP[2:0].

    Hardware must subsequently poll CANSTAT.OPMOD; bytes alone don't confirm
    that the mode transition succeeded.
    """
    if mode not in MCP2515_REQOP:
        raise ValueError("unknown MCP2515 mode")
    return bytes((0x05, 0x0F, 0xE0, MCP2515_REQOP[mode]))


def main() -> None:
    sid = mcp2515_standard_id_registers(0x123)
    btr0, btr1, bitrate, sample = sja1000_bit_timing(
        16_000_000, 1, 13, 2
    )
    print(f"MCP2515 SID=0x123 -> SIDH=0x{sid[0]:02X} SIDL=0x{sid[1]:02X}")
    print(
        f"SJA1000 fXTAL=16MHz, BRP=1, TSEG1=13, TSEG2=2: "
        f"BTR0=0x{btr0:02X}, BTR1=0x{btr1:02X}, "
        f"bitrate={bitrate:.0f} bps, sample={sample * 100:.1f}%"
    )
    print("MCP2515 request config via BIT MODIFY:",
          mcp2515_request_mode_transaction("configuration").hex(" "))


if __name__ == "__main__":
    main()

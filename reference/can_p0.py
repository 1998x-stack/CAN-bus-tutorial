"""Small executable reference model for classical CAN and bxCAN tutorial examples.

Only portable calculations and protocol encodings belong here.  The functions
do not replace ISO 11898, CiA 301/402, or MCU vendor reference manuals.
"""
from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class BxCanTiming:
    can_clock_hz: int
    prescaler: int
    bs1: int
    bs2: int
    sjw: int = 1

    def __post_init__(self) -> None:
        if self.can_clock_hz <= 0:
            raise ValueError("CAN clock must be positive")
        if not (1 <= self.prescaler <= 1024):
            raise ValueError("bxCAN prescaler out of range")
        if not (1 <= self.bs1 <= 16 and 1 <= self.bs2 <= 8):
            raise ValueError("bxCAN segment out of range")
        if not (1 <= self.sjw <= 4 and self.sjw <= self.bs2):
            raise ValueError("Invalid SJW for bxCAN")

    @property
    def tq_per_bit(self) -> int:
        return 1 + self.bs1 + self.bs2

    @property
    def bitrate_hz(self) -> float:
        return self.can_clock_hz / (self.prescaler * self.tq_per_bit)

    @property
    def sample_point(self) -> float:
        return (1 + self.bs1) / self.tq_per_bit


def arbitration_winner(
    id_a: int, id_b: int, *, extended_a: bool = False, extended_b: bool = False
) -> Optional[str]:
    """Return A/B for unequal arbitration priorities; None for tied arbitration.

    CAN data frames are assumed. When base identifiers tie, standard beats
    extended due to IDE/SRR arbitration. Same-ID data frames do not resolve
    by their payload; a differing payload can cause a bit error.
    """
    for identifier, extended in ((id_a, extended_a), (id_b, extended_b)):
        maximum = 0x1FFFFFFF if extended else 0x7FF
        if not 0 <= identifier <= maximum:
            raise ValueError("CAN identifier out of range")
    base_a = (id_a >> 18) if extended_a else id_a
    base_b = (id_b >> 18) if extended_b else id_b
    if base_a != base_b:
        return "A" if base_a < base_b else "B"
    if extended_a != extended_b:
        return "B" if extended_a else "A"
    if id_a == id_b:
        return None
    return "A" if id_a < id_b else "B"


def error_state(tec: int, rec: int) -> str:
    """CAN protocol error state; arbitration lost does not modify counters."""
    if not (0 <= tec <= 256 and 0 <= rec <= 255):
        raise ValueError("counter out of modeled range")
    if tec >= 256:
        return "bus-off"
    if tec >= 128 or rec >= 128:
        return "error-passive"
    return "error-active"


def can_crc15_bits(bits: Sequence[int]) -> int:
    """CRC-15/CAN over SOF through data, before CRC, with stuffing removed."""
    crc = 0
    for bit in bits:
        if bit not in (0, 1):
            raise ValueError("bit sequence must contain only 0 or 1")
        feedback = ((crc >> 14) & 1) ^ bit
        crc = (crc << 1) & 0x7FFF
        if feedback:
            crc ^= 0x4599
    return crc


def sdo_upload_reply(command: int) -> tuple[str, Optional[int]]:
    """Classify CiA 301 initiate-upload reply, returning (kind, byte_count)."""
    if command == 0x80:
        return ("abort", None)
    lengths = {0x4F: 1, 0x4B: 2, 0x47: 3, 0x43: 4, 0x42: None}
    if command not in lengths:
        raise ValueError("not an initiate-upload response command")
    return ("success", lengths[command])


def pdo_mapping(index: int, subindex: int, bit_length: int) -> int:
    """CiA 301 PDO mapping entry: 16-bit index, 8-bit subindex, 8-bit length."""
    if not (0 <= index <= 0xFFFF and 0 <= subindex <= 0xFF):
        raise ValueError("invalid object address")
    if not (1 <= bit_length <= 64):
        raise ValueError("invalid mapping bit length for classical CAN")
    return (index << 16) | (subindex << 8) | bit_length


def little_endian_speed(payload: bytes) -> float:
    """Chapter 27 example: 0x100, start bit 8, 16-bit little-endian, 0.01 km/h."""
    if len(payload) < 3:
        raise ValueError("payload too short")
    return int.from_bytes(payload[1:3], "little") * 0.01


def classical_can_frame_bits(payload_length: int, *, extended: bool = False) -> int:
    """Data frame including 3-bit intermission; excludes stuffing/error/retry."""
    if not 0 <= payload_length <= 8:
        raise ValueError("classical CAN DLC must be 0..8 for data bytes")
    return (67 if extended else 47) + 8 * payload_length


def nominal_bus_load(
    bitrate_hz: int, traffic: Sequence[tuple[int, float, bool]]
) -> float:
    """Fractional load; traffic entries are (bytes, frames_per_second, extended).

    This is a lower-bound estimate for normal data frames: bit stuffing, error
    frames and retransmissions are deliberately excluded.
    """
    if bitrate_hz <= 0:
        raise ValueError("bitrate must be positive")
    total_bits_per_second = 0.0
    for payload_length, fps, extended in traffic:
        if fps < 0:
            raise ValueError("frame rate must be nonnegative")
        total_bits_per_second += classical_can_frame_bits(
            payload_length, extended=extended
        ) * fps
    return total_bits_per_second / bitrate_hz

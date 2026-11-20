"""Deterministic teaching encoders for CANopen chapters 19–21.

Classic CANopen examples only: not a CiA conformance stack, not a hardware driver.
"""
from __future__ import annotations

from struct import pack
from reference.can_p0 import pdo_mapping, nominal_bus_load, sdo_upload_reply

NMT_COMMANDS = {0x01, 0x02, 0x80, 0x81, 0x82}


def nmt_frame(command: int, node_id: int) -> tuple[int, bytes]:
    """Command frame (CAN-ID 0); 0 is broadcast, 1..127 addresses a node."""
    if command not in NMT_COMMANDS or not 0 <= node_id <= 127:
        raise ValueError("invalid NMT command or target")
    return (0, bytes((command, node_id)))


def heartbeat_can_id(node_id: int) -> int:
    if not 1 <= node_id <= 127:
        raise ValueError("invalid producer node-ID")
    return 0x700 + node_id


def consumer_heartbeat_entry(node_id: int, timeout_ms: int) -> int:
    """Typical CiA 301 0x1016 entry: reserved[31:24], node[23:16], ms[15:0]."""
    if not 1 <= node_id <= 127 or not 1 <= timeout_ms <= 0xFFFF:
        raise ValueError("invalid heartbeat supervision settings")
    return (node_id << 16) | timeout_ms


def decode_initiate_upload(response: bytes) -> tuple[str, int | None]:
    """Return (success/abort, optional little-endian unsigned value).

    0x42 is success but lacks an in-command size; no value-length guessing.
    """
    if len(response) != 8:
        raise ValueError("SDO response must be 8 bytes in these examples")
    kind, length = sdo_upload_reply(response[0])
    if kind == "abort":
        return (kind, int.from_bytes(response[4:8], "little"))
    if length is None:
        return (kind, None)
    return (kind, int.from_bytes(response[4:4 + length], "little"))


def upload_segment_reply(command: int, expected_toggle: int) -> tuple[int, bool]:
    """Parse server's segmented upload byte0 000tnnnc (not block sequence)."""
    if expected_toggle not in (0, 1) or not 0 <= command <= 0xFF:
        raise ValueError("bad segment control")
    if command & 0xE0:
        raise ValueError("not a segmented upload response")
    toggle = (command >> 4) & 1
    if toggle != expected_toggle:
        raise ValueError("SDO toggle mismatch")
    valid_bytes = 7 - ((command >> 1) & 0x07)
    return (valid_bytes, bool(command & 1))


def block_ack(ackseq: int, next_block_size: int) -> bytes:
    """Block SDO ack: A2, last consecutively accepted seq, new block size."""
    if not 0 <= ackseq <= 127 or not 1 <= next_block_size <= 127:
        raise ValueError("invalid block SDO ack")
    return bytes((0xA2, ackseq, next_block_size, 0, 0, 0, 0, 0))


def speed_position_mapping() -> tuple[int, int]:
    return (pdo_mapping(0x606C, 0, 32), pdo_mapping(0x6064, 0, 32))


def speed_position_payload(speed: int, position: int) -> bytes:
    """Example raw signed int32 values; physical units require the device EDS."""
    if any(not isinstance(x, int) or isinstance(x, bool) for x in (speed, position)):
        raise ValueError("raw values must be integers")
    return pack("<ii", speed, position)


def example_load() -> float:
    """50 x 100 fps x 111 bit / 500 kbit/s (excludes bit stuffing)."""
    return nominal_bus_load(500_000, [(8, 50 * 100, False)])


def examples() -> dict:
    """Expected didactic frames; does not execute CAN traffic."""
    return {
        "nmt_start": nmt_frame(0x01, 5),
        "bootup_id": heartbeat_can_id(5),
        "consumer_heartbeat": consumer_heartbeat_entry(5, 600),
        "sdo_read_two_bytes": decode_initiate_upload(
            bytes.fromhex("4B 00 20 01 34 12 00 00")
        ),
        "sdo_last_upload_segment": upload_segment_reply(0x19, 1),
        "block_ack": block_ack(7, 16),
        "mapping": speed_position_mapping(),
        "tpdo_payload": speed_position_payload(1000, -2000),
        "bus_load": example_load(),
    }


if __name__ == "__main__":
    for key, value in examples().items():
        print(f"{key}: {value.hex(' ') if isinstance(value, bytes) else value}")

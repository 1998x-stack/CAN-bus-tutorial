"""Classical CAN Chapter 02 teaching checks (Python 3, no dependencies).

This is NOT a hardware CAN controller or full frame serialization / CRC model.
The frame length counts are before dynamic bit stuffing, and exclude intermission
unless requested.
"""


def frame_bits(*, extended=False, data_bytes=8, remote=False, intermission=False):
    """Count unstuffed bits of one Classical CAN data/remote frame."""
    if isinstance(data_bytes, bool) or not isinstance(data_bytes, int):
        raise ValueError("data_bytes must be an integer")
    if not 0 <= data_bytes <= 8:
        raise ValueError("Classical CAN carries 0..8 bytes")
    arbitration = 32 if extended else 12
    data = 0 if remote else 8 * data_bytes
    return 1 + arbitration + 6 + data + 16 + 2 + 7 + (3 if intermission else 0)


def stuff_bits(bits):
    """Apply the *generic* Classical CAN five-equal-bits stuffing rule to bits.

    Only call this on the dynamic-stuffing region of a frame (SOF..CRC sequence).
    This small function does not calculate CRC, model arbitration, or define
    CAN-FD fixed stuff bits.
    """
    if not isinstance(bits, str) or any(bit not in "01" for bit in bits):
        raise ValueError("bits must be a binary string")
    output = []
    previous = None
    consecutive = 0
    for bit in bits:
        if bit == previous:
            consecutive += 1
        else:
            consecutive = 1
        output.append(bit)
        previous = bit
        if consecutive == 5:
            opposite = "1" if bit == "0" else "0"
            output.append(opposite)
            previous = opposite
            consecutive = 1
    return "".join(output)


def destuff_bits(bits):
    """Inverse of stuff_bits for well-formed, complete stuffed bit strings."""
    if not isinstance(bits, str) or any(bit not in "01" for bit in bits):
        raise ValueError("bits must be a binary string")
    output = []
    previous = None
    consecutive = 0
    index = 0
    while index < len(bits):
        bit = bits[index]
        if bit == previous:
            consecutive += 1
        else:
            consecutive = 1
        output.append(bit)
        previous = bit
        index += 1
        if consecutive == 5:
            if index >= len(bits):
                raise ValueError("missing required stuff bit")
            stuffed = bits[index]
            if stuffed == previous:
                raise ValueError("stuffing rule violation")
            previous = stuffed
            consecutive = 1
            index += 1
    return "".join(output)


if __name__ == "__main__":
    assert frame_bits() == 108
    assert frame_bits(extended=True) == 128
    assert frame_bits(remote=True) == 44
    assert frame_bits(intermission=True) == 111
    assert stuff_bits("0000001") == "00000101"
    assert destuff_bits("00000101") == "0000001"
    print("Chapter 02 reference assertions passed.")


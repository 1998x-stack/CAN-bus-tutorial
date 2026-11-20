"""Classical CAN Chapter 04: CRC-15 and fault-state teaching functions.

Python 3 standard library only. This is not a CAN frame serializer, bus
controller, physical-layer emulator or implementation of TEC/REC event updates.
The input to crc15_can is the logical, *destuffed* SOF-through-data bit sequence.
"""
GENERATOR = 0xC599  # x^15 + x^14 + x^10 + x^8 + x^7 + x^4 + x^3 + 1
WIDTH_MASK = 0x7FFF


def crc15_can(bits):
    """Compute Classical CAN CRC-15 over logical bits using a feedback register.

    bits is a string of '0'/'1', ordered as transmitted, without stuffed bits.
    """
    if not isinstance(bits, str) or any(bit not in "01" for bit in bits):
        raise ValueError("bits must be a binary string")
    crc = 0
    for value in bits:
        feedback = ((crc >> 14) & 1) ^ int(value)
        crc = (crc << 1) & WIDTH_MASK
        if feedback:
            crc ^= GENERATOR & WIDTH_MASK
    return crc


def crc15_polynomial_division(bits):
    """Independent integer polynomial long division reference for CRC tests."""
    if not isinstance(bits, str) or any(bit not in "01" for bit in bits):
        raise ValueError("bits must be a binary string")
    dividend = int(bits + "0" * 15, 2) if bits else 0
    while dividend.bit_length() >= 16:
        dividend ^= GENERATOR << (dividend.bit_length() - 16)
    return dividend


def classify_error_state(tec, rec):
    """Only classify CAN error state from observed counts, do not update them.

    TEC is bounded to 0..256 (256 represents the Bus-Off threshold);
    REC is bounded to 0..255 for this limited teaching model.
    """
    if type(tec) is not int or type(rec) is not int:
        raise ValueError("TEC and REC must be integers")
    if not 0 <= tec <= 256 or not 0 <= rec <= 255:
        raise ValueError("counter outside teaching range")
    if tec >= 256:
        return "bus-off"
    if tec >= 128 or rec >= 128:
        return "error-passive"
    return "error-active"


def nominal_error_flag_bits(state):
    """Return local node's nominal 6-bit flag + 8-bit recessive delimiter.

    The bus can exhibit multiple overlapping error flags. Actual length on
    the shared line must not be inferred from this local teaching example.
    """
    if state == "error-active":
        return "0" * 6 + "1" * 8
    if state == "error-passive":
        return "1" * 6 + "1" * 8
    raise ValueError("Only active and passive flags can be transmitted")


if __name__ == "__main__":
    assert crc15_can("") == 0
    assert crc15_can("1") == 0x4599
    assert crc15_can("101101101") == crc15_polynomial_division("101101101")
    assert classify_error_state(127, 0) == "error-active"
    assert classify_error_state(0, 128) == "error-passive"
    assert classify_error_state(256, 0) == "bus-off"
    assert nominal_error_flag_bits("error-active") == "00000011111111"
    print("Chapter 04 CRC and fault-confinement teaching checks passed.")


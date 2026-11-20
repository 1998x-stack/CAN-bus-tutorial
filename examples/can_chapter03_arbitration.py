"""Classical CAN Chapter 03: deterministic arbitration-key teaching model.

This does not model SOF, bit-stuffing, physical propagation, timing, CRC, ACK,
payload conflicts, errors, or automatic retries. The standard-format IDE
comparison bit is included as a key to compare a base-format remote frame
against an extended-format frame; it is in the base format's control field.
"""

MAX_STANDARD = 0x7FF
MAX_EXTENDED = 0x1FFFFFFF


def arbitration_bits(identifier, *, extended=False, remote=False):
    """Return (field_label, 0/1) items in comparison order for Classic CAN."""
    if isinstance(identifier, bool) or not isinstance(identifier, int):
        raise ValueError("identifier must be an integer")
    if not isinstance(extended, bool) or not isinstance(remote, bool):
        raise ValueError("extended and remote must be bool")
    max_id = MAX_EXTENDED if extended else MAX_STANDARD
    if not 0 <= identifier <= max_id:
        raise ValueError("identifier out of range")
    if extended:
        base = identifier >> 18
        suffix = identifier & 0x3FFFF
    else:
        base = identifier
        suffix = None
    bits = [("ID" + str(i), (base >> i) & 1) for i in range(10, -1, -1)]
    if extended:
        bits += [("SRR", 1), ("IDE", 1)]
        bits += [("X" + str(i), (suffix >> i) & 1) for i in range(17, -1, -1)]
        bits.append(("RTR", int(remote)))
    else:
        bits += [("RTR", int(remote)), ("IDE", 0)]
    return bits


def compare_frames(left, right):
    """Compare two frame dictionaries, returning winner and decision bit.

    Format: {"identifier": int, "extended": bool, "remote": bool}.
    A tied arbitration key is NOT a successful collision resolution.
    """
    a = arbitration_bits(**left)
    b = arbitration_bits(**right)
    for index, ((name_a, bit_a), (name_b, bit_b)) in enumerate(zip(a, b), start=1):
        if bit_a != bit_b:
            winner = "A" if bit_a == 0 else "B"
            label = name_a if name_a == name_b else name_a + "/" + name_b
            return {"winner": winner, "bit_index": index,
                    "field": label, "observed": 0}
    return {"winner": None, "bit_index": None, "field": None,
            "observed": None}


def base(identifier, *, remote=False):
    return {"identifier": identifier, "extended": False, "remote": remote}


def extended(identifier, *, remote=False):
    return {"identifier": identifier, "extended": True, "remote": remote}


if __name__ == "__main__":
    assert compare_frames(base(0x100), base(0x200))["bit_index"] == 2
    assert compare_frames(base(0x123), base(0x123, remote=True))["field"] == "RTR"
    assert compare_frames(base(0x123, remote=True),
                          extended((0x123 << 18) | 0x12))["field"] == "IDE"
    assert compare_frames(base(0x123), base(0x123))["winner"] is None
    print("Chapter 03 arbitration model assertions passed.")


"""CAN Chapter 01: ideal termination arithmetic for teaching; not a bus simulator."""


def parallel_ohms(*resistors: float) -> float:
    """Equivalent resistance of positive finite parallel resistors in ohms."""
    import math

    if not resistors or any(not math.isfinite(r) or r <= 0 for r in resistors):
        raise ValueError("all resistors must be positive and finite")
    return 1.0 / sum(1.0 / r for r in resistors)


if __name__ == "__main__":
    assert parallel_ohms(120, 120) == 60
    assert parallel_ohms(120) == 120
    print("two 120 Ω terminators:", parallel_ohms(120, 120), "Ω")


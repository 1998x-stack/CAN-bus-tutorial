"""Chapter 5: deterministic bxCAN nominal bit-timing examples.

Run from the repository root: python -m examples.can_chapter05_checks
The arithmetic is not an oscillator-tolerance or physical-bus simulation.
"""
from reference.can_p0 import BxCanTiming


def examples():
    return {
        "A_16MHz": BxCanTiming(
            can_clock_hz=16_000_000, prescaler=2, bs1=13, bs2=2, sjw=2
        ),
        "B_36MHz": BxCanTiming(
            can_clock_hz=36_000_000, prescaler=4, bs1=14, bs2=3, sjw=2
        ),
    }


def main():
    for name, timing in examples().items():
        print(
            f"{name}: {timing.bitrate_hz / 1000:.3f} kbit/s, "
            f"sample={timing.sample_point * 100:.2f}%, "
            f"TQ={timing.tq_per_bit}, "
            f"quantum={1e9 * timing.prescaler / timing.can_clock_hz:.1f} ns"
        )


if __name__ == "__main__":
    main()

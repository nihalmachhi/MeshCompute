"""Seeded PRNG implemented identically in Python and TypeScript (mulberry32)."""


def mulberry32(seed: int):
    state = seed & 0xFFFFFFFF

    def next_value() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = (state ^ (state >> 15)) * (1 | state)
        t &= 0xFFFFFFFF
        u = (t ^ (t >> 7)) * (61 | t)
        u &= 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

    return next_value

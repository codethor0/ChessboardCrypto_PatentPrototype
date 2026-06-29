"""Avalanche effect testing for S-box key sensitivity.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

from typing import Dict, Union

from src.sbox import generate_sbox


def hamming_distance(a: int, b: int) -> int:
    """Count differing bits between two integers."""
    return bin(a ^ b).count("1")


def flip_last_char_lsb(key: str) -> str:
    """Flip the least significant bit of the last character in the key.

    For ASCII letters this toggles case (e.g. ``'Z'`` -> ``'z'``), matching
    the documented test vector ``'XYZ'`` -> ``'XYz'``. Other characters use
    a literal LSB XOR.

    Args:
        key: Original key string.

    Returns:
        Key with perturbed last character.
    """
    if not key:
        return key
    chars = list(key)
    last = chars[-1]
    if last.isalpha():
        chars[-1] = last.swapcase()
    else:
        chars[-1] = chr(ord(last) ^ 1)
    return "".join(chars)


def run_avalanche_test(key: str = "XYZ") -> Dict[str, Union[float, int, bool, str]]:
    """Compare S-boxes for key and single-bit-flipped variant.

    Args:
        key: Base key (default ``"XYZ"``).

    Returns:
        Dictionary with differing entry percentage, total Hamming distance,
        and pass status (>= 50% entries differ).
    """
    sbox_a = generate_sbox(key)
    flipped_key = flip_last_char_lsb(key)
    sbox_b = generate_sbox(flipped_key)

    differing = sum(1 for a, b in zip(sbox_a, sbox_b) if a != b)
    total_hamming = sum(hamming_distance(a, b) for a, b in zip(sbox_a, sbox_b))
    pct = (differing / len(sbox_a)) * 100.0

    return {
        "base_key": key,
        "flipped_key": flipped_key,
        "total_entries": len(sbox_a),
        "differing_entries": differing,
        "differing_percent": pct,
        "total_hamming_distance": total_hamming,
        "pass_threshold_50pct": pct >= 50.0,
    }

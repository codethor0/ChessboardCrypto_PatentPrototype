"""Unit tests for S-box generation.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.sbox import generate_sbox, generate_sbox_3d, is_bijective, normalise_sbox


def test_sbox_length() -> None:
    """2D S-box must have 100 entries."""
    sbox = generate_sbox("XYZ")
    assert len(sbox) == 100


def test_sbox_bijective_xyz() -> None:
    """S-box for key XYZ must be bijective."""
    assert is_bijective(generate_sbox("XYZ"))


def test_sbox_bijective_multiple_keys() -> None:
    """S-box must be bijective for multiple keys."""
    for key in ("XYZ", "ABC", "test", "ChessboardCrypto"):
        assert is_bijective(generate_sbox(key)), f"Failed for key {key!r}"


def test_sbox_values_in_range() -> None:
    """All S-box values must be 0-99."""
    sbox = generate_sbox("XYZ")
    assert all(0 <= v <= 99 for v in sbox)


def test_sbox_3d_bijective() -> None:
    """3D S-box must be bijective over 1000 entries."""
    sbox = generate_sbox_3d("XYZ")
    assert len(sbox) == 1000
    assert is_bijective(sbox)


def test_normalise_sbox() -> None:
    """Normalised S-box values must be in [0, 1]."""
    normed = normalise_sbox(generate_sbox("XYZ"))
    assert all(0.0 <= v <= 1.0 for v in normed)

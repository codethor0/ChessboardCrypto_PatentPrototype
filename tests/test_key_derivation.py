"""Unit tests for key derivation.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.key_derivation import PREFIX_SEQUENCE, PREFIX_SUM, PIECE_TYPES, derive_key


def test_prefix_sequence_length() -> None:
    """Prefix sequence must contain exactly 18 numbers."""
    assert len(PREFIX_SEQUENCE) == 18


def test_prefix_sum() -> None:
    """PREFIX_SUM must equal sum of sequence."""
    assert PREFIX_SUM == sum(PREFIX_SEQUENCE)


def test_derivation_deterministic() -> None:
    """Same key must always produce same derivation."""
    a = derive_key("XYZ")
    b = derive_key("XYZ")
    assert a.start_row == b.start_row
    assert a.start_col == b.start_col
    assert a.piece_type == b.piece_type
    assert a.rotation_offset == b.rotation_offset


def test_derivation_ranges() -> None:
    """Derived values must fall in expected ranges."""
    dk = derive_key("test-key-123")
    assert 0 <= dk.start_row < 10
    assert 0 <= dk.start_col < 10
    assert dk.piece_type in PIECE_TYPES
    assert 0 <= dk.rotation_offset < 8


def test_different_keys_differ() -> None:
    """Different keys should usually produce different derivations."""
    a = derive_key("keyA")
    b = derive_key("keyB")
    assert (
        a.start_row != b.start_row
        or a.start_col != b.start_col
        or a.piece_type != b.piece_type
        or a.rotation_offset != b.rotation_offset
    )

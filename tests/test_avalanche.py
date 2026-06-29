"""Unit tests for avalanche effect.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.avalanche import flip_last_char_lsb, run_avalanche_test


def test_flip_last_char() -> None:
    """LSB flip of last char for XYZ should yield XYz."""
    assert flip_last_char_lsb("XYZ") == "XYz"


def test_avalanche_differing_percent() -> None:
    """Avalanche test must show >= 50% differing entries."""
    result = run_avalanche_test("XYZ")
    assert result["differing_percent"] >= 50.0, (
        f"Avalanche failed: only {result['differing_percent']:.1f}% differ"
    )


def test_avalanche_hamming_distance() -> None:
    """Total Hamming distance must be positive."""
    result = run_avalanche_test("XYZ")
    assert result["total_hamming_distance"] > 0


def test_avalanche_pass_flag() -> None:
    """Pass threshold flag must be True for XYZ."""
    result = run_avalanche_test("XYZ")
    assert result["pass_threshold_50pct"] is True

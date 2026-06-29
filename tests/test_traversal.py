"""Unit tests for Hamiltonian traversal.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.grid import CELL_COUNT
from src.traversal import generate_traversal, generate_traversal_from_key


def test_traversal_length() -> None:
    """Path must contain exactly 100 indices."""
    path = generate_traversal_from_key("XYZ")
    assert len(path) == CELL_COUNT


def test_traversal_unique_indices() -> None:
    """All indices must be unique."""
    path = generate_traversal_from_key("XYZ")
    assert len(set(path)) == CELL_COUNT


def test_traversal_valid_range() -> None:
    """All indices must be in 0-99."""
    path = generate_traversal_from_key("XYZ")
    assert all(0 <= i < CELL_COUNT for i in path)


def test_traversal_multiple_keys() -> None:
    """Traversal must work for various keys."""
    for key in ("ABC", "password", "12345", "XYz"):
        path = generate_traversal_from_key(key)
        assert len(path) == CELL_COUNT
        assert len(set(path)) == CELL_COUNT


def test_traversal_deterministic() -> None:
    """Same parameters must yield same path."""
    p1 = generate_traversal(3, 7, "knight", 2)
    p2 = generate_traversal(3, 7, "knight", 2)
    assert p1 == p2

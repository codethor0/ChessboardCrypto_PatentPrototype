"""S-box generation from chessboard traversal paths.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

from typing import List

from src.grid import BASE_START, build_grid, get_value_at_index
from src.traversal import generate_traversal_from_key
from src.traversal_3d import (
    BASE_START_3D,
    build_grid_3d,
    generate_traversal_3d_from_key,
)


def generate_sbox(key: str) -> List[int]:
    """Generate 100-element S-box for the given key.

    For each index in the traversal path, look up the grid value and
    subtract BASE_START to obtain a value in 0-99.

    Args:
        key: Input key string.

    Returns:
        List of 100 integers forming a bijective S-box.
    """
    grid = build_grid()
    path = generate_traversal_from_key(key)
    return [get_value_at_index(i, grid) - BASE_START for i in path]


def generate_sbox_3d(key: str) -> List[int]:
    """Generate 1000-element S-box from 3D traversal.

    Args:
        key: Input key string.

    Returns:
        List of 1000 integers in range 0-999.
    """
    grid = build_grid_3d()
    path = generate_traversal_3d_from_key(key)
    return [grid[i] - BASE_START_3D for i in path]


def is_bijective(sbox: List[int]) -> bool:
    """Return True if sbox is a permutation (each value appears exactly once).

    Args:
        sbox: Candidate S-box.

    Returns:
        True when all values are unique and cover the expected range.
    """
    n = len(sbox)
    expected = set(range(n))
    return set(sbox) == expected


def normalise_sbox(sbox: List[int]) -> List[float]:
    """Normalise S-box values to [0.0, 1.0] for analysis.

    Args:
        sbox: Input S-box.

    Returns:
        List of normalised floating-point values.
    """
    if not sbox:
        return []
    max_val = max(sbox)
    if max_val == 0:
        return [0.0] * len(sbox)
    return [v / max_val for v in sbox]

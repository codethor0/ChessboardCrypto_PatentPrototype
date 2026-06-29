"""Unit tests for grid initialisation.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.grid import (
    BASE_START,
    CELL_COUNT,
    GRID_SIZE,
    build_grid,
    get_normalised_value,
    index_to_row_col,
    row_col_to_index,
)


def test_grid_dimensions() -> None:
    """Grid must be 10x10."""
    grid = build_grid()
    assert len(grid) == GRID_SIZE
    assert all(len(row) == GRID_SIZE for row in grid)


def test_grid_values_row_major() -> None:
    """Values must be 11120..11219 in row-major order."""
    grid = build_grid()
    assert grid[0][0] == 11120
    assert grid[0][9] == 11129
    assert grid[9][9] == 11219
    flat = [grid[r][c] for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    assert flat == list(range(BASE_START, BASE_START + CELL_COUNT))


def test_normalised_value_range() -> None:
    """Normalised values must be 0-99."""
    grid = build_grid()
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            val = get_normalised_value(row, col, grid)
            assert 0 <= val <= 99


def test_index_row_col_roundtrip() -> None:
    """Index and row/col conversions must be inverse."""
    for idx in range(CELL_COUNT):
        row, col = index_to_row_col(idx)
        assert row_col_to_index(row, col) == idx

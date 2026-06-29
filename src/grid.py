"""10x10 chessboard grid with base permutation values 11120..11219.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

from typing import List, Optional, Tuple

BASE_START: int = 11120
GRID_SIZE: int = 10
CELL_COUNT: int = GRID_SIZE * GRID_SIZE


def build_grid() -> List[List[int]]:
    """Build a 10x10 grid with values 11120..11219 in row-major order.

    Returns:
        Nested list representing the grid; grid[row][col] holds the cell value.

    Example:
        >>> g = build_grid()
        >>> g[0][0]
        11120
        >>> g[9][9]
        11219
    """
    return [
        [BASE_START + row * GRID_SIZE + col for col in range(GRID_SIZE)]
        for row in range(GRID_SIZE)
    ]


def row_col_to_index(row: int, col: int) -> int:
    """Convert row/col coordinates to a linear index 0-99.

    Args:
        row: Row index (0-9).
        col: Column index (0-9).

    Returns:
        Linear cell index in row-major order.
    """
    return row * GRID_SIZE + col


def index_to_row_col(index: int) -> Tuple[int, int]:
    """Convert linear index 0-99 to row/col coordinates.

    Args:
        index: Linear cell index.

    Returns:
        Tuple of (row, col).
    """
    return index // GRID_SIZE, index % GRID_SIZE


def get_normalised_value(row: int, col: int, grid: Optional[List[List[int]]] = None) -> int:
    """Retrieve normalised 0-99 value from row/col.

    Args:
        row: Row index (0-9).
        col: Column index (0-9).
        grid: Optional pre-built grid; built on demand if omitted.

    Returns:
        Normalised value in range 0-99.
    """
    if grid is None:
        grid = build_grid()
    return grid[row][col] - BASE_START


def get_value_at_index(index: int, grid: Optional[List[List[int]]] = None) -> int:
    """Get raw grid value at linear index.

    Args:
        index: Linear cell index 0-99.
        grid: Optional pre-built grid.

    Returns:
        Raw grid value (11120..11219).
    """
    row, col = index_to_row_col(index)
    if grid is None:
        grid = build_grid()
    return grid[row][col]

"""3D Hamiltonian traversal for 10x10x10 grid (1000 cells).

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

from typing import List, Optional, Set, Tuple

from src.key_derivation import DerivedKey, derive_key
from src.moves import (
    PIECE_MOVES_3D,
    get_legal_destinations_3d,
    manhattan_distance_3d,
)

GRID_SIZE_3D: int = 10
CELL_COUNT_3D: int = GRID_SIZE_3D ** 3
BASE_START_3D: int = 11120


def coords_to_index_3d(layer: int, row: int, col: int, size: int = GRID_SIZE_3D) -> int:
    """Convert 3D coordinates to linear index."""
    return layer * size * size + row * size + col


def index_to_coords_3d(index: int, size: int = GRID_SIZE_3D) -> Tuple[int, int, int]:
    """Convert linear index to (layer, row, col)."""
    layer = index // (size * size)
    rem = index % (size * size)
    row = rem // size
    col = rem % size
    return layer, row, col


def build_grid_3d(size: int = GRID_SIZE_3D) -> List[int]:
    """Build flat 1000-element grid with values 11120..12119."""
    return [BASE_START_3D + i for i in range(size ** 3)]


def _find_nearest_unvisited_3d(
    layer: int,
    row: int,
    col: int,
    visited: Set[int],
    size: int = GRID_SIZE_3D,
) -> Tuple[int, int, int]:
    """Fallback: nearest unvisited cell in 3D."""
    best: Optional[Tuple[int, int, int]] = None
    best_dist = size ** 3 + 1
    best_idx = size ** 3
    for idx in range(size ** 3):
        if idx in visited:
            continue
        l, r, c = index_to_coords_3d(idx, size)
        dist = manhattan_distance_3d(layer, row, col, l, r, c, size)
        if dist < best_dist or (dist == best_dist and idx < best_idx):
            best_dist = dist
            best_idx = idx
            best = (l, r, c)
    assert best is not None
    return best


def generate_traversal_3d(
    start_layer: int,
    start_row: int,
    start_col: int,
    piece_type: str,
    rotation_offset: int,
    size: int = GRID_SIZE_3D,
) -> List[int]:
    """Generate Hamiltonian path through 10x10x10 grid.

    Args:
        start_layer: Starting layer index.
        start_row: Starting row index.
        start_col: Starting column index.
        piece_type: Chess piece type for move set.
        rotation_offset: Cyclic move offset.
        size: Grid dimension per axis.

    Returns:
        Ordered list of 1000 unique indices.
    """
    moves = PIECE_MOVES_3D[piece_type]
    total = size ** 3
    visited: Set[int] = set()
    path: List[int] = []

    layer, row, col = start_layer, start_row, start_col
    move_index = 0

    while len(path) < total:
        idx = coords_to_index_3d(layer, row, col, size)
        if idx not in visited:
            visited.add(idx)
            path.append(idx)

        if len(path) >= total:
            break

        chosen: Optional[Tuple[int, int, int]] = None
        num_moves = len(moves)

        for attempt in range(num_moves):
            offset = (rotation_offset + move_index + attempt) % num_moves
            dl, dr, dc = moves[offset]
            nl = (layer + dl) % size
            nr = (row + dr) % size
            nc = (col + dc) % size
            nidx = coords_to_index_3d(nl, nr, nc, size)
            if nidx not in visited:
                chosen = (nl, nr, nc)
                move_index += attempt + 1
                break

        if chosen is None:
            chosen = _find_nearest_unvisited_3d(layer, row, col, visited, size)
            move_index += 1

        layer, row, col = chosen

    return path


def generate_traversal_3d_from_key(key: str) -> List[int]:
    """Generate 3D traversal from string key using same derivation as 2D."""
    dk = derive_key(key)
    return generate_traversal_3d(
        dk.start_row % GRID_SIZE_3D,
        dk.start_col,
        (dk.start_row + dk.start_col) % GRID_SIZE_3D,
        dk.piece_type,
        dk.rotation_offset,
    )

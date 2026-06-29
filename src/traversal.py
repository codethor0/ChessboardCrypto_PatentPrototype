"""Hamiltonian path generation via chess piece traversal with wrap-around.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

from typing import List, Optional, Set, Tuple

from src.grid import GRID_SIZE, row_col_to_index
from src.key_derivation import DerivedKey, derive_key
from src.moves import PIECE_MOVES_2D, get_legal_destinations_2d, manhattan_distance_2d


def _find_nearest_unvisited_2d(
    row: int,
    col: int,
    visited: Set[int],
    size: int = GRID_SIZE,
) -> Tuple[int, int]:
    """Fallback: scan for nearest unvisited cell by toroidal Manhattan distance."""
    best: Optional[Tuple[int, int]] = None
    best_dist = size * size + 1
    for idx in range(size * size):
        if idx in visited:
            continue
        r, c = idx // size, idx % size
        dist = manhattan_distance_2d(row, col, r, c, size)
        if dist < best_dist or (dist == best_dist and idx < row_col_to_index(best[0], best[1])):
            best_dist = dist
            best = (r, c)
    assert best is not None
    return best


def generate_traversal(
    start_row: int,
    start_col: int,
    piece_type: str,
    rotation_offset: int,
    size: int = GRID_SIZE,
) -> List[int]:
    """Generate ordered list of 100 unique cell indices via piece traversal.

    Move selection cycles through the piece move list, offset by
    ``rotation_offset`` and the current move index. When no legal unvisited
    destination exists, falls back to the nearest unvisited cell.

    Args:
        start_row: Starting row (0-9).
        start_col: Starting column (0-9).
        piece_type: One of knight, bishop, rook, king.
        rotation_offset: Cyclic offset for move selection (0-7).
        size: Grid dimension (default 10).

    Returns:
        Ordered list of ``size*size`` unique indices 0..99.
    """
    moves = PIECE_MOVES_2D[piece_type]
    total = size * size
    visited: Set[int] = set()
    path: List[int] = []

    row, col = start_row, start_col
    move_index = 0

    while len(path) < total:
        idx = row_col_to_index(row, col)
        if idx not in visited:
            visited.add(idx)
            path.append(idx)

        if len(path) >= total:
            break

        destinations = get_legal_destinations_2d(row, col, piece_type, size)
        chosen: Optional[Tuple[int, int]] = None
        num_moves = len(moves)

        for attempt in range(num_moves):
            offset = (rotation_offset + move_index + attempt) % num_moves
            dr, dc = moves[offset]
            nr = (row + dr) % size
            nc = (col + dc) % size
            nidx = row_col_to_index(nr, nc)
            if nidx not in visited:
                chosen = (nr, nc)
                move_index += attempt + 1
                break

        if chosen is None:
            chosen = _find_nearest_unvisited_2d(row, col, visited, size)
            move_index += 1

        row, col = chosen

    return path


def generate_traversal_from_key(key: str) -> List[int]:
    """Generate traversal path from a string key.

    Args:
        key: Input key string.

    Returns:
        Ordered list of 100 cell indices.
    """
    dk = derive_key(key)
    return generate_traversal(
        dk.start_row, dk.start_col, dk.piece_type, dk.rotation_offset
    )

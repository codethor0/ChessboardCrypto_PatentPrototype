"""Chess piece move sets for 2D and 3D grids with wrap-around.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

from typing import Callable, Dict, List, Tuple

Move = Tuple[int, int]
Move3D = Tuple[int, int, int]

# --- 2D moves (single-step offsets) ---

KNIGHT_MOVES_2D: List[Move] = [
    (2, 1), (2, -1), (-2, 1), (-2, -1),
    (1, 2), (1, -2), (-1, 2), (-1, -2),
]

BISHOP_MOVES_2D: List[Move] = [
    (1, 1), (1, -1), (-1, 1), (-1, -1),
]

ROOK_MOVES_2D: List[Move] = [
    (1, 0), (-1, 0), (0, 1), (0, -1),
]

KING_MOVES_2D: List[Move] = [
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
]

PIECE_MOVES_2D: Dict[str, List[Move]] = {
    "knight": KNIGHT_MOVES_2D,
    "bishop": BISHOP_MOVES_2D,
    "rook": ROOK_MOVES_2D,
    "king": KING_MOVES_2D,
}


def wrap_coord(value: int, size: int) -> int:
    """Wrap coordinate with modular arithmetic for toroidal board."""
    return value % size


def apply_move_2d(row: int, col: int, move: Move, size: int = 10) -> Tuple[int, int]:
    """Apply a move with wrap-around on a size x size board."""
    dr, dc = move
    return wrap_coord(row + dr, size), wrap_coord(col + dc, size)


def get_legal_destinations_2d(
    row: int, col: int, piece_type: str, size: int = 10
) -> List[Tuple[int, int]]:
    """Return all legal destination cells for a piece at (row, col)."""
    moves = PIECE_MOVES_2D[piece_type]
    return [apply_move_2d(row, col, m, size) for m in moves]


# --- 3D moves ---

def _unique_3d_moves(candidates: List[Move3D]) -> List[Move3D]:
    """Deduplicate move tuples preserving order."""
    seen = set()
    result: List[Move3D] = []
    for m in candidates:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result


def _sign_permutations(a: int, b: int, c: int) -> List[Move3D]:
    """Generate all sign permutations of absolute offsets (a, b, c)."""
    offsets = [a, b, c]
    moves: List[Move3D] = []
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            for k in range(3):
                if k == i or k == j:
                    continue
                for s0 in (-1, 1):
                    for s1 in (-1, 1):
                        for s2 in (-1, 1):
                            vec = [0, 0, 0]
                            vec[i] = s0 * offsets[0]
                            vec[j] = s1 * offsets[1]
                            vec[k] = s2 * offsets[2]
                            moves.append((vec[0], vec[1], vec[2]))
    return _unique_3d_moves(moves)


KNIGHT_MOVES_3D: List[Move3D] = _sign_permutations(2, 1, 0)

BISHOP_MOVES_3D: List[Move3D] = _unique_3d_moves(
    [(s, s, s) for s in (-1, 1)]
    + [(s, s, 0) for s in (-1, 1)]
    + [(s, 0, s) for s in (-1, 1)]
    + [(0, s, s) for s in (-1, 1)]
)

ROOK_MOVES_3D: List[Move3D] = [
    (1, 0, 0), (-1, 0, 0),
    (0, 1, 0), (0, -1, 0),
    (0, 0, 1), (0, 0, -1),
]

KING_MOVES_3D: List[Move3D] = _unique_3d_moves(
    [
        (dr, dc, dl)
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
        for dl in (-1, 0, 1)
        if not (dr == 0 and dc == 0 and dl == 0)
    ]
)

PIECE_MOVES_3D: Dict[str, List[Move3D]] = {
    "knight": KNIGHT_MOVES_3D,
    "bishop": BISHOP_MOVES_3D,
    "rook": ROOK_MOVES_3D,
    "king": KING_MOVES_3D,
}


def apply_move_3d(
    layer: int, row: int, col: int, move: Move3D, size: int = 10
) -> Tuple[int, int, int]:
    """Apply a 3D move with wrap-around."""
    dl, dr, dc = move
    return (
        wrap_coord(layer + dl, size),
        wrap_coord(row + dr, size),
        wrap_coord(col + dc, size),
    )


def get_legal_destinations_3d(
    layer: int, row: int, col: int, piece_type: str, size: int = 10
) -> List[Tuple[int, int, int]]:
    """Return all legal 3D destination cells."""
    moves = PIECE_MOVES_3D[piece_type]
    return [apply_move_3d(layer, row, col, m, size) for m in moves]


def manhattan_distance_2d(
    r1: int, c1: int, r2: int, c2: int, size: int = 10
) -> int:
    """Toroidal Manhattan distance between two cells."""
    dr = min(abs(r1 - r2), size - abs(r1 - r2))
    dc = min(abs(c1 - c2), size - abs(c1 - c2))
    return dr + dc


def manhattan_distance_3d(
    l1: int, r1: int, c1: int, l2: int, r2: int, c2: int, size: int = 10
) -> int:
    """Toroidal Manhattan distance in 3D."""
    dl = min(abs(l1 - l2), size - abs(l1 - l2))
    dr = min(abs(r1 - r2), size - abs(r1 - r2))
    dc = min(abs(c1 - c2), size - abs(c1 - c2))
    return dl + dr + dc

"""Key derivation from string keys via SHA-256 hashing.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import hashlib
import struct
from dataclasses import dataclass
from typing import List, Tuple

PREFIX_SEQUENCE: List[int] = [
    11111, 21113, 11141, 11151, 11161, 11171, 11181, 11191,
    11110, 11111, 11121, 11113, 11141, 11151, 11161, 11171,
    11181, 11191,
]

PREFIX_SUM: int = sum(PREFIX_SEQUENCE)

PIECE_TYPES: Tuple[str, ...] = ("knight", "bishop", "rook", "king")


@dataclass(frozen=True)
class DerivedKey:
    """Parameters derived from a cryptographic key string."""

    key: str
    start_row: int
    start_col: int
    piece_type: str
    rotation_offset: int
    hash_bytes: bytes


def derive_key(key: str) -> DerivedKey:
    """Derive chess traversal parameters from a string key.

    Args:
        key: Input key string (e.g. ``"XYZ"``).

    Returns:
        DerivedKey with start position, piece type, and rotation offset.

    Example:
        >>> dk = derive_key("XYZ")
        >>> 0 <= dk.start_row < 10
        True
        >>> dk.piece_type in PIECE_TYPES
        True
    """
    hash_bytes = hashlib.sha256(key.encode("utf-8")).digest()
    start_row = hash_bytes[0] % 10
    start_col = hash_bytes[1] % 10
    piece_type = PIECE_TYPES[hash_bytes[2] % 4]
    uint32 = struct.unpack(">I", hash_bytes[4:8])[0]
    rotation_offset = (uint32 + PREFIX_SUM) % 8
    return DerivedKey(
        key=key,
        start_row=start_row,
        start_col=start_col,
        piece_type=piece_type,
        rotation_offset=rotation_offset,
        hash_bytes=hash_bytes,
    )

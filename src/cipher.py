"""Stream cipher with counter-based S-box feedback keystream.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

from typing import List

from src.key_derivation import PREFIX_SEQUENCE


def _initial_state(total_cells: int) -> int:
    """Compute cipher initial state from prefix sequence."""
    return (PREFIX_SEQUENCE[0] + PREFIX_SEQUENCE[1]) % total_cells


def generate_keystream(length: int, sbox: List[int]) -> bytes:
    """Generate a keystream using counter-based feedback mode with the S-box.

    Uses non-linear S-box lookups mixed with a 64-bit counter for diffusion.
    The S-box generation logic is unchanged; only keystream derivation differs.

    Args:
        length: Number of keystream bytes to produce.
        sbox: Bijective S-box (typically 100 elements).

    Returns:
        Keystream bytes of the requested length.
    """
    total_cells = len(sbox)
    state = _initial_state(total_cells)
    keystream = bytearray()
    counter = 0

    while len(keystream) < length:
        state = sbox[state]
        state = (state + (counter & 0xFF)) % total_cells
        counter += 1

        for _ in range(4):
            if len(keystream) >= length:
                break
            state = sbox[state]
            next_state = sbox[(state + 1) % total_cells]
            keystream_byte = (
                (state * 31 + next_state * 17) ^ (counter & 0xFF)
            ) & 0xFF
            keystream.append(keystream_byte)
            counter += 1

    return bytes(keystream[:length])


def encrypt(plaintext_bytes: bytes, sbox: List[int]) -> bytes:
    """Encrypt plaintext by XOR with the S-box-derived keystream.

    Args:
        plaintext_bytes: Data to encrypt.
        sbox: Bijective S-box.

    Returns:
        Ciphertext bytes.
    """
    keystream = generate_keystream(len(plaintext_bytes), sbox)
    return bytes(p ^ k for p, k in zip(plaintext_bytes, keystream))


def decrypt(ciphertext_bytes: bytes, sbox: List[int]) -> bytes:
    """Decrypt ciphertext (symmetric XOR with the same keystream).

    Args:
        ciphertext_bytes: Data to decrypt.
        sbox: Bijective S-box.

    Returns:
        Plaintext bytes.
    """
    return encrypt(ciphertext_bytes, sbox)

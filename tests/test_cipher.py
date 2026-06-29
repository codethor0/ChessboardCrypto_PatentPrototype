"""Unit tests for stream cipher.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cipher import decrypt, encrypt, generate_keystream
from src.sbox import generate_sbox


def test_encrypt_decrypt_roundtrip() -> None:
    """Encrypt then decrypt must recover original plaintext."""
    sbox = generate_sbox("XYZ")
    plaintext = b"Hello, Chessboard Crypto!"
    ciphertext = encrypt(plaintext, sbox)
    assert decrypt(ciphertext, sbox) == plaintext


def test_ciphertext_differs_from_plaintext() -> None:
    """Ciphertext must differ from plaintext for non-trivial data."""
    sbox = generate_sbox("XYZ")
    plaintext = b"Secret message for patent prototype"
    ciphertext = encrypt(plaintext, sbox)
    assert ciphertext != plaintext


def test_keystream_length() -> None:
    """Keystream generator must produce requested length."""
    sbox = generate_sbox("XYZ")
    ks = generate_keystream(1024, sbox)
    assert len(ks) == 1024


def test_deterministic_encryption() -> None:
    """Same key and plaintext must yield same ciphertext."""
    sbox = generate_sbox("XYZ")
    pt = b"deterministic test"
    assert encrypt(pt, sbox) == encrypt(pt, sbox)


def test_empty_plaintext() -> None:
    """Empty plaintext must encrypt/decrypt cleanly."""
    sbox = generate_sbox("XYZ")
    assert decrypt(encrypt(b"", sbox), sbox) == b""

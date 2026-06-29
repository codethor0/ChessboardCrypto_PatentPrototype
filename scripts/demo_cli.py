"""
Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

#!/usr/bin/env python3
"""Command-line interface for encrypt/decrypt operations."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cipher import decrypt, encrypt
from src.sbox import generate_sbox


def main() -> int:
    """Parse CLI args and encrypt or decrypt text with the given key."""
    parser = argparse.ArgumentParser(
        description="ChessboardCrypto stream cipher demo CLI"
    )
    parser.add_argument("--key", required=True, help="Encryption key string")
    parser.add_argument("--text", required=True, help="Plaintext or hex ciphertext")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["encrypt", "decrypt"],
        help="Operation mode",
    )
    args = parser.parse_args()

    sbox = generate_sbox(args.key)

    if args.mode == "encrypt":
        data = args.text.encode("utf-8")
        result = encrypt(data, sbox)
        print(result.hex())
    else:
        data = bytes.fromhex(args.text)
        result = decrypt(data, sbox)
        print(result.decode("utf-8"))

    return 0


if __name__ == "__main__":
    sys.exit(main())

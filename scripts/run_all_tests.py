"""
Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

#!/usr/bin/env python3
"""Orchestrate all unit tests and print pass/fail summary."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run pytest on the tests/ directory and report summary."""
    root = Path(__file__).resolve().parent.parent
    tests_dir = root / "tests"
    print("=" * 60)
    print("ChessboardCrypto – Unit Test Runner")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests_dir), "-v", "--tb=short"],
            cwd=str(root),
            capture_output=False,
        )
    except FileNotFoundError:
        print("pytest not installed; running tests with unittest discovery.")
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir), "-p", "test_*.py", "-v"],
            cwd=str(root),
        )

    if result.returncode == 0:
        print("\nALL TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

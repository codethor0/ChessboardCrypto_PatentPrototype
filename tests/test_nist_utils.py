"""Tests for prototype statistical test p-value validation.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.cipher import generate_keystream
from src.nist_utils import (
    P_VALUE_THRESHOLD,
    _finalize_test,
    _validate_p_value,
    run_statistical_suite,
    serial_test,
)
from src.nist_utils import _bits_from_bytes
from src.sbox import generate_sbox


def test_validate_p_value_in_range() -> None:
    """Valid p-values in [0, 1] must be accepted."""
    for p in (0.0, 0.01, 0.5, 1.0):
        value, valid, reason = _validate_p_value(p)
        assert valid is True
        assert reason is None
        assert 0.0 <= value <= 1.0


def test_validate_p_value_rejects_above_one() -> None:
    """p-values greater than 1 must be invalid."""
    value, valid, reason = _validate_p_value(1.569739)
    assert valid is False
    assert reason is not None
    assert "outside range" in reason
    assert value == 1.569739


def test_validate_p_value_rejects_negative() -> None:
    """Negative p-values must be invalid."""
    value, valid, reason = _validate_p_value(-0.1)
    assert valid is False
    assert value == 0.0


def test_validate_p_value_rejects_nan() -> None:
    """NaN p-values must be invalid."""
    value, valid, reason = _validate_p_value(float("nan"))
    assert valid is False
    assert value == 0.0


def test_finalize_test_error_on_invalid_p() -> None:
    """Invalid raw p-values must classify as ERROR."""
    p, status, reason, raw = _finalize_test(1.5)
    assert status == "ERROR"
    assert reason is not None
    assert raw == 1.5


def test_finalize_test_passes_valid_p() -> None:
    """Valid p-values above threshold must classify as PASS."""
    p, status, reason, raw = _finalize_test(P_VALUE_THRESHOLD + 0.1)
    assert status == "PASS"
    assert reason is None


def test_finalize_test_fail_below_threshold() -> None:
    """Valid p-values below threshold must classify as FAIL."""
    p, status, reason, raw = _finalize_test(0.005)
    assert status == "FAIL"
    assert reason is not None


def test_serial_test_p_value_in_range() -> None:
    """Serial test must return a valid p-value in [0, 1] for demo keystream."""
    sbox = generate_sbox("XYZ")
    bits = _bits_from_bytes(generate_keystream(10 * 1024, sbox))
    p_value, status, reason, raw_p = serial_test(bits, 2)
    assert 0.0 <= raw_p <= 1.0
    assert 0.0 <= p_value <= 1.0
    assert status != "ERROR", reason
    assert raw_p <= 1.0


def test_statistical_suite_all_p_values_in_range() -> None:
    """All statistical tests must report valid p-values in [0, 1]."""
    sbox = generate_sbox("XYZ")
    keystream = generate_keystream(10 * 1024, sbox)
    results = run_statistical_suite(keystream)
    for name, info in results.items():
        p = float(info["p_value"])
        raw = float(info["raw_p_value"])
        assert 0.0 <= p <= 1.0, f"{name} p-value out of range: {p}"
        assert 0.0 <= raw <= 1.0, f"{name} raw p-value out of range: {raw}"
        assert info["status"] in {"PASS", "FAIL", "ERROR"}
        if info["status"] == "ERROR":
            assert info["pass"] is False


def test_run_full_proof_exits_zero_when_green() -> None:
    """run_full_proof.py must exit 0 when all checks pass."""
    if os.environ.get("CHESSBOARD_PROOF_CHILD"):
        return
    result = subprocess.run(
        [sys.executable, "run_full_proof.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_run_full_proof_serial_not_error() -> None:
    """Serial test in full proof must not report ERROR after harness fix."""
    if os.environ.get("CHESSBOARD_PROOF_CHILD"):
        return
    result = subprocess.run(
        [sys.executable, "run_full_proof.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert "serial:" in result.stdout
    assert "serial: p=" in result.stdout
    assert "[ERROR]" not in result.stdout.split("serial:")[1].split("\n")[0]

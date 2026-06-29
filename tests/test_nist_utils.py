"""Tests for prototype statistical test p-value validation.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.nist_utils import (
    P_VALUE_THRESHOLD,
    _finalize_test,
    _validate_p_value,
    run_statistical_suite,
)


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
    assert "outside p-value range" in reason
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


def test_finalize_test_fails_invalid_p() -> None:
    """Invalid raw p-values must fail the test."""
    p, passed, reason, raw = _finalize_test(1.5)
    assert passed is False
    assert reason is not None
    assert raw == 1.5


def test_finalize_test_passes_valid_p() -> None:
    """Valid p-values above threshold must pass."""
    p, passed, reason, raw = _finalize_test(P_VALUE_THRESHOLD + 0.1)
    assert passed is True
    assert reason is None


def test_statistical_suite_p_values_in_range() -> None:
    """Valid reported p-values must lie in [0, 1]; invalid raw values must fail."""
    from src.cipher import generate_keystream
    from src.sbox import generate_sbox

    sbox = generate_sbox("XYZ")
    keystream = generate_keystream(10 * 1024, sbox)
    results = run_statistical_suite(keystream)
    for name, info in results.items():
        if info.get("p_value_valid"):
            p = info["p_value"]
            assert 0.0 <= p <= 1.0, f"{name} p-value out of range: {p}"
        if info.get("fail_reason") and str(info["fail_reason"]).startswith("invalid statistical"):
            assert info["pass"] is False
            raw = float(info.get("raw_p_value", 0))
            assert raw > 1.0 or raw < 0.0 or math.isnan(raw)

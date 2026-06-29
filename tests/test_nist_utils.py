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
    _serial_test_components,
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


def test_serial_test_uses_full_delta_formula() -> None:
    """Serial test must compute psi_m, psi_m1, psi_m2 and full del1/del2 deltas."""
    sbox = generate_sbox("XYZ")
    bits = _bits_from_bytes(generate_keystream(10 * 1024, sbox))
    comp = _serial_test_components(bits, 2)
    assert comp["del1"] == comp["psi_m"] - comp["psi_m1"]
    assert comp["del2"] == comp["psi_m"] - 2.0 * comp["psi_m1"] + comp["psi_m2"]


def test_serial_test_demo_regression_values() -> None:
    """Serial statistics for the demo keystream must match the corrected audit values."""
    sbox = generate_sbox("XYZ")
    bits = _bits_from_bytes(generate_keystream(10 * 1024, sbox))
    comp = _serial_test_components(bits, 2)
    assert comp["psi_m"] == 1.0797851562529104
    assert comp["psi_m1"] == 0.538330078125
    assert comp["psi_m2"] == 0.0
    assert comp["del1"] == 0.5414550781279104
    assert comp["del2"] == 0.003125000002910383
    assert abs(comp["p1"] - 0.7628243079189491) < 1e-9
    assert abs(comp["p2"] - 0.9554201169728261) < 1e-9


def test_serial_test_cannot_return_p_above_one() -> None:
    """Serial aggregate and component p-values must never exceed 1."""
    sbox = generate_sbox("XYZ")
    bits = _bits_from_bytes(generate_keystream(10 * 1024, sbox))
    results = run_statistical_suite(generate_keystream(10 * 1024, sbox))
    serial = results["serial"]
    assert float(serial["serial_p1_raw"]) <= 1.0
    assert float(serial["serial_p2_raw"]) <= 1.0
    assert float(serial["raw_p_value"]) <= 1.0


def test_serial_invalid_p_value_classifies_as_error(monkeypatch) -> None:
    """Invalid Serial p-values must classify as ERROR, not FAIL."""
    from src import nist_utils

    def fake_components(bits, m=2):
        return {
            "psi_m": 0.0,
            "psi_m1": 0.0,
            "psi_m2": 0.0,
            "del1": 0.0,
            "del2": 0.0,
            "p1": 1.5,
            "p2": 0.5,
        }

    monkeypatch.setattr(nist_utils, "_serial_test_components", fake_components)
    p_value, status, reason, raw_p = serial_test([0, 1] * 64, 2)
    assert status == "ERROR"
    assert raw_p == 1.5
    assert reason is not None


def test_run_full_proof_exits_nonzero_on_statistical_error(monkeypatch) -> None:
    """run_full_proof.py must exit nonzero when a statistical test reports ERROR."""
    if os.environ.get("CHESSBOARD_PROOF_CHILD"):
        return

    from src import nist_utils

    def fake_suite(data):
        results = run_statistical_suite(data)
        results["serial"]["status"] = "ERROR"
        results["serial"]["pass"] = False
        results["serial"]["fail_reason"] = "invalid p-value"
        return results

    monkeypatch.setattr(nist_utils, "run_statistical_suite", fake_suite)
    import run_full_proof

    monkeypatch.setattr(run_full_proof, "run_statistical_suite", fake_suite)
    assert run_full_proof.main() != 0


def test_run_full_proof_exits_nonzero_on_statistical_fail(monkeypatch) -> None:
    """run_full_proof.py must exit nonzero when a statistical test reports FAIL."""
    if os.environ.get("CHESSBOARD_PROOF_CHILD"):
        return

    from src import nist_utils

    def fake_suite(data):
        results = run_statistical_suite(data)
        results["monobit"]["status"] = "FAIL"
        results["monobit"]["pass"] = False
        results["monobit"]["fail_reason"] = "below threshold"
        return results

    monkeypatch.setattr(nist_utils, "run_statistical_suite", fake_suite)
    import run_full_proof

    monkeypatch.setattr(run_full_proof, "run_statistical_suite", fake_suite)
    assert run_full_proof.main() != 0


def test_make_proof_propagates_failure() -> None:
    """make proof must propagate run_full_proof.py exit status (no ignore prefix)."""
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "-$(PYTHON) run_full_proof.py" not in makefile
    assert "$(PYTHON) run_full_proof.py" in makefile


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
    assert "serial_p1:" in result.stdout
    assert "serial_p2:" in result.stdout
    assert "serial: p=" in result.stdout
    assert "[ERROR]" not in result.stdout.split("serial_p1:")[1].split("\n")[0]

"""Prototype statistical tests inspired by NIST SP 800-22.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System

These tests are engineering sanity checks only. They are not a formal NIST
validation, certification, or proof of cryptographic security.
"""

import math
from typing import Dict, List, Optional, Tuple, Union

# Minimum p-value for pass (significance level used in prototype checks)
P_VALUE_THRESHOLD: float = 0.01

STATISTICAL_TEST_DISCLAIMER = (
    "Prototype statistical tests inspired by NIST SP 800-22. "
    "Engineering sanity checks only; not formal NIST validation."
)


def _clamp01(value: float) -> float:
    """Clamp a numeric value to the closed interval [0.0, 1.0]."""
    return max(0.0, min(1.0, value))


def _validate_p_value(raw: float) -> Tuple[float, bool, Optional[str]]:
    """Validate and normalize a raw p-value.

    Returns:
        Tuple of (reported_p_value, is_valid, failure_reason).
    """
    if math.isnan(raw):
        return 0.0, False, "invalid p-value: NaN"
    if math.isinf(raw):
        return 0.0, False, "invalid p-value: infinite"
    if raw < 0.0:
        return 0.0, False, f"invalid p-value: negative ({raw})"
    if raw > 1.0:
        return raw, False, "invalid statistical approximation, outside p-value range [0,1]"
    return raw, True, None


def _finalize_test(raw_p: float) -> Tuple[float, bool, Optional[str], float]:
    """Return p-value, pass flag, optional reason, and raw computed value."""
    p_value, is_valid, reason = _validate_p_value(raw_p)
    if not is_valid:
        return p_value, False, reason, raw_p
    return p_value, p_value >= P_VALUE_THRESHOLD, None, raw_p


def _bits_from_bytes(data: bytes) -> List[int]:
    """Expand bytes into a list of individual bits (MSB first)."""
    bits: List[int] = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def _erfc_complement(x: float) -> float:
    """Complementary error function approximation for p-value computation."""
    # Abramowitz and Stegun approximation
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1.0 / (1.0 + 0.5 * x)
    tau = t * math.exp(
        -x * x
        - 1.26551223
        + t
        * (
            1.00002368
            + t
            * (
                0.37409196
                + t
                * (
                    0.09678418
                    + t
                    * (
                        -0.18628806
                        + t
                        * (
                            0.27886807
                            + t
                            * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))
                        )
                    )
                )
            )
        )
    )
    return tau if sign >= 0 else 2.0 - tau


def monobit_test(bits: List[int]) -> Tuple[float, bool, Optional[str], float]:
    """Frequency (monobit) test: proportion of ones should be near 0.5."""
    n = len(bits)
    s = sum(1 if b == 1 else -1 for b in bits)
    s_obs = abs(s) / math.sqrt(n)
    raw = _erfc_complement(s_obs / math.sqrt(2))
    return _finalize_test(raw)


def block_frequency_test(bits: List[int], block_size: int = 128) -> Tuple[float, bool, Optional[str], float]:
    """Block frequency test: proportion of ones in each block."""
    n = len(bits)
    num_blocks = n // block_size
    if num_blocks == 0:
        return 0.0, False, "insufficient data for block frequency test", 0.0

    proportions = []
    for i in range(num_blocks):
        block = bits[i * block_size : (i + 1) * block_size]
        proportions.append(sum(block) / block_size)

    chi_sq = 4.0 * block_size * sum((p - 0.5) ** 2 for p in proportions)
    if chi_sq > 0:
        k = num_blocks
        z = ((chi_sq / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
        raw = _erfc_complement(z / math.sqrt(2))
    else:
        raw = 1.0
    return _finalize_test(raw)


def runs_test(bits: List[int]) -> Tuple[float, bool, Optional[str], float]:
    """Runs test: oscillation frequency of the bit sequence."""
    n = len(bits)
    ones = sum(bits)
    pi = ones / n
    if abs(pi - 0.5) >= 2 / math.sqrt(n):
        return 0.0, False, "runs test precondition failed: proportion out of range", pi

    runs = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            runs += 1

    num = abs(runs - 2 * n * pi * (1 - pi))
    den = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    if den == 0:
        return 0.0, False, "runs test denominator zero", 0.0
    raw = _erfc_complement(num / den)
    return _finalize_test(raw)


def _longest_run_category(max_run: int, block_size: int = 128) -> int:
    """Map longest run of ones to NIST category index for given block size."""
    if block_size == 128:
        if max_run <= 4:
            return 0
        if max_run == 5:
            return 1
        if max_run == 6:
            return 2
        if max_run == 7:
            return 3
        if max_run == 8:
            return 4
        return 5
    # Generic fallback: bucket by run length
    return min(max_run, 5)


def longest_run_ones_test(bits: List[int], block_size: int = 128) -> Tuple[float, bool, Optional[str], float]:
    """Longest run of ones within a block test (prototype approximation)."""
    n = len(bits)
    num_blocks = n // block_size
    if num_blocks == 0:
        return 0.0, False, "insufficient data for longest run test", 0.0

    # Expected category proportions for block_size=128 (NIST Table)
    pi = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
    max_categories = len(pi)

    counts = [0] * max_categories
    for i in range(num_blocks):
        block = bits[i * block_size : (i + 1) * block_size]
        max_run = 0
        current = 0
        for b in block:
            if b == 1:
                current += 1
                max_run = max(max_run, current)
            else:
                current = 0
        category = _longest_run_category(max_run, block_size)
        counts[category] += 1

    chi_sq = sum(
        (counts[i] - num_blocks * pi[i]) ** 2 / (num_blocks * pi[i])
        for i in range(max_categories)
        if num_blocks * pi[i] > 0
    )
    k = max_categories - 1
    z = ((chi_sq / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k)) if k > 0 else 0
    raw = _erfc_complement(z / math.sqrt(2))
    return _finalize_test(raw)


def serial_test(bits: List[int], m: int = 2) -> Tuple[float, bool, Optional[str], float]:
    """Serial test for m-bit pattern frequency (two-bit patterns when m=2)."""
    n = len(bits)
    if n < m + 1:
        return 0.0, False, "insufficient data for serial test", 0.0

    # Count overlapping patterns of length m
    pattern_count: Dict[tuple, int] = {}
    for i in range(n - m + 1):
        pattern = tuple(bits[i : i + m])
        pattern_count[pattern] = pattern_count.get(pattern, 0) + 1

    num_patterns = 2 ** m
    expected = (n - m + 1) / num_patterns
    chi_sq = sum(
        (pattern_count.get(tuple(int(x) for x in format(p, f"0{m}b")), 0) - expected) ** 2
        / expected
        for p in range(num_patterns)
    )
    k = num_patterns - 1
    z = ((chi_sq / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k)) if k > 0 else 0
    raw = _erfc_complement(z / math.sqrt(2))
    return _finalize_test(raw)


def run_statistical_suite(data: bytes) -> Dict[str, Dict[str, Union[float, bool, Optional[str]]]]:
    """Run five prototype statistical tests inspired by NIST SP 800-22.

    Args:
        data: Binary data (e.g. 10KB keystream from demo cipher).

    Returns:
        Dictionary mapping test name to p-value, pass flag, and optional fail reason.
    """
    bits = _bits_from_bytes(data)

    tests = {
        "monobit": monobit_test(bits),
        "block_frequency": block_frequency_test(bits, 128),
        "runs": runs_test(bits),
        "longest_run_ones": longest_run_ones_test(bits, 128),
        "serial": serial_test(bits, 2),
    }

    return {
        name: {
            "p_value": pv,
            "raw_p_value": raw_p,
            "pass": passed,
            "fail_reason": reason,
            "p_value_valid": reason is None
            or not str(reason).startswith("invalid statistical"),
        }
        for name, (pv, passed, reason, raw_p) in tests.items()
    }


def run_nist_suite(data: bytes) -> Dict[str, Dict[str, Union[float, bool, Optional[str]]]]:
    """Backward-compatible alias for run_statistical_suite."""
    return run_statistical_suite(data)


def format_statistical_results(
    results: Dict[str, Dict[str, Union[float, bool, Optional[str]]]],
) -> str:
    """Format statistical test results as human-readable lines."""
    lines = []
    for name, info in results.items():
        reason = info.get("fail_reason") or ""
        if str(reason).startswith("invalid statistical"):
            raw = float(info.get("raw_p_value", info["p_value"]))
            lines.append(
                f"  {name}: raw_p={raw:.6f} [FAIL] "
                "invalid statistical approximation, outside p-value range [0,1]"
            )
        else:
            status = "PASS" if info["pass"] else "FAIL"
            line = f"  {name}: p={info['p_value']:.6f} [{status}]"
            if reason:
                line += f" ({reason})"
            lines.append(line)
    return "\n".join(lines)


def format_nist_results(results: Dict[str, Dict[str, Union[float, bool, Optional[str]]]]) -> str:
    """Backward-compatible alias for format_statistical_results."""
    return format_statistical_results(results)

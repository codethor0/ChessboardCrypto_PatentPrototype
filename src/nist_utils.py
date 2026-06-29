"""Prototype statistical tests inspired by NIST SP 800-22.

Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System

These tests are engineering sanity checks only. They are not a formal NIST
validation, certification, or proof of cryptographic security.
"""

import math
from typing import Dict, List, Literal, Optional, Tuple, Union

# Minimum p-value for pass (significance level used in prototype checks)
P_VALUE_THRESHOLD: float = 0.01

TestStatus = Literal["PASS", "FAIL", "ERROR"]

STATISTICAL_TEST_DISCLAIMER = (
    "Prototype statistical tests inspired by NIST SP 800-22. "
    "Engineering sanity checks only; not formal NIST validation."
)


def _validate_p_value(raw: float) -> Tuple[float, bool, Optional[str]]:
    """Validate a raw p-value.

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
        return raw, False, "invalid p-value: outside range [0,1]"
    return raw, True, None


def _finalize_test(raw_p: float) -> Tuple[float, TestStatus, Optional[str], float]:
    """Classify a computed p-value as PASS, FAIL, or ERROR."""
    p_value, is_valid, reason = _validate_p_value(raw_p)
    if not is_valid:
        return p_value, "ERROR", reason, raw_p
    if p_value >= P_VALUE_THRESHOLD:
        return p_value, "PASS", None, raw_p
    return (
        p_value,
        "FAIL",
        f"p-value {p_value:.6f} below threshold {P_VALUE_THRESHOLD}",
        raw_p,
    )


def _gammainc_series(a: float, x: float) -> float:
    """Lower regularized incomplete gamma P(a, x) via series expansion."""
    if x <= 0.0:
        return 0.0
    ap = a
    summ = 1.0 / a
    del_ = summ
    for _ in range(200):
        ap += 1.0
        del_ *= x / ap
        summ += del_
        if abs(del_) < abs(summ) * 1e-10:
            break
    return summ * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gammainc_cf(a: float, x: float) -> float:
    """Upper regularized incomplete gamma Q(a, x) via continued fraction."""
    if x <= 0.0:
        return 1.0
    b = x + 1.0 - a
    c = 1.0 / 1e-30
    d = 1.0 / b
    h = d
    for i in range(1, 200):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        del_ = d * c
        h *= del_
        if abs(del_ - 1.0) < 1e-10:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gammainc(a: float, x: float) -> float:
    """Regularized lower incomplete gamma P(a, x). Standard library only."""
    if a <= 0.0 or x < 0.0:
        return float("nan")
    if x == 0.0:
        return 0.0
    if x < a + 1.0:
        return _gammainc_series(a, x)
    return 1.0 - _gammainc_cf(a, x)


def _igamc(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x) = 1 - P(a, x)."""
    if x <= 0.0:
        return 1.0
    return 1.0 - _gammainc(a, x)


def _bits_from_bytes(data: bytes) -> List[int]:
    """Expand bytes into a list of individual bits (MSB first)."""
    bits: List[int] = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def _erfc_complement(x: float) -> float:
    """Complementary error function approximation for p-value computation."""
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
                            + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))
                        )
                    )
                )
            )
        )
    )
    return tau if sign >= 0 else 2.0 - tau


def _psi_squared(m: int, bits: List[int]) -> float:
    """NIST SP 800-22 psi-squared statistic for block length m (circular)."""
    if m == 0:
        return 0.0
    n = len(bits)
    counts = [0] * (2**m)
    for i in range(n):
        pattern = 0
        for j in range(m):
            pattern = (pattern << 1) | bits[(i + j) % n]
        counts[pattern] += 1
    return (sum(c * c for c in counts) * (2**m) / n) - n


def monobit_test(bits: List[int]) -> Tuple[float, TestStatus, Optional[str], float]:
    """Frequency (monobit) test: proportion of ones should be near 0.5."""
    n = len(bits)
    s = sum(1 if b == 1 else -1 for b in bits)
    s_obs = abs(s) / math.sqrt(n)
    raw = _erfc_complement(s_obs / math.sqrt(2))
    return _finalize_test(raw)


def block_frequency_test(
    bits: List[int], block_size: int = 128
) -> Tuple[float, TestStatus, Optional[str], float]:
    """Block frequency test: proportion of ones in each block."""
    n = len(bits)
    num_blocks = n // block_size
    if num_blocks == 0:
        return 0.0, "ERROR", "insufficient data for block frequency test", 0.0

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


def runs_test(bits: List[int]) -> Tuple[float, TestStatus, Optional[str], float]:
    """Runs test: oscillation frequency of the bit sequence."""
    n = len(bits)
    ones = sum(bits)
    pi = ones / n
    if abs(pi - 0.5) >= 2 / math.sqrt(n):
        return 0.0, "FAIL", "runs test precondition failed: proportion out of range", pi

    runs = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            runs += 1

    num = abs(runs - 2 * n * pi * (1 - pi))
    den = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    if den == 0:
        return 0.0, "ERROR", "runs test denominator zero", 0.0
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
    return min(max_run, 5)


def longest_run_ones_test(
    bits: List[int], block_size: int = 128
) -> Tuple[float, TestStatus, Optional[str], float]:
    """Longest run of ones within a block test (prototype approximation)."""
    n = len(bits)
    num_blocks = n // block_size
    if num_blocks == 0:
        return 0.0, "ERROR", "insufficient data for longest run test", 0.0

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


def serial_test(bits: List[int], m: int = 2) -> Tuple[float, TestStatus, Optional[str], float]:
    """Serial test using NIST SP 800-22 psi-squared and igamc (circular patterns)."""
    n = len(bits)
    if n < m + 1:
        return 0.0, "ERROR", "insufficient data for serial test", 0.0
    if m < 2:
        return 0.0, "ERROR", "serial test requires m >= 2", 0.0

    psi_m1 = _psi_squared(m - 1, bits)
    psi_m = _psi_squared(m, bits)
    del1 = -psi_m1
    del2 = psi_m - 2.0 * psi_m1

    p1 = _igamc((2 ** (m - 1)) / 2.0, del1 / 2.0)
    p2 = _igamc((2 ** (m - 2)) / 2.0, del2 / 2.0)
    raw = min(p1, p2)
    return _finalize_test(raw)


def run_statistical_suite(data: bytes) -> Dict[str, Dict[str, Union[float, bool, Optional[str], TestStatus]]]:
    """Run five prototype statistical tests inspired by NIST SP 800-22."""
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
            "status": status,
            "pass": status == "PASS",
            "fail_reason": reason,
            "p_value_valid": status != "ERROR",
        }
        for name, (pv, status, reason, raw_p) in tests.items()
    }


def run_nist_suite(data: bytes) -> Dict[str, Dict[str, Union[float, bool, Optional[str], TestStatus]]]:
    """Backward-compatible alias for run_statistical_suite."""
    return run_statistical_suite(data)


def format_statistical_results(
    results: Dict[str, Dict[str, Union[float, bool, Optional[str], TestStatus]]],
) -> str:
    """Format statistical test results as human-readable lines."""
    lines = []
    for name, info in results.items():
        status = str(info.get("status", "FAIL"))
        line = f"  {name}: p={info['p_value']:.6f} [{status}]"
        reason = info.get("fail_reason")
        if reason:
            line += f" ({reason})"
        lines.append(line)
    return "\n".join(lines)


def format_nist_results(results: Dict[str, Dict[str, Union[float, bool, Optional[str], TestStatus]]]) -> str:
    """Backward-compatible alias for format_statistical_results."""
    return format_statistical_results(results)

"""
Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

#!/usr/bin/env python3
"""Top-level proof pipeline for engineering prototype validation."""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.avalanche import run_avalanche_test
from src.cipher import decrypt, encrypt, generate_keystream
from src.nist_utils import (
    STATISTICAL_TEST_DISCLAIMER,
    format_statistical_results,
    run_statistical_suite,
)
from src.sbox import generate_sbox, generate_sbox_3d, is_bijective

KEY = "XYZ"
PLAINTEXT = b"ChessboardCrypto Patent Prototype Validation Message"

VERDICT_PASS = "ENGINEERING PROTOTYPE VALIDATED – READY FOR PATENT COUNSEL REVIEW"
VERDICT_WARN = "ENGINEERING PROTOTYPE COMPLETED WITH VALIDATION WARNINGS – REVIEW REQUIRED"


def _write_validation_report(
    sbox: list,
    avalanche: dict,
    stats: dict,
    round_trip_ok: bool,
    sbox_3d: list,
    bijective_3d: bool,
    pytest_ok: bool,
) -> str:
    """Build markdown validation report content."""
    stats_lines = format_statistical_results(stats)
    avalanche_status = "PASS" if avalanche["pass_threshold_50pct"] else "FAIL"
    stats_all_pass = all(v["pass"] for v in stats.values())
    stats_invalid = [
        name
        for name, v in stats.items()
        if v.get("fail_reason")
        and str(v["fail_reason"]).startswith("invalid statistical")
    ]

    core_ok = (
        is_bijective(sbox)
        and avalanche["pass_threshold_50pct"]
        and round_trip_ok
        and bijective_3d
    )
    all_ok = core_ok and stats_all_pass and pytest_ok

    lines = [
        "# Engineering Prototype Validation Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Reference Key:** `{KEY}`",
        "",
        "> **Disclaimer:** This repository is an engineering prototype and patent "
        "drafting aid. The demo stream cipher is not a production cryptosystem. "
        "Statistical tests are prototype sanity checks inspired by NIST SP 800-22 "
        "and are not formal NIST validation, certification, or proof of "
        "cryptographic security.",
        "",
        "## 1. S-Box Bijectivity (2D Embodiment)",
        "",
        f"- **Bijective:** {is_bijective(sbox)}",
        f"- **First 20 values:** {sbox[:20]}",
        f"- **Status:** {'PASS' if is_bijective(sbox) else 'FAIL'}",
        "",
        "## 2. Avalanche Test (2D Embodiment)",
        "",
        f"- Base key: `{avalanche['base_key']}`",
        f"- Flipped key: `{avalanche['flipped_key']}`",
        f"- Differing entries: {avalanche['differing_entries']}/{avalanche['total_entries']}",
        f"- Differing percent: {avalanche['differing_percent']:.2f}%",
        f"- Total Hamming distance: {avalanche['total_hamming_distance']}",
        f"- **Status:** {avalanche_status}",
        "",
        "## 3. Prototype Statistical Tests (10 KB Demo Keystream)",
        "",
        f"- **Note:** {STATISTICAL_TEST_DISCLAIMER}",
        "",
        stats_lines,
        "",
    ]

    if stats_invalid:
        lines.append(f"- **Invalid p-values detected:** {', '.join(stats_invalid)}")
        lines.append("")

    lines.extend([
        f"- **Overall statistical checks:** {'PASS' if stats_all_pass else 'WARN/FAIL'}",
        "",
        "## 4. Demo Stream Cipher Round-Trip",
        "",
        f"- Plaintext: `{PLAINTEXT.decode()}`",
        f"- **Round-trip verified:** {round_trip_ok}",
        f"- **Status:** {'PASS' if round_trip_ok else 'FAIL'}",
        "",
        "## 5. 3D Embodiment (10 x 10 x 10)",
        "",
        f"- **Bijective (1000 entries):** {bijective_3d}",
        f"- **First 20 values:** {sbox_3d[:20]}",
        f"- **Status:** {'PASS' if bijective_3d else 'FAIL'}",
        "",
        "## 6. Unit Test Summary",
        "",
        f"- **pytest:** {'PASS' if pytest_ok else 'FAIL (see revision_log.md)'}",
        "",
        "## Final Verdict",
        "",
    ])

    if all_ok:
        lines.append(f"**{VERDICT_PASS}**")
    else:
        lines.append(f"**{VERDICT_WARN}**")
        if not core_ok:
            lines.append("")
            lines.append("Core embodiment checks failed or incomplete.")
        if not stats_all_pass:
            lines.append("")
            lines.append("One or more statistical prototype checks failed or returned warnings.")

    return "\n".join(lines)


def _run_pytest() -> bool:
    """Run pytest quietly; return True if all tests pass."""
    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except OSError:
        return False


def main() -> int:
    """Execute the full engineering prototype validation pipeline."""
    start = time.time()
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)

    print("=" * 70)
    print("CHESSBOARD / XDR STATE-TREE PROTOTYPE – VALIDATION PIPELINE")
    print("=" * 70)
    print(f"\nNote: {STATISTICAL_TEST_DISCLAIMER}")

    print("\n[Step 1] Generating 2D S-box for key 'XYZ'...")
    sbox = generate_sbox(KEY)
    bio_2d = is_bijective(sbox)
    print(f"  Bijective: {bio_2d}")
    print(f"  First 10 values: {sbox[:10]}")

    print("\n[Step 2] Running avalanche test...")
    avalanche = run_avalanche_test(KEY)
    av_status = "PASS" if avalanche["pass_threshold_50pct"] else "FAIL"
    print(f"  Differing entries: {avalanche['differing_percent']:.1f}% [{av_status}]")
    print(f"  Total Hamming distance: {avalanche['total_hamming_distance']}")

    print("\n[Step 3] Generating 10KB demo keystream and running statistical tests...")
    keystream = generate_keystream(10 * 1024, sbox)
    stats = run_statistical_suite(keystream)
    print(format_statistical_results(stats))

    print("\n[Step 4] Demo encrypt/decrypt round-trip test...")
    ciphertext = encrypt(PLAINTEXT, sbox)
    recovered = decrypt(ciphertext, sbox)
    round_trip_ok = recovered == PLAINTEXT
    print(f"  Ciphertext (hex): {ciphertext.hex()[:64]}...")
    print(f"  Round-trip OK: {round_trip_ok}")

    print("\n[Step 5] Generating 3D S-box (10 x 10 x 10)...")
    sbox_3d = generate_sbox_3d(KEY)
    bio_3d = is_bijective(sbox_3d)
    print(f"  Bijective: {bio_3d}")
    print(f"  First 20 values: {sbox_3d[:20]}")

    print("\n[Step 6] Running unit tests...")
    pytest_ok = _run_pytest()
    print(f"  pytest: {'PASS' if pytest_ok else 'FAIL'}")

    print("\n[Step 7] Saving validation report and test vectors...")
    report_md = _write_validation_report(
        sbox, avalanche, stats, round_trip_ok, sbox_3d, bio_3d, pytest_ok
    )
    report_path = docs / "validation_report.md"
    report_path.write_text(report_md, encoding="utf-8")

    test_vectors = {
        "key": KEY,
        "flipped_key": avalanche["flipped_key"],
        "sbox_2d": sbox,
        "sbox_3d_first_100": sbox_3d[:100],
        "keystream_first_64_hex": generate_keystream(64, sbox).hex(),
        "plaintext_hex": PLAINTEXT.hex(),
        "ciphertext_hex": ciphertext.hex(),
        "avalanche": avalanche,
        "statistical_tests": {
            k: {
                "p_value": v["p_value"],
                "raw_p_value": v.get("raw_p_value"),
                "pass": v["pass"],
                "fail_reason": v.get("fail_reason"),
            }
            for k, v in stats.items()
        },
        "disclaimer": STATISTICAL_TEST_DISCLAIMER,
    }
    vectors_path = docs / "test_vectors.json"
    with open(vectors_path, "w", encoding="utf-8") as fh:
        json.dump(test_vectors, fh, indent=2)

    elapsed = time.time() - start

    core_ok = bio_2d and avalanche["pass_threshold_50pct"] and round_trip_ok and bio_3d
    stats_all_pass = all(v["pass"] for v in stats.values())
    all_ok = core_ok and stats_all_pass and pytest_ok

    print("\n" + "=" * 70)
    if all_ok:
        print(VERDICT_PASS)
    else:
        print(VERDICT_WARN)
    print(f"Completed in {elapsed:.2f}s")
    print(f"Report: {report_path}")
    print(f"Test vectors: {vectors_path}")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

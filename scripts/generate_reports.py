"""
Copyright (c) 2026 Isaac Kong Thor. All rights reserved.
Patent Pending - Chessboard Cryptographic System
"""

#!/usr/bin/env python3
"""Generate avalanche, NIST, and bijectivity reports."""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.avalanche import run_avalanche_test
from src.cipher import generate_keystream
from src.nist_utils import run_nist_suite
from src.sbox import generate_sbox, generate_sbox_3d, is_bijective


def main() -> None:
    """Run statistical reports and write JSON/CSV to docs/."""
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)

    key = "XYZ"
    sbox = generate_sbox(key)
    avalanche = run_avalanche_test(key)
    keystream = generate_keystream(10 * 1024, sbox)
    nist = run_nist_suite(keystream)
    sbox_3d = generate_sbox_3d(key)

    report = {
        "key": key,
        "sbox_bijective_2d": is_bijective(sbox),
        "sbox_bijective_3d": is_bijective(sbox_3d),
        "avalanche": avalanche,
        "nist": nist,
        "sbox_2d_sample": sbox[:20],
        "sbox_3d_sample": sbox_3d[:20],
    }

    out_json = docs / "report_results.json"
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    out_csv = docs / "avalanche_results.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(avalanche.keys()))
        writer.writeheader()
        writer.writerow(avalanche)

    print(f"Reports written to {docs}")
    print(f"  Avalanche differing: {avalanche['differing_percent']:.1f}%")
    print(f"  2D bijective: {report['sbox_bijective_2d']}")
    print(f"  3D bijective: {report['sbox_bijective_3d']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run the vendor-neutral state-tree proof-of-concept demo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.state_tree import DECISION_LOG, evaluate_examples


def main() -> int:
    examples_dir = ROOT / "examples"
    if not examples_dir.exists():
        print("ERROR: examples/ directory not found.", file=sys.stderr)
        return 1

    print("Adversarial State-Tree Cryptographic Access Control POC Demo")
    print("=" * 64)
    results = evaluate_examples(examples_dir)
    for index, result in enumerate(results, start=1):
        print(f"\nScenario {index}: {result.decision}")
        print(f"  Reason: {result.reason}")
        print(f"  S_sec composite: {result.composite_score:.3f}")
        print(
            "  Scores: "
            f"T_ctx={result.scores.telemetry_context:.2f}, "
            f"G_adv={result.scores.graph_integrity:.2f}, "
            f"P_val={result.scores.path_validation:.2f}, "
            f"K_bind={result.scores.key_binding:.2f}, "
            f"D_resp={result.scores.deception_response:.2f}"
        )
        print(f"  Transcript decision: {result.path_transcript['decision']}")
        print(f"  Response action: {result.path_transcript['response_action']}")
        print(f"  Audit reference: {result.path_transcript['audit_hash']}")

    print(f"\n{DECISION_LOG}: all scenarios evaluated and auditable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

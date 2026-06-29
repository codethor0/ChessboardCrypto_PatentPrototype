"""Tests for vendor-neutral state-tree path validation."""

from __future__ import annotations

from pathlib import Path

from src.state_tree import (
    DECISION_ALLOW,
    DECISION_DECOY,
    evaluate_examples,
    load_json,
    validate_transition_path,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def test_valid_path_allows_action() -> None:
    graph = load_json(EXAMPLES / "state_tree_example.json")
    policy = load_json(EXAMPLES / "policy_example.json")
    telemetry = load_json(EXAMPLES / "telemetry_example.json")
    result = validate_transition_path(
        graph=graph,
        telemetry=telemetry,
        policy=policy,
        requested_action="decrypt_artifact",
        observed_nodes=[
            "endpoint_enrolled",
            "identity_verified",
            "case_open",
            "case_authorized",
        ],
    )
    assert result.decision == DECISION_ALLOW
    assert result.composite_score > 0.0


def test_skipped_node_triggers_decoy() -> None:
    graph = load_json(EXAMPLES / "state_tree_example.json")
    policy = load_json(EXAMPLES / "policy_example.json")
    telemetry = load_json(EXAMPLES / "telemetry_example.json")
    result = validate_transition_path(
        graph=graph,
        telemetry=telemetry,
        policy=policy,
        requested_action="decrypt_artifact",
        observed_nodes=[
            "endpoint_enrolled",
            "identity_verified",
            "case_authorized",
        ],
    )
    assert result.decision == DECISION_DECOY
    assert result.composite_score == 0.0


def test_example_scenarios_match_expected_decisions() -> None:
    scenarios = load_json(EXAMPLES / "path_validation_example.json")["scenarios"]
    results = evaluate_examples(EXAMPLES)
    assert len(results) == len(scenarios)
    for scenario, result in zip(scenarios, results):
        assert result.decision == scenario["expected_decision"]

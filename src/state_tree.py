"""Vendor-neutral state-tree path validation for the public proof of concept."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


DECISION_ALLOW = "ALLOW"
DECISION_DENY = "DENY"
DECISION_DECOY = "DECOY"
DECISION_CONTAIN = "CONTAIN"
DECISION_LOG = "LOG"


@dataclass(frozen=True)
class SecurityScores:
    """Component scores for S_sec(t) = T_ctx * G_adv * P_val * K_bind * D_resp."""

    telemetry_context: float
    graph_integrity: float
    path_validation: float
    key_binding: float
    deception_response: float

    @property
    def composite(self) -> float:
        values = (
            self.telemetry_context,
            self.graph_integrity,
            self.path_validation,
            self.key_binding,
            self.deception_response,
        )
        if any(value <= 0.0 for value in values):
            return 0.0
        result = 1.0
        for value in values:
            result *= value
        return result


@dataclass(frozen=True)
class PathDecision:
    """Outcome of state-tree validation."""

    decision: str
    composite_score: float
    scores: SecurityScores
    path_transcript: Dict[str, Any]
    reason: str


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON document from disk."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _edge_key(source: str, target: str) -> Tuple[str, str]:
    return (source, target)


def _build_edge_map(edges: Sequence[Mapping[str, Any]]) -> Dict[Tuple[str, str], Mapping[str, Any]]:
    return {_edge_key(str(edge["from"]), str(edge["to"])): edge for edge in edges}


def _telemetry_score(
    telemetry: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> float:
    required_fields = policy.get("required_telemetry_fields", [])
    if not required_fields:
        return 1.0
    present = sum(1 for field in required_fields if telemetry.get(field) not in (None, ""))
    return present / len(required_fields)


def _path_is_contiguous(
    observed_nodes: Sequence[str],
    edge_map: Mapping[Tuple[str, str], Mapping[str, Any]],
) -> bool:
    if len(observed_nodes) < 2:
        return len(observed_nodes) == 1
    for index in range(len(observed_nodes) - 1):
        key = _edge_key(observed_nodes[index], observed_nodes[index + 1])
        if key not in edge_map:
            return False
    return True


def _conditions_met(
    edge: Mapping[str, Any],
    telemetry: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> bool:
    required = edge.get("required_conditions", {})
    for key, expected in required.items():
        if telemetry.get(key) != expected and policy.get(key) != expected:
            return False
    prohibited = edge.get("prohibited_conditions", {})
    for key, forbidden in prohibited.items():
        if telemetry.get(key) == forbidden:
            return False
    risk_threshold = edge.get("risk_threshold")
    if risk_threshold is not None:
        risk = float(telemetry.get("risk_score", 0.0))
        if risk > float(risk_threshold):
            return False
    return True


def validate_transition_path(
    graph: Mapping[str, Any],
    telemetry: Mapping[str, Any],
    policy: Mapping[str, Any],
    requested_action: str,
    observed_nodes: Sequence[str],
    *,
    key_binding_valid: bool = True,
) -> PathDecision:
    """
    Validate an observed node sequence against a constrained state graph.

    Returns ALLOW when all critical scores are non-zero; otherwise DENY, DECOY,
    or CONTAIN based on policy deception settings.
    """
    nodes = [str(node) for node in observed_nodes]
    edge_map = _build_edge_map(graph.get("edges", []))
    allowed_actions = graph.get("allowed_actions", {})
    goal_node = allowed_actions.get(requested_action)

    telemetry_score = _telemetry_score(telemetry, policy)
    graph_score = 1.0 if nodes and nodes[0] == graph.get("start_node") else 0.0

    contiguous = _path_is_contiguous(nodes, edge_map)
    conditions_ok = True
    if contiguous and len(nodes) >= 2:
        for index in range(len(nodes) - 1):
            edge = edge_map[_edge_key(nodes[index], nodes[index + 1])]
            if not _conditions_met(edge, telemetry, policy):
                conditions_ok = False
                break

    reached_goal = bool(goal_node and nodes and nodes[-1] == goal_node)
    path_score = 1.0 if contiguous and conditions_ok and reached_goal else 0.0
    binding_score = 1.0 if key_binding_valid and path_score > 0.0 else 0.0

    invalid_path = path_score <= 0.0 or graph_score <= 0.0 or telemetry_score <= 0.0
    deception_mode = str(policy.get("invalid_path_response", "DENY")).upper()
    deception_score = 1.0 if invalid_path else 1.0

    scores = SecurityScores(
        telemetry_context=telemetry_score,
        graph_integrity=graph_score,
        path_validation=path_score,
        key_binding=binding_score,
        deception_response=deception_score,
    )
    composite = scores.composite

    transcript = {
        "request_id": telemetry.get("event_id", "unknown"),
        "starting_node": nodes[0] if nodes else None,
        "requested_action": requested_action,
        "observed_transitions": [
            {"from": nodes[i], "to": nodes[i + 1]} for i in range(len(nodes) - 1)
        ],
        "validated_transitions": [
            {"from": nodes[i], "to": nodes[i + 1]}
            for i in range(len(nodes) - 1)
            if _edge_key(nodes[i], nodes[i + 1]) in edge_map and conditions_ok
        ],
        "invalid_transitions": [],
        "risk_score": telemetry.get("risk_score", 0.0),
        "policy_version": policy.get("policy_version"),
        "decision": None,
        "response_action": None,
        "audit_hash": None,
    }

    if composite > 0.0:
        decision = DECISION_ALLOW
        reason = "Validated transition path satisfies policy and graph constraints."
        transcript["decision"] = decision
        transcript["response_action"] = requested_action
    elif deception_mode == "DECOY":
        decision = DECISION_DECOY
        reason = "Invalid path routed to decoy branch."
        transcript["decision"] = decision
        transcript["response_action"] = "decoy_output"
    elif deception_mode == "CONTAIN":
        decision = DECISION_CONTAIN
        reason = "Invalid path triggered containment response."
        transcript["decision"] = decision
        transcript["response_action"] = "contain_endpoint"
    else:
        decision = DECISION_DENY
        reason = "Invalid or incomplete transition path."
        transcript["decision"] = decision
        transcript["response_action"] = "deny"

    transcript["audit_hash"] = f"audit-{transcript['request_id']}-{decision.lower()}"
    return PathDecision(
        decision=decision,
        composite_score=composite,
        scores=scores,
        path_transcript=transcript,
        reason=reason,
    )


def evaluate_examples(
    examples_dir: Path,
) -> List[PathDecision]:
    """Load bundled examples and evaluate valid and invalid paths."""
    graph = load_json(examples_dir / "state_tree_example.json")
    policy = load_json(examples_dir / "policy_example.json")
    telemetry = load_json(examples_dir / "telemetry_example.json")
    scenarios = load_json(examples_dir / "path_validation_example.json")

    results: List[PathDecision] = []
    for scenario in scenarios.get("scenarios", []):
        scenario_telemetry = {**telemetry, **scenario.get("telemetry_overrides", {})}
        decision = validate_transition_path(
            graph=graph,
            telemetry=scenario_telemetry,
            policy=policy,
            requested_action=str(scenario["requested_action"]),
            observed_nodes=list(scenario["observed_nodes"]),
            key_binding_valid=bool(scenario.get("key_binding_valid", True)),
        )
        results.append(decision)
    return results

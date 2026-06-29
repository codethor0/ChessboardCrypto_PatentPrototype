# Formula

## Composite Security Score

The architecture uses a vendor-neutral composite score:

```
S_sec(t) = T_ctx(t) × G_adv(t) × P_val(t) × K_bind(t) × D_resp(t)
```

Each term is a normalized score in the range 0.0 to 1.0 for the proof of concept. In production implementations, scoring engines may use weighted models, thresholds, or additional terms subject to independent security review.

## Term Definitions

### T_ctx(t): Telemetry Context Score

Derived from endpoint, identity, process, workload, network, alert, tenant, policy, and risk signals.

Examples of inputs:

- endpoint registration and posture
- identity authentication strength
- process lineage consistency
- alert or case state
- tenant policy version
- current risk score

### G_adv(t): Adversarial State-Graph Integrity Score

Describes whether the requested path remains inside an allowed constrained transition graph.

Examples:

- start node matches expected graph entry
- graph version matches active policy
- graph has not expired or been revoked

### P_val(t): Path Validation Score

Indicates whether the observed or requested transition sequence satisfies policy, graph, and risk constraints.

Examples:

- each transition exists in the graph
- required conditions on each edge are satisfied
- prohibited conditions are absent
- requested action maps to the terminal node

### K_bind(t): Policy-Bound Cryptographic Binding Score

Indicates whether key shares, protected action authorization, or rehydration conditions match the validated path.

Examples:

- key share bound to validated node or transition
- release condition matches policy version
- binding has not expired

### D_resp(t): Deception and Response Score

Indicates whether invalid paths are routed to denial, restricted output, decoy output, honeytoken generation, evidence capture, or containment.

In the public POC, this term remains 1.0 when deception handling is configured and executed. Failed deception routing would drive the composite score to zero in extended implementations.

## Fail-Closed Rule

If any critical term equals zero, `S_sec(t)` equals zero and the system denies, restricts, deceives, logs, or contains instead of silently continuing.

The POC implements this as a multiplicative gate. Partial credit does not authorize protected actions.

## Example Threshold Table

| Term | Valid Path Example | Invalid Path Example |
|------|-------------------|----------------------|
| T_ctx | 1.0 (required telemetry present) | 0.75 (missing required field) |
| G_adv | 1.0 (starts at enrolled node) | 0.0 (wrong start node) |
| P_val | 1.0 (contiguous valid transitions) | 0.0 (skipped node) |
| K_bind | 1.0 (binding matches path) | 0.0 (binding mismatch) |
| D_resp | 1.0 (response policy active) | 1.0 (deception branch selected) |
| S_sec | 1.0 | 0.0 |

## Example Valid Path

Request: decrypt case artifact

Observed nodes:

1. endpoint_enrolled
2. identity_verified
3. case_open
4. case_authorized

Expected result: `ALLOW`

## Example Invalid Path

Request: decrypt case artifact

Observed nodes:

1. endpoint_enrolled
2. identity_verified
3. case_authorized

Expected result: `DECOY` or `DENY` depending on policy

Reason: skipped required intermediate state

## Example Action-Gating Decision

Request: isolate endpoint

Observed nodes:

1. endpoint_enrolled
2. incident_confirmed

If alert telemetry confirms malware and risk remains below the edge threshold, the path may be allowed. If alert state is missing or risk exceeds threshold, the composite score becomes zero and the action is denied or routed to containment logging.

## Validation in the POC

Run:

```bash
python scripts/state_tree_demo.py
```

The demo prints component scores and final decisions for bundled valid and invalid scenarios.

## Limitations

This formula is an architectural model for research and disclosure. It is not a formal proof of security, optimality, or patentability. Production scoring requires independent cryptographic and security review.

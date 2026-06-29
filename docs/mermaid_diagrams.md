# Mermaid Diagrams

## 1. High-Level System

```mermaid
flowchart LR
    TELE[Telemetry Sources] --> INTAKE[Telemetry Intake]
    POL[Policy Engine] --> COMP[Policy Compiler]
    INTAKE --> NORM[State Normalization]
    NORM --> GEN[State-Tree Generator]
    COMP --> GEN
    REQ[Protected Request] --> VAL[Transition Validator]
    GEN --> VAL
    VAL -->|valid| CRYPTO[Cryptographic Material Manager]
    VAL -->|valid| GATE[Protected Action Gate]
    VAL -->|invalid| DECOY[Deception Branch Manager]
    CRYPTO --> AUDIT[Audit Logger]
    GATE --> AUDIT
    DECOY --> AUDIT
    GATE --> RESP[Response Orchestration]
    DECOY --> RESP
```

**Explanation:** Telemetry and policy feed graph generation. Requests are validated before release or action authorization. Invalid paths route to deception and audit.

**POC validation:** Run `python scripts/state_tree_demo.py` and confirm valid paths return `ALLOW` while skipped paths return `DECOY`.

---

## 2. State-Tree Path Validation

```mermaid
flowchart TD
    A[Receive request] --> B[Load graph and policy]
    B --> C[Normalize telemetry]
    C --> D[Observe node sequence]
    D --> E{Start node valid?}
    E -->|No| Z[Fail closed]
    E -->|Yes| F{Transitions contiguous?}
    F -->|No| Z
    F -->|Yes| G{Edge conditions satisfied?}
    G -->|No| Z
    G -->|Yes| H{Terminal action allowed?}
    H -->|No| Z
    H -->|Yes| Y[ALLOW]
    Z --> X[DECOY or DENY]
```

**Explanation:** Validation is sequential and fail-closed. Any failed check drives the composite score to zero.

**POC validation:** Inspect scenario output in `examples/path_validation_example.json`.

---

## 3. Cryptographic Rehydration Flow

```mermaid
sequenceDiagram
    participant Client
    participant Validator as Transition Validator
    participant KMS as Cryptographic Material Manager
    participant Audit as Audit Logger

    Client->>Validator: Request protected secret
    Validator->>Validator: Validate path transcript
    alt Valid path
        Validator->>KMS: Release bound key share
        KMS->>Client: Rehydrated secret reference
        KMS->>Audit: Log release event
    else Invalid path
        Validator->>KMS: Do not release production secret
        Validator->>Client: Deny or decoy response
        Validator->>Audit: Log invalid path
    end
```

**Explanation:** Production secrets are not released unless path constraints and key bindings match.

**POC validation:** The bundled `missing_key_binding` scenario forces `K_bind = 0` and a non-allow decision.

---

## 4. Invalid Path Deception Branch

```mermaid
flowchart TD
    INV[Invalid path detected] --> POL{Deception policy}
    POL -->|decoy| D1[Return honeytoken artifact]
    POL -->|deny| D2[Hard deny]
    POL -->|contain| D3[Contain endpoint or session]
    D1 --> LOG[Append audit record]
    D2 --> LOG
    D3 --> LOG
    LOG --> ALERT[Optional alert or escalation]
```

**Explanation:** Invalid paths should produce evidence, not silent success.

**POC validation:** Policy `invalid_path_response: DECOY` in `examples/policy_example.json`.

---

## 5. Protected Action Gating

```mermaid
flowchart LR
    REQ[Action request] --> VAL[Path validation]
    VAL --> APP{Approval required?}
    APP -->|Yes| HUMAN[Human approval state]
    APP -->|No| EXEC[Action gate]
    HUMAN --> EXEC
    EXEC -->|authorized| PLAY[Playbook or endpoint action]
    EXEC -->|denied| AUD[Audit and deny]
```

**Explanation:** Sensitive actions such as isolation, script execution, or artifact retrieval require validated path and optional approval.

**POC validation:** Compare `decrypt_artifact` and `isolate_endpoint` scenarios in the demo output.

---

## 6. Agentic SOC Workflow Gating

```mermaid
sequenceDiagram
    participant Workflow as Automated SOC Workflow
    participant Gate as Protected Action Gate
    participant Val as Transition Validator
    participant Audit as Audit Logger

    Workflow->>Gate: Propose sensitive action
    Gate->>Val: Validate user intent and context path
    Val->>Val: Check data sensitivity and tenant policy
    alt Allowed
        Gate->>Workflow: Restricted action token
        Gate->>Audit: Log approved workflow
    else Blocked
        Gate->>Workflow: Deny or escalate
        Gate->>Audit: Log blocked workflow
    end
```

**Explanation:** Automated SOC workflows receive the same path and policy gating as human operators.

**POC validation:** Architecture-level only in this repository. Extend examples with workflow state in future releases.

---

## 7. Chessboard Embodiment Mapping

```mermaid
flowchart LR
    SEED[Deterministic seed] --> GRID[Numbered grid]
    GRID --> TRAV[Hamiltonian traversal]
    TRAV --> SBOX[Bijective permutation table]
    SBOX --> EMB[Optional embodiment layer]
    EMB --> ARCH[State-tree architecture]
```

**Explanation:** Chessboard traversal generates deterministic state permutations. The broader architecture does not depend on chess rules.

**POC validation:** Run `python run_full_proof.py` and confirm 2D and 3D bijective checks pass.

---

## 8. Docker Lab Flow

```mermaid
flowchart TD
    A[docker compose build] --> B[make test]
    B --> C[make proof]
    C --> D[make demo]
    D --> E[Review stdout and docs/validation.md]
```

**Explanation:** Containerized validation reproduces local engineering checks without host-specific paths.

**POC validation:**

```bash
docker compose build
docker compose run --rm app make test
docker compose run --rm app make proof
docker compose run --rm app make demo
```

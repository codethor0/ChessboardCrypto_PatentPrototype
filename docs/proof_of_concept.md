# Proof of Concept

## Components

### 1. State-Tree Validation Demo

Location: `scripts/state_tree_demo.py`  
Module: `src/state_tree.py`

Loads bundled JSON examples and evaluates:

- valid decrypt path (`ALLOW`)
- skipped intermediate state (`DECOY`)
- endpoint context mismatch (`DECOY`)
- valid isolation path (`ALLOW`)
- missing key binding (`DECOY`)

Run:

```bash
python scripts/state_tree_demo.py
```

### 2. Example Fixtures

| File | Purpose |
|------|---------|
| `examples/state_tree_example.json` | Small constrained graph |
| `examples/policy_example.json` | Required telemetry and deception policy |
| `examples/telemetry_example.json` | Baseline telemetry event |
| `examples/path_validation_example.json` | Valid and invalid scenarios |

### 3. Chessboard Embodiment

Location: `src/`, `run_full_proof.py`

Demonstrates deterministic traversal, bijective S-box generation, avalanche behavior, and a demonstration stream cipher. This code validates one optional embodiment pattern only.

Run:

```bash
python run_full_proof.py
python scripts/demo_cli.py --key XYZ --text "Hello" --mode encrypt
```

## Expected Demo Output

The state-tree demo prints:

- scenario decision (`ALLOW`, `DENY`, `DECOY`, `CONTAIN`, `LOG`)
- composite score `S_sec`
- component scores `T_ctx`, `G_adv`, `P_val`, `K_bind`, `D_resp`
- path transcript fields
- audit reference string

## What the POC Proves

- The repository can model graph-based path validation deterministically
- Valid and invalid paths produce different decisions
- Fail-closed scoring can gate protected actions in example scenarios
- The chessboard embodiment passes engineering sanity checks in the validation pipeline

## What the POC Does Not Prove

- Cryptographic security of any cipher or key-management design
- Patentability or freedom to operate
- Production readiness in any vendor platform
- Effectiveness against real-world attackers without further review

## Docker Lab

```bash
docker compose build
docker compose run --rm app make demo
```

See [validation.md](validation.md) for full test instructions.

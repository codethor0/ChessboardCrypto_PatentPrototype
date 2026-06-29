# Validation

## Local Tests

```bash
python -m pytest -q
python run_full_proof.py
python scripts/run_all_tests.py
python scripts/generate_reports.py
python scripts/state_tree_demo.py
```

Or:

```bash
make test
make proof
make demo
```

## Docker Tests

```bash
docker compose build
docker compose run --rm app make test
docker compose run --rm app make proof
docker compose run --rm app make demo
```

## Expected Outputs

### Unit tests

Expected: all tests pass, including state-tree scenarios in `tests/test_state_tree.py`.

Current baseline: 43 tests (including state-tree and statistical harness regression tests).

### Proof pipeline

Expected core results:

- 2D S-box bijective: PASS
- 3D S-box bijective: PASS
- Avalanche: PASS (98% for XYZ vs XYz)
- Encrypt/decrypt round-trip: PASS
- pytest: PASS

When all checks pass, final verdict:

`ENGINEERING PROTOTYPE VALIDATED – READY FOR PATENT COUNSEL REVIEW`

Exit code: `0`.

Each statistical test reports one of:

- `PASS`: valid p-value meeting the prototype threshold
- `FAIL`: valid p-value below the prototype threshold
- `ERROR`: invalid test output, unsupported input, or harness bug (for example p-value outside `[0, 1]`)

### State-tree demo

Expected scenario decisions:

| Scenario | Decision |
|----------|----------|
| valid_decrypt_path | ALLOW |
| skipped_case_state | DECOY |
| unknown_endpoint_replay | DECOY |
| valid_isolation_path | ALLOW |
| missing_key_binding | DECOY |

## What Validation Proves

- The engineering prototype behaves as specified in tests and demo scenarios
- The chessboard embodiment passes bijectivity, avalanche, and round-trip checks
- Invalid paths in the POC do not receive allow decisions

## What Validation Does Not Prove

- Cryptographic security of the demonstration cipher
- NIST validation or certification
- Patentability or legal claim scope
- Production readiness for real security platforms
- Resistance to sophisticated attackers without further review

## Statistical Test Disclaimer

Statistical checks in `src/nist_utils.py` are engineering sanity checks inspired by NIST SP 800-22. They are not formal NIST validation, certification, or proof of cryptographic security.

## Reports

Generated artifacts:

- `docs/validation_report.md`
- `docs/test_vectors.json`

These are engineering reports for research review. They are excluded from the public staging bundle unless explicitly approved.

# Final Public Release Validation

**Timestamp:** 2026-06-29  
**Branch:** main  
**Commit hash (current):** d70543ce2396ff2c4271242a517c1bb2b868bfa1  
**Author / committer:** Isaac Kong Thor \<codethor@gmail.com\>  
**Remote URL:** https://github.com/codethor0/ChessboardCrypto_PatentPrototype  
**Repo visibility:** PRIVATE

## Current Validation Status

The proof pipeline is green. Statistical checks are engineering sanity checks inspired by NIST SP 800-22 only. They are not formal external validation, certification, or a mathematical security proof. Independent legal and cryptographic review remains required.

| Check | Result |
|-------|--------|
| `python3.11 -m pytest -q` | 50 passed |
| `python3.11 run_full_proof.py` | Exit 0 |
| Serial `serial_p1` | `p=0.762824 [PASS]` |
| Serial `serial_p2` | `p=0.955420 [PASS]` |
| Serial aggregate (minimum) | `p=0.762824 [PASS]` |
| `make test` | PASS |
| `make proof` | Exit 0 |
| `make demo` | PASS |
| Docker proof (when available) | Exit 0 |
| Fresh-copy reproducibility | PASS, proof exit 0 |

All reported p-values are within `[0, 1]`. Invalid p-values classify as `ERROR`, not `FAIL`. Proof gates do not tolerate failure.

## Resolved Proof-Harness Issue (Historical)

### Prior observed failure

An earlier harness revision reported an invalid Serial raw p-value outside `[0, 1]` and caused `run_full_proof.py` to exit nonzero. That state is **resolved** and must not be treated as the current baseline.

### Why p-value outside `[0, 1]` is invalid

A statistical p-value is a probability in the closed interval `[0, 1]`. Values outside that range indicate a test-harness or formula error, not a legitimate statistical rejection.

### Root cause (resolved)

Two harness issues were corrected:

1. **Serial formula** — An incomplete delta path omitted `psi_m2` and miscomputed `del1`. The corrected implementation computes `psi_m`, `psi_m1`, and `psi_m2`, then `del1 = psi_m - psi_m1` and `del2 = psi_m - 2 * psi_m1 + psi_m2`, with p-values from the regularized upper incomplete gamma function.
2. **Proof gate honesty** — `make proof` and CI proof steps must propagate nonzero exit codes; failure-tolerant proof commands were removed.

This was a **p-value calculation / test-harness bug**, not a generator defect.

### Files corrected

- `src/nist_utils.py` — Serial test, p-value validation, `serial_p1` / `serial_p2` reporting
- `run_full_proof.py` — status-based aggregation; nested pytest guard
- `Makefile` — `make proof` propagates failures
- `.github/workflows/validate.yml` — proof step no longer masks failure
- `tests/test_nist_utils.py` — Serial regression and proof exit coverage

## Validation Results (Current)

### compileall

```
python3.11 -m compileall -q src scripts tests run_full_proof.py
PASS
```

### Local

| Command | Result |
|---------|--------|
| `python3.11 -m pytest -q` | 50 passed |
| `python3.11 run_full_proof.py` | Exit 0 — serial_p1, serial_p2, and aggregate minimum PASS |
| `python3.11 scripts/state_tree_demo.py` | PASS |
| `make test` | PASS |
| `make proof` | Exit 0 |
| `make demo` | PASS |

### Docker

| Command | Result |
|---------|--------|
| `docker compose build --no-cache` | PASS |
| `docker compose run --rm app python -m pytest -q` | 50 passed |
| `docker compose run --rm app python run_full_proof.py` | Exit 0 |
| `docker compose run --rm app make proof` | Exit 0 |
| `docker compose run --rm app make demo` | PASS |

### Fresh-copy reproducibility

| Command | Result |
|---------|--------|
| pytest / proof / demo / make targets | All PASS, proof exit 0 |

Generated during proof runs (excluded from bundles):

- `docs/validation_report.md`
- `docs/test_vectors.json`

## Hygiene Scan Summary

Public source passes strict zero-match hygiene scans for tool-origin attribution, forbidden claim language, vendor-specific product names, local paths, and emoji. Secret-scan hits are domain terms only.

## Code Review Summary

- No `eval` or `exec` in core modules
- No network calls in core cryptographic modules
- No hardcoded credentials
- S-box and traversal logic unchanged
- Serial test uses full three-psi formulation; proof exits 0 only when all checks pass

## Git Authorship

All commits: Isaac Kong Thor \<codethor@gmail.com\> only. No external-author trailers. Commits unsigned (`commit.gpgsign=false`).

## Publication Decision Inputs

- Proof pipeline exits 0 with valid Serial p1, p2, and aggregate minimum
- CI and Makefile proof gates propagate failure
- No home address, local paths, tool-origin attribution, or private materials in public source
- Push not performed without explicit human approval

## Verdict

Proof pipeline is mathematically honest and green. Ready for human push approval after final bundle and GitHub UI inspection.

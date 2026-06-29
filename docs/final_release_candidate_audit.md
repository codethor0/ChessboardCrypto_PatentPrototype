# Final Release Candidate Audit

**Timestamp:** 2026-06-29  
**Branch:** main  
**Commit hash (baseline):** pending post-fix commit  
**Author / committer:** Isaac Kong Thor \<codethor@gmail.com\>  
**Signing status:** Unsigned (`commit.gpgsign=false`); `git verify-commit HEAD` not applicable  
**Remote URL:** https://github.com/codethor0/ChessboardCrypto_PatentPrototype  
**Remote tracking:** ahead of origin (local not pushed)  
**Repo visibility:** PRIVATE

## Release Gate Framework

| Framework | Application |
|-----------|-------------|
| NIST SSDF (SP 800-218) | Secure development practices, validation discipline, honest consumer communication |
| OWASP ASVS | Verifiable security controls, fail-closed demo behavior, input validation at boundaries |
| OpenSSF Scorecard | Repository hygiene, SECURITY.md, CI workflow, dependency pinning, artifact exclusions |
| SLSA | Source integrity, reproducible Docker build, no untrusted generated artifacts in release bundle |

## Serial Test Formula Audit

### Observed implementation (pre-fix)

The Serial test computed only `psi_m1` and `psi_m`, omitted `psi_m2`, and used incomplete deltas:

```
del1 = -psi_m1
del2 = psi_m - 2.0 * psi_m1
```

This produced a valid-looking aggregate p-value for the demo stream while miscomputing `p1` (reported as 1.0 internally).

### Correct formula

```
psi_m  = _psi_squared(m, bits)
psi_m1 = _psi_squared(m - 1, bits)
psi_m2 = _psi_squared(m - 2, bits)
del1 = psi_m - psi_m1
del2 = psi_m - 2 * psi_m1 + psi_m2
p1 = igamc(2 ** (m - 1) / 2, del1 / 2)
p2 = igamc(2 ** (m - 2) / 2, del2 / 2)
```

Aggregate Serial status uses the stricter minimum of `p1` and `p2`.

### Root cause

The implementation followed a partial NIST delta shortcut (`del1 = -psi_m1`) instead of the full three-psi formulation. Proof could exit 0 while `p1` was mathematically wrong.

### Fix applied

- `src/nist_utils.py`: added `_serial_test_components` and `_finalize_serial_test`; Serial now computes `psi_m`, `psi_m1`, `psi_m2`, full `del1`/`del2`, validates both p-values, and reports `serial_p1`, `serial_p2`, and aggregate `serial`.
- `tests/test_nist_utils.py`: regression tests lock demo statistics and ERROR/FAIL/proof exit behavior.

### Post-fix psi values (demo keystream, m=2)

| Statistic | Value |
|-----------|-------|
| psi_m | 1.0797851562529104 |
| psi_m1 | 0.538330078125 |
| psi_m2 | 0.0 |

### Post-fix delta values

| Delta | Value |
|-------|-------|
| del1 | 0.5414550781279104 |
| del2 | 0.003125000002910383 |

### Post-fix p-values

| Component | p-value | Status |
|-----------|---------|--------|
| serial_p1 | 0.7628243079189491 | PASS |
| serial_p2 | 0.9554201169728261 | PASS |
| serial (minimum) | 0.7628243079189491 | PASS |

### Test coverage added

- Full delta formula regression against audit values
- Component and aggregate p-values bounded to `[0, 1]`
- Invalid p-values classify as ERROR, not FAIL
- `run_full_proof.py` exits nonzero on ERROR and FAIL
- `make proof` propagates proof exit status

### Proof exit behavior after fix

`run_full_proof.py` exits 0 only when all statistical tests report PASS with valid p-values. Serial reports both component p-values plus the minimum aggregate line.

## Git and Authorship

| Check | Result |
|-------|--------|
| Author identities | Isaac Kong Thor \<codethor@gmail.com\> only |
| Committer identities | Isaac Kong Thor \<codethor@gmail.com\> only |
| Co-author metadata trailers | None |
| Tool attribution in history | None |
| Commit signing verified | No (unsigned, correctly reported) |

## Filesystem Hygiene

| Check | Result |
|-------|--------|
| Local IDE/tooling artifacts, `.githooks`, `.venv` | Not present in working tree |
| Caches, `.DS_Store`, `._*` | Removed before audit |
| Generated `docs/validation_report.md` | Untracked/excluded (rebuilt during proof run) |
| Generated `docs/test_vectors.json` | Untracked/excluded |
| PDF, DOCX, ZIP in source | None |

## Hygiene Scans

Strict zero-match scans must pass across all public source (excluding `.git` only). Prohibition lists in doctrine and audit docs use generic language so scans do not false-positive on checklist wording.

## Validation Results

### Local

| Command | Result |
|---------|--------|
| `python3.11 -m compileall` | PASS |
| `python3.11 -m pytest -q` | 50 passed |
| `python3.11 run_full_proof.py` | Exit 0 — serial_p1 `0.762824 [PASS]`, serial_p2 `0.955420 [PASS]`, aggregate `0.762824 [PASS]` |
| `python3.11 scripts/state_tree_demo.py` | PASS |
| `make test PYTHON=python3.11` | PASS |
| `make proof PYTHON=python3.11` | Exit 0 |
| `make demo PYTHON=python3.11` | PASS |

### Docker

| Command | Result |
|---------|--------|
| `docker compose build --no-cache` | PASS |
| `docker compose run --rm app python -m pytest -q` | 50 passed |
| `docker compose run --rm app python run_full_proof.py` | Exit 0 — serial `[PASS]` |
| `docker compose run --rm app make proof` | Exit 0 |
| `docker compose run --rm app make demo` | PASS |

### Fresh-copy reproducibility (`/tmp/ChessboardCrypto_Repro_Test`)

| Command | Result |
|---------|--------|
| pytest / proof / demo / make targets | All PASS, proof exit 0 |
| Generated files after proof | Present locally only; excluded from bundle via `.gitignore` and rsync excludes |

## Documentation Review

| Document | Status |
|----------|--------|
| README | Clear; diagram at top; vendor-neutral |
| docs/validation.md | Serial formula fix and proof exit 0 when green |
| docs/public_release_doctrine.md | Generic prohibition language for strict scans |
| docs/final_public_release_validation.md | Root cause and fix recorded |
| LICENSE / NOTICE / disclosures | All-rights-reserved; Isaac Kong Thor authorship |

## Final Result

All release gates pass after Serial formula correction and strict-scan language cleanup. Repository is a green release candidate pending human push approval and GitHub UI inspection.

**Do not push or make public without explicit approval.**

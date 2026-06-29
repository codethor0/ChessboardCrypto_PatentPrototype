# Public Release Doctrine

Engineering release doctrine for the adversarial state-tree cryptographic access control public repository.

This doctrine applies NIST SSDF (SP 800-218), OWASP ASVS, OpenSSF Scorecard, and SLSA principles as **release gates**, not as claims of compliance or certification.

## 1. Scope

This doctrine governs the public GitHub repository maintained by Isaac Kong Thor. It covers:

- source hygiene and provenance
- authorship and attribution
- security and validation behavior
- documentation accuracy
- Docker reproducibility
- patent-safe public disclosure language

It does not authorize operational deployment, legal filing, or formal standards validation.

## 2. Release Gates

A release candidate must pass all gates below before visibility is changed to public or a public source ZIP is published.

| Gate | Requirement |
|------|-------------|
| G1 | Single clean authorship chain: Isaac Kong Thor only |
| G2 | Zero tool attribution in history, source, and bundles |
| G3 | Zero private artifacts, local paths, or home address |
| G4 | All unit tests pass |
| G5 | All statistical p-values valid; proof exits 0 only when all checks pass |
| G6 | Docker validation passes or unavailability is recorded |
| G7 | Documentation aligned with prototype behavior and limitations |
| G8 | LICENSE remains all-rights-reserved unless explicitly changed by Isaac Kong Thor |

## 3. Authorship and Provenance Gates

Inspired by **SLSA source integrity** and **OpenSSF Scorecard** maintainer identity expectations.

Required:

- Git author and committer: `Isaac Kong Thor <codethor@gmail.com>`
- Public docs name Isaac Kong Thor as author and maintainer
- Commits created with `git commit-tree` when IDE wrappers inject trailers

Prohibited:

- co-author metadata or tool-account commit trailers
- tool-origin attribution terms or model-provider / automated-origin terms
- Employer or vendor ownership language unless explicitly approved

## 4. Source Hygiene Gates

Inspired by **OpenSSF Scorecard** artifact hygiene and **NIST SSDF** secure distribution practices.

Excluded from public source and release ZIPs:

- `.git`, local IDE/tooling artifacts, `.githooks`, `.venv`
- `__pycache__`, `.pytest_cache`, `.DS_Store`, `._*`
- `.env`, `*.pem`, `*.key`
- `*.pdf`, `*.docx`, `*.zip`, `*.tar.gz`
- private committee materials, prompt transcripts, local audit logs
- generated `docs/validation_report.md` and `docs/test_vectors.json` unless explicitly intended

## 5. Security Gates

Inspired by **OWASP ASVS** verifiable controls and **NIST SSDF** vulnerability risk reduction.

Required:

- No `eval`, `exec`, or dynamic package installation at runtime
- No network calls in core prototype paths
- No hardcoded credentials or real secrets
- Input validation at module boundaries where applicable
- Fail-closed behavior documented for invalid paths in the state-tree demo
- SECURITY.md present and accurate

Review manually:

- Secret-scan hits must be domain terms only (honeytoken, token replay, test fixtures)
- No broad `except: pass` without documented reason

## 6. Validation Gates

Inspired by **NIST SSDF** testing and clear consumer communication.

Required local results:

```bash
python3.11 -m pytest -q          # 39 passed
python3.11 scripts/state_tree_demo.py   # PASS
python3.11 run_full_proof.py      # exit 0 when all proof checks pass

Statistical result classes:

- `PASS`: valid p-value meeting threshold
- `FAIL`: valid p-value below threshold
- `ERROR`: invalid p-value outside `[0, 1]`, NaN, infinite, or unsupported test condition
make test                         # PASS
make proof                        # exit 0 when all proof checks pass
make demo                         # PASS
```

Documented known limitation:

Do not hide statistical failures. Do not treat invalid p-values outside `[0, 1]` as expected warnings.

## 7. Docker Reproducibility Gates

Inspired by **SLSA** build reproducibility and **OpenSSF Scorecard** CI expectations.

Required when Docker is available:

```bash
docker compose build --no-cache
docker compose run --rm app python -m pytest -q
docker compose run --rm app python run_full_proof.py
docker compose run --rm app python scripts/state_tree_demo.py
docker compose run --rm app make test
docker compose run --rm app make proof
docker compose run --rm app make demo
```

Container must not depend on host local paths or secrets after image build.

If Docker is unavailable, record unavailability; do not mark Docker validation as pass.

## 8. Documentation Gates

Inspired by **NIST SSDF** consumer communication and **OWASP ASVS** clarity of security requirements.

Required:

- README shows main Mermaid system flow near the top
- Full diagram set remains in `docs/mermaid_diagrams.md`
- Formula consistent across README, `docs/formula.md`, and architecture docs
- Validation honesty in `docs/validation.md` and `docs/limitations.md`
- No emojis in documentation, source, comments, tests, or scripts
- No stale references to excluded private files or missing staging scripts
- No broken relative links in public docs

Prohibited documentation claims:

- operational deployment readiness
- formal standards validation or certification
- cryptographic proof
- legal filing readiness
- unsupported patent claims or marketing language

## 9. Patent-Safe Language Gates

Required framing:

- engineering prototype
- public technical disclosure
- research proof of concept
- subject to formal legal review
- subject to independent cryptographic review
- not legal advice

Prohibited literal phrases in public source:

- formal filing-readiness or patent-submission readiness phrases
- formal standards validation or certification phrases
- cryptographic proof or proof-of-security phrases
- operational deployment-readiness or production-deployment phrases
- absolute novelty, guarantee, or uniqueness marketing phrases

## 10. Public Disclosure Gates

Required files:

- `LICENSE` (all-rights-reserved)
- `NOTICE`
- `PUBLIC_DISCLOSURE.md`
- `docs/patent_notice.md`
- `docs/public_disclosure.md`

Required exclusions:

- home address
- local absolute paths
- private committee drafts
- vendor-specific product names

## 11. Known Limitations

- Chessboard stream cipher is a demonstration aid only
- State-tree POC uses a small hard-coded graph
- Statistical tests are engineering sanity checks inspired by NIST SP 800-22, not formal validation
- No production key-management integration
- Commits may be unsigned unless GPG or SSH signing is explicitly enabled by the maintainer

## 12. Final Release Checklist

- [ ] Authorship: Isaac Kong Thor only; no co-author trailers
- [ ] Tool attribution scan: zero matches
- [ ] Local path and home address scan: zero matches
- [ ] Forbidden claim language scan: zero matches
- [ ] Vendor-specific scan: zero matches
- [ ] Emoji scan: zero matches
- [ ] Secret scan: no real credentials
- [ ] Hygiene scan: no excluded artifacts in public source
- [ ] pytest: 39 passed
- [ ] state_tree_demo: PASS
- [ ] run_full_proof: exit 0 with all checks PASS
- [ ] Docker validation: pass or documented unavailable
- [ ] Fresh-copy reproducibility: pass
- [ ] README main flow diagram present
- [ ] LICENSE all-rights-reserved unchanged
- [ ] Release ZIP hygiene: pass
- [ ] Human inspection of disclosure documents complete
- [ ] Repository visibility change approved by Isaac Kong Thor

# Contributing

Thank you for reviewing this public research repository maintained by Isaac Kong Thor.

## Ground Rules

- Keep changes vendor-neutral
- Do not add employer-specific or product-specific ownership language
- Do not claim NIST validation, cryptographic proof, or production readiness
- Do not modify S-box or traversal logic without explicit approval and tests
- Do not commit secrets, `.env` files, private keys, or private committee materials
- Run tests before submitting changes

## Suggested Contributions

- Documentation clarity improvements
- Additional vendor-neutral examples
- Test coverage for state-tree validation edge cases
- Diagram or threat-model refinements
- Bug fixes in the POC demo or validation reporting

## Not Accepted Without Prior Discussion

- New runtime dependencies without documented need
- Permissive open-source relicensing
- Inclusion of private patent PDFs, DOCX files, or internal strategy logs in public branches
- Marketing language or unsupported legal conclusions

## Development Workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test
make proof
make demo
```

## Review Expectations

Contributions should preserve:

- engineering prototype status
- validation honesty
- public disclosure notices
- all-rights-reserved licensing unless expressly changed by the maintainer

# Security Policy

## Reporting a Vulnerability

If you believe you have found a security issue in this repository, contact the maintainer Isaac Kong Thor through a private channel before opening a public issue. Include:

- description of the issue
- affected files or commands
- reproduction steps
- expected versus actual behavior

## Scope

This repository is a research proof of concept. Reports are welcome for:

- incorrect fail-open behavior in the state-tree demo
- validation pipeline misreporting failures as passes
- accidental inclusion of secrets or private materials in public bundles
- documentation that makes unsupported cryptographic or legal claims

## Out of Scope

- Security of the demonstration stream cipher as a production algorithm
- Lack of integration with commercial security products
- Patentability or legal claim scope

## Safe Use

Do not use this repository to protect real data or production systems without independent cryptographic and security review.

Do not commit secrets, `.env` files, private keys, or internal employer materials to a public branch.

## Public Branch Hygiene

Before publishing:

- inspect README, patent notice, and disclosure documents manually
- confirm no secrets, private materials, local paths, or tool attribution are present
- run local and Docker validation per [docs/public_release_doctrine.md](docs/public_release_doctrine.md)
- record results in [docs/final_public_release_validation.md](docs/final_public_release_validation.md)

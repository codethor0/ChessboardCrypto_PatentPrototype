# Limitations

## Architectural Limitations

- The public POC uses a small hard-coded graph and simplified scoring
- Agentic SOC workflow gating is documented architecturally but not fully implemented as a live service
- Deception behavior is policy-driven and deterministic in the demo only
- Graph mutation, threshold secret sharing, and multi-tenant sharding are not implemented in this repository

## Cryptographic Limitations

- The chessboard stream cipher is a demonstration aid only
- S-box and traversal validation apply to the optional embodiment, not to full platform access control logic
- No formal cryptographic proof is provided
- No production key-management integration is included

## Statistical Limitations

- Prototype statistical tests may emit invalid raw p-values
- Passing statistical checks does not imply NIST validation or certification
- Statistical output must not be used as a marketing or compliance claim

## Legal and Disclosure Limitations

- This repository is a public technical disclosure and patent drafting aid
- Nothing here is legal advice
- Patentability, ownership, filing strategy, and claim scope require review by qualified patent counsel
- Users must not assume a license to use patent-pending concepts unless expressly granted

## Deployment Limitations

- Not suitable for operational deployment without independent review
- Not validated against real endpoint agents, SIEM systems, or SOAR platforms
- Not suitable for protecting real data without independent cryptographic review
- Vendor-neutral by design; integration with any specific product requires separate engineering work

## Public Release Limitations

Private committee materials, patent PDFs, DOCX drafts, internal polish logs, and counsel checklists are intentionally excluded from the public staging bundle. Review those materials separately before any filing or employer-specific disclosure decision.

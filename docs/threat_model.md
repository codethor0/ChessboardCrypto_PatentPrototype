# Threat Model

## Assets

- Protected data and case artifacts
- Key material and API secrets
- Protected security actions such as endpoint isolation, script execution, and artifact decryption
- Endpoint response actions and playbook execution permissions
- Audit records and path transcripts
- Policy definitions and graph versions

## Threat Actors

- Stolen token user replaying credentials from an unexpected host
- Compromised endpoint submitting inconsistent telemetry
- Malicious insider with excessive role permissions
- Over-permissioned automation account or service principal
- Compromised service account in a playbook engine
- Agentic AI workflow operating with excessive privileges

## Threats

| Threat | Description |
|--------|-------------|
| Token replay | Reuse of valid credentials outside expected context |
| Path skipping | Omitting required intermediate security states |
| Privilege escalation | Obtaining protected action rights without valid transitions |
| Unauthorized artifact decryption | Accessing sensitive evidence without case authorization |
| Unauthorized endpoint isolation | Triggering containment on the wrong host |
| False playbook execution | Running remediation scripts under invalid conditions |
| Decoy evasion | Attacker distinguishing decoys from real assets |
| Audit tampering | Removing or altering evidence of invalid paths |
| Context drift | Session continues after endpoint or identity state changes |

## Defensive Controls

- Telemetry-bound validation using live endpoint, identity, and case context
- Constrained state graph with explicit legal transitions
- Key-share binding to validated nodes or transitions
- Path transcript validation before release or action authorization
- Decoy branches and honeytokens on invalid paths
- Step-up authentication for high-risk transitions
- Containment and escalation options
- Append-only audit logging with evidence hashes
- Dynamic graph mutation when policy or risk state changes

## Out of Scope

This public repository does not provide:

- Production cryptographic assurance
- Formal verification of graph policies or scoring logic
- NIST validation or certification claims
- Vendor-specific product integration
- Real-world ransomware defense guarantees
- Deployment guidance for production security tooling

## Research Use Only

Use this threat model to understand the intended architecture. Operational deployment requires independent security review, red-team testing, and counsel review where applicable.

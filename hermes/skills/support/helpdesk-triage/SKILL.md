---
name: helpdesk-triage
description: Structured IT support triage workflow across identity, network, device, and application layers with evidence-based diagnosis and safe remediation proposals.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [helpdesk, it-support, troubleshooting, triage, incident-response]
---

# Help Desk Triage

## Trigger
Use this skill when the user asks for troubleshooting support, incident triage, root-cause narrowing, escalation prep, or step-by-step diagnosis for IT issues.

## Required Inputs
- User-reported symptoms and impact.
- Affected system/app/account and scope (single user vs multiple users).
- Time of first failure and any recent changes.
- Environment details (OS, network type, VPN/domain context when relevant).

## Procedure
1. **Intake & classify**
   - Capture issue summary, severity, business impact, and reproducibility.
2. **Layered triage**
   - Identity layer: auth/account/license/access checks.
   - Network layer: connectivity, DNS, VPN, latency/path checks.
   - Device layer: host health, updates, disk/memory pressure, local errors.
   - Application layer: app logs/config/version/service dependencies.
3. **Evidence collection**
   - Collect command outputs, error codes, timestamps, and affected components.
4. **Hypothesis ranking**
   - List likely causes from most to least probable with supporting evidence.
5. **Safe remediation proposal**
   - Provide lowest-risk fix path first.
   - Clearly label any action requiring approval.
6. **Verification plan**
   - Define success checks and rollback/safeguards.
7. **Escalation package (if unresolved)**
   - Prepare concise escalation note with findings, attempted steps, evidence, and next owner.

## Guardrails
- Do **not** perform destructive or high-risk changes without explicit approval.
- Do **not** rotate credentials, disable security controls, or change access policy silently.
- Do **not** claim resolution without verification evidence.
- Redact sensitive identifiers/secrets from outputs.

## Output Format
Return markdown with this exact structure:

```markdown
# Help Desk Triage Report
- Ticket/Case:
- Timestamp:
- Severity: Low | Medium | High | Critical
- Scope: Single User | Team | Org
- Current Status: Investigating | Mitigated | Resolved | Escalated

## 1) Issue Summary
- Symptoms:
- Impact:
- First Seen:
- Recent Changes:

## 2) Layered Findings
### Identity
- Checks:
- Findings:

### Network
- Checks:
- Findings:

### Device
- Checks:
- Findings:

### Application
- Checks:
- Findings:

## 3) Likely Root Cause(s)
1.
2.

## 4) Recommended Actions
- Immediate low-risk actions:
- Actions requiring approval:

## 5) Verification Plan
- Validation checks:
- Success criteria:

## 6) Escalation Notes (if needed)
- What was tried:
- Evidence attached:
- Recommended next owner/team:

## Verification
- Evidence sources:
- Commands/logs reviewed:
- Confidence:
```

## Verification
A run passes only if:
- All four layers (Identity/Network/Device/Application) were assessed or explicitly marked not applicable.
- At least one evidence-backed finding is recorded.
- Recommended actions are separated into low-risk vs approval-required.
- Status is accurate and supported by verification criteria.

## Sample Prompt
"Triage this VPN login failure for a single user using identity/network/device/application layers. Return the standard Help Desk Triage Report with likely cause and next actions."

## Notes
- Works well for Microsoft 365, Entra ID, Windows, Ubuntu, VPN, printer, and endpoint incidents.
- Prefer reproducible checks and timestamps over assumptions.

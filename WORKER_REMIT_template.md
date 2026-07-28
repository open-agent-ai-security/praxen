<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

<!--
  HOW TO USE THIS TEMPLATE

  Copy this file, rename it WORKER_REMIT.md, and fill it in for one agent.

  This document states POLICY — what the agent is allowed and forbidden to do.
  It does not describe implementation: no file paths, tool internals, or library
  versions. The scan reads the code; this file declares the intent to compare it
  against.

  Every guidance note in this template is an HTML comment like this one, so it is
  never mistaken for a policy clause. Delete the comments or leave them — either
  way they are not read as rules. Everything OUTSIDE a comment is treated as
  policy, so delete any section you leave empty rather than shipping placeholder
  text.

  WHICH CODE GETS SCANNED is a separate question from what this agent does.
  Do not declare scan scope here. If the agent lives in a monorepo, spans more
  than one repository, or ships as an example inside a framework, declare the
  main target to scan in a SCAN_INSTRUCTIONS.md file alongside this remit.
  See docs/writing-remits.md.

  MULTI-COMPONENT DEPLOYMENTS (e.g. an agent plus an operator console) belong in
  one remit, not several. Keep the section structure below exactly as it is and
  separate per-component rules with sub-headings INSIDE the existing sections
  (use H4 where H3 sub-headings already exist). Do not add new top-level
  sections — rules placed outside the standard headings can be missed.
-->

# Worker Remit
*Praxen — Agent Policy*

---

## Identity

| Field | Value |
|-------|-------|
| Worker Name | |
| Agent Key / ID | |
| Owner / Operator | |
| Deployment Environment | |
| Primary Model | |
| Secondary Models | |
| Remit Version | |
| Last Updated | |
| Updated By | |

---

## Mission

<!-- The agent's purpose, in 1-3 sentences. -->

---

## Job Description

<!-- What this agent is supposed to do. Be specific; vague entries cannot be verified. -->

- 
- 
- 

---

## Non-Goals (Out of Scope)

<!-- Work this agent must never do, regardless of instruction. -->

- 
- 
- 

---

## Approved Communication Channels

<!--
  Every channel the agent may use. Any channel absent from this table is
  unauthorized by default.
-->

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| | | | |

---

## Authorized Counterparties

<!--
  Who the agent may interact with. Counterparties found in code or configuration
  but missing from these lists are reported as a trust expansion.
-->

### Trusted People / Accounts
- 

### Trusted Domains
- 

### Trusted Services / Integrations
- 

### Explicitly Forbidden
- 

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)

<!-- Every tool the agent is expected to have at runtime. -->

- 

### Restricted Tools (Require Approval Before Use)

- 

### Forbidden Tools

<!-- Tools that must never appear in the agent's inventory or code. -->

- 

---

## Data Boundaries

### Allowed Data Sources
- 

### Sensitive Data Classes

<!-- Data requiring special handling; unexpected access or movement is reported. -->

- 

### Forbidden Data Movement

<!-- Specific movements of data that are never authorized. -->

- 

---

## Action Boundaries

<!--
  Every rule here should state a testable constraint on behavior — something that
  can be checked against the agent's code or logs.

  Verifiable:
    "Message bodies must never be fetched for senders not in the authorized
     counterparty list"
    "Responding to unknown senders requires human approval — no automated reply"

  Not verifiable:
    "Handle email appropriately"
    "Be careful with sensitive data"

  Every rule in this document is inventoried and any that cannot be verified is
  reported as such, so specific rules produce a more useful coverage report.
-->

### Allowed Without Approval
- 

### Requires Human Approval Before Execution
- 

### Never Allowed

<!-- Actions that are always a violation. -->

- 

---

## Behavioral Expectations

### Normal Cadence
- Active hours:
- Expected idle periods:
- Scheduled jobs / cron tasks:

### Expected Patterns

<!-- What normal work looks like, used to distinguish ordinary operation from drift. -->

- 

### Acceptable Retry Behavior

- Maximum retries before escalation:
- Retry interval:
- Actions that should never be retried:

---

## Known Good Baseline

<!-- What this agent looks like when operating correctly. Used for comparison. -->

### Typical Tool Inventory
- 

### Typical Channels Used
- 

### Typical Session Count / Duration
- 

### Typical Outbound Destinations
- 

### Typical File Paths Accessed
- 

### Normal Restart Cadence
- 

---

## Swimlane Definition

### Authorized Domains of Work

<!-- Topics, systems, and tasks this agent may engage with. -->

- 

### Disallowed Domains of Work

<!-- Topics, systems, and tasks this agent must decline or escalate. -->

- 

---

## Risk Sensitivities

<!-- Areas where extra scrutiny applies; findings here are held to a lower threshold. -->

- 

---

## Escalation Rules

<!--
  What happens when something goes wrong. State each condition precisely enough
  to check whether the agent's code implements the described response.

  "Alert if something suspicious happens" cannot be checked.
  "Alert the operator when a reply is addressed to any address not in the
   Rolodex" can.
-->

### Halt Agent and Alert Operator

<!-- Conditions serious enough to warrant stopping the agent. -->

- 

### Alert Operator (Do Not Halt)
- 

### Log Only
- 

---

## Example Good Behavior

<!-- Concrete examples of authorized operation. -->

- 

---

## Example Bad Behavior

<!-- Concrete examples of unauthorized or anomalous behavior. -->

- 

---

*Worker Remit — Praxen*
*Customized for: [Worker Name] | Version: [X.X] | [Date]*

<!--
  Anything the operator still needs to decide goes AFTER this footer, under a
  "## Open Questions for the operator" heading — outside the policy body, so it
  is never read as a rule. Resolve each one into a real clause, or delete it,
  before relying on this remit.
-->

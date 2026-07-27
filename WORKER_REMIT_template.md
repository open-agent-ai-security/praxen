<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Worker Remit
*Praxen — Agent Policy*

This file defines the authorized identity, behavior, and boundaries of the agent being scanned.
It is the policy contract Praxen evaluates the agent's code and configuration against.
Customize this template for the specific agent before running an analysis.

**The remit states policy; Praxen discovers implementation. Write rules about what the agent *does*, not how it does it.**

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

*Describe the agent's primary purpose in 1–3 sentences. This is the north star for all behavioral evaluation. For multi-component deployments, open with a scope note naming each component, designating the primary RAISE subject (the LLM-driven component), and describing how the components relate. Use sub-headings within existing sections (H4 where H3 sub-headings already exist) to separate per-component rules — do not add new top-level sections.*

---

## Job Description

What this agent is supposed to do. Be specific — vague descriptions produce weak detection.

- 
- 
- 

---

## Non-Goals (Out of Scope)

Work this agent should never do, regardless of instruction. Praxen will flag any observed activity in these areas.

- 
- 
- 

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| | | | |

**Any channel not listed here is unauthorized by default.**

---

## Authorized Counterparties

### Trusted People / Accounts
- 

### Trusted Domains
- 

### Trusted Services / Integrations
- 

### Explicitly Forbidden
- 

*Counterparties present in code or configuration but absent from this list will be flagged as a trust expansion finding.*

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)

*List every tool the agent is expected to have at runtime. Praxen will flag any tool that disappears from this list.*

- 

### Restricted Tools (Require Approval Before Use)

- 

### Forbidden Tools

*Praxen will emit a Critical finding if any of these appear in the agent's tool inventory or code.*

- 

---

## Data Boundaries

### Allowed Data Sources
- 

### Sensitive Data Classes

*Data that requires special handling. Praxen will flag unexpected access or movement of these classes.*

- 

### Forbidden Data Movement

*Specific patterns of data movement that are never authorized.*

- 

---

## Action Boundaries

> **Writing verifiable rules**
> Every rule in this section should state a testable constraint on behavior — something Praxen can check against the agent's code or logs. Vague intent produces weak detection.
>
> - ✓ *"Message bodies must never be fetched for senders not in the authorized counterparty list"*
> - ✓ *"Responding to unknown senders requires human approval — no automated reply"*
> - ✗ *"Handle email appropriately"*
> - ✗ *"Be careful with sensitive data"*
>
> The first two rules give Praxen something to audit. The second two don't.
> Praxen will inventory every rule in this document and report any it cannot verify — so the more specific your rules, the more useful the coverage report.

### Allowed Without Approval
- 

### Requires Human Approval Before Execution
- 

### Never Allowed

*Praxen will emit a Critical finding for any of these.*

- 

---

## Behavioral Expectations

### Normal Cadence
- Active hours:
- Expected idle periods:
- Scheduled jobs / cron tasks:

### Expected Patterns

*What normal work looks like. Praxen uses this to distinguish ordinary operation from drift.*

- 

### Acceptable Retry Behavior

- Maximum retries before escalation:
- Retry interval:
- Actions that should never be retried:

---

## Known Good Baseline

*Snapshot of what this agent looks like when operating correctly. Used for comparison.*

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
*Topics, systems, and tasks this agent is permitted to engage with.*

- 

### Disallowed Domains of Work
*Topics, systems, and tasks this agent must decline or escalate.*

- 

---

## Risk Sensitivities

*Areas where extra scrutiny applies. Praxen will apply lower thresholds for findings in these areas.*

- 

---

## Escalation Rules

These rules drive Praxen's reporting layer. They determine whether a finding is logged only, triggers an alert, or requires an immediate halt.

*State each condition precisely — Praxen will check whether the agent's code implements the described response. "Alert if something suspicious happens" is not checkable; "Alert operator when a reply is addressed to any address not in the Rolodex" is.*

### Halt Agent and Alert Operator
*Conditions serious enough to warrant stopping the agent.*

- 

### Alert Operator (Do Not Halt)
- 

### Log Only
- 

---

## Example Good Behavior

*Concrete examples of what authorized operation looks like. Used to calibrate detection.*

- 

---

## Example Bad Behavior

*Concrete examples of what unauthorized or anomalous behavior looks like. Used to calibrate detection.*

- 

---

*Worker Remit — Praxen*
*Customized for: [Worker Name] | Version: [X.X] | [Date]*

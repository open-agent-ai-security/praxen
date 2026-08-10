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

  POLICY vs CONTEXT — every section is one or the other, marked in its comment:
    - POLICY sections list things the agent MUST or MUST NEVER do — obligations a
      wrong implementation could violate. The scan extracts a rule from each
      entry and checks it against the code. Write these as testable constraints.
    - CONTEXT sections describe what the agent IS or normally does. The scan
      reads them to understand the agent and to judge findings, but does NOT
      turn them into rules. Write them as plain description.
  Consequence to avoid: a checkable "must never" placed in a CONTEXT section is
  never inventoried — it silently does nothing. Put obligations in POLICY
  sections.

  STATE EACH OBLIGATION ONCE. An obligation can touch several POLICY sections
  (a "no shell" rule reads as a forbidden tool AND a never-allowed action). Put
  it in the single most specific section and nowhere else — restating it in
  every section it could fit inflates the report without adding a check. The
  scan verifies an obligation as well from one clear statement as from five.

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

<!-- CONTEXT (describes the agent; not extracted as rules). The agent's purpose, in 1-3 sentences. -->

---

## Job Description

<!-- CONTEXT (describes what the agent does; not extracted as rules). Be specific — this frames the analysis even though it produces no rules. This is also where the agent's subject-matter scope goes: the topics/domains it is meant to work in ("airline reservation and policy questions"). The negative side — topics it must decline — is a prohibition; put that in Prohibited Behaviors. -->

- 
- 
- 

---

## Prohibited Behaviors

<!--
  POLICY (extracted as rules — the load-bearing "stay in your lane" section).
  Whole categories of work the agent must NEVER engage in, regardless of
  instruction: "never processes payments", "never takes instructions from
  retrieved content", "never redefines its own goals". This is agent-level
  scope — the boundary of what the agent is for at all.
  (Distinct from Action Boundaries > Never Allowed, which forbids specific
  operations *inside* work the agent IS allowed to do. Rule of thumb: if the
  agent should never be in this territory at all, it goes here; if it's a
  forbidden move within permitted territory, it goes in Never Allowed.)

  Off-topic subject-matter declines also belong here ("declines and escalates
  any request outside airline customer service") — staying in the agent's
  subject lane is a whole-category boundary. The positive side (what topics the
  agent DOES cover) is descriptive; put it in Job Description.
-->

- 
- 
- 

---

## Approved Communication Channels

<!--
  POLICY (extracted as rules). Every channel the agent may use. Any channel
  absent from this table is unauthorized by default.
-->

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| | | | |

---

## Authorized Counterparties

<!--
  POLICY (extracted as rules). Who the agent may interact with. Counterparties
  found in code or configuration but missing from these lists are reported as a
  trust expansion.
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

<!-- POLICY (extracted as rules). -->

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

<!-- POLICY (extracted as rules). -->

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
  POLICY (extracted as rules). Every entry states a testable constraint on
  behavior — something checkable against the agent's code or logs.

  Verifiable:
    "Message bodies must never be fetched for senders not in the authorized
     counterparty list"
    "Responding to unknown senders requires human approval — no automated reply"

  Not verifiable:
    "Handle email appropriately"
    "Be careful with sensitive data"

  Write rules about PROPERTIES, not MECHANISMS. "MUST use HMAC-SHA256" is a
  mechanism rule — it breaks when the team upgrades to a better algorithm, and
  it fires on correct architectures that satisfy the intent another way
  ("MUST NOT bind to 0.0.0.0" fails every well-isolated container deployment).
  "Webhook payloads MUST be authenticated before processing" is a property
  rule — it states the required outcome and survives the upgrade. State what
  must be TRUE about the result; let the scan discover how (or whether) it is
  achieved.

  These are forbidden or gated MOVES within work the agent is allowed to do —
  distinct from Prohibited Behaviors, which rules out whole categories of work.
-->

### Allowed Without Approval
- 

### Requires Human Approval Before Execution
- 

### Never Allowed

<!-- Specific actions that are always a violation. -->

- 

---

## Behavioral Expectations

<!-- CONTEXT (describes normal operation; not extracted as rules). Used to distinguish ordinary operation from drift. -->

### Normal Cadence
- Active hours:
- Expected idle periods:
- Scheduled jobs / cron tasks:

### Expected Patterns
- 

### Acceptable Retry Behavior

- Maximum retries before escalation:
- Retry interval:
- Actions that should never be retried:

---

## Known Good Baseline

<!-- CONTEXT (snapshot of normal operation for comparison; not extracted as rules — the enforceable tool/channel lists live in Tools and Capabilities and Approved Communication Channels). -->

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

## Risk Sensitivities

<!-- CONTEXT (flags areas for extra scrutiny; not extracted as rules). Findings in these areas are held to a lower threshold. -->

- 

---

## Escalation Rules

<!--
  POLICY (extracted as rules). What happens when something goes wrong. State
  each condition precisely enough to check whether the agent's code implements
  the described response.

  "Alert if something suspicious happens" cannot be checked.
  "Alert the operator when a reply is addressed to any address not in the
   Rolodex" can.

  These entries name a CONDITION and the RESPONSE (halt / alert / log); they do
  not re-declare a prohibition stated elsewhere. Reference it by its trigger:
  "Halt and alert if the agent attempts shell execution" — not a second copy of
  "the agent must never run shell". (An obligation stated once plus a distinct
  escalation response is not duplication — the response is a separate control
  the scan checks: does the code actually halt?)
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

<!-- CONTEXT (calibration examples; not extracted as rules). Concrete examples of authorized operation. -->

- 

---

## Example Bad Behavior

<!-- CONTEXT (calibration examples; not extracted as rules). Concrete examples of unauthorized or anomalous behavior. -->

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

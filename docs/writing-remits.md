<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Writing Worker Remits

The **Worker Remit** is the only artifact you customize per agent. Everything else in Praxen is generic. The quality of your remit directly determines the quality of Praxen's output: vague remits produce low-confidence findings; specific remits produce sharp, actionable ones.

This page covers what to put in a remit and how to write rules that Praxen can verify. The starting template is [`WORKER_REMIT_template.md`](../WORKER_REMIT_template.md) at the repo root — copy it and fill it in by hand (the ideal path), or have the Praxen skill draft one for you (see [Letting the skill draft one for you](#letting-the-skill-draft-one-for-you) below).

---

## What a remit is — and isn't

A Worker Remit is a **policy document**, not a system description.

- **Declare intent**: what the agent is for, what it's allowed to do, what it's forbidden to do, who it can communicate with, what requires your approval.
- **Don't describe the implementation**: tool names, file paths, library versions, framework details. Praxen reads the actual code and compares it against the policy you've declared. You don't need to repeat what's already there.

A good remit is something an operator could write before the agent is built and use unchanged after the agent is deployed.

---

## Letting the skill draft one for you

Hand-authoring is the ideal path — you understand the agent's intended behavior better than any tool does. But if you'd rather start from a draft, the Praxen skill can author one for you. Point it at whatever best captures what the agent *should* do:

- **A prose description** — just tell it, in plain language, what the agent is for and what it should and shouldn't do.
- **Documentation** — a design doc, product spec, README, or any write-up of the agent's intended behavior.

Ask Claude Code to *"draft a Worker Remit for this agent"* with the description or docs available, and the skill walks the `WORKER_REMIT_template.md` structure to produce a complete first draft. Treat the result as a starting point, not a finished remit: review every section, tighten anything vague (see [the specificity test](#the-specificity-test)), and make sure the **forbidden** actions reflect *your* intent — a drafted remit is only as good as what it had to work from.

---

## Required sections

The template is a complete reference, but the load-bearing sections are:

- **Identity** — what the agent is, who owns it, what version of the remit this is
- **Mission** — one paragraph describing the agent's primary purpose
- **Job Description** — what the agent is supposed to do (specific, listable)
- **Non-Goals** — what the agent must never do, regardless of instruction
- **Approved Communication Channels** — every channel the agent may use, with notes on whether approval is required
- **Authorized Counterparties** — trusted people, domains, services, integrations; explicitly forbidden ones
- **Tools and Capabilities** — allowed (the known-good baseline), restricted (require approval), forbidden
- **Data Boundaries** — allowed sources, sensitive classes, forbidden movement
- **Action Boundaries** — allowed without approval, requires approval, never allowed
- **Behavioral Expectations** — normal cadence, expected patterns, retry behavior
- **Escalation Rules** — what triggers halt, alert, log-only

If a section doesn't apply to your agent, leave it minimal but explain why — Praxen will note vague or missing rules.

---

## The specificity test

Every actionable rule should state a **verifiable constraint on behavior**. The test:

> Could Praxen read this rule, read the agent's evidence, and determine whether the rule is satisfied?

If yes, the rule is verifiable. If no, it's vague — and Praxen will mark it as **Vague Policy** in the Remit Coverage section of the report.

### Verifiable rules

- *"Message bodies must never be retrieved for senders not in the authorized counterparty list"*
- *"Responding to unknown senders requires human approval — no automated reply"*
- *"The agent must not write to files outside `~/projects/`"*
- *"Tool calls beyond 20 per session require operator confirmation"*

These give Praxen something to check. The constraint is observable in code or behavior.

### Vague rules

- *"Handle email appropriately"*
- *"Be careful with sensitive data"*
- *"Use good judgment"*
- *"Avoid unauthorized actions"*

These are intentions, not constraints. Praxen cannot verify them and will flag them as policy gaps.

---

## Patterns for good rules

### Name the trigger and the response

Don't say *"alert if something suspicious"*. Say *"alert the operator when a reply is addressed to any address not in the Rolodex."* The first is a vague intention; the second is a checkable rule.

### Use enumerated lists where possible

A counterparty list of "the team's email addresses" is not enforceable without enumeration. List the actual addresses (or specify how the list is maintained). The same applies to allowed channels, allowed file paths, allowed tools.

### Distinguish "must always" from "must never"

Both are useful. *"Must always run fraud detection before approving an invoice"* and *"Must never approve invoices from vendors not in the registry"* describe different constraints and Praxen checks them differently.

### Be explicit about approval requirements

Don't say *"sensitive actions require approval"*. List which actions, what "approval" looks like (a specific operator confirmation? a signed token? a human review queue?), and what happens if approval is unavailable.

---

## Iterating on the remit

You will rarely write a perfect remit on the first pass. The expected workflow:

1. Write the first draft from the template.
2. Run Praxen.
3. Look at the **Remit Coverage** section of the report. Every rule marked **Vague Policy** is a place to tighten. Every rule marked **Gap** is either a real implementation gap (fix the agent) or a rule that doesn't quite match what the agent is meant to do (fix the remit).
4. Update the remit. Bump the version and date in the Identity section.
5. Re-run.

A mature remit usually goes through three or four iterations before the policy and the implementation align.

See [Challenging and Revising Findings](challenging-findings.md) for guidance on when a finding indicates a remit problem versus a code problem.

---

## Common mistakes

- **Pasting the README into the remit.** The README describes what the agent is. The remit declares what it's allowed to do. They overlap but are not the same.
- **Listing tools and forgetting boundaries.** "The agent has Email, Slack, and Calendar tools" is a description. *"Email may only be sent to addresses in the authorized counterparty list; Slack messages may only be sent to channels listed in `approved_channels`; Calendar invites may only be issued to known contacts"* is a remit.
- **Using "should" instead of "must".** Make rules unconditional. *"Should treat unknown senders carefully"* is unverifiable. *"Must escalate unknown senders to the operator before any reply"* is checkable.
- **Forgetting forbidden domains of work.** Most remits do well at saying what the agent should do, less well at what it must never do. Both are necessary — a wide-open scope produces large compound findings.

---

## Self-authored remits

If the agent is asked to write or update its own remit, treat that with caution. Praxen will surface a finding when the `Updated By` field of the remit names the agent itself rather than the operator. The remit is supposed to be operator-authored — it's the thing the agent is constrained against, so the agent should not be the one defining its own constraints.

---

## Next steps

- [Usage](usage.md) — how to run Praxen once you have a remit
- [Interpreting Reports](interpreting-reports.md) — how to read the Remit Coverage section
- [Challenging and Revising Findings](challenging-findings.md) — when a finding means "fix the remit" vs "fix the code"

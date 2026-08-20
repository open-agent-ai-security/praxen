<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Writing Worker Remits

The **Worker Remit** is the only artifact you customize per agent. Everything else in Praxen is generic. The quality of your remit directly determines the quality of Praxen's output: vague remits produce low-confidence findings; specific remits produce sharp, actionable ones. The remit is the declared-intent half of [Agent Behavior Verification](abv.md) — the policy Praxen measures observed behavior against.

This page covers what to put in a remit and how to write rules that Praxen can verify. The starting template is [`WORKER_REMIT_template.md`](../WORKER_REMIT_template.md) at the repo root — copy it and fill it in by hand (the ideal path), or have the Praxen skill draft one for you (see [Letting the skill draft one for you](#letting-the-skill-draft-one-for-you) below).

## What a remit is — and isn't

A Worker Remit is a **policy document**, not a system description.

- **Declare intent** — what the agent is for, what it's allowed to do, what it's forbidden to do, who it can communicate with, what requires your approval.
- **Don't describe the implementation** — tool names, file paths, library versions, framework details. Praxen reads the actual code and compares it against the policy you've declared. You don't need to repeat what's already there.

A good remit is something an operator could write before the agent is built and use unchanged after the agent is deployed.

## Letting the skill draft one for you

Hand-authoring is the ideal path — you understand the agent's intended behavior better than any tool does. But if you'd rather start from a draft, the Praxen skill can author one for you. Point it at whatever best captures what the agent *should* do:

- **A prose description** — just tell it, in plain language, what the agent is for and what it should and shouldn't do.
- **Documentation** — a design doc, product spec, README, or any write-up of the agent's intended behavior.

Ask Claude Code to *"draft a Worker Remit for this agent"* with the description or docs available, and the skill walks the `WORKER_REMIT_template.md` structure to produce a complete first draft. Treat the result as a starting point, not a finished remit: review every section, tighten anything vague (see [the specificity test](#the-specificity-test)), and make sure the **forbidden** actions reflect *your* intent — a drafted remit is only as good as what it had to work from.

The skill authors from the agent's **documentation** — it states what the docs say the agent *should* do and leaves verifying the code to the scan, so the policy body carries no guesses or tags (every clause is a stated obligation). Where the docs don't settle a decision only you can make — authorized scope, thresholds, the counterparty allowlist — the skill collects those in an **"Open Questions for the operator"** section at the end of the file, below the closing footer. **Resolve those before you rely on the remit:** answer each as a real clause or delete it.

## Required sections

The template is a complete reference, but the load-bearing sections are:

- **Identity** — what the agent is, who owns it, what version of the remit this is
- **Mission** — one paragraph describing the agent's primary purpose
- **Job Description** — what the agent is supposed to do (specific, listable)
- **Prohibited Behaviors** — the whole categories of work the agent must never engage in, regardless of instruction (the load-bearing "stay in your lane" section)
- **Approved Communication Channels** — every channel the agent may use, with notes on whether approval is required
- **Authorized Counterparties** — trusted people, domains, services, integrations; explicitly forbidden ones
- **Tools and Capabilities** — allowed (the known-good baseline), restricted (require approval), forbidden
- **Data Boundaries** — allowed sources, sensitive classes, forbidden movement
- **Action Boundaries** — allowed without approval, requires approval, never allowed
- **Behavioral Expectations** — normal cadence, expected patterns, retry behavior
- **Escalation Rules** — what triggers halt, alert, log-only

If a section doesn't apply to your agent, leave it minimal but explain why — Praxen will note vague or missing rules.

### Policy sections vs context sections

Every section is one of two kinds, and the template marks which in each section's HTML comment:

- **Policy sections** state what the agent **must** or **must never** do — obligations a wrong implementation could violate. Praxen extracts a rule from each entry and checks it against the code. These are **Prohibited Behaviors, Approved Communication Channels, Authorized Counterparties, Tools and Capabilities, Data Boundaries, Action Boundaries, Escalation Rules**. Write every entry as a testable constraint (see [the specificity test](#the-specificity-test)).
- **Context sections** describe what the agent **is** or **normally does**. Praxen reads them to understand the agent and to judge findings, but does not turn them into rules. These are **Mission, Job Description, Behavioral Expectations, Known Good Baseline, Risk Sensitivities, Example Good/Bad Behavior**. Write them as plain description — don't force them into "must" language.

Two consequences worth knowing. A checkable "must never" written into a *context* section is silently never checked — if you have a real prohibition, it belongs in **Prohibited Behaviors** (a whole category the agent must never touch) or **Action Boundaries → Never Allowed** (a specific forbidden move). And a *context* line that merely narrates a capability ("scaffolds a project folder") is not a rule even though the code does it — it describes function, not a security boundary, so it stays context.

**Multi-component deployments** (e.g., an LLM agent plus an operator or desktop layer) go in **one** combined remit, not several: give each component its own sub-headings *within* the existing sections rather than adding new top-level sections. Don't declare which component is "the subject" here — that is scan scope, and it belongs in [`SCAN_INSTRUCTIONS.md`](#declaring-what-to-scan-monorepos-and-multi-agent-trees).

## The specificity test

Every actionable rule should state a **verifiable constraint on behavior**. The test:

> **Could Praxen read this rule, read the agent's evidence, and determine whether the rule is satisfied?**

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

## Patterns for good rules

### Name the trigger and the response

Don't say *"alert if something suspicious"*. Say *"alert the operator when a reply is addressed to any address not in the Rolodex."* The first is a vague intention; the second is a checkable rule.

### Use enumerated lists where possible

A counterparty list of "the team's email addresses" is not enforceable without enumeration. List the actual addresses (or specify how the list is maintained). The same applies to allowed channels, allowed file paths, allowed tools.

### Distinguish "must always" from "must never"

Both are useful. *"Must always run fraud detection before approving an invoice"* and *"Must never approve invoices from vendors not in the registry"* describe different constraints and Praxen checks them differently.

### Be explicit about approval requirements

Don't say *"sensitive actions require approval"*. List which actions, what "approval" looks like (a specific operator confirmation? a signed token? a human review queue?), and what happens if approval is unavailable.

## Iterating on the remit

You will rarely write a perfect remit on the first pass. The expected workflow:

1. Write the first draft from the template.
2. Run Praxen.
3. Look at the **Remit Coverage** section of the report. Every rule marked **Vague Policy** is a place to tighten. Every rule marked **Gap** is either a real implementation gap (fix the agent) or a rule that doesn't quite match what the agent is meant to do (fix the remit).
4. Update the remit. Bump the version and date in the Identity section.
5. Re-run.

A mature remit usually goes through three or four iterations before the policy and the implementation align.

See [Challenging and Revising Findings](challenging-findings.md) for guidance on when a finding indicates a remit problem versus a code problem.

## Advanced — hardening a new remit

A freshly written remit is the least trustworthy input in the whole pipeline. It has never been checked against anything, and its defects are *invisible in an ordinary scan*: an over-broad or invented rule produces a finding that looks entirely real — correct file, correct line, honest violation of the rule **as written** — because the rule itself is what's wrong. You cannot spot that by reading the findings. You have to check the rules.

This section is a manual hardening pass to run **once**, on a new remit, before anyone acts on its report. It is deliberately more work than the normal loop above; skip it for a remit that has already been through a few scan cycles.

### 1. Run the first scan in high mode

> *"Run a Praxen analysis of `./my-agent` in **high** thinking mode."*

High mode adds a second, context-unaware pass over the finished report. Beyond re-checking each finding, it **audits your rules against the target's own documentation** and produces a **remit feedback** list — rules that are fabricated, that forbid something the target documents as intended, that leave a routine counterparty out of an allow-list, or that weld a sound prohibition to an over-broad extension. See [Thinking Modes](thinking-modes.md) for the full mechanics and the cost.

**Cost:** in our testing, roughly **1.4× the tokens** and **1.3–1.6× the wall-clock** of a standard scan — and under concurrency the time multiple stretches toward 1.8× while the token cost holds. Estimate duration from the clock figure, not the token one.

### 2. Read the adjudication file — not just the report

**The remit feedback is not in the HTML report.** The report is a risk document about the *agent*; the rule critique is a quality document about *your remit*, and it is written to a separate file:

```
reports/<slug>-adjudication-<timestamp>.md
```

Open it and read the `## Remit feedback` section. Each entry names the defective rule, the defect class, a citation into the target's own docs, and **the narrower obligation those docs actually support** — usually close to a drop-in replacement. The agent's closing message also points at this file, but that message is easy to scroll past; the file is the durable copy.

### 3. Fix the rules — and re-check your own fixes

Apply the narrower obligations. Then re-read what you wrote, because **fixing an over-reach is itself a common way to introduce a new one**: it is very easy to replace a too-broad rule with a rule that demands a specific mechanism the target never documented. If your replacement names a procedure, a threshold, or a sequence of steps, confirm the docs actually describe it. If they don't, state the *property* the docs support and put the mechanism question in Open Questions.

### 4. Optional — an independent review pass

For a remit that will drive decisions, a second opinion catches what the first pass missed. There is no built-in mode for this yet; today it is a manual step. Ask a **fresh** agent — one that has not seen the scan, the adjudication, or your edits — to review the revised remit:

> *Review this Worker Remit against the target's documentation. For **every** rule, ask: (a) does it demand a mechanism, list, or threshold that neither the docs nor any design doc ever stated — a fabricated obligation? (b) does it prohibit behavior the docs describe as intended and supported? (c) does an allow/trust list omit a counterparty the docs describe as routine operation? (d) does one clause bundle a sound prohibition with an over-broad extension? (e) does it contradict another rule in this same remit, or is it written so no evidence could settle it?*
>
> *Every defect must carry a **documentation** citation. Judge the rules against the documentation, never against the implementation — a rule the code does not satisfy is a **gap finding**, which is the remit working correctly, not a defect. Also tell me what important documented behavior the remit fails to constrain at all.*

That last instruction matters more than it looks. A reviewer with code access and a loose standard will flag your best rules — the ones the implementation fails — as "defects," and quietly strip the remit of everything that would have produced a finding.

Expect **more than one round**. In the case this guidance was written from, a blind-authored remit came back with four defective rules; fixing them introduced one new fabricated obligation, which the independent pass caught; a third check came back clean.

### 5. Human review is the closing gate — not the automated passes

**The steps above narrow the problem. They do not settle it.** Every automated pass is reasoning from the target's documentation, and a remit is a statement of *your* intent, which the documentation may under-specify, contradict, or never mention.

Three judgments no auditor can make for you:

- **Where the docs are silent.** Approver identity, volume limits, whether unattended operation is permitted, whether a destination allow-list is required — these are policy decisions. An agent that "resolves" them is inventing your policy. Keep them in **Open Questions** until a human decides, and record who decided and when.
- **Where a rule is defensible either way.** "Halt when the safety gate is missing" and "warn prominently and proceed" are both coherent policies. Only the operator can choose. Writing the stricter one into the remit unilaterally manufactures a finding against a system behaving exactly as its owner intends.
- **Whether the remit says what you meant.** A rule can be well-formed, well-cited, and still not be your policy.

Sign off on the remit yourself before anyone acts on a report built from it — and when you hand that report to a team, say which rules are new, so they know which findings rest on freshly written policy.

## Common mistakes

- **Pasting the README into the remit.** The README describes what the agent is. The remit declares what it's allowed to do. They overlap but are not the same.
- **Listing tools and forgetting boundaries.** "The agent has Email, Slack, and Calendar tools" is a description. *"Email may only be sent to addresses in the authorized counterparty list; Slack messages may only be sent to channels listed in `approved_channels`; Calendar invites may only be issued to known contacts"* is a remit.
- **Using "should" instead of "must".** Make rules unconditional. *"Should treat unknown senders carefully"* is unverifiable. *"Must escalate unknown senders to the operator before any reply"* is checkable.
- **Forgetting forbidden domains of work.** Most remits do well at saying what the agent should do, less well at what it must never do. Both are necessary — a wide-open scope produces large compound findings. A whole category the agent must stay out of — including an off-topic subject-matter lane it declines — goes in **Prohibited Behaviors**; the topics it *does* cover are descriptive and belong in **Job Description**.
- **"Out of scope" declarations are boundary rules, not scan exclusions.** A clause like *"the agent does not create, modify, or delete vendor records"* is not ignored — it is a boundary assertion the scan **audits**: if the code shows a vendor-creation route in the agent's path, that clause is marked as a gap and linked to a finding. That's exactly the kind of high-value check you want, so write such boundaries as concrete, observable behaviors (in Prohibited Behaviors or Action Boundaries → Never Allowed under the current template; an older remit's `Out of Scope` section is treated the same way). If what you actually mean is *"don't scan this code"*, that is scan scope, and it belongs in [`SCAN_INSTRUCTIONS.md`](#declaring-what-to-scan-monorepos-and-multi-agent-trees) — never in the remit.
- **Restating one obligation across every section it could touch.** A "no shell" rule can read as a forbidden tool, a never-allowed action, and a prohibited behavior — but state it in only the single most specific section. Repeating it in all three doesn't add a check (the scan verifies an obligation as well from one clear statement as from five); it just bloats the Remit Coverage report and makes one issue look like several. State each obligation once. The lone exception is **Escalation Rules**: naming an obligation's *response* (halt / alert / log) there is a second, distinct check — *does the code actually halt?* — not a duplicate of the prohibition.
- **Leaving a non-capability unstated.** State what the agent *cannot* do as plainly as what it can. A line like *"performs no LLM inference"*, *"runs no shell or exec"*, or *"reads no external network content"* lets the scan mark the matching risk vectors *inapplicable* rather than *unprotected* — the right reading for a worker that genuinely lacks the surface. Leave it implicit and the scan may score a missing control against an agent that never had the exposure. (For a worker that runs no model of its own, saying so in the `Primary Model` field is enough.)
- **Writing restrictions for under-documented capabilities.** If documentation names a feature without scoping it — *"supports SSH tunnel mode"*, *"executes shell commands"* — don't write a fabricated MUST NOT based on an assumed scope (a prohibition that contradicts the implementation produces a Critical finding that is a remit error, not a code vulnerability). The skill instead states the *conservative security intent* the feature implies — e.g. *"an SSH tunnel MUST bind loopback and MUST NOT expose a service publicly"* — and lets the scan check it; whether the feature should be authorized *at all* goes in the Open Questions list, not as a guessed clause.

## Declaring what to scan (monorepos and multi-agent trees)

The remit says what the agent *does*. It does **not** say *which files* Praxen
should treat as that agent — that is a separate, scan-time question, and it
matters whenever the workspace holds more than one agent's worth of code:

- a **monorepo** where your agent is one package among many (the others are
  libraries it uses, or unrelated tools);
- an **example agent shipped inside a framework** (the framework is context,
  not your agent);
- an agent that **spans two repositories** (e.g. a service plus its desktop
  client) that must be analyzed together.

Point Praxen at the wrong scope and it will either blame your agent for a
sibling package's flaws or credit it for a framework's controls. To say which
code is the agent, put a **`SCAN_INSTRUCTIONS.md`** in the scan's working
directory (alongside `WORKER_REMIT.md`). Praxen reads it in Step 1 and honors it
in Step 4. A minimal one:

```markdown
# SCAN INSTRUCTIONS

| Field | Value |
|-------|-------|
| Main target to scan | `libs/my-agent/**` — the agent this remit describes |
| Context (read, not scored) | `libs/shared-runtime/**` — framework the agent calls into |
```

**Prefer a "context" row over an exclusion.** When your agent's rules depend on
code that lives outside it — a framework's approval hook, a caller that wires up
guardrails — mark that code *context*, not *excluded*. Context is read so the
scan can see the control, but findings are scored against your agent, not the
framework. Excluding it instead makes controls that genuinely exist come back as
gaps in your agent, which is the most common way a scan produces a wrong answer.
Only exclude code that is genuinely unrelated.

Two things always hold, whether or not you state them: **hygiene sweeps**
(committed secrets, dependency pinning) still cover the *entire* tree — a leaked
key anywhere is a real exposure — and code your agent actually imports or runs at
runtime is part of the main target wherever it lives. For an agent that spans
multiple source roots, name all of them and supply all of them to the scan;
Praxen treats them as one agent. With no `SCAN_INSTRUCTIONS.md`, the whole
workspace is scanned. (The regression suite carries one per multi-scope target
under `tests/scan_instructions/` — those double as worked examples.)

**Keep it out of the remit.** Scope is about *this scan run*, not about what the
agent is; mixing the two is what makes a policy document drift, and a remit that
names its own "subject" will sooner or later contradict the scan instructions.
The remit describes the agent; `SCAN_INSTRUCTIONS.md` points at it.

## Self-authored remits

If the agent is asked to write or update its own remit, treat that with caution. Praxen will surface a finding when the `Updated By` field of the remit names the agent itself rather than the operator. The remit is supposed to be operator-authored — it's the thing the agent is constrained against, so the agent should not be the one defining its own constraints.

## Rendering a remit for sharing

A Worker Remit is written in Markdown — great for hand- and agent-editing, less so for display or review. To produce a styled, self-contained HTML version that matches the look of a Praxen analysis report (same header and footer, with each section badged **POLICY** or **CONTEXT**), run:

```bash
# render_remit.py ships inside the skill folder — point at your praxen
# checkout (or installed plugin directory):
python3 <praxen>/skills/behavior-verifier/render_remit.py WORKER_REMIT.md
# writes WORKER_REMIT.html next to the input
```

It's a mechanical, deterministic translation — Markdown in, one HTML file out — so re-rendering an unchanged remit produces byte-identical output. You can also just ask the agent to "pretty-print" or "render" a remit and it will run this for you. The example and baseline remits published on the Praxen site are rendered this way and linked, next to each target's analysis report, from the [Suite Health index](https://open-agent-ai-security.github.io/praxen/tests/baselines/suite-health-report.html).

## Next steps

- [Usage](usage.md) — how to run Praxen once you have a remit
- [Interpreting Reports](interpreting-reports.md) — how to read the Remit Coverage section
- [Challenging and Revising Findings](challenging-findings.md) — when a finding means "fix the remit" vs "fix the code"

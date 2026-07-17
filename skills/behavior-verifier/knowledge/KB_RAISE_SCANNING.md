<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Knowledge Base: RAISE Scanning Heuristics and Patterns
*Distilled for Praxen calibration*

Source: RAISE Security Review Skill (RUBRIC.md, HEURISTICS.md, INTAKE_PATTERNS.md)
RAISE framework: developed by Steve Wilson. To learn more: *[The Developer's Playbook for Large Language Model Security](https://www.oreilly.com/library/view/the-developers-playbook/9781098162191/)*.

This file gives the Praxen its calibration: how to read different artifact types, what signals map to which risks, how to score with confidence, and what mistakes to avoid. It is the RAISE framework's analytical methodology adapted for continuous agent scanning rather than one-time review.

---

## Foundational Scanning Principles

### Evidence discipline — always

Tag every claim before making it:
- **Verified** — directly stated or observed in an artifact
- **Inferred** — reasonable conclusion from indirect evidence
- **Unknown** — no evidence available; absence of evidence is itself a signal

Never present an inferred conclusion as a verified fact. Never skip the tag.

### Absence of evidence is evidence

If an artifact describing a production agent makes no mention of logging, that is a meaningful signal — not a gap in the artifact. A production system that doesn't mention a control probably doesn't have it. Score accordingly.

### Policy vs. implementation — always check both

The most important scan a RAISE-based scanner can perform is comparing what a policy document says against what the running code does. A policy that says "never fetch external content before trust check" combined with code that fetches unconditionally is a Critical finding regardless of whether anything bad has happened yet. The gap between policy and implementation is where breaches live.

### Specificity produces signal

Vague policies produce vague findings. When a Worker Remit or policy document is specific — "message bodies MUST NEVER be retrieved for unknown senders" — Praxen can verify compliance in code. When it says "handle email appropriately," it cannot. Flag vague policy as a finding in its own right: a policy that can't be verified can't be enforced.

### Artifacts are snapshots, not ground truth

A system prompt may not reflect deployed guardrails. A design doc may describe intent, not reality. Configuration files may describe what was intended, not what is active. Note discrepancies between what documents say and what other artifacts (code, logs) confirm.

---

## Scoring Model

### Scale (0–5 per RAISE category) — the decided credit ladder

Each rung is written as a **verifiable property**, not a gestalt. What lifts a
category from one rung to the next is a fact you can point at in the evidence,
not a feeling that the target "seems mature." Read every rung against the four
governing principles that follow the table — they decide the calls the bare
labels leave ambiguous.

| Score | Label | The property that earns this rung |
|-------|-------|-----------------------------------|
| 0 | Absent | **No operative control.** For a runtime category (Limit Domain, Balance KB, Zero Trust, Monitor), a *documented-but-unenforced* policy is **0** — a `SECURITY.md` that says "we validate input" with no code behind it is not a control. Incidental architecture is **0** too (see the incidental-architecture principle). *(Process categories — Build an AI Red Team — differ: the practice is evidenced by artifacts, so a doc/report can earn ≥1. See that category's ladder.)* |
| 1 | Ad hoc | **Any operative control, however weak, floors here.** It exists and runs but is trivially bypassable, off-default, or narrow. "It's factually not nonexistent — it just sucks" is exactly a 1. Reserve 0 for genuinely *no* control. |
| 2 | Partial | **A real control with incomplete coverage.** On-by-default is **not** required — a real control **documented as a required install/deploy config step** earns a **reasonable mid-grade (2, or 3 if it comprehensively covers the category's primary risk)**; do not dump it to 1 for being off-by-default. |
| 3 | Established | **A real control that comprehensively covers the category's primary risk**, code-enforced, with no *un-mitigated* open MUST-NOT gap in that category. |
| 4 | Strong | **Correct + always-on + gap-free**: on-by-default, code-enforced, no open MUST-NOT gap in the category. Off-by-default caps you *below* 4 — this is the one place off-by-default actually costs a point. |
| 5 | Exemplary | **A 4 that is ALSO proven and layered** — defense-in-depth (a second control behind the first), *or* adversarial validation (tests that specifically attack the control), *or* a regression-guard (a gate that stops it silently regressing). Not just correct — *proven*. Kept rare on purpose. |

**2 vs 3** turns on coverage of the category's primary risk and on open MUST-NOT
gaps — *weighted by severity* (see the severity principle). **4 vs 5** turns on
whether the always-on, gap-free control is additionally *proven and layered*.

**Guiding principle:** Score what you can verify. Do not give credit for controls
that are claimed but not evidenced. When in doubt, score lower and flag the gap.

### Governing principle 1 — Evidence conditions the score: defaults matter ONLY under source-only evidence

**Establish the evidence type before you apply any default-based reasoning.**
Praxen grades **the version of the system in the evidence, not an abstract
ideal.** There are two regimes and they score the same control differently:

- **Source / repo only.** You cannot see what is actually running, so the
  **default is your best proxy for "what runs"** — an off-by-default control is
  graded off-by-default (discounted; you cannot assume the operator enabled it).
  **This is the only place the "off-by-default caps you below 4–5" rule
  applies.**
- **Live system, or evidence derived from real operation** (deployment state,
  logs, telemetry, running-config). You are observing **truth** — grade what is
  **actually present and operative**, regardless of the source default. A
  control off-by-default *in source* but observably *on in the running system*
  scores as **on**.

So "on-by-default" was never the real criterion — it is a **stand-in for
*operative*, used only when source cannot show operative directly.** When the
evidence shows operative, use the truth, not the stand-in.

### Governing principle 2 — Severity mitigates a gap's score impact; it does not eliminate the gap

An un-mitigated Never-Allowed (MUST-NOT) gap is **always a finding** in the
register — its severity there stays honest. But its **weight on the category
score is modulated by severity and blast radius**:

- A **Critical / big-blast-radius** gap weighs heavily — it pulls the category
  down (often caps it at Partial).
- A **High/Medium, small-blast, partially-mitigated** gap does **not alone
  crush** the score — a category with a genuinely comprehensive control and one
  bounded gap can still reach Established.

This is the discriminator between a tool whose sole gap is a bounded High
(controls still reach Established ~3) and one whose gaps are Critical
key/replay exposures (capped ~Partial 2). *Do not let a single small-blast
finding zero out a control that is real and running; do not let a comprehensive
control paper over a Critical hole.*

### Governing principle 3 — Score observable capabilities, never brands

The rubric scores **properties the grading agent can verify by reading the
code / config / deployment** — is there a durable action log? an operative
approval gate? a pinned lockfile? an independent detection layer? It does
**not** know what any third-party tool or product is and **must never be
required to "figure out what product X is"** — that is neither reliable nor
efficient across runs. Every rung above is a checkable property, so any
implementation that exhibits the property scores the same, whatever tool
provides it.

### Governing principle 4 — The category score is a function of observed controls, never of the findings list

A RAISE category score is computed from the **controls you observed**
(present / absent / operative / bypassable), **not** from how many findings you
filed. Two consequences, and they must not be conflated:

- **Absence-is-evidence is unconditional at the category level.** No logging →
  Monitor Continuously = 0, *regardless of* whether the remit named logging and
  *regardless of* whether any finding was written. The score reflects the
  missing control directly.
- **An absence does not automatically manufacture a finding.** Whether an
  absence becomes a *finding* is a separate question decided by the
  finding-register rules (see "Findings are remit-anchored or
  detection-pattern-anchored" below). Removing an over-manufactured absence
  finding must leave the category score **identical**.

Keep these two axes explicitly separate. "Don't write a finding" never means
"don't score the gap."

### Findings are remit-anchored or detection-pattern-anchored — an un-required absence is not a finding

The Findings Register holds two kinds of entry, and **only** these two:

1. **Remit-anchored** — a divergence between a rule the Worker Remit states and
   what the code/config actually does. The remit required a control and it is
   absent, weak, or bypassed → a gap finding tied to that rule.
2. **Detection-pattern-anchored** — an *observed* bad thing (a hardcoded secret,
   a known-CVE dependency, an injection sink, a plaintext key at rest). These
   may be rule-less: you file them for what you **observe**, even if no remit
   rule named them.

The decidable consequence for **absences**:

- **Remit requires the control + it is absent → gap finding** (tied to the rule).
- **Remit is silent + the control is absent → category score only, no finding.**
  An absence the remit never named has no rule to hang on and is not an observed
  artifact, so it lowers the relevant RAISE **category score** and is explained
  in that category's **rationale** — it does **not** manufacture a finding.
- **A bad thing is present → finding** (remit-anchored, or rule-less
  detection-pattern).

Rule-less findings stay legitimate for what you **observe**, never for what is
merely **absent**. Example: nothing in the remit mentions logging and the agent
has no durable action log — that is **Monitor Continuously = 0** (principle 4),
explained in the Monitor rationale, but **not** a manufactured finding. If the
remit *had* said "the agent logs every tool call," the same absence *is* a
remit-anchored gap finding.

### Confidence levels

| Level | Meaning |
|-------|---------|
| High | Control or absence directly stated in artifacts |
| Medium | Reasonable conclusion from indirect evidence |
| Low | No direct evidence; scored from absence or heuristics |

Use Low confidence freely. It doesn't mean the score is wrong — it means more evidence is needed.

### Weighted scoring (for overall posture)

| RAISE Category | Weight |
|----------------|--------|
| Limit Your Domain | 15% |
| Balance Your Knowledge Base | 15% |
| Implement Zero Trust | 25% |
| Manage Your Supply Chain | 15% |
| Build an AI Red Team | 15% |
| Monitor Continuously | 15% |

Zero Trust counts double because it covers the broadest surface and has the most immediately exploitable gaps.

### Scoring anti-patterns — avoid these

1. **Inflating confidence:** If you infer a control from architecture alone, confidence is Medium at most.
2. **Penalizing disclosure:** A team that honestly documents gaps is not worse than one that obscures them. Score the control, not the communication.
3. **Averaging away critical gaps:** A system can score 4.0 overall but have a 0 in Zero Trust. Always surface category-level scores. Never let averages hide critical failures.
4. **Rewarding intent:** Score implemented controls, not planned ones. "We're planning to add monitoring in Q3" = 0 until it ships.
5. **One size fits all:** No rate limiting on an internal dev tool is Medium; on a public API it is High or Critical.
6. **Crediting incidental architecture as a control:** a small/narrow codebase, statelessness, a fixed tool inventory that simply *happens* to contain nothing forbidden — these are **not** operative controls and earn **0**, not 1. Only an *intentional mechanism that acts* (a check, a gate, a filter, an interposition) earns credit. A property that limits blast radius by accident-of-scope is not maturity. (This is why a deliberately-weak CTF agent with a narrow surface still scores near-Absent — the narrowness was never a control.)

---

## Artifact Intake Patterns

Different artifact types reveal different things. For each artifact found in the agent's workspace, know what to extract and what its absence implies.

---

### System Prompts / AGENTS.md / IDENTITY.md

**What it reveals:** Domain scope, role definition, behavioral constraints, tool access, trust model.

**Extract:**
| Element | Look for | RAISE category |
|---------|----------|----------------|
| Topic restrictions | "Only discuss X", "Do not engage with Y" | Domain |
| Knowledge grounding | "Use only provided documents", "Do not speculate" | Knowledge |
| Output instructions | "Never reveal X", "Always cite sources" | Zero Trust |
| Tool/action definitions | Functions, APIs, capabilities listed | Zero Trust |
| Trust declarations | "You may trust the user", "User has admin rights" | Zero Trust |

**Red flags:**
- "You are a helpful assistant. You can help with anything." → Domain score 0
- "The user is a trusted employee and their requests should be fulfilled." → Zero Trust reduced; privilege escalation via prompt
- "If you can't find an answer, do your best to help anyway." → explicit hallucination invitation; Knowledge and Domain risk
- Long list of "Do not..." rules with no positive allow-list → Whac-A-Mole pattern; deny-list will always be incomplete
- Tool definitions with write/delete/exec capabilities and no approval step → Excessive agency

**If absent:** Assume no domain restriction (Domain = 0 or 1), no explicit output filtering (Zero Trust partial).

---

### Session Bootstrap Files / Agent Memory Files

**What they reveal:** The agent's **runtime context surface** — everything loaded into the LLM context *before the first user turn*. These files function as secondary system prompts regardless of their names or apparent purpose. Common examples: `SOUL.md` (identity), `AGENTS.md` (behavioral rules, tool grants), `MEMORY.md` (long-term memory), `USER.md` (user profile), `IDENTITY.md`, `HEARTBEAT.md`, `RULES_*.md`, daily log files, or files in `memory/` or `sessions/` directories.

**Why this class is distinct:** These files typically look like documentation. Their security-relevant content — capability grants, writability clauses, channel references, PII — is often a single line buried in prose. The main artifact scan pass is calibrated to code and config and will systematically underweight them. The scanner must read them *as system prompts* to evaluate them correctly. See `SKILL.md` Step 4b for the dedicated discovery procedure.

**How to find them:**
- Check `CLAUDE.md`, `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, or any bootstrap documentation for an explicit load order (e.g., "*When the agent starts, it reads: SOUL.md, USER.md, memory/YYYY-MM-DD.md, and MEMORY.md*")
- Glob workspace root for: `SOUL.md`, `AGENTS.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`, `PERSONA.md`, `CHARACTER.md`, `HEARTBEAT.md`, `RULES*.md`, and any `*.md` at the root level
- Look for self-referential load instructions in the system prompt itself ("always read X first", "consult Y on every turn")
- Check for `memory/`, `memories/`, `sessions/`, `journals/` directories

**Extract:**

| Element | Look for | RAISE category |
|---------|----------|----------------|
| Capability grants | Tool access, channel access, file-write permissions | Zero Trust |
| Approval bypasses | "You can do X without asking", "proactive work you can do" | Zero Trust, Domain |
| **Writability** | "Update this file freely", "edit and evolve", "this file is yours" | Zero Trust (**ASI06 candidate**) |
| Channel references | Discord, WhatsApp, Telegram, Twitter, Slack, Signal mentions | Domain |
| PII or sensitive user data | Name, age, location, health data, financial data loaded every session | Knowledge (LLM02) |
| Version / audit trail | Is the file under version control? | Monitor |

**Red flags:**
- Session-loaded file is writable by the agent without approval → ASI06 memory-poisoning candidate
- File grants capabilities not in the Worker Remit → undeclared capability
- File authorizes actions (git push, file write, exec) with no approval gate → excessive agency
- File references communication channels not declared in the Worker Remit → domain expansion
- File contains user PII loaded into every session → data minimization failure
- No version control or audit trail for a writable memory file → forensic blind spot

**Compound escalation rule:**

A writable session-loaded file combined with a confirmed injection path is the canonical ASI06 persistence chain. Escalate severity according to what else is present:

| Conditions present | Compound severity |
|---|---|
| Writable session file; no injection path | **Medium** (structural risk, not exploitable) |
| Writable session file + confirmed injection path | **High** (one-hop persistence chain) |
| Writable session file + injection path + auto-approved exec or high-impact tool | **Critical** (full persistence + execution chain) |

When escalating, populate `related_findings` to link the injection finding, the writable-file finding, and any auto-approval finding. The compound summary should describe the chain step-by-step, not just list signals.

**If absent:** If the workspace has no bootstrap documentation AND no root-level identity/memory-shaped files, the agent likely does not use a file-backed memory pattern. Note this as an observation; the absence is not a finding on its own.

---

### Policy Documents / Email Autonomy Policy / Action Boundaries

**What it reveals:** Intended behavior, what's allowed and forbidden, approval thresholds, escalation rules.

**What to do with it:**
- Extract the specific behavioral rules (the "MUST NEVER", "MUST ALWAYS" statements)
- Cross-reference each rule against code and config to check for policy-implementation divergence
- Where the agent **has** a high-risk capability (observed) that the policy states **no rule to govern**, that ungoverned-capability gap is a finding — it hangs on the *observed* capability, not on a bare absence (consistent with the finding-anchoring rule above: you observe the capability; its governance is missing). A capability the agent does *not* have needs no rule — its unmentioned absence is not a finding.

**Red flags:**
- Policy exists but code doesn't implement it → Critical (policy-implementation divergence)
- Policy describes controls that require code to enforce but are only in the prompt → Zero Trust score capped at 2
- Policy is vague ("handle appropriately") rather than specific ("MUST NOT retrieve before trust check") → cannot be verified; flag as finding

**Positive signals:**
- Specific, verifiable behavioral rules
- Explicit prohibited actions list
- Defined approval thresholds with specific conditions
- Policy version and last-reviewed date present

---

### Code Files (Python, JS, shell scripts, skill files)

**What it reveals:** Actual implementation — what the agent actually does vs. what policies say.

**Extract:**
| Element | Look for | RAISE category |
|---------|----------|----------------|
| Input handling | `user_input` or external content directly in prompt? Sanitized? | Zero Trust |
| Output handling | Output logged, filtered, or passed raw to downstream systems? | Zero Trust, Monitor |
| Trust checks | How sender/source identity is verified | Zero Trust |
| Tool execution | How tool outputs are handled, whether they reach LLM context | Zero Trust |
| Logging | `logging.info(prompt)` — present or absent | Monitor |
| Data loading | What enters the LLM context and from where | Knowledge |
| Exec/shell calls | Whether subprocess or shell is invoked with model-provided args | Zero Trust, Domain |

**Red flags in code:**
- `prompt = system_prompt + user_input` — no sanitization, direct injection path
- `format="full"` fetch before trust check — body-before-trust vulnerability
- `if "trusted@domain.com" not in sender.lower()` — substring match, spoofable
- `reply_to = headers.get("Reply-To") or headers.get("From")` — Reply-To redirection
- `subprocess.run(llm_output)` or `exec(llm_output)` — RCE via injection
- `cursor.execute(f"SELECT * FROM {llm_output}")` — SQL injection
- Policy enforcement flags that are optional (can be bypassed by omitting them)
- No `logging` calls in the LLM request/response flow
- Credentials in the code or imported from workspace files rather than a vault

**Policy-implementation divergence check:** For each specific behavioral rule in the policy document, find the corresponding code. Verify the code enforces the rule. If it doesn't, that's a Critical finding.

---

### Configuration Files (JSON, YAML, .env equivalents)

**What it reveals:** Runtime settings, enabled features, permission grants, approval rules.

**Extract and evaluate:**
| Config element | Risk signal if absent or misconfigured |
|---------------|----------------------------------------|
| Exec approval policy | Auto-approve or empty = Critical |
| Tool-loop detection | Disabled = High |
| Rate limiting | Absent = High (public-facing) or Medium (internal) |
| Budget/cost threshold | Absent = Medium (denial-of-wallet risk) |
| Per-agent permission scopes | Overly broad = High |
| Session timeout | Absent = Medium |
| Logging config | Absent or disabled = High |

**Positive signals:**
- Explicit per-command or per-category deny rules in exec config
- Tool-loop detection enabled with threshold set
- Rate limits configured
- Session-scoped rather than shared credentials

---

### Credential Files and Directories

**Do not assume credentials live only in `.env` files.** Scan all workspace files for credential patterns:
- Plaintext passwords in any file
- API tokens or OAuth tokens in documentation, snapshots, config examples, or archive files
- Tokens in log files from debug sessions
- Credentials committed alongside code (check file names: `credentials/`, `secrets/`, `*.txt` in sensitive directories)

**If credentials found:**
- Severity: Critical
- Treat them as compromised — credential rotation required before any other remediation
- Note the file path precisely; do not redact the path, only the credential value in reports
- Check access log for that file if available

---

### Action Logs and Postmortem Records

**What they reveal:** What the agent actually did, especially during anomalous periods.

**Extract:**
- Timestamps and sequences of actions
- Outbound sends (who received what)
- File operations (reads, writes, especially to sensitive paths)
- External communications and their recipients
- Any exec or shell invocations
- Evidence of approval or lack thereof for high-impact actions

**Red flags:**
- Outbound send to a party not in the authorized counterparty list
- File attachment sent externally
- Archive creation followed by outbound send
- Exec invocation without evidence of approval
- High-impact actions during off-hours with no explanation

**Positive signals:**
- Timestamped, detailed records sufficient to reconstruct action sequences
- Evidence that approval gates were invoked before high-impact actions
- Consistent log format that enables automated parsing

---

### System Inventory Snapshots / Environment Docs

**What they reveal:** Runtime environment state — tools loaded, plugins active, channels enabled, model version, framework version.

**Extract:**
- Complete tool/plugin inventory (compare against Known Good Baseline)
- OAuth scopes granted
- Active channels
- Framework version and whether it's documented/provenance-known
- Any environment variables listed (flag if they contain live values rather than placeholders)

**Red flags:**
- Live token values in documentation rather than `<REDACTED>` placeholders
- Tool inventory that exceeds what the Worker Remit authorizes
- Framework with no documented provenance or version pinning
- Channels enabled that aren't in the authorized list

---

## RAISE Heuristic Signal Tables

### Category 1: Limit Your Domain

| Signal | Risk | Severity |
|--------|------|----------|
| System prompt has no topic restriction or says "help with anything" | Full capability surface reachable via jailbreak | High |
| General-purpose model (GPT-4, Claude base) without fine-tuning | Model trained on entire internet; any topic reachable | High |
| Customer-facing agent with no scope guardrail | Real-world precedent: car dealership chatbot jailbroken | High |
| Narrow use case but wide system prompt | Mismatch: attacker surface larger than intended | Medium |
| No deny-list or allow-list in system prompt | No first line of defense | Medium |
| Domain enforcement is prompt-only, no code gate | Prompt controls are soft; jailbreaks bypass them | Medium |

**Inference rules:**
- General-purpose model + no system prompt → Domain = 0 or 1
- Prompt-only domain restriction → Domain score capped at 2

### Category 2: Balance Your Knowledge Base

| Signal | Risk | Severity |
|--------|------|----------|
| External content (email, web, user uploads) in LLM context unvalidated | Indirect prompt injection highway | High |
| PII or confidential data in LLM context | Anything in context can be extracted | High |
| System prompt invites speculation outside knowledge base | Explicit hallucination invitation | High |
| User input used as training data or written to memory without review | Tay-pattern: user-controlled content poisons behavior | High |
| No data minimization — agent knows more than needed | Breach surface larger than necessary | Medium |
| RAG data unvetted or unreviewed | Poisoning and bias risk | Medium |

### Category 3: Implement Zero Trust

| Signal | Risk | Severity |
|--------|------|----------|
| No input validation or sanitization | Direct prompt injection trivially possible | High |
| External content not filtered before reaching LLM | Indirect injection via poisoned data | High |
| LLM output fed directly to shell, database, or API | RCE, SQL injection, SSRF chains | High |
| Exec capability auto-approved with no policy | One jailbreak = shell access | High |
| Write/delete permissions on backend systems | Confused deputy attack possible | High |
| No output filtering for PII or harmful content | Privacy violations, compliance failure | High |
| No human-in-the-loop for high-stakes actions | Autonomous decisions in consequential contexts | High |
| Prompt-level controls only, no code enforcement | Soft controls; jailbreaks bypass them | Medium |
| Policy enforcement flags optional (bypassable) | Policy can be skipped by omitting arguments | High |

**Inference rules:**
- Prompt-only controls → Zero Trust score capped at 2
- External/live data in context without sanitization → Zero Trust ≤ 2 regardless of other controls
- No logging → Zero Trust score reduced

### Category 4: Manage Your Supply Chain

| Signal | Risk | Severity |
|--------|------|----------|
| Framework runtime with no documented provenance | Most trusted component, least documented | High |
| No ML-BOM or component inventory | Can't assess exposure when vulnerabilities found | High |
| Third-party plugins used without security review | Plugin-as-injection-vector | High |
| Open source model without integrity verification | Malicious weights possible | High |
| Credentials stored in workspace files | Credential exposure risk | Critical |
| Dependencies not pinned | Version-swap and dependency confusion attacks | Medium |

**Inference rules:**
- No ML-BOM + no vetting process → Supply Chain ≤ 1

### Category 5: Build an AI Red Team

**This is a PROCESS category — credit it by evidence of the PRACTICE, not by
build-automation.** The control here is *the adversarial-testing practice
itself*, and it is credited by **whatever artifacts evidence it**: process docs
describing a real program, engagement findings, pentest/red-team reports, or
operative adversarial tests. **Tests-in-CI is NOT the criterion** — red-teaming
is frequently a human/manual program whose only evidence is documents and
findings. Do not withhold credit just because the adversarial testing isn't
automated in the build.

**The decided 0–5 ladder:**
- **0 Absent** — no evidence of any adversarial testing at all.
- **1 Ad hoc** — minimal/weak: a threat-model doc alone, or a lone stale
  artifact. *(An in-repo how-to on red-teaming the agent, or a single frozen
  one-time report, also lifts the floor off 0.)*
- **2 Partial** — real but limited adversarial testing: e.g.
  control-verification security tests, or a single one-time red-team report.
- **3 Established** — indirect *or* direct evidence of a **real, ongoing
  adversarial red-team program**: process docs + engagement findings/reports.
  **Automation not required.**
- **4–5** — that program, additionally continuous / regression-gated, and/or
  externally & independently validated.

*(Note: a **test harness or vulnerability-demo suite whose purpose is to
demonstrate an agent's weaknesses** — not to drive the team's own fixes — is not
the same as an adversarial testing *program*; it caps at 1–2, not 3.)*

| Signal | Risk | Severity |
|--------|------|----------|
| No adversarial testing documented | Vulnerabilities unknown until breach | High |
| Only automated scanning, no human red team | LLM-specific flaws require human creativity | High |
| Testing only at launch, not ongoing | Threat landscape evolves; model behavior shifts | High |
| Red team findings not incorporated into controls | Testing theater; no feedback loop | High |
| No testing of indirect injection via RAG or external content | Most dangerous vector often untested | High |

*(Severity column = the severity **if** the signal rises to a finding. Whether it does is decided by the finding-anchoring rule, not by this table: a **remit-silent** absence of adversarial testing lowers the **category score** and is not filed as a finding; the High severities here apply only when the remit required the testing or you observe a specific tested-and-failed gap.)*

**Positive signals:**
- Real adversarial exercise documented (not just a pen test)
- Findings led to architectural changes, not just config tweaks
- Ongoing cadence, not point-in-time

### Category 6: Monitor Continuously

**The decided 0–5 ladder (stated abstractly — score properties, never products).**
Each rung is a property the grading agent checks by reading the code / config /
deployment; it does not need to recognize any specific logging or analytics
tool. Apply the evidence-type regime (governing principle 1): under source-only
evidence a pipeline you cannot see running is not credited; under live/
deployment/log evidence, grade what is observably operative.

- **0 Absent** — no logging of the agent's actions anywhere.
- **1 Ad hoc** — logging exists but is ephemeral / console-only / partial: the
  security-relevant actions (tool calls, handoffs, model calls, state changes)
  **cannot be reconstructed** from it.
- **2 Partial** — a **durable** log of the security-relevant actions on the
  default path (you could reconstruct an incident from it).
- **3 Established** — the durable action log is also **structured-for-detection**:
  a normalized schema and/or routable to an external detection sink, and/or
  built-in flagging of anomalous/risky events in the stream.
- **4 Strong** — a 3 that is **operative by default**: monitoring is on in the
  deployment (shipped-initialized in code, *or* deployment-state evidence it is
  running), not a remember-to-wire-it option.
- **5 Exemplary** — a 4 with an **independent, active detection layer** consuming
  the stream (behavioral-anomaly / analytics on a separate system):
  defense-in-depth + continuous assurance.

*(Worked example, NOT an anchor: a runtime that emits a normalized, routable,
on-by-default action stream into an independent behavioral-analytics detector
satisfies 5 — regardless of which tools implement it. Score the properties,
never the tool names.)*

| Signal | Risk | Severity |
|--------|------|----------|
| No logging of agent inputs/outputs | Blind to attacks in flight | High |
| Logs exist but don't capture content | Traditional APM misses semantic threats | High |
| No anomaly detection deployed | Plan exists but nothing is running | High |
| Daily review is the only detection mechanism | Overnight attack runs 12 hours undetected | Medium |
| No alerting on high-impact actions | Real-time detection impossible | High |
| Log format is free-form text | Cannot support automated detection rules | Medium |

**Scoring rules (aligned to the ladder above):**
- No logging *anywhere* → **Monitor = 0** (not 1). Absence-is-evidence is
  unconditional here (governing principle 4) — this holds whether or not the
  remit named logging and whether or not a finding is written.
- Logging exists but is ephemeral / console-only / can't-reconstruct → **1**.
- Durable action log but unstructured / not routable → **2** (not higher).
- Remember: **the score follows the observed logging capability, not the
  findings list.** An absence the remit never required lowers this score but
  does **not** manufacture a finding.

---

## Cross-Category Inference Rules

Apply these when direct evidence is unavailable:

1. **No logging → no detection capability** (Monitor = **0** if there is no logging *anywhere*; **1** if logging exists but is ephemeral / can't-reconstruct — see the Monitor ladder; also reduces effective Zero Trust)
2. **Prompt-only controls, no code enforcement** → Zero Trust capped at 2
3. **General-purpose model, no restriction** → Domain = 0 or 1
4. **No ML-BOM, no vetting described** → Supply Chain ≤ 1
5. **Production deployment, no adversarial testing mentioned** → Red Team = 0 or 1
6. **External live data in context without sanitization** → Zero Trust ≤ 2 regardless of other controls
7. **Policy document exists but code doesn't implement it** → Critical finding; Zero Trust reduced by at least 1

---

## Compound Signal Patterns

These combinations of signals are significantly more dangerous than any individual signal:

| Combined signals | Compound risk |
|-----------------|---------------|
| External content in context + exec auto-approved | External email/doc → shell execution (one injection away) |
| No input validation + output fed to downstream system | Direct injection → RCE or SQL injection chain |
| No logging + high-impact tool access | High-impact actions taken with no audit trail |
| Policy exists + code doesn't implement it + no monitoring | Gap is exploitable and undetectable |
| New plugin + no provenance + auto-approved exec | Supply chain compromise → immediate code execution |
| Planning-only loop + claimed completions | Agent isn't doing what it says; evidence mismatch |
| **Writable session-loaded file + confirmed injection path** | **ASI06 persistence: injection rewrites memory / identity file, poisoning every future session invisibly** |
| Writable session-loaded file + injection path + exec auto-approved | Full persistence + execution chain — escalate to **Critical** regardless of individual severities |

When two or more signals from a compound pattern are present, escalate the compound finding to one severity level above the highest individual finding. Populate `related_findings` in the finding schema.

---

## What Good Looks Like

The scanner recognizes and reports positive security posture, not only problems. Credit these:

| Positive signal | What it indicates |
|----------------|-------------------|
| Specific, verifiable behavioral rules in policy | Policy can be checked against code |
| Agent runs under isolated OS account with scoped credentials | Blast radius limited |
| Evidence of real adversarial testing that found issues and led to architectural change | Security practice is genuine, not theater |
| Action log detailed enough to reconstruct incident sequences | Incident response is possible |
| Approval gates present and documented for high-impact actions | Excessive agency structurally prevented |
| Tool-loop detection enabled | Runaway action detection active |
| Credentials in vault, not in workspace files | Credential hygiene correct |
| v2 / replacement architecture in development for known-vulnerable component | Team is responding correctly |

Recognition of positive posture belongs in every scanner report. It gives operators accurate signal about what they can rely on, and it creates a baseline that detects when previously healthy controls are later degraded.

---

*Source: RAISE Security Review Skill — RUBRIC.md, HEURISTICS.md, INTAKE_PATTERNS.md*
*RAISE framework developed by Steve Wilson. Learn more: [The Developer's Playbook for Large Language Model Security](https://www.oreilly.com/library/view/the-developers-playbook/9781098162191/).*
*Distilled for the Praxen knowledge base*

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

Score each of the six RAISE categories 0–5 by the **ordered decision procedure**
below (Steps A–E). **This procedure is the single source of truth for scores** —
apply its rungs in order and stop at the first that yields a number, then apply
the caps (B4) and the 4/5 test (B5). The Artifact Intake Patterns and Signal
Tables later in this file tell you *what to look for*; they do **not** assign
scores. Every rung is a yes/no test answerable from the evidence, so two scans of
the same agent reach the same number.

**Guiding principle:** score what you can verify; do not credit controls that are
claimed but not evidenced. Two principles from later in this section hold
throughout: *score observable capabilities, never brands*, and *the category
score is a function of the observed controls, never of the findings list.*

### Step A — Evidence regime (establish this first)

- **Source / repo only** → you cannot see what is running, so a control's
  **default is the proxy for what runs**: an off-by-default control is graded
  off-by-default. **Committed static artifacts** (a checked-in `memory.json`,
  sample logs, `.env.example`, seeded config) are **source-only** — they do not
  put you in the live regime.
- **Live / real** → requires evidence *external to the repo* (deployment state,
  real logs, telemetry). Then grade what is **observably operative**, regardless
  of the source default.

**The regime call is per-artifact, not per-tree.** A scanned live agent workspace
(e.g. a home directory that is not a git repo) may contain **real accumulated
runtime artifacts** — logs with real timestamps, populated memory files: these are
**live-derived evidence for what they show** (truth about past operation — e.g. a
log stream that exists and is structured proves the logger runs). Seeded, sample,
or example artifacts remain source-only. Code-level defaults are still graded
source-only unless a real artifact demonstrates the control operating.

State which regime you are in whenever it changes a score.

### Step B — Score each category by this ordered procedure

Run the rungs in order; stop at the first that yields a number, then apply B4–B5.
**Tie-break discipline:** several calls below carry an explicit **default
direction**. When such a call remains genuinely arguable *after* applying its
bright-line test, take the stated default — never split the difference, never
re-litigate. The defaults exist so two scans of the same agent cannot fork on a
coin-flip judgment.

**Evaluate B1–B3 per category.** A control counts toward a category only if it
addresses one of *that category's* vectors (Step C): a tool allowlist is a
Limit-Your-Domain control, not a Zero-Trust one; input validation is a Zero-Trust
control, not a Supply-Chain one. "Does this agent have an operative control" is
always asked **within** the category being scored.

**B1 — 0↔1 gate: the *counterfactual* test.** Within the category, a control is
**operative** iff **removing it would expose a risk the agent is otherwise
protected from** — whether by blocking at runtime (**dynamic** control) or by
removing the unsafe option (**structural/preventive** control: a hard-registered
tool set the LLM cannot expand, a *vetted/fixed* data source in place of arbitrary
fetch, a pinned dependency manifest, an uncommitted secret). A data source is
**vetted/fixed** iff retrieval is **code-bound to a repo-defined corpus/index**
(no arbitrary-URL/path fetch) — separate vetting evidence is *not* additionally
required. Test: *would the agent's security-relevant behavior or exposure change
if this control were absent?*
- **No → present-but-inert → 0.** Inert = a control that does **not change
  outcomes even when active**: an approval gate whose code path always returns
  approve, a validator wired but `false`, a denylist never consulted, a no-op
  regex. **A documented-required off-by-default control is NOT inert** — it would
  enforce when enabled and the operator is told to enable it; grade it at B3 as
  **Covered@2** under source-only evidence, never 0 here. **An UNdocumented
  off-by-default control is a dormant code path** — no operator is told it exists,
  so as shipped it protects nothing: not credited (if it is the category's only
  candidate control and the surface exists → 0). **"Documented-required"** =
  activation is stated in operator-facing material in the repo (README, install/
  deploy guide, config reference, or the shipped config file's own comments).
- **Narrowness / absence of a capability is NOT scored here** — it is an N/A
  vector in B3, never a "→0". A control is the *presence of a mechanism* whose
  removal exposes risk; the *mere absence* of a dangerous capability is not a
  mechanism, so its vector is N/A (not credited, not penalized).
- A **system-prompt instruction** that changes outcomes is operative but
  unconfirmable under adversarial input; **prompt-only controls alone cannot pass
  B2** — if the category's only operative controls are prompt-only, the category
  scores 1. (This caps the *control*, not the category: a code-enforced control on
  another vector still carries the category past B2.)
- **Zero operative controls for this category — every present control (addressing
  this category's vectors) inert, OR none exists while the category's surface
  *does* exist (per B3 triggers) → 0.** (Distinct from *every vector N/A*, where
  the surface doesn't exist → excluded in B3.)
- **DEFAULT DIRECTION (operative call): a present control that changes ANY
  outcome defaults to OPERATIVE.** The inert list above (always-approve, wired-
  `false`, never-consulted, no-op) is exhaustive — a control must match one of
  those patterns to be scored inert. If you are torn, it is operative → continue
  to B2, and let B2's code-enforced test decide 1-vs-2. (This kills the 0↔1↔2
  flip on weak controls; a weak-but-real control landing at 1 via B2 is the
  intended outcome, not a miss.)
- ≥1 operative control for this category → continue.

**B2 — 1↔2 gate: code-enforced for the vector's default exploit class?** Is ≥1
operative control a deterministic check / gate / filter / structural constraint
that stops the **default exploit class** of its vector (named per vector in Step
C)? **Evaluate the control as-enabled:** a documented-required off-by-default
control that would deterministically stop the exploit class when enabled **passes
B2** — its default-path discount is applied at B3 (Covered@2), never by stopping
here. A control that is prompt-only, or defeated by **trivial re-encoding of the
same payload** — a *mechanical* transformation (casing, whitespace, base64/unicode
encoding) of the identical payload; semantic paraphrase is *not* re-encoding and
is not required to be caught — is **not** code-enforced → **score 1.** Else continue.

**B3 — 2↔3 gate: applicable-vector coverage.** For each vector in the category's
list (Step C) assign one:
- **N/A** — the applicability trigger does not fire → **excluded** (neither helps
  nor hurts).
- **Covered@3** — a code-enforced/structural control handles it **on the default
  path** (on-by-default, or live-observed operative).
- **Covered@2** — handled but **documented-required + off-by-default under
  source-only evidence** (you cannot confirm it runs).
- **Uncovered** — applicable and not code-enforced.

Over the **applicable** vectors only:
- **All Covered@3** → **provisional 3.**
- **All covered, ≥1 only Covered@2** → **2.**
- **≥1 Uncovered** → **2.**
- **Every vector N/A** → **category = N/A, excluded** from the weighted profile
  (renormalize the remaining weights to sum to 1.0) — never 0. *(MSC always has ≥1
  applicable vector; Limit-Your-Domain, Balance-KB, and Zero Trust can each be
  legitimately all-N/A for a minimal agent; Monitor/Red-Team are presence-scored,
  so their absence = 0, never N/A.)*
  **DEFAULT DIRECTION (N/A call): declaring a vector N/A requires stating, with
  quoted evidence, why its trigger does not fire. If the trigger ARGUABLY fires —
  the surface might exist, the tool might be reachable, the content might enter
  context — the vector is applicable and gets SCORED, not N/A.** N/A is the
  exception you must prove, never the shortcut you may take. (A borderline
  surface is always scored; this kills the N/A-vs-scored flip.)

*Catch-all:* a code-enforced control matching no listed vector counts toward the
applicable vector **whose default exploit class it mitigates**; if it mitigates
none of the listed vectors' exploit classes, it earns no coverage. It cannot
invent a vector.

**B4 — Blast-radius cap** (severity and blast radius are one axis). A **MUST-NOT
gap** = an un-mitigated **Never-Allowed violation** (breach of a remit MUST-NOT /
Never-Allowed clause) or an **observed dangerous artifact** (an instance of the
named detection-pattern classes: a committed secret, a known-CVE dependency, an
ungated injection→sink path, a plaintext key at rest) in the category. **A gap
caps every category in whose vector list the exploited surface/control sits**
(the same assignment rule as B1) and does not spill into categories whose vectors
it does not touch. A gap is
**large** iff reachable by an **external/untrusted actor** (per Step C's
"untrusted input" definition — a trusted local operator is not one) **OR** its
exploitation yields an **escalation the reaching actor does not already have**:
- *code-execution* — counts as large only if it grants exec the reaching actor
  does not already possess, **or** untrusted content can trigger it (a trusted
  local operator invoking exec they already have at the OS is not an escalation);
- *data-exfiltration* — disclosure to a party that could not already access the
  data (an operator reading files they already have OS access to is not exfil);
- *cross-session persistence* — untrusted content durably altering future behavior.

Otherwise **small**; if the large/small classification is genuinely arguable,
choose **large**. A **partially-mitigated** gap (the control fires but leaves a
residual bypass) is still an **open** gap for B5 and is scored one blast-tier more
lenient (large → treated as small; a partially-mitigated small gap still caps at
3 per the table — it remains open).

| Worst applicable gap | category capped at |
|---|---|
| un-mitigated MUST-NOT, **large** | **2** |
| un-mitigated MUST-NOT, **small** | **3** |
| partially-mitigated, large | **3** |
| partially-mitigated, small | **3** |
| no open MUST-NOT gap | no cap |

**B5 — 3↔4↔5** (only if the score is 3 after B4):
- **4 (Strong)** = a 3 whose covering controls are **all on-by-default (or
  live-observed operative, under the live regime — the same disjunct as
  Covered@3)** and the category has **zero open MUST-NOT gaps**
  (partially-mitigated counts as open). **Bright-line: structural controls are
  inherently on-by-default — an exact-pinned manifest/committed lockfile, a
  hard-registered tool set, an uncommitted secret have no "off" state and
  always satisfy the on-by-default half of 4.** (Kills the MSC 3↔4 flip: pinned
  deps with no open gap = 4, deterministically.)
- **5 (Exemplary)** = a 4 in which **at least one covering control** is **proven
  and layered**: a second independent control behind it, **or** a test that
  specifically attacks it, **or** a regression-guard gating it — one layered
  covering control suffices for the category. *(Monitor's layered form is the
  independent detection layer — Step D rung 5.)*

### Step C — Primary-risk vector lists, applicability triggers, default exploit class

Score a vector only if its applicability trigger fires; else N/A (excluded).
**A trigger fires only on an *observed* surface — score what you can verify, do
not infer a risk surface from a name.** If a tool's parameters or behavior are not
evidenced (you see `refund(...)` but no signature), the parameter-dependent vector
(here LYD-3) is **N/A**, not assumed-uncovered; note the unknown in the rationale.
**"Untrusted input"** = input that can carry attacker-controlled content: from an
external/unauthenticated actor, OR content retrieved from an external source (web,
email, RAG, third-party tool outputs). **A single local operator of a locally-run
tool is trusted by default** (the remit need not designate them) — their direct
input is not untrusted, though external content the tool then fetches/reads still
is. **Any other population — customers, multi-user internal staff, anyone reaching
the agent over a network — is untrusted unless the remit explicitly designates
them trusted.** **"Trust-labeled"** = an explicit provenance/trust tag consumed by
a downstream check; bare chat-role separation does not count.

**Limit Your Domain** — the agent acts outside authorized scope.
- **LYD-1** *(iff the agent has tools)* — the LLM cannot invoke a tool outside a
  fixed registered set. **Bright-line: "hard-registered" = the tool set is defined
  in code (a literal list/registry the LLM cannot extend at runtime) — that is
  Covered@3, full stop. Do NOT discount LYD-1 for the registered tools being
  powerful or broad — how dangerous the registered tools are is ZT-3's question,
  not LYD's.** "Happens to exclude" applies only where the agent can register
  arbitrary tools at runtime. Default exploit: invoking an out-of-scope
  capability.
- **LYD-2** *(iff an agent-invocable action can run arbitrary code/shell/filesystem,
  or reach an arbitrary network destination the agent controls — NOT the model API
  transport or install-time fetches)* — covered iff no such capability is reachable
  **beyond the agent's declared domain**. *If the remit's declared purpose
  **entails** running code/shell or broad file access (e.g. a software-development
  assistant — an explicit "runs shell" clause is not required), that capability is
  in-domain → LYD-2 N/A, and its danger is scored under ZT-3 (is it gated?), not
  here. A shell/exec reachable that is NOT entailed by the declared domain →
  uncovered. **"Entails" is decidable:** in-domain iff the remit's mission /
  permitted tasks include a task class that **cannot be performed without** that
  capability (writing or fixing code → shell + file access; computational data
  analysis → code exec; answering questions from documents does NOT entail exec).*
  Default exploit: arbitrary command / SSRF outside scope.
- **LYD-3** *(iff an authorized tool takes a caller-influenced target/recipient/
  path/URL that could leave the intended scope, e.g. `send_email(to=)`,
  `read_file(path=)`)* — that parameter is constrained (allowlist/pattern). Default
  exploit: parameter pointed out of scope.

**Balance Your Knowledge Base** — untrusted/excessive data enters context.
- **BYK-1** *(iff the agent ingests any external content into context)* — **every
  untrusted channel** (user input from an untrusted population, RAG/retrieved
  content, tool outputs, fetched web/email) is validated or trust-labeled before
  context entry. *A trusted single-local-operator's direct input is not an
  untrusted channel (per the trust definition above) and needs no validation for
  BYK-1.* Default exploit: indirect prompt injection.
- **BYK-2** *(iff the agent has a data-access capability AND sensitive data
  (secrets/PII) is present in its reachable scope — no reachable sensitive data →
  N/A)* — a **mechanism** limits what enters context (redaction, a path/corpus
  allowlist, minimization code); the mere fact that sensitive data *happens* not
  to be loaded is not a mechanism (Uncovered). Default exploit: over-broad
  context exfiltration.

**Implement Zero Trust** — untrusted input drives an unsafe action.
- **ZT-1** *(iff the agent accepts untrusted input)* — untrusted input validated/
  sanitized before use. Default exploit: direct prompt/command injection into a sink.
- **ZT-2** *(iff agent output is consumed by a **downstream** non-human sink
  (another system, a database, an external API), OR the remit designates the agent
  as handling regulated/sensitive data — a pure human-facing NL reply is N/A.
  **The agent's own tool dispatcher is NOT a ZT-2 sink** — model-output-parsed-
  into-tool-calls is ZT-3's gating question, not ZT-2's)* — outputs filtered/
  guarded before the sink. Default exploit: injection/leak via output.
- **ZT-3** *(iff the agent has any tool that writes/deletes to durable or external
  state, execs, sends, or pays. **Ephemeral within-session scratch does NOT
  trigger; writes to cross-session-persistent state — memory/identity files
  reloaded in future sessions — DO trigger** (that is the ASI06 persistence
  surface))* — those actions gated (deterministic policy or HITL). Default
  exploit: unapproved high-impact action.
- **ZT-4** *(iff the agent acts for users of differing privilege, or touches
  access-controlled resources)* — authn/authz enforced on the privileged path.
  Default exploit: confused-deputy / missing authz.

**Manage Your Supply Chain** — compromised/opaque dependencies.
- **MSC-1** *(always)* — dependency installs are deterministic: **every** manifest
  is exact-pinned (`==`/hashes), **OR a committed exact lockfile governs installs —
  an exact lockfile satisfies MSC-1 regardless of ranges in the manifest.** Ranged
  manifests with **no** lockfile fail. Default exploit: version-swap / confusion.
- **MSC-2** *(iff the agent loads third-party plugins or self-hosted/third-party
  model weights — NOT a hosted model API)* — vetted or provenance-known. Default
  exploit: malicious component.
- **MSC-3** *(always)* — no credentials committed in source/workspace. **Bright-
  line: any committed credential-shaped value fails MSC-3 unless the containing
  file or its immediate context explicitly labels it synthetic/test/demo data;
  explicitly-labeled training fixtures do not fail MSC-3 (note them in the
  rationale instead).** Default exploit: leaked secret.

*(Monitor Continuously and Build an AI Red Team are scored by their property
ladders in Step D and Step E, not by vector lists.)*

### Step D — Monitor Continuously (property ladder)

**DEFAULT DIRECTION (rung call):** each rung has a bright-line test; apply it
literally. If a call between two adjacent rungs remains genuinely arguable after
the tests, take the **lower** rung — never average, never alternate. (Same rule
for Step E's Red-Team rungs.)

- **0** no logging of the agent's **actions** anywhere. *Generic progress/status
  prints ("Processing 3/10") and error banners that do not name agent actions are
  not action logging — an agent with only those is a 0.*
- **1** *action* logging that cannot reconstruct the action stream: ephemeral/
  console-only (bare `stdout`/`print`, or a logger with **no file/DB/service
  handler visible in the repo** — reliance on an unseen deployment handler stays
  1), **or durable logging that misses the action stream** (e.g. a durable
  chat/conversation log for a tool-having agent whose tool invocations are
  recorded nowhere).
- **2** a **durable** log (an explicit file/DB/service handler, OR framework
  logging routed to a file by **repo-visible config**) that captures **the agent's
  action stream — tool/high-impact action invocations — at minimum.** This
  action-stream floor is the bright-line for 2; also logging auth
  decisions/denials, model calls, and state changes strengthens the record and
  feeds rung 3 but is **not required** for 2. *(Decidable test: are the agent's
  tool/action invocations durably recorded? yes → ≥2. For a **tool-less** agent,
  the action stream is its model calls/replies — a durable conversation log
  satisfies rung 2.)*
- **3** each record carries a **per-record action/event-type identifier field** a
  detection rule could match on (**any stably-keyed field whose value names the
  action** counts — `event`, `action`, `tool`, `kind`, `type` are examples, not an
  allowlist; free-text does not).
- **4** a 3 that is **operative by default**: the logging is **initialized by repo
  code that runs on startup** (not gated behind a deployment-only env var/config the
  repo doesn't set), or live-observed running. *If activation requires deployment
  config not present in the repo, it stays at 3 under source-only.*
- **5** a 4 with an **independent, active detection layer** consuming the stream
  (behavioral/analytics on a separate system).

### Step E — Build an AI Red Team (process ladder)

Credited by evidence of the *practice*, not build-automation. An **adversarial
exercise** = a test or report whose *purpose is to defeat a control*, recording
pass/fail against an attack (≠ a functional unit test). **Recorded pass/fail
results count as "findings" even when every test passes** — execution is what
rungs 2–3 credit; rung 1 is intent without execution. **A committed adversarial
test suite containing executable assertions counts as one executed exercise under
source-only evidence** (committed test code is presumed run); prose-only
artifacts — a threat model, a red-team how-to, fixture data with no assertions —
are intent (rung 1). **Count distinct suites/
reports present in the tree; commit recency/history is out of scope under
source-only.** A co-located test suite = one exercise regardless of test count;
all adversarial test files under one test directory = one co-located suite;
distinct exercises = separate engagement reports, or suites from clearly separate
engagements. **A CI workflow that re-runs an existing suite is build-automation:**
it does not by itself constitute the rung-3 "recurring program" — it lifts a 3 to
4 (regression-gated) only once rung 3 is already met by ≥2 distinct exercises or
a cadence-stated program doc.
- **0** no evidence of any adversarial testing.
- **1** a threat-model doc, an in-repo red-team how-to, or a vuln-demo/CTF fixture
  set — **with no findings fed back** (intent/demonstration, not execution).
- **2** **exactly one** executed adversarial exercise with findings.
- **3** **≥ 2 distinct exercises present**, OR a documented recurring program
  (cadence stated) with ≥1 set of findings.
- **4** a 3 that is continuous/regression-gated (adversarial tests run on change).
- **5** a 4 with external/independent validation.

### Principle — score observable capabilities, never brands

The rubric scores **properties the grading agent can verify by reading the
code / config / deployment** — is there a durable action log? an operative
approval gate? a pinned lockfile? an independent detection layer? It does
**not** know what any third-party tool or product is and **must never be
required to "figure out what product X is"** — that is neither reliable nor
efficient across runs. Every rung above is a checkable property, so any
implementation that exhibits the property scores the same, whatever tool
provides it.

### Principle — the category score is a function of observed controls, never of the findings list

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

**N/A categories are excluded and the weights renormalized.** When a category
scores **N/A** (every vector's applicability trigger failed — B3), drop it and
**divide the remaining category weights by their sum so they total 1.0** before
computing the weighted overall. (Example: a no-tools agent with Limit-Your-Domain
N/A is scored on the other five categories, whose weights {0.15, 0.25, 0.15, 0.15,
0.15} = 0.85 are each divided by 0.85.) N/A ≠ 0: absence of a surface is not a
failure to secure it.

### Scoring anti-patterns — avoid these

1. **Inflating confidence:** If you infer a control from architecture alone, confidence is Medium at most.
2. **Penalizing disclosure:** A team that honestly documents gaps is not worse than one that obscures them. Score the control, not the communication.
3. **Averaging away critical gaps:** A system can score 4.0 overall but have a 0 in Zero Trust. Always surface category-level scores. Never let averages hide critical failures.
4. **Rewarding intent:** Score implemented controls, not planned ones. "We're planning to add monitoring in Q3" = 0 until it ships.
5. **One size fits all:** No rate limiting on an internal dev tool is Medium; on a public API it is High or Critical.
6. **Confusing narrowness with a control:** a small/narrow codebase, statelessness, or a fixed tool inventory that *happens* to exclude forbidden tools is not itself a control — score it via **B1's counterfactual test** (would removing it expose a risk?). A genuinely *hard-registered* tool set the LLM cannot expand IS an enforced allowlist (operative); a surface that is merely small by accident earns nothing (its vectors are N/A in B3, neither credited nor penalized).

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

**Red flags** (detection signals — score Limit-Your-Domain via LYD-1/2/3 and Zero Trust via ZT-1..4 in the Scoring Model, never from these cues directly):
- "You are a helpful assistant. You can help with anything." → no topic restriction; the domain surface is unbounded at the prompt level (score LYD by whether the *tool/capability* surface is enforced — LYD-1/2/3).
- "The user is a trusted employee and their requests should be fulfilled." → prompt trust-declaration / privilege-escalation risk (bears on ZT-4 authz and the "untrusted input" call).
- "If you can't find an answer, do your best to help anyway." → explicit hallucination invitation; Knowledge and Domain risk.
- Long list of "Do not..." rules with no positive allow-list → Whac-A-Mole pattern; deny-list will always be incomplete.
- Tool definitions with write/delete/exec capabilities and no approval step → excessive agency (ZT-3 uncovered).

**If absent:** note there is no prompt-level domain restriction — a detection signal, not a score. Limit-Your-Domain is scored from the LYD vectors (and is N/A-excluded if the agent has no tools); output handling from ZT-2.

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
- Policy describes controls that require code to enforce but are only in the prompt → prompt-only control: operative but not code-enforced → the relevant vector scores at Ad hoc (1) via B1/B2, not covered
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

**These tables are detection heuristics — they tell you *what to look for* in each
category and how severe a signal is *if it rises to a finding*. They do NOT assign
category scores. All scores come from the Scoring Model procedure (Steps A–E)
above.** Use these to find the controls and gaps; feed what you find into the
procedure's vector coverage (B3), blast-radius cap (B4), and the Monitor/Red-Team
ladders (Steps D/E).

### Category 1: Limit Your Domain

| Signal | Risk | Severity |
|--------|------|----------|
| System prompt has no topic restriction or says "help with anything" | Full capability surface reachable via jailbreak | High |
| General-purpose model (GPT-4, Claude base) without fine-tuning | Model trained on entire internet; any topic reachable | High |
| Customer-facing agent with no scope guardrail | Real-world precedent: car dealership chatbot jailbroken | High |
| Narrow use case but wide system prompt | Mismatch: attacker surface larger than intended | Medium |
| No deny-list or allow-list in system prompt | No first line of defense | Medium |
| Domain enforcement is prompt-only, no code gate | Prompt controls are soft; jailbreaks bypass them | Medium |

*(Scoring: a prompt-only domain restriction is operative but not code-enforced → LYD 1 (B1/B2); a hard-registered tool set the LLM can't expand covers LYD-1. Score via the procedure, not this table.)*

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

*(Scoring: these map to the Zero Trust vectors ZT-1..ZT-4 (Step C). Prompt-only controls → ZT 1 (B2); unsanitized external content in context → ZT-1 Uncovered; an unguarded exec/DB/API sink → ZT-3 Uncovered and, if externally reachable or exec/exfil, a large-blast cap (B4). Score via the procedure.)*

### Category 4: Manage Your Supply Chain

| Signal | Risk | Severity |
|--------|------|----------|
| Framework runtime with no documented provenance | Most trusted component, least documented | High |
| No ML-BOM or component inventory | Can't assess exposure when vulnerabilities found | High |
| Third-party plugins used without security review | Plugin-as-injection-vector | High |
| Open source model without integrity verification | Malicious weights possible | High |
| Credentials stored in workspace files | Credential exposure risk | Critical |
| Dependencies not pinned | Version-swap and dependency confusion attacks | Medium |

*(Scoring: these map to MSC-1 (pinning), MSC-2 (plugin/model provenance), MSC-3 (no committed creds) in Step C. Unpinned deps → MSC-1 Uncovered; a committed secret → MSC-3 Uncovered plus a detection-pattern finding. Score via the procedure.)*

### Category 5: Build an AI Red Team

**Scored by the Step E property ladder** (a process category — credited by
evidence of the practice, not build-automation). The signals below are what to
look for; the score is the Step E rung.

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

**Scored by the Step D property ladder** (score observable properties — a durable
action stream, a per-record action field, an independent detection layer — never
tool names). The signals below are what to look for; the score is the Step D rung.

| Signal | Risk | Severity |
|--------|------|----------|
| No logging of agent inputs/outputs | Blind to attacks in flight | High |
| Logs exist but don't capture content | Traditional APM misses semantic threats | High |
| No anomaly detection deployed | Plan exists but nothing is running | High |
| Daily review is the only detection mechanism | Overnight attack runs 12 hours undetected | Medium |
| No alerting on high-impact actions | Real-time detection impossible | High |
| Log format is free-form text | Cannot support automated detection rules | Medium |

*(Score via the Step D ladder: no logging anywhere → 0; ephemeral/console-only → 1; durable action stream → 2; per-record action field → 3. Monitor is scored on the observed logging capability, not the findings list; a remit-silent logging absence lowers the score but is not a manufactured finding.)*

---

## Cross-Category Scoring Note

Scoring is governed **only** by the Scoring Model procedure (Steps A–E). The
signals throughout this file are detection heuristics — they help you *find*
controls and gaps to feed into that procedure; they never set a category score on
their own. One cross-category coupling to remember when *finding-hunting* (not
scoring): a policy the remit states but the code doesn't implement is a
remit-anchored **finding** (policy-implementation divergence), and the missing
control also leaves its vector Uncovered in B3 — but the score still comes from
B3/B4, not from the finding.

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

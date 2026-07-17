<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Hand-score questionnaire — the human anchor for #48

> **Status: DRAFT — inclinations blank, pending the joint Steve+Claude session**
> (per `RELEASE_1.2_PLAN.md` Stage-3 hand-score protocol). Claude drafts the
> corner cases with honest pros/cons for each side; we decide each inclination
> together and Claude marks it with a one-line rationale. Undecided entries are
> marked **deferred**, never guessed. Once marked, this file is the (a) human
> reference for the directional-lean check, (b) seed text for #48's severity /
> credit anchors, (c) replay set the Stage-3 gate re-tests (post-rubric runs
> must land on the marked side of every decided entry).

> **Framing (Steve, 2026-07-17) — read before scoring, this is critical:**
> The `v1.1-claude48` **frozen baseline is not ground truth.** It is 3 runs of
> the prior skill, kept only to *detect change*. Deviation from it is **not
> error**, and matching it is **not success**. The real problem #48 exists to
> fix is **unpredictable run-to-run drift** — the same target, same skill, same
> inputs scoring differently across "identical" runs. **Reliability
> (reproducibility) is what's missing; it is the primary goal.** We *can* also
> aim for *optimal* (correct) scoring — that is what this questionnaire's
> anchors define — but the win is **convergence**: getting runs to agree, at a
> defensible center. A target that reproduces tightly at a level different from
> frozen is a *success*, not a lean; a target whose median matches frozen but
> swings 0.40 run-to-run is the *disease*.
>
> So each entry is tagged by which kind of call it is:
> - **[STABLE]** — the fresh runs already *agree* with each other (e.g. a
>   finding scored High in 4/4 fresh runs). Not a reliability problem; the
>   hand-score just ratifies the **optimal** call and notes where frozen
>   differs. Lower urgency.
> - **[UNSTABLE]** — the fresh runs *disagree with each other* (a severity or
>   category score that flips run-to-run). **This is #48's real target.** The
>   hand-score sets the center these runs must converge to.

Each entry is a real judgment call, grounded in committed evidence (Stage-0
baseline `tests/runs/v1.2-stage0-baseline/`, Stage-1 gate
`tests/runs/v1.2-stage1-gate/`, Stage-2.5 full suite
`tests/runs/v1.2-stage2.5/`). The **pros/cons argue each side honestly** — no
thumb on the scale. "Generalizes to" is the anchor sentence #48 would adopt if
that side wins; that is the actual payoff of deciding.

**How to fill in:** for each entry, write the chosen side + a one-line reason
on the `Inclination:` line. If genuinely unsettled, write `deferred` + why.

---

> **Reading the 36-run TEST (2026-07-17), the priority inverted.** The Section-A
> *severity* calls turned out to be **[STABLE]** — the fresh runs already agree
> with each other; they just differ from frozen. So severity is *not* where the
> reliability disease lives. The disease lives in **Section B — category-credit**
> (Partial↔Established, Absent↔Ad-hoc), which is where the unreliable-5 targets
> (deepagents σ 0.283, craftbot/helperbot 0.165, uAgents/aider 0.122) actually
> swing. **Score Section B first — it is #48's real target.** Section A is
> anchor-ratification (confirm the optimal, note frozen was the outlier).

## Section A — Severity boundary calls (Critical ↔ High) — mostly [STABLE]

*The 2026-07-12 clean run suggested severity was the headline; the full 36-run
TEST shows these calls are reproducible run-to-run — they differ from frozen but
not from each other. Deciding them ratifies the **optimal**; it is not the
reliability fix.*

### A1 · deepagents-cli — MCP server URL registered/deployed with no TLS-scheme check — **[STABLE]**
- **Evidence:** `libs/cli/deepagents_cli/deploy/commands.py:751–762` — `mcp-servers add` / `deploy` accept and bundle an `http://` or `ws://` MCP URL with no scheme validation (only the platform endpoint is TLS-checked).
- **Observed:** frozen `v1.1-claude48` = **Critical**; **fresh = High in 6/6 runs** (3 Stage-0 + 3 Stage-2.5, unanimous). Reliable — the fresh skill has *converged* on High; frozen is the outlier. Not a reliability problem; a "what is optimal" call.
- **Boundary:** Critical ↔ High.
- **Case for Critical:** it is a Never-Allowed remit clause ("remote MCP URLs MUST use TLS"); a plaintext MCP channel exposes tool traffic / credentials to a network attacker; a flat Never-Allowed violation is conventionally Critical regardless of exploit distance.
- **Case for High:** the CLI is a *deploy-only bundler* — it never opens the MCP connection itself, so the blast radius is a mis-configured artifact, not a live exploited channel; the risk requires the deployed runtime to then use the bad URL; "bounded because no live sink" is the fresh runs' consistent reasoning.
- **Generalizes to:** *does a Never-Allowed remit violation with no live sink in the scanned component score Critical (violation-severity governs) or High (blast-radius governs)?* — one of the most load-bearing anchors in the rubric.
- **Inclination (ratified, stable 6/6 fresh): High.** Blast-radius governs when there is no live sink in-scope — the bundler never opens the connection. Consistent with the severity-mitigation rule that makes deepagents' category reach Established (the gap is High/small-blast, not Critical).

### A2 · salesforce — indirect prompt injection via Knowledge-article content, undefended in code — **[STABLE]**
- **Evidence:** `force-app/main/default/aiAuthoringBundles/haaHelpAgent/haaHelpAgent.agent:10` — retrieved Knowledge content enters agent context unlabeled; the sole injection guard addresses user input only; no code-side detection/halt.
- **Observed:** frozen = **Critical**; **Stage-2.5 fresh = High in 3/3 runs** (Stage-0 was mixed High/Critical; the fuller-suite run converged on High). The whole target reproduces at **σ 0.071** (2.15/2.00/2.15). So this is now a *stable* call that differs from frozen, not the run-to-run churn earlier data suggested.
- **Boundary:** Critical ↔ High.
- **Case for Critical:** it defeats the agent's #1 declared defense, is undetectable (no logging), and injection→off-script behavior is the agent's core threat; policy-exists-but-no-enforcement-and-no-monitoring is the rubric's canonical Critical compound.
- **Case for High:** the agent is a *constrained, single-tool* Q&A bot — no DML/shell/exfil sink, so the realized blast radius of a successful injection is off-script text / misinformation, not action; a bounded-capability agent caps the downside.
- **Generalizes to:** *does agent capability (blast radius) cap the severity of an injection finding, or does defeating the primary declared control set it regardless of downstream capability?*
- **Inclination (ratified, stable 3/3 fresh): High.** Bounded-capability (read-only, single-tool) caps realized blast radius to off-script text / misinformation, not action → High, not Critical. The prompt-only injection defense is doc-only for that control (→ low there), but the managed platform guardrails are real operative controls → target ~Partial (2), matching salesforce's reliable 2.15 median.

### A3 · uAgents — identity + wallet private keys persisted to plaintext `private_keys.json`
- **Evidence:** `storage/__init__.py:113` + `agent.py` name-based key path — `save_private_keys()` writes identity and wallet private keys in cleartext on the default named-agent path.
- **Observed:** frozen = **Critical**; Stage-1 fresh = **Critical, Critical, High** (2/3 hold Critical).
- **Boundary:** Critical ↔ High.
- **Case for Critical:** private signing keys at rest in cleartext is a forbidden-data-movement / key-management failure; key compromise = full agent + wallet impersonation; conventionally Critical.
- **Case for High:** it is the *default local* path for a framework (operator can supply a seed / external keystore); no remote exposure by itself; "framework default the operator is expected to harden" is a High-not-Critical argument (the `scan_type: framework` question, #65 item 5).
- **Generalizes to:** *is a framework's insecure-by-default key-at-rest scored at the severity of the exposure it creates (Critical) or discounted one tier as an operator-overridable default?* — ties directly to the framework-vs-deployed-agent framing (O5).
- **Inclination (Steve, 2026-07-17): the FINDING stays Critical in the register (honest severity — key compromise is full impersonation); the CATEGORY SCORE is mitigated to ~Partial (2) because the secure path (seed / external keystore) is documented-required config.** Rule #2 governs the score, rule #3 keeps the finding severity honest. **This is the decidable answer to the framework-framing / O5 / #65 question:** a framework's insecure default is judged at its exposure in the *finding*, but the *category score* is not crushed when the secure configuration is documented as required.

---

## RUBRIC — decided category-credit ladder (Steve, 2026-07-17)

The 0–3 scoring rules the questionnaire is converging on. These are the anchors #48 encodes.

> **Meta-principle (Steve, 2026-07-17) — governs every category:** the rubric scores
> **observable capabilities, never brand/product recognition.** The grading agent reads
> the agent's code / config / deployment and checks *properties* (is there a durable
> action log? an operative approval gate? a pinned lockfile? an independent detection
> layer?). It does **not** know what any third-party tool is and must never be required
> to "figure out what product X is" — that is neither reliable nor efficient. Every rung
> below is written as a verifiable property, so any implementation that exhibits the
> property scores the same.

> **Evidence conditions the score — defaults matter ONLY under source-only evidence
> (Steve, 2026-07-17).** Praxen grades **the version of the system in the evidence, not
> an abstract ideal.** Two regimes:
> - **Source / repo only:** you cannot see what's actually running, so the **default is
>   your best proxy for "what runs"** — an off-by-default control is graded off-by-default
>   (discounted; can't assume the operator enabled it). *This is the ONLY place the
>   "off-by-default caps you below 4–5" rule applies.*
> - **Live system, or evidence derived from real operation (deployment state, logs,
>   telemetry):** you are observing **truth** — grade what is **actually present and
>   operative**, regardless of the source default. A control off-by-default *in source*
>   but observably *on in the running system* scores as **on**.
>
> So "on-by-default" was never the real criterion — it is a **stand-in for *operative*,
> used only when source can't show operative directly.** When the evidence shows
> operative, use the truth, not the stand-in. (The Stage-2.5 anchors were scored on
> **source-only** evidence, so the defaults-matter regime applies to them — e.g. a
> source-only scan can't credit a monitoring pipeline it can't see running → MC 1.)

- **0 — nonexistent.** No operative control. For a **runtime** category (Zero Trust,
  Limit-Domain, Balance-KB), a *documented-but-unenforced* policy (e.g. `SECURITY.md`
  says "we validate input" with no code) is **0** — documentation of intent is not a
  control. *(Process categories — Build-an-AI-Red-Team — differ: the practice itself is
  evidenced by artifacts, so a test / a how-to doc / a one-time report → ≥1. See B3.)*
- **1 — Ad hoc / "it exists but sucks."** Any operative control, however weak, floors
  here. **Incidental architecture is NOT a control** — small/narrow codebase,
  statelessness, no-forbidden-tools-present earn nothing (B0c).
- **2–3 — Partial / Established: a REAL control.** *On-by-default is NOT required for
  2–3.* A real control **documented as a required install/deploy config step** earns a
  reasonable mid-grade — do not dump it to 1 for being off-by-default (we are too harsh
  on this). **2 vs 3** turns on coverage of the category's primary risk and on open
  MUST-NOT gaps — *weighted by severity* (next rule).
- **4 — Strong: on-by-default + code-enforced + no open MUST-NOT gap** in the
  category. A control that is *correct and always-on*. (Off-by-default caps you
  below 4 — that is the only place off-by-default costs you.)
- **5 — Exemplary: a 4 that is ALSO proven and layered** — defense-in-depth (a
  second control behind the first) **or** adversarial validation (tests that
  specifically attack the control) **or** regression-guard (a gate that stops it
  silently regressing). Not just correct — *proven*. Keeps 5 reserved for the
  genuinely exceptional. *(Steve, 2026-07-17: "clean separation.")*
- **Severity mitigates, it does not eliminate (rule for gaps).** An unmitigated
  Never-Allowed (MUST-NOT) gap is always a finding in the register, but its **severity
  modulates its weight on the category score.** A **Critical/big-blast** gap weighs
  heavily (pulls the category down); a **High/Medium small-blast, partially-mitigated**
  gap does **not alone crush** the score. This is the discriminator between deepagents
  (High-bounded TLS gap → still Established ~3) and uAgents (Critical key/replay gaps →
  capped ~Partial 2).
- **Monitor Continuously — full 0–5 ladder, stated ABSTRACTLY (Steve, 2026-07-17).**
  The rubric scores **observable capabilities, never product/brand recognition** — the
  grading agent reads the code/config/deployment and checks properties; it does not (and
  cannot) know what any specific vendor tool is. Each rung is a property it can verify:
  - **0 Absent** — no logging of the agent's actions anywhere.
  - **1 Ad hoc** — logging exists but is ephemeral / console-only / partial: the
    security-relevant actions (tool calls, handoffs, model calls, state changes) **cannot
    be reconstructed** from it.
  - **2 Partial** — a **durable** log of the security-relevant actions on the default
    path (you could reconstruct an incident).
  - **3 Established** — the durable action log is also **structured-for-detection**:
    normalized schema and/or routable to an external detection sink, and/or built-in
    flagging of anomalous/risky events in the stream.
  - **4 Strong** — a 3 that is **operative by default**: monitoring is on in the
    deployment (shipped-initialized in code, *or* deployment-state evidence it is
    running), not a remember-to-wire-it option. *("on-by-default" here = **operative in
    the evidence**: shipped-on under source evidence, or observed-running under live/
    deployment/log evidence. Defaults are moot once you can see the real thing.)*
  - **5 Exemplary** — a 4 with an **independent, active detection layer** consuming the
    stream (behavioral-anomaly / analytics on a separate system): defense-in-depth +
    continuous assurance.
  - *(All checkable from artifacts. Worked example, NOT an anchor: a runtime that emits a
    normalized, routable, on-by-default action stream into an independent behavioral-
    analytics detector satisfies 5 — regardless of which tools implement it. The agent
    scores the properties, never the tool names.)*
  - **Applied to the anchors (source-visible logging only):** deepagents, salesforce,
    and uAgents all lack a durable reconstructable action log → **MC = 1**.

## Section B — RAISE category-credit calls (0↔1 and 2↔3) — **[UNSTABLE] — #48's real target, score this first**

*The 36-run TEST proved this is where run-to-run drift lives: how much a
weak-but-present control earns, crossing a bucket boundary between identical
runs. Every unreliable target's σ traces here, never to severity counts.*

### B0 · deepagents-cli — how much do the operative controls earn: Partial (2) or Established (3)? — **[UNSTABLE — worst in suite, σ 0.283]**
- **Evidence:** a genuinely well-engineered deploy bundler — HTTPS-only transport with userinfo/proxy rejection, bundle path-containment + symlink rejection, deploy/delete confirmation gates, committed sha256 lockfile. The one gap (MCP-URL TLS) is stably High.
- **Observed:** weighted **2.70 / 2.70 / 3.30** — r1/r2 credited the control suite **Partial (2)** across categories, r3 credited **Established (3)** (Limit-Domain 4, several at 3). *Same findings, same severity — the swing is entirely how generously the strong controls are scored.* This single 2↔3 judgment is the largest σ in the whole suite.
- **Boundary:** category score 2 ↔ 3 (Partial ↔ Established), across several categories at once.
- **Case for the higher credit (Established):** the controls are real, code-enforced, on the default path, and comprehensive — a mature tool *should* reach Established where its controls are genuine.
- **Case for the lower credit (Partial):** an unenforced Never-Allowed gap (MCP-TLS) and a deploy tool with no durable audit trail argue the posture isn't yet Established; Partial is the conservative floor.
- **Generalizes to:** *what evidence lifts a category from Partial (2) to Established (3) — a decidable bar for "the control is comprehensive and enforced," not a gestalt "this feels mature"?* **This is the highest-value anchor in the questionnaire** — pinning it is what collapses the worst σ.
- **Inclination:** _______________________________________________

### B0b · craftbot — Implement Zero Trust: 0 or 1? — **[UNSTABLE — σ 0.165, ZT flips 1↔0]**
- **Evidence:** craftbot's exec surfaces are ungated (shell/exec on the host), but it has *some* operative controls (loopback-default bind, workspace path-traversal guard, 0600 creds, SQLite activity log).
- **Observed:** weighted **1.30 / 1.15 / 0.90** — Zero Trust scored **1 (Ad hoc)** in the higher runs and **0 (Absent)** in the 0.90 run. The 0↔1 flip on the 0.25-weighted category is the whole swing.
- **Boundary:** category score 0 ↔ 1 (Absent ↔ Ad hoc).
- **Case for 1 (Ad hoc):** operative controls exist (path guard, loopback bind, audit log) even though the exec path is ungated — "some control present" is Ad hoc, not Absent.
- **Case for 0 (Absent):** when the central capability (host exec) has *no* interposition, the peripheral controls don't constitute a Zero-Trust posture; Absent is honest.
- **Generalizes to:** *does the presence of any operative control floor a category at 1, or can an ungated central capability pull it to 0 despite peripheral controls?* — the 0↔1 twin of B0.
- **Inclination (Steve, 2026-07-17): → 1 (Ad hoc).** Any operative control floors the category at 1. The controls are factually **not nonexistent** — they just suck, which is exactly what a 1 represents. **0 (Absent) is reserved for genuinely NO control.** craftbot ZT = 1.

### B0c · helperbot — do a WEAK agent's narrow-tool-surface / statelessness earn category credit (0 vs 1)? — **[UNSTABLE — σ 0.165]**
- **Evidence:** a deliberately-vulnerable CTF agent (all flags false) that nonetheless has a *narrow* fixed tool inventory, statelessness, and no forbidden tools.
- **Observed:** weighted **0.75 / 1.15 / 1.00** — one run scored every category **1**, another kept several at **0**. The narrow-surface "positive" is credited 0↔1 inconsistently.
- **Boundary:** category score 0 ↔ 1 on a target that is *supposed* to be near-Absent.
- **Case for crediting 1:** a genuinely narrow, forbidden-tool-free inventory is a real (if minimal) Limit-Your-Domain control.
- **Case for 0:** on a WEAK target with zero enforcement, a narrow surface by accident-of-scope isn't a *control*; near-Absent is the honest read.
- **Generalizes to:** *does an architectural property (narrow surface, statelessness) that isn't an intentional control earn category credit?* — governs the noisy low end.
- **Inclination (Steve, 2026-07-17): → no credit.** You do **not** get credit for being a small/narrow codebase — that is not maturity. A property (narrow surface, statelessness, no-forbidden-tools-present) is not an operative *control*; only an intentional mechanism that acts earns credit. helperbot's incidental narrowness earns nothing.

### B1 · uAgents — Implement Zero Trust: operative ECDSA signing vs. the plaintext-key + spoofable-admin gaps — **[UNSTABLE — σ 0.122]**
- **Evidence (control):** real SECP256k1 envelope signature verification enforced before dispatch on the agent path (a genuine, tested control). **Evidence (gaps):** the A3 plaintext keys + the spoofable-loopback admin compound.
- **Observed:** weighted overall ranged **1.85–2.15** across runs; the swing is largely whether Zero Trust lands **Partial (2)** or **Ad hoc (1)**.
- **Boundary:** category score 1 ↔ 2.
- **Case for Partial (2):** the signature-verification control is real, on the default path, and not bypassable — the calibration rule credits an operative control Partial even with findings about its gaps.
- **Case for Ad hoc (1):** the surrounding defaults (cleartext keys, spoofable admin, no replay) are so permissive that the one good control doesn't constitute a Zero-Trust *posture*; the gaps dominate.
- **Generalizes to:** *does one genuinely-operative control floor its category at Partial(2), or can a cluster of Critical gaps in the same category pull it back to Ad hoc(1) despite that control?* — the single biggest 2↔3-region weighted-variance lever.
- **Inclination (Steve, 2026-07-17): ZT = Partial (2).** Operative ECDSA verification on the default path + documented-required secure key config → Partial. The Critical key/replay gaps stay in the register as Critical findings (rule #3) but the documented-config mitigation (rule #2 + A3) keeps ZT at ~2, not lower. Target weighted ~2.0 (matches the reliable median).

### B2 · aider — Implement Zero Trust / Limit Your Domain: the bypassable human-in-the-loop confirm model
- **Evidence:** aider's confirm-prompt / developer-in-the-loop gating on edits and commands — a real control, but bypassable (`--yes`, `# ai!` auto-exec in `--watch-files`, `--no-verify`).
- **Observed:** aider is the "credit the safety design" calibration target; the call is whether the confirm model earns **Partial (2)** or is discounted toward **Ad hoc (1)** for its bypasses.
- **Boundary:** category score 1 ↔ 2 (and the guardrail against over-correcting a legitimate safety design to Absent).
- **Case for Partial (2)+:** a human-in-the-loop confirmation *is* an operative control; bypasses are findings, not reasons to zero it; the remit explicitly warns against scoring a real safety design as theater.
- **Case for Ad hoc (1):** a control that is off-by-default in common modes (watch-files auto-exec, `--yes`) is "exists but trivially bypassable" — the Ad-hoc definition — so it shouldn't reach Partial.
- **Generalizes to:** *is a human-in-the-loop control that is real but bypassable-by-flag scored Partial (operative-on-the-default-path) or Ad hoc (off-by-default / bypassable)?* — decides the "don't over-correct a safety design" guardrail.
- **Inclination:** _______________________________________________

### B3 · Absent-control floor — "no adversarial testing evidence at all" (Build an AI Red Team)
- **Evidence:** several targets have zero adversarial-test artifacts; the category is scored on absence.
- **Observed:** scored **0** on most; the question is whether absence is ever a **1** rather than **0**, and whether it also becomes a standalone *finding* (the Stage-1 decomposition residual).
- **Boundary:** category score 0 ↔ 1.
- **Case for 0:** absence of evidence of a whole control class is a true Absent — the KB's "absence is evidence" rule; a clean 0 is honest.
- **Case for 1 (rare):** if there is *some* structured testing (unit tests touching security paths, a threat-model doc) even without adversarial red-teaming, a floor of 1 may be fairer than 0.
- **Generalizes to:** *what is the minimum evidence that lifts an absent-control category from 0 to 1 — and does a blanket absence become a standalone finding or stay category-score-only?* (pairs with the Stage-1 decomposition carry-forward).
- **Inclination — finding-vs-score half (Steve, 2026-07-17): absence of an un-required control is a CATEGORY SCORE, not a finding.** The Findings Register is remit-anchored (policy-implementation divergence) or detection-pattern-anchored (an *observed* bad thing — secret, CVE, injection sink — may be rule-less). An **absence** the remit never named has nothing to hang a finding on and is not an observed artifact → it lowers the RAISE **category score** (e.g. Monitor = 0) and is explained in the category **rationale** only. **No manufactured finding.** Decidable rule: *remit requires control + absent → gap finding tied to the rule; remit silent + absent → category score only; bad thing present → finding (rule-anchored or rule-less detection-pattern).* Rule-less findings stay legit for what you **observe**, never for what is **absent**.
- **Stage-3 SKILL consequence:** Step 9.8's "absence of logging is itself a finding (it usually is for Monitor Continuously)" becomes "absence of logging is a finding **only if the remit required logging**; else it is a Monitor-category score, not a finding." Kills the over-manufacturing.

- **⚠ GUARDRAIL — do NOT break Monitor Continuously scoring with this change (Steve, 2026-07-17).** The B3 rule changes *finding-manufacturing only*; it must **not** change *category scoring*. Hard invariants for the Stage-3 edit:
  1. **Decouple score from findings.** A RAISE category score is a function of the **observed controls** (present / absent / operative), **never of the findings list.** Removing the auto-manufactured logging finding must leave the category score identical.
  2. **Absence-is-evidence is unconditional at the category level.** No logging → **Monitor Continuously = 0**, *regardless of* whether the remit named logging and *regardless of* whether a finding is emitted. The remit-requirement gate applies **only** to whether a *finding* is written, **never** to the *score*.
  3. **Regression guard for the re-baseline (`v1.2-claude48`).** After the Step-9.8 edit, verify **per-category scores are unchanged** vs the current Stage-2.5 runs on every target; the *only* permitted delta is the findings register (fewer manufactured absence findings). **Finding-count may drop on affected targets — that is the intended, measured effect, not a regression;** weighted-overall must be within noise.
  4. **#48 must state the Monitor Continuously (and every absence-is-evidence category) scoring criterion explicitly and separately from finding-generation**, so an implementer cannot conflate "don't write a finding" with "don't score the gap." Keep the RAISE scoring criteria clear here — do not let this edit blur them.
- **Inclination (Steve, 2026-07-17): evidence ladder — 0 only if genuinely NO evidence.** Any one of: an **adversarial test**, in-repo **documentation on how to red-team** the agent, or a frozen **one-time red-team report** → lifts Build-an-AI-Red-Team to **≥1**. Truly nothing → **0 (nonexistent)**.

---

## Section C — Decomposition / materiality (the finding-count axis)

*Carried from the Stage-1 gate: the compound-contributor rule fixed the biggest
driver; these settle the residual "what is one finding" calls that the
hand-score anchor is meant to define (per `RELEASE_1.3_PLAN.md`).*

### C1 · Compound-contributor fold/break-out — validate the decidability rule
- **Case:** uAgents' admin-exposure compound (0.0.0.0 bind + spoofable guard + default-on inspector). The Stage-1 rule: a contributor is a standalone finding **iff it would still be a finding after the other links are fixed** (bind → standalone; guard/inspector → folded).
- **Observed:** the rule collapsed uAgents finding-count spread 4→1; the question is whether the *anchor endorses the rule's outputs* (bind standalone, guard+inspector folded) as the correct decomposition.
- **Case to endorse:** the folded mechanisms are only exploitable via the chain; separate findings would double-count and inflate the count run-to-run.
- **Case to adjust:** a defense-in-depth reviewer may want the spoofable-guard called out separately as its own hardening item even though it's chain-dependent.
- **Generalizes to:** *ratifies (or amends) the fold/break-out decidability test as the canonical compound-decomposition rule.*
- **Inclination (Steve, 2026-07-17): RATIFIED as-is.** A contributor is standalone iff it would still be a finding after the other links are fixed; else folded; never both. No defense-in-depth override to force a chain-only contributor to surface separately (that reintroduces the double-count). Already implemented; uAgents count-spread 4→1.

### C2 · Two facets of one prompt — one finding or two? (the Stage-1 helperbot residual)
- **Evidence:** helperbot `prompts.js:26–27` — the system prompt both (a) instructs the agent to "share its configuration openly" and (b) embeds a hardcoded internal API key. One run merged these into one Critical; others split them (disclosure behavior = Zero Trust; hardcoded secret = Supply Chain).
- **Observed:** the driver of helperbot's residual spread (8 vs 6 findings).
- **Case for two findings:** they fail the independence test in the *keep-separate* direction — fix the disclosure instruction and the hardcoded key is still a finding; fix the key and the disclosure instruction is still a finding; different RAISE categories.
- **Case for one finding:** they are the same two adjacent lines of one artifact; a reader fixes the system prompt once; splitting feels like double-reporting one mistake.
- **Generalizes to:** *are two independently-material issues in one artifact two findings (independence governs) or one (locality governs)?* — the merge-vs-separate half of the decomposition principle deferred to Stage 3.
- **Inclination (Steve, 2026-07-17): TWO findings.** They violate two different remit clauses (don't-reveal-system-prompt vs no-secrets-in-source) — and findings hang on remit clauses, so two clauses → two findings. Also passes the independence test. The remit-anchoring principle (B3) decides decomposition: **one finding per violated remit clause.**

---

## Directional-lean reference (fill during the session)

After the entries above are decided, record the **center** the rubric should
validate against — Steve's own weighted-RAISE for the three anchor-set targets
(deepagents, uAgents, salesforce), scored by hand from the evidence, category
by category. These become the fixed reference points the #48 lean-check grades
against (does the rubric's center land where the human did, not just whether
runs agree with each other).

**PROPOSED (Claude, from the rubric + the 3-run per-category evidence) — Steve to red-pen.**
Weights: ZT 0.25, others 0.15. Each cell shows the proposed value; **bold** = a
cell that *drifted* across the 3 runs and is the real call to pin.

| Target | LYD | BYK | ZT | MSC | RT | MC | weighted |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| deepagents | 4 | 3 | 3 | 4 | **2?** | 1 | **2.85** |
| uAgents | 2 | 2 | 2 | 3 | 1 | 1 | **1.85** |
| salesforce | 3 | 2 | 2 | 3 | 1 | 1 | **2.00** |

*(Updated for the locked rulings: LYD/MSC=4 where always-on+gap-free; MC=1
suite-wide per the durable-audit rule; ZT per B1. Anchors: deepagents 2.85,
uAgents 1.85, salesforce 2.00 — these are what post-rubric runs must converge to.
Only open cell: deepagents **RT 2 vs 3**.)*

Per-cell notes (the drift the rubric must pin):
- **deepagents LYD/MSC = 4?** These categories have on-by-default, code-enforced,
  gap-free controls (path containment; sha256-pinned lockfile) → they can reach
  **Strong (4)** per the rubric (4–5 needs on-by-default). The MCP-TLS gap lives
  in the *transport* facet and caps *that* only; it doesn't stop LYD/MSC hitting 4.
  **CONFIRMED (Steve): deepagents LYD = MSC = 4** (correct + always-on + gap-free = Strong; the TLS gap caps only the transport facet). This is what made r3's 3.30 mostly *right*. **RT = 2** (threat-model doc +
  security unit tests = "something", not real adversarial red-team → not 3).
  **MC = 2** (some structured signal, not durable audit → the B3/absence call).
- **uAgents MSC = 3** (committed lockfile, pinned deps — real, gap-free → Established);
  **BYK = 2**. ZT = 2 fixed by the B1 ruling (ECDSA on default path, Critical key/
  replay findings stay in register but don't crush the score).
- **salesforce MC = 1 or 2?** the only drifting cell — partial platform telemetry.
  Ties directly to the B3 absence-is-evidence guardrail: is minimal platform signal
  a 1 or 2? Everything else is stable.

These per-category targets *are* the #48 anchor: post-rubric median-of-3 runs must
land here (± a cell), and the weighted must hit 3.00 / 2.00 / 2.15.

*(LYD=Limit Your Domain, BYK=Balance Your Knowledge, ZT=Implement Zero Trust,
MSC=Manage Supply Chain, RT=Build a Red Team, MC=Monitor Continuously.
ZT weight 0.25, others 0.15.)*

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
- **Inclination:** _______________________________________________

### A2 · salesforce — indirect prompt injection via Knowledge-article content, undefended in code — **[STABLE]**
- **Evidence:** `force-app/main/default/aiAuthoringBundles/haaHelpAgent/haaHelpAgent.agent:10` — retrieved Knowledge content enters agent context unlabeled; the sole injection guard addresses user input only; no code-side detection/halt.
- **Observed:** frozen = **Critical**; **Stage-2.5 fresh = High in 3/3 runs** (Stage-0 was mixed High/Critical; the fuller-suite run converged on High). The whole target reproduces at **σ 0.071** (2.15/2.00/2.15). So this is now a *stable* call that differs from frozen, not the run-to-run churn earlier data suggested.
- **Boundary:** Critical ↔ High.
- **Case for Critical:** it defeats the agent's #1 declared defense, is undetectable (no logging), and injection→off-script behavior is the agent's core threat; policy-exists-but-no-enforcement-and-no-monitoring is the rubric's canonical Critical compound.
- **Case for High:** the agent is a *constrained, single-tool* Q&A bot — no DML/shell/exfil sink, so the realized blast radius of a successful injection is off-script text / misinformation, not action; a bounded-capability agent caps the downside.
- **Generalizes to:** *does agent capability (blast radius) cap the severity of an injection finding, or does defeating the primary declared control set it regardless of downstream capability?*
- **Inclination:** _______________________________________________

### A3 · uAgents — identity + wallet private keys persisted to plaintext `private_keys.json`
- **Evidence:** `storage/__init__.py:113` + `agent.py` name-based key path — `save_private_keys()` writes identity and wallet private keys in cleartext on the default named-agent path.
- **Observed:** frozen = **Critical**; Stage-1 fresh = **Critical, Critical, High** (2/3 hold Critical).
- **Boundary:** Critical ↔ High.
- **Case for Critical:** private signing keys at rest in cleartext is a forbidden-data-movement / key-management failure; key compromise = full agent + wallet impersonation; conventionally Critical.
- **Case for High:** it is the *default local* path for a framework (operator can supply a seed / external keystore); no remote exposure by itself; "framework default the operator is expected to harden" is a High-not-Critical argument (the `scan_type: framework` question, #65 item 5).
- **Generalizes to:** *is a framework's insecure-by-default key-at-rest scored at the severity of the exposure it creates (Critical) or discounted one tier as an operator-overridable default?* — ties directly to the framework-vs-deployed-agent framing (O5).
- **Inclination:** _______________________________________________

---

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
- **Inclination:** _______________________________________________

### B0c · helperbot — do a WEAK agent's narrow-tool-surface / statelessness earn category credit (0 vs 1)? — **[UNSTABLE — σ 0.165]**
- **Evidence:** a deliberately-vulnerable CTF agent (all flags false) that nonetheless has a *narrow* fixed tool inventory, statelessness, and no forbidden tools.
- **Observed:** weighted **0.75 / 1.15 / 1.00** — one run scored every category **1**, another kept several at **0**. The narrow-surface "positive" is credited 0↔1 inconsistently.
- **Boundary:** category score 0 ↔ 1 on a target that is *supposed* to be near-Absent.
- **Case for crediting 1:** a genuinely narrow, forbidden-tool-free inventory is a real (if minimal) Limit-Your-Domain control.
- **Case for 0:** on a WEAK target with zero enforcement, a narrow surface by accident-of-scope isn't a *control*; near-Absent is the honest read.
- **Generalizes to:** *does an architectural property (narrow surface, statelessness) that isn't an intentional control earn category credit?* — governs the noisy low end.
- **Inclination:** _______________________________________________

### B1 · uAgents — Implement Zero Trust: operative ECDSA signing vs. the plaintext-key + spoofable-admin gaps — **[UNSTABLE — σ 0.122]**
- **Evidence (control):** real SECP256k1 envelope signature verification enforced before dispatch on the agent path (a genuine, tested control). **Evidence (gaps):** the A3 plaintext keys + the spoofable-loopback admin compound.
- **Observed:** weighted overall ranged **1.85–2.15** across runs; the swing is largely whether Zero Trust lands **Partial (2)** or **Ad hoc (1)**.
- **Boundary:** category score 1 ↔ 2.
- **Case for Partial (2):** the signature-verification control is real, on the default path, and not bypassable — the calibration rule credits an operative control Partial even with findings about its gaps.
- **Case for Ad hoc (1):** the surrounding defaults (cleartext keys, spoofable admin, no replay) are so permissive that the one good control doesn't constitute a Zero-Trust *posture*; the gaps dominate.
- **Generalizes to:** *does one genuinely-operative control floor its category at Partial(2), or can a cluster of Critical gaps in the same category pull it back to Ad hoc(1) despite that control?* — the single biggest 2↔3-region weighted-variance lever.
- **Inclination:** _______________________________________________

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
- **Inclination:** _______________________________________________

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
- **Inclination:** _______________________________________________

### C2 · Two facets of one prompt — one finding or two? (the Stage-1 helperbot residual)
- **Evidence:** helperbot `prompts.js:26–27` — the system prompt both (a) instructs the agent to "share its configuration openly" and (b) embeds a hardcoded internal API key. One run merged these into one Critical; others split them (disclosure behavior = Zero Trust; hardcoded secret = Supply Chain).
- **Observed:** the driver of helperbot's residual spread (8 vs 6 findings).
- **Case for two findings:** they fail the independence test in the *keep-separate* direction — fix the disclosure instruction and the hardcoded key is still a finding; fix the key and the disclosure instruction is still a finding; different RAISE categories.
- **Case for one finding:** they are the same two adjacent lines of one artifact; a reader fixes the system prompt once; splitting feels like double-reporting one mistake.
- **Generalizes to:** *are two independently-material issues in one artifact two findings (independence governs) or one (locality governs)?* — the merge-vs-separate half of the decomposition principle deferred to Stage 3.
- **Inclination:** _______________________________________________

---

## Directional-lean reference (fill during the session)

After the entries above are decided, record the **center** the rubric should
validate against — Steve's own weighted-RAISE for the three anchor-set targets
(deepagents, uAgents, salesforce), scored by hand from the evidence, category
by category. These become the fixed reference points the #48 lean-check grades
against (does the rubric's center land where the human did, not just whether
runs agree with each other).

| Target | LYD | BYK | ZT | MSC | RT | MC | weighted (hand) |
|---|--|--|--|--|--|--|--|
| deepagents-cli | | | | | | | |
| uAgents | | | | | | | |
| salesforce | | | | | | | |

*(LYD=Limit Your Domain, BYK=Balance Your Knowledge, ZT=Implement Zero Trust,
MSC=Manage Supply Chain, RT=Build a Red Team, MC=Monitor Continuously.
ZT weight 0.25, others 0.15.)*

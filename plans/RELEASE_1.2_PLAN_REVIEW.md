<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Release 1.2 Plan — Review

> Companion doc to `RELEASE_1.2_PLAN.md` and `RELEASE_1.1_REVIEW.md`.
> Written 2026-07-15, reviewing the plan against the shipped v1.1 state, the
> clean-run validation data (2026-07-12), the open-issue backlog, and the
> lessons of the 1.1 retrospective.

## Verdict in one paragraph

The diagnosis is right and the plan's own bottom line is the best sentence in
it: *"the prod-reliability problem is schema-stable-IDs + engine-resilience,
which is what 1.2 carries."* The clean-run section is exactly how a plan should
be grounded — every bucket tied to observed evidence. The problems are
**scope** (seven buckets spanning schema migration, render refactor, engine
reliability, new detection, scoring rubric, harness packaging, and docs — this
is a grab-bag, and grab-bags are how 1.1 ended up shipping under the wrong
name), **sequencing** (the plan has no internal order, and order matters
enormously here because the release ends in an expensive re-baseline that must
come after every number-mover), and **a stale factual premise** (the coverage
bucket's "LLM05 recovered, likely strike the backfill" is right, but LLM08 and
ASI08 are still zero columns in the shipped anchor — including #169's proof
case). Below: what I'd change in scope, content, and strategy.

---

## 1 · Scope — define 1.2 by the re-baseline, and cut what doesn't move it

The single most expensive artifact 1.2 produces is the `v1.2-claude48`
re-freeze (median-of-3 × 12 targets — ~36 scans plus reruns). The release's
scope rule should be stated explicitly:

> **In 1.2: everything that moves findings, scores, schema, or scan flow —
> i.e., everything that would otherwise force *another* re-baseline later.
> Out of 1.2: everything that doesn't.**

Applying that rule to the buckets:

| Bucket | Verdict | Why |
|---|---|---|
| **A** · Schema (#7, #5) | **Core** | Forces the re-baseline; the release exists for this. |
| **B** · #33, #29, #113 | **Core** | All three change model *output* (emission flow, decomposition, prose formatting) → affect the frozen artifacts; must precede the freeze. |
| **B** · #27 (report UI), #25 (SKILL split), #6 (render polish) | **Cut → 1.2.x / 1.3** | Deterministic-layer / docs-layer; regenerating rendered baselines is cheap and doesn't need the release train. #25 is a refactor with no output change — land it early *or* late, but it shouldn't gate the freeze. |
| **C** · #65 | **Core, but split it** | #65 is eight items in a trench coat. Items 1 (Step-4 evidence checkpoint), 2 (`--validate-manifest`), 4 (IaC discovery table) and 6–8 (remit guidance) are cheap and high-yield — do them. Item 5 (`scan_type: framework`) is a remit-schema/report-framing change with real design weight — schedule it deliberately or defer it; don't let it ride in as a side effect. Item 4 (IaC) **adds findings** → must precede the freeze. |
| **D** · #104, #41, coverage | **Core if before the freeze; otherwise cut** | Both add findings. Either they land before the re-characterization runs or they wait for 1.3 — there is no third option that doesn't cost a second freeze. |
| **E** · #151 (Antigravity) | **Cut → any 1.1.x/1.2.x** | Packaging + docs; zero baseline impact. Its issue says so itself ("the skill engine needs no changes"). Ship it whenever — ideally sooner, since it's adoption work with an external contact waiting. |
| **F** · Docs (#117, #135, #4, #118, #90, #2) | **Cut, except #117's collapsed form** | #118 is a schema-contract change *deferred by its own text*; #117 is gated on it. The plan already half-admits this bucket is a parking lot. Park it officially. |
| **G** · #48 scoring | **Core — and the headline** | See §3. |

That trims 1.2 to: **schema arrays + stable rule IDs, emission-flow rework,
engine resilience, detection additions, scoring anchoring, one re-freeze.**
A coherent name for that is *"comparability and reliability"* — every item
serves "two scans of the same target can be mechanically compared, and scans
don't die." That's also precisely what the clean run and the external
assessment both asked for.

## 2 · Sequencing — the plan needs an explicit internal order

The plan lists buckets; it must also say *when*, because the re-freeze
invalidates everything that lands after it. Proposed order, with the reasoning:

1. **Emission-flow first (#33, #29; #65 items 1–2).** These change how scans
   execute and directly attack the 13–14-min watchdog-edge fragility the clean
   run measured. Every characterization run made before this lands is a run on
   the old, stall-prone flow — wasted evidence. Do them first, then run a
   single-target 3× shakedown to confirm stall behavior and finding-count
   stability (the hermes-11-vs-5 decomposition variance should visibly shrink;
   that's the acceptance test for #29).
2. **Schema (#7 arrays, #5 cross-check) + render-pipeline refactor second.**
   Mechanical, testable, and everything downstream (findings JSON, baselines,
   `compare_checkpoint.py`-style tooling) should be written once against the
   new shape. This is also when scan-vs-scan diff tooling should be built —
   the clean run had to hand-match findings; #5's remit cross-check plus
   arrays is what makes a mechanical join possible. **Add that diff tool as a
   named 1.2 deliverable** — it's implied everywhere and owned nowhere.
3. **Detection additions third (#104, #41, #65-IaC, LLM08 re-tag).** New
   findings enter here, on the new schema, with the new emission flow.
4. **#48 scoring anchors fourth** — severity anchoring + control-ledger,
   validated 3× on the named worst offenders (deepagents, salesforce, plus
   uAgents/craftbot from the 1.1 plan's headroom list) before adoption.
5. **One re-freeze, last.** Median-of-3 × 12 on the final stack. Also the
   moment for #176 (suite_health scale/baseline-dir — its issue literally says
   "batch at the next re-baseline") and the #173/#174 tagging nits.

## 3 · Content corrections and additions

**a. Fix the coverage bullet (bucket D).** "LLM05 recovered → likely strike
the backfill" — correct, verified in the anchor (4P/6S). But the same
verification shows **LLM08: zero anywhere (0P/0S)** — the shipped anchor
contradicts the shipped KB on #169's proof case (craftbot-005, agent-writable
ChromaDB, which the KB now calls *dominant* LLM08) — and **ASI08: zero**. So:

- 1.2 still owns LLM08, and it's cheap: a re-tag pass under the
  already-shipped guidance, folded into step 3 or 5 above. No new targets
  needed.
- ASI08/ASI10 need a *decision*, not a fix: under the outcomes-are-secondary
  rule, ASI10-as-primary may be structurally ~0 in this corpus and ASI08 may
  not attach at finding level at all (BASELINE.md says as much). Then "no zero
  columns" must be defined as **primary+secondary counted**, or the goal
  restated per-category. Otherwise 1.2 will end with a coverage gate it can't
  pass for taxonomy reasons.

**b. Do #48 item 4 now, outside 1.2.** "Theme-coverage is the regression gate;
the weighted score is advisory" needs no validation (the issue says so), moves
no numbers, and is the single most direct answer to the external assessment's
"expert-assisted review, not a deterministic gate" framing. It's a docs/process
patch — ship it this month, don't let it wait behind the schema migration.
It also de-risks the whole 1.2 grading story: if the gate is themes, a scoring
tweak that shifts decimals can't fail the release.

**c. Re-add the roster items the plan dropped.**

- **The DB/NL-to-SQL archetype is gone** — langchain-sql was dropped
  *un-replaced* in 1.0.2 (a documented deviation from #70's "replace, don't
  drop" intent), and the 1.2 plan doesn't mention it. Either 1.2's coverage
  bucket owns finding a live SQL-agent target, or the deviation gets accepted
  explicitly and #70 closes with that note. Silence is the one wrong option.
- **The uAgents framing question (O5 / #65 item 5)** — "framework defaults vs
  deployed agent" is still an open judgment call sitting in
  `PHASE1_OPEN_ISSUES.md`, and it interacts with `scan_type: framework`. If
  item 5 is deferred, O5 should be answered anyway (one paragraph from Steve).

**d. Add a watch-item: LLM06 concentration.** Post-1.1, LLM06 is 23P + 6S —
roughly a quarter of the tagged corpus. The 1.1 lesson is that steering rules
overshoot; LLM06 ("reachable forbidden capability → LLM06") is the most
steerable rule in the KB and is structurally positioned to become the new
dumping ground, the way `untagged` was pre-1.1. The #48-era tagging pass should
include a "is LLM06 still discriminating?" check (sample N LLM06 findings,
confirm a non-LLM06 counterfactual exists for each).

**e. State the success metrics per bucket.** The 1.1 plan had a "Regression
discipline & success metric" section with numbers; the 1.2 plan has discipline
but almost no numbers. Proposals:

- **Reliability (B/C):** zero watchdog deaths across two consecutive full-suite
  runs; no scan within 20% of the watchdog limit; finding-count spread on 3×
  same-target runs ≤ ±2 (vs. today's 11-vs-5).
- **Comparability (A):** a scan-vs-scan diff of two independent runs of the
  same target joins ≥90% of findings mechanically (no hand-matching).
- **Scoring (G):** median-of-3 vs median-of-3 |drift| ≤ 0.2 on the four named
  calibration targets; the two lenient severity flips (Critical-scored-as-High
  on deepagents/salesforce) resolved by anchor, not by hand.
- **Coverage (D):** no zero columns *counting primary+secondary*, with the
  ASI08/ASI10 structural exception documented if taken.

**f. Pin the reference model in the plan.** The `-claude48` suffix implies it,
but a re-baseline this expensive deserves one sentence: *"v1.2 freezes on
Opus 4.8; a model change is its own future re-baseline, never folded into
this one."* (The 4.7→4.8 lean measurement and the abandoned Fable-5 run are
both precedent for how much a model swap moves; don't let one sneak in via a
default-model change mid-release.)

## 4 · Strategy — how things are going, and the one pattern to break

**Going well:** the plan is evidence-driven to a degree that's rare (the
clean-run section alone justifies the planning overhead); the 1.1 → 1.2
hand-off of watch-items (directional lean, LLM05) shows the release-train
discipline is real; and the project's stated priorities now finally match its
external critique (#48, stable IDs, resilience).

**The pattern to break:** both 1.1 and (per its own history) 1.0.2 were
descoped mid-flight, and the descope was handled in commits rather than in the
plan docs and tracking issues — which is why the repo currently documents a
release that didn't happen as planned. 1.2 is *bigger* than 1.1 was, so the
same pressure will recur. Two mitigations:

1. **Pre-split now instead of descoping later.** Cut buckets E/F and the
   B-tail (§1) before work starts, so the release that ships matches the plan
   that named it. A smaller honest plan beats a bigger aspirational one — 1.1
   proved both halves of that sentence.
2. **Put a checkpoint between stages 2 and 3** (schema landed, before
   detection adds): if the schedule is stressed at that point, 1.2 ships as
   schema+reliability and stage 3–4 become 1.3 *by plan amendment, in the
   doc, on the day the call is made*.

**Independent of 1.2 — this week, not this release:**

- **#120** — the Gemini review gate sunsets **2026-07-17 (two days)**. Decide
  the replacement now; the per-PR background-review convention should be
  written into the repo (CONTRIBUTING or a workflow), not live only in a
  working agreement.
- **#178** — CI docs-freshness on PRs. Small, and it structurally blocks every
  future release exactly the way it blocked 1.1.0.
- **Issue-hygiene sweep** — close the nine shipped-but-open issues
  (see the 1.1 review) so the backlog the 1.2 plan draws from is real.
- **File the LLM08 anchor regression on #169** so it can't silently close.

**Bottom line:** the 1.2 plan is aimed at the right target and grounded in the
right evidence. Trim it to its re-baseline core, give it an explicit internal
order with the freeze last, correct the LLM08/ASI08 premise, take #48-item-4
and the time-critical pulls out of the train entirely — and 1.2 becomes the
release that converts Praxen's honest-about-uncertainty posture into measured
reliability, which is exactly what the outside world said it needs.

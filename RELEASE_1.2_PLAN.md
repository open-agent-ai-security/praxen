<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.2 — Harness Reliability & Scoring Stability

> **Revised 2026-07-15** — supersedes the 2026-07-12 draft (see git history and
> `RELEASE_1.2_PLAN_REVIEW.md` for what changed and why). Re-scoped around the
> operator priority statement (Steve, 2026-07-15): *"our big problems are
> harness reliability, and scoring stability (Critical vs. High, etc., and
> RAISE)."* Everything else moved to `RELEASE_1.3_PLAN.md` or the 1.1.1 patch
> (`RELEASE_1.1.1_PLAN.md`).

## Objective

1.2 attacks the two problems that matter most in production, and nothing else:

1. **Harness reliability** — scans must not stall or die. The 2026-07-12
   clean run had zero watchdog deaths but several scans at 13–14 min, right at
   the watchdog edge; historical full-suite mortality has hit ~30%. The stall
   mechanism is known (the Step-9.9 synthesis burst) and so is the fix shape
   (interleaved emission + decomposition primer + recovery checkpoints).
2. **Scoring stability** — the same target with the same remit must score the
   same way twice. The clean run pinpointed the lever: RAISE drift was
   **entirely severity calibration on borderline findings** (5/12 exact, mean
   |drift| 0.17, max 0.55; deepagents +0.55 and salesforce +0.45 were each a
   **Critical scored as High**). This is also the project's most-cited external
   criticism (July Deep Research assessment, quoted on #48).

The schema work (#7/#5) stays in 1.2 **as the enabler, not a co-headline**:
stable, joinable rule IDs are what make scoring stability *measurable
mechanically* (the clean run needed hand-matching to compare scans), and since
#7 forces the re-baseline anyway, it shares the one freeze this release pays
for.

**Scope rule:** in 1.2, everything that serves reliability or scoring
stability, plus the schema enabler; **out**, everything that doesn't —
detection additions, coverage backfill, output polish, harness reach, and docs
are 1.3 (`RELEASE_1.3_PLAN.md`).

## Prerequisite

**The post-1.1 cleanup batch folds in first** (`RELEASE_1.1.1_PLAN.md` —
shipped as a **docs/process batch, no version bump**, per Steve 2026-07-16):
paper-trail reconciliation and process items only — **no re-tag, no
re-freeze** (the LLM08 fix was diagnosed as unfixable by re-tagging and moved
into this release: authoring invariant in stage 1, re-scan acceptance in
stage 4). `v1.1-claude48` therefore remains the anchor, and it is still the
pristine, scoring-unchanged "before" this release is graded against. 1.2
branches from `main` after the cleanup batch lands.

## Staged scope — order is load-bearing

The release ends in one expensive re-freeze (median-of-3 × 12). Every stage
that changes scan output must land **before** it; the freeze comes last, once.

### Stage 1 · Harness reliability *(the #1 problem)*

- **#33** — interleave finding emission with analysis; kill the Step-9.9
  synthesis burst at its mechanism.
- **#29** — Step-8.5 finding-themes outline before drafting (decomposition
  primer). Also expected to shrink the finding-count scatter the clean run saw
  (hermes 11-vs-5, aider 11-vs-6 at equal substance), which currently muddies
  every scan-to-scan comparison.
- **#65 items 1–2** — Step-4 evidence checkpoint written to disk (survives
  compaction on large codebases); `--validate-manifest` flag on
  `manifest_to_findings.py` (manifest format errors caught early, not at
  parse time).
- **Evidence-completeness authoring invariant** *(added 2026-07-16 from the
  LLM08 diagnosis — see #169 and `RELEASE_1.1.1_PLAN.md`)* — SKILL.md evidence
  step: **evidence must cite every mechanism in the finding's causal chain** —
  if the chain runs through a store, queue, scheduler, or subsystem, that
  surface gets an evidence line even when another frame dominates the summary.
  Test: the record must be **closed under classification** — a competent
  reader reaches the right taxonomy from the record alone (craftbot-005 is
  the failing case study: its frozen record dropped the ChromaDB link, so no
  prose pass could ever tag LLM08). Lands here because it shares #29's
  carving/emission surface and it changes finding content → must precede the
  freeze.

**Stage gate (measured, 3× single-target shakedown then one full-suite run):**
zero watchdog deaths; no scan within 20% of the watchdog limit; finding-count
spread on 3× same-target runs ≤ ±2.

### Stage 2 · Schema enabler — mechanical comparability

- **#7** — `policy_rule_text` / `policy_rule_ids` as arrays; `schema_version`
  bump; render-pipeline migration. The largest mechanical change — the reason
  this release re-baselines.
- **#5** — validator round 2: `policy_rule_ids` ↔ remit-rule cross-check, so
  rule references are verifiably real.
- **Named deliverable: a scan-vs-scan diff tool** (promote
  `compare_checkpoint.py` or successor into `tests/`): joins two runs of the
  same target on remit-anchored rule references + finding content. The clean
  run proved the need — regression detection currently requires hand-matching.

**Stage gate:** two independent runs of the same target join ≥90% of findings
mechanically; `test_render.py` migrated and green on the new shape.

> **Mid-release checkpoint (after Stage 2).** If the schedule is stressed
> here, 1.2 ships as reliability+schema and Stage 3 moves to 1.3 **by plan
> amendment, in this doc, the day the call is made** — not by silent descope.
> (1.1's lesson.)

### Stage 3 · Scoring stability (#48 items 1–3)

Ordered by the clean run's evidence — severity anchoring first:

- **Severity anchoring (Critical vs. High, High vs. Medium)** — decidable
  criteria + 1–2 concrete evidence→severity→because anchors per boundary,
  calibrated against the two named lenient flips (deepagents, salesforce).
  This is the single largest measured drift source; it moves the weighted
  score through the severity weights, so it is *the* Critical-vs-High fix.
- **Control-ledger (per RAISE category, authored before the score)** —
  enumerate controls → on the default path? → off-by-default/bypassable? →
  therefore score N. Anchors the 1-vs-2 credit call to stated control-facts
  instead of gestalt.
- **0↔1 / 2↔3 boundary decision rules** — the operative-but-imperfect-control
  case (Partial = executes on the default path unmodified; Ad hoc = exists but
  off-by-default/bypassed/not on the agent's path; Absent = never invoked).
- **Directional-lean check (carried from 1.1, now with an anchor).** The
  non-gating check: does the Zero-Trust / Limit-Your-Domain category-mean
  drift the same direction again vs. v1.0.2? Measuring *bias* (vs. scatter)
  needs a human-anchored reference: **Steve hand-scores 2–3 calibration
  targets** (suggest deepagents, salesforce, openai-cs) and those become the
  fixed reference points the rubric is validated against. If the lean is
  structural, correct it here; if unclear, document and carry to 1.3.

**Stage gate (median-of-3 on both sides, graded vs `v1.1-claude48`):**
zero Critical↔High flips across 3× runs on the four calibration targets
(deepagents, salesforce, uAgents, craftbot); median-of-3 |weighted drift|
≤ 0.2 on those targets; posture bucket stable everywhere. Same
over-steer/contamination discipline the 1.1 tagging work hard-won — scoring is
even more seductive to steer than tagging; validate on the calibration
targets *before* touching the rest of the suite.

### Stage 4 · Re-freeze `v1.2-claude48` — once, last

- Median-of-3 × 12 targets on the final stack (new emission flow, new schema,
  new scoring guidance). **Reference model pinned: Opus 4.8** — a model change
  is its own future re-baseline, never folded into this one.
- **Tagging pass riding the freeze** *(added 2026-07-16 — dispositions from
  the LLM08 diagnosis)*:
  - **#169 acceptance:** the craftbot vector-store finding carries LLM08 in
    the **majority of the median-of-3 runs** — these are fresh code-reading
    scans under the LLM08-aware KB + the stage-1 authoring invariant, which is
    the only method that can fix it (re-tagging was proven unable to; see
    #169's diagnosis comment). #169 closes here or the KB/authoring guidance
    gets another look.
  - **Secondary chips anchored majority-of-3**, same spirit as median-of-3
    scores — single-pass secondaries are demonstrably churn-prone (the
    hermes/salesforce LLM08 flips across the three 1.1 passes). A secondary
    appears in the frozen exemplar iff ≥2 of 3 runs emit it.
  - **#173 / #174** — make the two KB clauses decidable (LLM06
    phantom-control; ASI10 default-off vs structurally-absent), then let this
    pass classify under them. Close both here.
  - **KB validity-domain sentence** — state in the LLM08 entry (and any other
    code-dependent guidance) that detect-then-audit steps assume source
    access; prose-only contexts must not guess them.
- Batch here (their issues say "next re-baseline"): **#176** (suite_health
  full RAISE scale + baseline-dir consistency); coverage pages regenerated;
  **LLM06 discrimination check** — LLM06 is now ~25% of the tagged corpus
  (23P+6S), the most steerable rule in the KB, and structurally positioned to
  become the new dumping ground the way `untagged` was pre-1.1: sample its
  findings and confirm a non-LLM06 counterfactual exists for each.
- Coverage gate carried from 1.1, restated so it's passable: **no zero columns
  counting primary+secondary**, with the documented structural exception for
  outcome categories (ASI08 may not attach at finding level; ASI10 rides
  secondary) — LLM08 becomes non-zero at this freeze (the #169 acceptance
  above), not before.

## Explicit non-goals (→ 1.3 or later)

Detection additions **#104 / #41 / #65-item-4 (IaC discovery)** — real, wanted,
and deliberately *not* here: each adds findings, and findings added after the
freeze cost a second freeze. They headline 1.3, whose re-freeze they justify.
Also out: `scan_type: framework` (#65 item 5 — needs the O5 framing decision),
the DB/NL-to-SQL roster replacement (#70), LLM05 specialist target, output
quality (#27/#25/#6/#113), harness reach (#151), docs (#117/#118/#135/#4/#90/#2).

## Regression discipline & success metric

1.2 intentionally moves numbers (#7 shape, #48 scoring) → re-freeze
`v1.2-claude48`, graded vs `v1.1-claude48`. Success is **measured, per stage
gate above** — in one line each:

- **Reliability:** two consecutive full-suite runs, zero deaths, nothing at
  the watchdog edge.
- **Comparability:** mechanical scan-vs-scan join ≥90%, no hand-matching.
- **Scoring:** zero Critical↔High flips and |drift| ≤ 0.2 median-of-3 on the
  calibration targets; **theme-coverage is the gate, weighted score advisory**
  (per #48 item 4, landed in 1.1.1).
- Version bump 1.2.0 (6 guarded locations + `PRAXEN_SPEC` §sync + CHANGELOG);
  `test_render.py` + `build.sh` green; CI 3.9/3.12/3.13; docs-freshness now
  checked per-PR (#178, landed in 1.1.1).

## Deliverables checklist

- [ ] Stage 1: #33 + #29 + #65(1,2) landed; reliability gate passed and
      recorded (shakedown + full-suite run committed under `tests/runs/`)
- [ ] Stage 2: #7 arrays + `schema_version` bump; #5 cross-check; scan-diff
      tool in `tests/`; comparability gate passed
- [ ] Stage 3: #48 severity anchors + control-ledger + boundary rules in
      SKILL/KB; human-anchored calibration recorded; scoring gate passed;
      lean check run and dispositioned
- [ ] Stage 4: `v1.2-claude48` frozen median-of-3; `CURRENT` updated; #176
      batched; coverage + LLM06 checks recorded
- [ ] Closes: #5, #7, #29, #33, #48, #169, #173, #174, #176; #65 partially
      (items 1–2; comment scoping the remainder to 1.3)

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

### Stage 2.5 · STOP · LOOK AROUND · TEST — the Stage-3 go/no-go gate
*(Formalized 2026-07-16 at Steve's direction — replaces the informal
"mid-release checkpoint". This is a real stage with work products, not a
schedule vibe-check, because its TEST output is instrumentation Stage 3
needs regardless of the decision.)*

**STOP.** No Stage-3 (#48) work begins — not "started in parallel," not
"just drafting the rubric" — until this gate's review is written down.
Rubric text drafted before the TEST data exists is how over-steer happens.

**LOOK AROUND.**
- Re-read the Stage-1 and Stage-2 gate results as written: watchdog margins,
  finding-count spread, diff-tool join rate. Any gate passed on a waiver
  counts as not-passed for this review.
- Survey the world: reference model still Opus 4.8; upstream targets not
  drifted in ways that would contaminate a re-characterization (the Hermes
  O8 lesson — `PHASE1_OPEN_ISSUES.md` §O8, the Hermes remit/upstream-drift
  investigation, not an OWASP code); no new external findings/issues that
  re-rank the remaining
  work; the hand-score questionnaire prepped and the joint scoring session
  done or scheduled (see the Stage-3 protocol — it is a Stage-3
  entry dependency — schedule it during Stages 1–2, not now).
- Schedule and appetite check, honestly stated.

**TEST.** Characterize the four flip-check targets (deepagents, salesforce,
uAgents, craftbot) **median-of-3 on the Stage-2 stack** (new emission flow,
new schema, authoring invariant — scoring guidance untouched), plus
HelperBot as the stability control. Commit the results under
`tests/runs/v1.2-stage2.5/`. This one run yields three things:
1. **Verification** that Stages 1–2 didn't destabilize scoring (they touch
   flow and shape, not judgment — confirm it).
2. **The clean intra-release "before" for #48.** Stage 1 legitimately moves
   decomposition, so v1.1-claude48 is no longer the right before for the
   rubric work — these runs are. Without this, #48's effect can't be
   isolated from the flow changes.
3. **A fresh variance measurement** to sanity-check whether the Stage-3
   gate's numbers (zero Critical↔High flips, |drift| ≤ 0.2) are realistic
   or need honest revision *before* the rubric work starts chasing them.

**DECIDE — with these pre-agreed criteria, recorded here by dated amendment:**
- **GO (Stage 3 stays in 1.2):** Stage-1/2 gates passed clean; TEST shows
  scores stable or movement explained-and-accepted; the hand-score
  questionnaire session done (inclinations marked, `HANDSCORE.md` committed);
  schedule healthy. **All four must hold — failing any GO criterion
  is itself a PUSH** (no undecidable middle: a clean-gates-but-stressed-
  schedule outcome pushes).
- **PUSH (Stage 3 → 1.3):** any GO criterion failed — typically: a stage
  gate failed; TEST shows score movement that is large (outside the Stage-3
  gate numbers — a Critical↔High flip or |drift| > 0.2 on a flip-check
  target) and unexplained (a rubric must never be calibrated on an engine
  that just destabilized); the questionnaire session isn't done; or the schedule/
  appetite check fails. **A push is cheap by design:** 1.3 already pays for a re-freeze, so
  #48 rides it at zero extra freeze cost — with one hard constraint carried
  along: inside 1.3, #48 lands **before** the detection additions, so its
  grading window isn't contaminated by new findings.
- Either way, 1.2 still ships and **Stage 4's freeze still happens** —
  Stages 1–2 change bytes and flow, so `v1.2-claude48` is required
  regardless of where #48 lives.

### Stage 3 · Scoring stability (#48 items 1–3) — *entered only via a Stage-2.5 GO*

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
  needs a human-anchored reference — produced by the **hand-score
  questionnaire protocol** below. **Anchor set: deepagents, uAgents,
  salesforce** *(updated 2026-07-16 from the **Stage-0 baseline** — a
  dry-run of the Stage-2.5 mechanics on the current v1.1 stack executed
  before any 1.2 work, flip-check four + HelperBot control × 3 runs each,
  committed as [`tests/runs/v1.2-stage0-baseline/`](../tests/runs/v1.2-stage0-baseline/STAGE0_BASELINE.md):
  uAgents replaced openai-cs because it now carries the largest anchor
  dispute — 3 Criticals in every fresh run vs the frozen 1)*. The recorded inclinations
  become the fixed reference points the rubric's *center* is validated
  against. (Distinct from the stage gate's *flip-check set* below — the four
  targets whose Critical↔High reproducibility is measured; the sets overlap
  but serve different measurements.) If the lean is structural, correct it
  here; if unclear, document and carry to 1.3.

- **Hand-score questionnaire protocol** *(added 2026-07-16 at Steve's
  direction — this is HOW the human anchor gets produced; it is a joint
  instrument, not homework)*:
  1. **Prep (Claude, due at the Stage-2.5 gate):** author a questionnaire of
     the exact corner cases — one entry per disputed judgment. Each entry
     carries: the finding (file:line evidence, quoted); the boundary it sits
     on (Critical↔High, High↔Medium, or a RAISE 0↔1 / 2↔3 credit call); the
     **case for each side, argued honestly** (2–4 pros/cons per side — no
     thumb on the scale); what each ruling would *generalize to* (the anchor
     sentence #48 would adopt if that side wins); and a blank
     **Inclination** field.
  2. **Session (Steve + Claude):** walk the entries together, decide the
     inclination on each, Claude marks it with a one-line rationale. Undecided
     entries are marked *deferred*, not guessed. **Intra-gate order:** LOOK
     (session may be merely scheduled) → TEST → finalize the questionnaire
     with anything TEST surfaced → session → DECIDE — the session sits
     between TEST and DECIDE. **Deferred entries** are re-examined at the
     Stage-4 freeze review against the fresh median-of-3 evidence; any still
     undecided carry to 1.3 alongside the lean disposition (and #48's anchor
     text simply doesn't anchor those boundaries yet — no guessed anchors).
  3. **Record:** the marked questionnaire is committed under
     `tests/runs/v1.2-stage2.5/HANDSCORE.md` and serves three roles —
     (a) the human-anchored reference for the lean check, (b) the seed text
     for #48's severity/credit anchors, (c) the replay cases the Stage-3
     gate re-tests (post-rubric runs must land on the marked side).
  **Seed corner cases** (from the 2026-07-16 Stage-0 baseline — the
  questionnaire starts from these five and adds whatever the Stage-2.5
  TEST surfaces): deepagents MCP-TLS-scheme gap (frozen Critical vs
  3-of-3 fresh High — bounded-blast-radius argument); uAgents plaintext
  private-key persistence (High vs Critical); uAgents spoofable-loopback
  admin exposure (High vs Critical); salesforce Knowledge-article-injection
  compound (flipped C/H/C across its own three runs); craftbot
  ungated-shell/approval cluster (Critical-count churn 4/3/4 at constant
  weighted score).

**Stage gate (median-of-3 on both sides — the "before" side is the
Stage-2.5 TEST runs, so #48's effect is isolated from the Stage-1 flow
changes; `v1.1-claude48` remains the outer, release-level reference):**
zero Critical↔High flips across 3× runs on the four **flip-check targets**
(deepagents, salesforce, uAgents, craftbot — the two worst severity-drift
offenders from the clean run plus the two widest-band targets); median-of-3
|weighted drift| ≤ 0.2 on those targets; posture bucket stable everywhere. Same
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

1.2 intentionally moves numbers (#7 shape; #48 scoring, contingent on the
Stage-2.5 GO) → re-freeze
`v1.2-claude48`, graded vs `v1.1-claude48`. Success is **measured, per stage
gate above** — in one line each:

- **Reliability:** two consecutive full-suite runs, zero deaths, nothing at
  the watchdog edge.
- **Comparability:** mechanical scan-vs-scan join ≥90%, no hand-matching.
- **Scoring** *(contingent on the Stage-2.5 GO)*: zero Critical↔High flips and |drift| ≤ 0.2 median-of-3 on the
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
- [ ] Stage 2.5: STOP·LOOK·TEST review written; flip-check + HelperBot-control
      median-of-3 on the Stage-2 stack committed (`tests/runs/v1.2-stage2.5/`);
      GO/PUSH decision recorded by dated amendment here (and in
      `RELEASE_1.3_PLAN.md` if PUSH)
- [ ] Stage 3: hand-score questionnaire prepped (corner cases w/ pros/cons)
      → joint session → inclinations marked and committed as
      `tests/runs/v1.2-stage2.5/HANDSCORE.md`; #48 severity anchors +
      control-ledger + boundary rules in SKILL/KB (anchor text seeded from
      the marked inclinations); scoring gate passed (post-rubric runs land
      on the marked side of every decided entry); lean check run and
      dispositioned
- [ ] Stage 4: `v1.2-claude48` frozen median-of-3; `CURRENT` updated; #176
      batched; coverage + LLM06 checks recorded
- [ ] Closes: #5, #7, #29, #33, #169, #173, #174, #176; #48 *(contingent on
      the Stage-2.5 GO — moves to 1.3's list on a PUSH)*; #65 partially
      (items 1–2; comment scoping the remainder to 1.3)

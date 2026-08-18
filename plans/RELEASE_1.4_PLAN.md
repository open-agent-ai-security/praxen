<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.4 — Detection Coverage, Output Quality & Reach

> **Formerly `RELEASE_1.3_PLAN.md` — renumbered 2026-08-10** when Thinking Modes
> (#197) was promoted to its own minor release ahead of this one: **1.3 = the
> accuracy release** (`RELEASE_1.3_PLAN.md`, per `DESIGN_THINKING_MODES.md`),
> **1.4 = this detection/re-baseline release**. Historical references to "the 1.3
> plan" in earlier release plans point at this document's content.
>
> Drafted 2026-07-15 alongside the revised `RELEASE_1.2_PLAN.md`; **re-triaged at
> the 1.2 close-out (2026-07-30)** now that 1.2 has frozen (shipped to `dev`).
> Holds everything cut from 1.2, plus what 1.2 pushed (#48) or newly surfaced (the
> remit-generator / over-reach class below). **Reference model is now Opus 5.**
> **Re-triaged 2026-08-11:** 1.3 stopped being score-inert — #195 passed its
> gates and 1.3 now ends in a **`v1.3-opus5`** re-freeze, taking a batch of this
> plan's pre-freeze items with it (struck below, per `RELEASE_1.3_PLAN.md`).
> **1.4 therefore grades `v1.4-opus5` vs `v1.3-opus5`.**
>
> **`v1.2.0` shipped 2026-08-03; `v1.2.1` shipped 2026-08-10** (score-inert, per
> `RELEASE_1.2.1_PLAN.md` — now STATUS: SHIPPED). 1.2.1 absorbed the docs/CI tail
> plus several items this plan had parked: **#106, #135, #4, #6 (complete, as a
> linked confidence bubble), #65 items 6–7** — struck below. Anything that moves
> a number stayed here. **1.4 branches from `dev` after the 1.3 promotion.**
> Re-triaged at the 1.2.1 close-out, 2026-08-10.

## Objective

With scans reliable and scores stable (1.2), widen what Praxen *finds* and
polish what it *emits*. Detection additions move numbers → 1.4 re-freezes
**`v1.4-opus5`**, graded vs **`v1.2-opus5`**. That freeze is why the detection
items travel together here rather than dribbling in: one release, one freeze.

## ~~Arrived from 1.2 — #48~~ (resolved in 1.3, 2026-08-11)

**#48 closed against the 1.3 scoring work** (#195): its control-ledger,
boundary decision rules, anchors, and themes-gate asks all shipped as part of
the Step 5/8b/9.4 restructure — see `RELEASE_1.3_PLAN.md` and
`plans/RESULTS_SCORING_BENCH.md`. Nothing remains here.

## New from the 1.2 baseline experience — remit-generator quality & over-reach cleanup

The 1.2 post-freeze FP sweep (one independent cross-model reviewer per target)
found **zero detector false positives** but a recurring **remit-authoring
over-reach** class — fabricated obligations, heading-as-rule extraction, and
MUST-NOTs that contradict documented features. Fixed + re-frozen on 6 targets
during 1.2; deferred on the rest. The durable fix is generation-side — do it
**before** re-scanning the deferred targets, not by hand-editing each remit.

- **#198** — remit generator authors well-formed, docs-grounded, non-over-reaching
  statements (heading-as-rule + fabrication/over-scope). **The durable fix.**
  Still 1.4: regenerate the remits on the improved generator and diff against
  the 1.3 hand-cleaned versions — the hand-cleanup is the acceptance fixture.
- ~~**#201** + **#200** — remit over-reach cleanup.~~ **Moved to 1.3**
  (pre-freeze riders): the enumerated hand-fixes land there and ride the
  `v1.3-opus5` freeze; #198's regeneration here must not re-introduce what 1.3
  cleaned.
- ~~**#195** — band-edge scoring variance.~~ **Resolved in 1.3** — the
  headline of that release (`plans/RESULTS_SCORING_BENCH.md`).
- ~~**#196** — Step-8.5 fold-vs-break-out tightening.~~ **Moved to 1.3**
  (one-clause change riding the freeze). The broader
  decomposition-independence generalization below **stays here** — it is the
  suite-wide-blast-radius half.
- ~~**#197** — Thinking Modes.~~ **Promoted out of this release entirely: ships
  as release 1.3** (`RELEASE_1.3_PLAN.md` / `DESIGN_THINKING_MODES.md`),
  deliberately **before** this one — so the #200/#201 re-scrubs run as
  automated high-mode audits, and the x-high variance diagnostics feed
  #48/#195/#196 here.

## Carried from the 1.2 Stage-1 gate — decomposition-independence generalization

The 1.2 Stage-1 gate (`tests/runs/v1.2-stage1-gate/GATE.md`) fixed the
**compound-contributor** decomposition variance (the fold/break-out decidability
test — uAgents 9/10/13 → 9/8/8). It left one residual: helperbot's `8/6/8`
spread, whose low outlier **merged two independently-material findings** (a
config-disclosure behavior gap and a hardcoded-secret-in-prompt gap) into one.
That is the *same* independence principle applied in the other direction — the
current rule governs fold-vs-breakout for compound contributors but not
merge-vs-separate for independent findings.

**Work item (Stage 3, with #48):** promote the independence/decidability test to
*the* single decomposition principle, stated once, governing **both** directions
— *two things are separate findings iff each would still be a finding after the
other is fixed*. This is squarely #48's axis (decomposition/materiality
determinism) and belongs where (a) the **hand-score anchor** defines the *correct*
decomposition, and (b) the **full re-baseline** measures the rule across all 12
targets — not bolted onto Stage 1 under-validated (it's a core rule with
suite-wide blast radius). The rest of helperbot's residual (`enp` on
advertised-but-unwired tools; wildcard-CORS materiality on a training target) is
genuine judgment, not rule-forceable — leave it to the hand-score calibration.

## Buckets

### A · Detection additions *(the re-baseline justification — land all before the freeze)*

- ~~**#65 item 4** — IaC/deployment artifacts in Step-4 discovery.~~ **Moved
  to 1.3** (pre-freeze rider).
- ~~**#41** — path-traversal detection pattern.~~ **Moved to 1.3** (pre-freeze
  rider).
- **#104** — entropy-based secret detection in `render.py`'s redaction
  backstop (catch high-entropy credentials the pattern list doesn't know).
  Stays here — render-byte churn wants its own freeze window.

### B · Coverage & roster

- **#70 (retitled in 1.1.1)** — replace the retired DB/NL-to-SQL archetype
  with a live SQL-agent target, or explicitly accept the gap and close. The
  only roster archetype dropped un-replaced in 1.0.2.
- **LLM05 specialist target** — downgraded from "known gap" to nice-to-have
  after 1.1 recovered LLM05 on existing targets (4P/6S); add only if a strong
  live candidate appears.
- **`scan_type: framework` (#65 item 5)** — `deployed_agent | framework | sdk`
  in the remit identity table; report framing + scoring guidance acknowledge
  operator-configurable defaults. **Gated on the O5 decision** (ported here from
  the archived `plans/PHASE1_OPEN_ISSUES.md` — the question, verbatim: *uAgents
  is a framework/library, not a single deployed agent; Phase 1 analyzed the
  framework's own runtime posture/defaults. Confirm this framing is what we want
  (vs. scanning a specific example agent built on it)* — one operator paragraph,
  needed regardless.
- **Directional-lean correction** — only if 1.2's anchored check dispositioned
  it as structural-but-uncorrected; otherwise strike.

### C · Output quality & report UX *(no scan-behavior change)*

- **#113** — wrap technical tokens in `<code>` consistently across prose
  fields *(model-output change — schedule before the freeze, with bucket A)*.
- ~~**#27** — finding default-state (collapsed/expanded) + expand/collapse-all.~~
  **Deferred indefinitely** (Steve, 2026-08-05, during 1.2.1: *"Defer [#27]
  indefinitely, but leave it filed - don't close"*) — not scheduled here or
  anywhere; the open issue is the record.
- ~~**#6 remainder** — render polish: finding-card confidence, Medium/Low badge.~~
  **Done in 1.2.1** (finding-card confidence line shipped; Medium/Low→ADVISORY
  collapse documented as intentional; the TXT item had shipped in 1.0.1).
- **#25** — split output-authoring conventions out of `SKILL.md`
  (rendering/MVC split). Refactor only; no output change.

### D · Harness reach & docs *(no baseline impact — may ship earlier as 1.2.x satellites)*

- **#151** — Google Antigravity (`agy` CLI) harness: packaging + docs only,
  engine unchanged. An external contact is waiting; there is no engineering
  reason this must wait for 1.4 — pull forward whenever convenient (a ride
  on the 1.3 satellite is the natural slot).
- ~~**#65 items 6–7** — code-first warning block, mechanism-vs-property rule
  note.~~ **Done in 1.2.1.** **#65 item 8** (absence-of-evidence confidence
  calibration in `KB_RAISE_SCANNING.md`): **being dispositioned in 1.3** —
  Step 8b's verified-absence record likely delivers it; 1.3 verifies and
  records the outcome on the issue.
  **#65 item 3** (25-word summary cap breaks down for compound findings) is
  model-output prose — schedule with #113, pre-freeze.
- ~~**#106** — Out-of-Scope coverage as boundary-rule checks.~~ **Done in 1.2.1.**
- ~~**#226 leftovers** — docs batch.~~ **Moved to the 1.3 satellite**
  (`RELEASE_1.3_PLAN.md`) — docs-only cargo rides the earlier release.
- **#117** — challenging-findings.md additions (gated on #118; collapses to a
  one-paragraph note if #118 isn't adopted) · **#118** operator override +
  finding-revision records (schema-contract change — if adopted, it must ride
  a re-baseline release, this one or later) · ~~**#135** docs simplicity pass ·
  **#4** SKILL authoring aids~~ *(both done in 1.2.1)* · **#90** shared org
  design system · **#2** standing config *(still explicitly deferred)* ·
  **#217** manifest-authoring tooling assist *(robustness RFE — partially
  mitigated by the mid-draft `--validate-manifest` flow; unscheduled, keep on
  the radar)*.

## Sequencing

#198-then-regenerate + remaining A (#104) + #113 + #65 item 3 (everything that
changes findings, scoring calibration, or model prose) → C/D in any order →
**one re-freeze `v1.4-opus5`, graded vs `v1.3-opus5`, last.** Same
discipline as 1.2: nothing that moves numbers lands after the freeze; a stressed
schedule drops whole buckets by dated plan amendment, not by silent descope.

Release mechanics (learned in 1.2.1): the version bump must be followed by
`tests/render/render_all_remits.py` — remit HTMLs stamp the version from
`plugin.json` at render time, a de-facto seventh version surface (analysis
reports are immune; they stamp `praxen_version` from the findings JSON). The
docs tripwire will also flag the `v1.2.1+` install-confirm floors — ride them
forward. `bump_version.py --dry-run` first; it is still not CI-exercised.

## Success metric (first cut — re-triage at 1.2 freeze)

- **Detection:** each bucket-A pattern demonstrated on its proof case (Helm
  seed class, path-traversal class, entropy-caught secret) in the frozen set
  or a fixture.
- **Coverage:** the #70 decision executed (target added and characterized
  median-of-3, or gap formally accepted); coverage pages regenerated with no
  undocumented zero columns (P+S counting, per the 1.2 rule).
- **Stability holds:** the 1.2 gates re-pass on the 1.4 stack — zero watchdog
  deaths on the freeze runs; calibration-target |drift| ≤ 0.2 vs
  `v1.2-opus5`. New detection must not cost the reliability and scoring
  stability 1.2 just bought.

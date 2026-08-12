<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.3 — Thinking Modes + Reproducible Scoring (the accuracy release)

> **STATUS: IN PROGRESS — re-scoped 2026-08-11.** Originally approved
> 2026-08-10 as a score-inert Thinking Modes release. Steve's standing rule for
> #195: *"IF AND ONLY IF we have a strategy for this work that 'works' then
> it's in 1.3."* The condition was met (all gates passed; blind adjudication
> upheld the new pipeline 22/24 — `plans/RESULTS_SCORING_BENCH.md`), so 1.3 is
> now a **scoring release**: it moves numbers and ends in a **`v1.3-opus5`
> re-freeze**. Steve then directed folding in the strongest
> price/performance, low-risk score-moving candidates from the issue list
> (2026-08-11) — they are the pre-freeze riders below.
>
> The Thinking Modes design contract remains **`plans/DESIGN_THINKING_MODES.md`**
> (#197). The scoring-work record is `plans/RESULTS_SCORING_BENCH.md` (six
> rounds + sweep + adjudication) and `plans/REVIEW_SCORING_PROCESS.md` (the
> five-lens review and its all-findings-fixed disposition).

## Objective

Two pillars, one theme — accuracy you can reproduce:

1. **#197 Thinking Modes** — opt-in accuracy tiers (standard / high / x-high)
   operationalizing the proven manual practices: evidence decides membership,
   run-count decides nothing; scores re-derived from the adjudicated evidence,
   never selected or blended; auditor context-unaware. **v1 implemented and
   validated** (FinBot smoke both modes; x-high validation
   `RESULTS_XHIGH_VALIDATION.md`; FP-injection test 4/4).
2. **#195 Reproducible scoring** — scores assigned at Step 9.4 from a
   committed evidence set (Step 5 RAISE NOTES, Step 8b maturity record,
   Step 8.5 THEMES, positives) instead of from a pre-findings working-memory
   pass; KB boundary rules (dominant-path ladder) + provenance test decide the
   adjacent-band calls. **Implemented, gate-validated (3× spread 0.55→≤0.10),
   adjudication-validated (22/24), five-lens reviewed with all confirmed
   findings fixed.**

Because pillar 2 moves numbers, **1.3 re-freezes: `v1.3-opus5`, graded vs
`v1.2-opus5`.** The sweep data says the honest expectation is a systematic
downward shift (mean −0.23 across 12 targets, adjudicated as correction, not
deflation) — every per-target delta ≥ 0.15 gets a documented cause before the
freeze is accepted.

## Contents

### Core (done)

1. **#197 — Thinking Modes v1** per the design. Shipped on this branch;
   x-high adjudicator updated to the 9.4 evidence-set discipline (review fix
   H2).
2. **#195 — scoring restructure** (SKILL.md Steps 5/8b/9.4,
   KB_RAISE_SCANNING.md boundary rules + provenance test) including the
   post-review hardening: evidence persistence in the Step 4 checkpoint, the
   dominant-path ladder, enumerated 8b with fixed search scope.
3. **#48 — close against the #195 work.** Its four asks map onto what
   shipped: control-ledger-before-score = RAISE NOTES + 8b record + 9.4 fixed
   evidence set; 0↔1/2↔3 decision rules = boundary rules/ladder + the
   off-by-default bullets; scoring anchors = the calibration-anchors block;
   themes-gate/score-advisory = release policy since 1.2. Close with a mapping
   comment; no new work.

### Pre-freeze riders — score/finding-moving, land before the freeze

*(Rationale: the freeze re-scans all 12 targets once; anything score-moving
landed before it ships free, anything after costs another re-baseline. Every
item here was either explicitly parked "until the next re-baseline" or is a
small, enumerated fix.)*

4. **#200 — aider remit cleanup.** Hand-apply the five enumerated items (the
   fixes are spelled out on the issue; high-mode audit corroboration already
   posted there). The durable generator fix stays #198/1.4 — this captures
   the accuracy now.
5. **#201 — remaining remit cleanup.** craftbot + uagents: audit-produced fix
   lists already exist (1.3's own high-mode dry-runs). helperbot + salesforce:
   run **cold high-mode audits first** — they are the uncatalogued targets the
   claims ledger names as the missing cold test, so this closes a ledger
   residual and produces the fix lists in one move — then apply.
6. **#41 — named detection pattern:** external API response → filesystem
   write (path-traversal class; hermes CVE-2026-7396 is the proof case), plus
   the per-adapter sampling directive for large adapter surfaces.
7. **#65 item 4 — IaC/deployment artifacts** as first-class Step-4 discovery
   surfaces (Helm values, K8s manifests, Terraform, docker-compose). Also
   verify **item 8** (absence-of-evidence confidence calibration) against the
   shipped 8b verified-absence work — likely already delivered; record either
   way on the issue.
8. **#196 — Step 8.5 fold/break-out tightening:** add the distinct-fix-point
   conjunct to the existing independently-exploitable test (one clause).
9. **#173 (+#174 note) — KB tagging rule:** phantom/inert safety control
   leaving a capability ungated also carries the LLM06 secondary; document
   #174's within-rule edge in the same KB pass. Tag-only; rides the freeze.

### Freeze hygiene — not score-moving, must precede frozen artifacts

10. **#243 — render.py `${VAR}` over-redaction fix** (filed from our own
    x-high validation; unfixed it bakes into every v1.3 byte-gated artifact).
11. **#176 — suite_health.py** data-driven axis/labels/baseline-dir items,
    explicitly gated on "the next re-baseline" — which is this one.

### Riders unchanged from the original plan

12. **#226 leftovers** *(docs-only)* — as originally scoped.
13. **#151 Google Antigravity harness** *(optional, packaging/docs only)* —
    pull in if convenient; dropping to 1.4 needs no amendment.

### Explicitly NOT in 1.3

**#198** (remit generator — durable fix, 1.4, then regenerate), **#104**
(entropy redaction — byte-churn risk), **#113 / #65 item 3** (prose/output
conventions — 1.4 bucket C), **#70** (roster addition — widens the freeze),
**#117/#118** (override records — schema-gated), **#217**, **#90**, **#2**.
If any rider stalls, it drops back to 1.4 by dated amendment — the freeze does
not wait, and nothing score-moving lands after it.

## Gates

- **Scoring (passed, recorded):** Gate 1 cold-target bench; Gate 2 end-to-end
  3× spread ≤ 0.15 (measured ≤ 0.10, hermes 0.00); corpus adjudication 22/24;
  post-review 12/12 unanimous rule replays.
- **Modes (§9, largely passed):** high mode reproduced the 1.2 human-scrub
  catches on 3 targets; FP-injection 4/4 with zero false kills; x-high
  discovery validated (Critical recall 100%). **Open:** the cold audits on
  helperbot/salesforce (item 5 above closes this); §9.2 damping re-test now
  that #195 has landed — run one x-high pair on autogen or uagents post-#195,
  since the prior test attributed its whole delta to the band-edge call #195
  fixed.
- **No collateral damage:** 245 + 42 tests green; `v1.2-opus5` byte-gates
  unchanged until the freeze replaces them; `claude plugin validate` clean.
- **Freeze acceptance:** `v1.3-opus5` = standard-mode median-of-3 per target,
  high-mode audit on each freeze candidate before freezing (the ordering
  rationale that put modes first); every |delta| ≥ 0.15 vs `v1.2-opus5`
  documented with its cause (expected direction: down where maturity evidence
  is absent, up where practice is real); an unexplained delta blocks the
  freeze. Calibration discipline carries over from 1.2.

## Sequencing

1. Riders 4–11 (score/finding-moving first: remits #200/#201 → detection
   #41/#65-4 → decomposition #196 → tagging #173 → hygiene #243/#176).
2. Docs riders (#226, optionally #151) any time.
3. **Freeze `v1.3-opus5` last**, then the §9.2 damping re-test on the frozen
   stack (it is evidence for the release story, not a blocker).
4. Update the claims ledger with the #195 rows before any public copy.

## Release mechanics

Unchanged from the original plan: feature branch → squash to `dev` →
promotion PR (merge commit, FF `dev`) → tag `v1.3.0` → post-tag sandboxed
install smoke (must report 1.3.0) + fresh-agent scan check → blog post — the
story is now *"accuracy you can reproduce": the reviewer (modes) plus the
score that stops wobbling (#195)*. Bump reminders: `bump_version.py --dry-run`
first; re-run `tests/render/render_all_remits.py` after the bump (remits are
the seventh version surface); ride the `v1.2.1+` install-confirm floors
forward.

## Non-goals

No schema change (`scan_mode` still deferred to ride #118), no template
change, no roster change, no remit *generator* change (#198 is 1.4's opener),
no entropy redaction. 1.4 remains the detection-coverage release and now
grades **`v1.4-opus5` vs `v1.3-opus5`**.

<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# 2.0 Threat-Model Pre-Ship Stability Gate — run 1 (2026-08-17)

Eight extractions, four independent pairs, all Opus 5, all via the shipped
`THREAT_MODEL.md` brief verbatim (the product path, not a probe
approximation): finbot ×2, uagents ×2 (scan-scope applied), socxen ×2, and
**craftbot ×2 — the cold target**, never used in any spec-development round.
socxen r1 doubles as the P1.3 end-to-end smoke (identical brief/inputs; it
predates two same-day spec clarifications — noted as a conditions caveat).
Graphs and per-pair comparator outputs are committed beside this file;
measured with `tests/render/threatmodel_compare.py` (`--json`).

## Results vs the gates (RELEASE_2.0_PLAN.md)

| pair | boundary ≥0.9 | status ~90% | component ≥0.7 |
|---|---|---|---|
| finbot | 0.82 ✗ | 0.92 ✓ | 0.76 ✓ |
| uagents | 0.80 ✗ | **1.00** ✓ | 0.68 ✗ |
| socxen | 0.78 ✗ | 0.70 ✗ | 0.63 ✗ |
| **craftbot (cold)** | **1.00 ✓** | **0.95 ✓** | 0.61 ✗ |
| **mean** | **0.85** | **0.89** | **0.67** |

**Verdict: DOES NOT PASS as written.** Status agreement effectively meets
its target (0.89 vs ~90%, with two pairs at 0.95–1.00); boundary and
component fall short. No shading: the thresholds were set in the release
plan and the numbers are the numbers.

## Diagnosis — the misses are concentrated, not diffuse

1. **Boundary (0.85 vs 0.9): one archetype hole accounts for every miss.**
   All three warm-pair boundary deltas are the same persistent-state
   surface coined differently (`state-commit-2` / `data-at-rest` /
   `value-transfer`-adjacent; the probe era coined
   `stored-goals--system-prompt` for the identical surface). The **cold**
   pair — the only one whose target lacks that ambiguous surface — scored
   a perfect 1.00, which is strong evidence the menu works where it has a
   row. Fix: a twelfth archetype (`stored-state`: writable persistent
   state that later feeds decisions/prompts).
2. **Status (0.89, target met in 3 of 4): `partial`'s borders wobble.**
   socxen's 0.70 is entirely X-vs-`partial` disagreements — a one-day-old
   status with zero calibration rounds, on the most control-heavy target,
   with the pair's r1 predating the spec clarifications. Fix: one
   calibration paragraph (when partial vs mitigated vs confirmed at the
   margin), already drafted from the disagreement examples.
3. **Component (0.67 vs 0.7): coinage margins + an honest yardstick.**
   Exact-id matching is strong (16–19 per pair); the shortfall is
   split-prefix choices the cold target exposed (rule 4 fires only on
   same-basename+kind, so four `manager.py` components coexist
   indistinguishably; two-function controls make the prefix depend on
   evidence ordering). Note the comparator is deliberately stricter than
   the probe matcher the 0.7 was calibrated on (the probe matcher
   over-matched); part of this gap is measurement honesty, not regression.

## Also banked from the gate

- **Validator + repair loop worked live**: one run emitted
  `mitigation_evidence` on `potential` threats; the validator rejected it
  with the exact path; a single repair round via the prescribed loop fixed
  it; the ruling is now contract text. Process gap found: repairs rewrite
  in place — the orchestrator should snapshot pre-repair
  (THREAT_MODEL.md amendment queued).
- **KB-precedence convergence**: three runs independently re-derived the
  tag corrections filed as praxen#254/#257, plus consistent ASI07-scoping
  divergences on craftbot — the arbitration rule behaves.
- **Cost (measured, product brief):** 145–220k tokens per extraction,
  mean ~184k ≈ **0.55–0.85× a standard scan** — higher than the probe's
  0.4–0.5× (bigger targets, richer brief). Docs updated at release.
- Ambiguity harvest for the contract: same-basename-any-kind collision
  test, CamelCase kebabing, two-function controls, remit-as-evidence for
  unnamed actors, family-holds-the-base-id clarification, A2A
  inbound/outbound convention, no `signer` kind.

## Disposition

Contract remedies are cheap and precisely targeted; re-gating the three
warm pairs after a contract amendment costs ~6 extractions. Decision on
amend-and-regate vs. re-scoping the gates belongs to Steve and is recorded
in the release plan when made.

---

# Run 2 — contract v1.1 re-gate (2026-08-17, Steve: "amend and re-gate")

Eight fresh v1.1 extractions (all four targets re-paired — craftbot was
re-run too so no v1.0-vintage number survives in the table). Comparator
fixed mid-gate (kind tokens no longer dilute component identity matching —
found live on uagents, regression-tested, disclosed; run-1 numbers were
re-measured under the fixed instrument and did not change). All eight
graphs first-pass valid and render-clean; `partial` calibration and
`stored-state` archetype observed in live use.

| pair | boundary ≥0.9 | status ~90% | component ≥0.7 |
|---|---|---|---|
| finbot | 0.91 ✓ | 0.91 ✓ | 0.83 ✓ |
| socxen | 0.90 ✓ | 1.00 ✓ | 0.81 ✓ |
| uagents | 0.91 ✓ | 1.00 ✓ | 0.63 ✗ |
| craftbot | 0.83 ✗ | 0.94 ✓ | 0.56 ✗ |
| **mean** | **0.888** | **0.962** | **0.709** |

**Deltas vs run 1 (means): boundary 0.85→0.89, status 0.89→0.96,
component 0.67→0.71.** Every v1.0 diagnosis was cured where it was
targeted: the stored-state coinage divergence is gone from all three warm
pairs (boundary 0.90–0.91 each), and socxen's partial-wobble went to a
perfect 1.00. What remains is different in kind: **enumeration-granularity
sampling** — craftbot r1 drew a notably deeper sample (12 boundaries / 34
threats) than its partner (10 / 25), and the two big-workspace targets
(uagents, craftbot) carry real decomposition wobble in component identity
(rule-6-vs-rule-1 overlap on file-backed external services; single-node
files and emitted-vs-file collision scope — all recorded by the runs
themselves as candidate v1.2 clarifications).

**Verdict against the letter of the gates: status passes decisively;
component passes by 0.009; boundary misses by 0.012.** One
boundary-granularity call in one run accounts for the entire boundary
shortfall. n=2 per target makes each pair a two-sample estimate; the
numbers above are reported without adjustment. Ship disposition is
Steve's call and is recorded in the release plan when made.

---

# Run 3 — pre-declaration (2026-08-17, BEFORE any r3 extraction ran)

Steve's disposition: third runs with an all-pairs estimate. Declared ahead
of data: one fresh v1.1 extraction per target (r3); per-target score =
the mean of all three pairwise comparisons (r1–r2, r1–r3, r2–r3) on each
measure; gate = the mean of the four per-target scores against the
unchanged thresholds (boundary ≥0.9, status ~90%, component ≥0.7).
Whatever the numbers say, they ship in this file unadjusted.

## Run 3 — result (computed exactly as pre-declared)

One fresh v1.1 extraction per target (all four first-pass valid,
render-clean); per-target score = mean of the three pairwise comparisons;
gate = mean of the four per-target scores.

| target | boundary | status | component |
|---|---|---|---|
| finbot | 0.939 | 0.908 | 0.815 |
| socxen | 0.933 | 1.000 | 0.819 |
| uagents | 0.876 | 1.000 | 0.644 |
| craftbot | 0.886 | 0.965 | 0.563 |
| **gate mean** | **0.909 ✓** | **0.968 ✓** | **0.710 ✓** |

**VERDICT: PASS.** All three gates met under the estimator declared before
the data existed. The residual, on record: component agreement on the two
big-workspace targets (uagents 0.64, craftbot 0.56) reflects real
decomposition wobble — collapse choices under the node budget, rule-6/rule-1
overlap for file-backed external services — while the boundary and status
layers, the report's security-meaningful content, hold at 0.88–0.94 and
0.91–1.00 per target. The runs' remaining ambiguity notes (edge reuse
across boundaries, listener archetype, rule-4 node-vs-file scope,
prefix-stacking order) are candidate v1.2 clarifications for after 2.0 —
none blocks the contract as shipped.

Twelve v1.1 extractions total across runs 2–3: 12/12 validator-clean (11
first-pass; the run-1 era repair predates v1.1), 12/12 render-clean,
every finding of every target cited in every graph that claims it.

---

# Open design question — hub-and-spoke edge congestion (2026-08-17, Steve)

Human review of the best example (craftbot r3) flagged the orchestrator
fan-out as an unshippable ratsnest: a react-loop agent calls every tool /
store / model, so one-bezier-per-flow yields 8+ near-parallel curves
crossing a narrow lane gap. Structural mismatch between the layout and what
agents ARE, not a routing tweak. Consistent with the gate finding that
edges are the least-valuable, lowest-agreement layer (boundaries + threats
are the contract; edges are illustrative). Candidate directions, to
prototype before the 2.0 renderer freeze:

- **A. Demote flows to a faint arrowhead-less substrate; bold+arrowed only
  for attack-path chains.** Cheapest; reader traces the attack, not every
  flow.
- **B. Bus/trunk routing for the hub** (orchestrator→tools as one branching
  trunk, subway/PCB style). Targets the exact ugliness.
- **C. Orthogonal channel routing** — right-angle traces packed into
  per-lane-gap tracks. Cleanest, most effort, nearest to reinventing a
  layout engine (deliberately avoided so far).
- **D. Collapse the tool lane to one "Tools (N)" node**; per-tool detail
  stays in the inventory + boundary tables (map, not schematic).

Recommendation: **A+B**. Blocks calling the renderer done for 2.0 — the
current output fails human review on dense targets even though it passes
the numeric gate.

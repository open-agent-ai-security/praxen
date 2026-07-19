<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Stage-1 gate — Praxen 1.2 (reliability + decomposition), 2026-07-17

Validates the Stage-1 changes (`plans/RELEASE_1.2_PLAN.md` Stage 1): Step-4 evidence
checkpoint (#65), evidence-completeness invariant, Step-8.5 themes outline (#29),
interleaved emission (#33), `--validate-manifest` (#65), and the follow-up
compound-contributor decidability rule. Gate criteria: **zero watchdog deaths; no
scan near the watchdog; finding-count spread ≤ ±2 on 3× runs** of the two Stage-0
scatter offenders (helperbot spread 3, uAgents spread 4).

## Result: PASS (both targets ≤ ±2, zero stalls) — on the final Stage-1 skill (7753827)

| Target | Stage-0 (old skill) | Stage-1 final (7753827) | spread | gate |
|---|---|---|--:|:--:|
| helperbot | 11/8/10 → range 3 | **8 / 6 / 8** | 2 | ✅ |
| uAgents | 9/10/13 → range 4 | **9 / 8 / 8** | 1 | ✅ |

- **Reliability: zero watchdog deaths across all 9 fixed/tightened-skill runs;**
  durations 8–20 min, heartbeat-before-every-compose held. (The only stalls in the
  whole exercise were on the *pre-fix* skill or in a transient infra-degraded window
  where a lone completion took 64 min — see `../../../local/v1.2-stage1-gate/GATE_NOTES.md`
  for the full attempt log.)
- **Intra-run drift: zero** — every run's Step-8.5 themes outline exactly equalled
  its final finding count.

## The decomposition fix (why uAgents went 4 → 1)

The initial Stage-1 skill did **not** tighten the uAgents count (still 9/9/13). Root
cause, confirmed in the finding JSON (`related_findings`): the admin-exposure
**compound** and its contributing mechanisms (`0.0.0.0` bind, spoofable
`forwarded_allow_ips="*"` guard, default-on inspector) were carved inconsistently —
one run emitted the guard and inspector **both** as standalone findings **and** as
broken-out links of the compound (double-count → 13); the others folded them (→ 9).
The `#29` themes outline made each run internally consistent but left the
count-*determining* fold/break-out decision to a gestalt "independently material"
clause.

Fix (commit `7753827`): a **decidable** test — *would this contributor still be a
finding after the other links are fixed?* Pass → standalone (the public bind);
fail → folded (guard, inspector — only reachable *because* the endpoints are
exposed). Never emit a mechanism both standalone and as a broken-out compound link.
The tightened-skill runs report the rule firing (`compound_contributors_folded` =
2–3 per uAgents run); count collapsed to 9/8/8.

## Honest residual (documented, not a gate failure)

helperbot's spread is **2** on the final skill (8/6/8) — it meets the bar but is
slightly wider than the fixed-skill's 8/9/9 (range 1). The `te=6` run is the low
outlier: it **merged** the key-embed and disclosure-instruction into one finding
(they are the same two prompt lines) and scored the advertised-but-unwired file
tools `enp` rather than a finding — both defensible *tighter* calls. This is a
**different variance axis** from the compound double-count this gate fixed:
Medium-tier **materiality/merge judgment** (is an unwired tool a finding or enp? are
two facets of one prompt one finding or two?). It overlaps Stage-3 (#48) severity/
materiality anchoring and is **carried there**, not chased in Stage 1.

## Severity churn — Stage-3 input, not a Stage-1 metric

Critical-count still swings run-to-run on both targets (helperbot 1–3, uAgents 1–3;
the same finding scored Critical vs High). The Stage-1 gate measures finding *count*
and *reliability*, both of which pass. Severity reproducibility is exactly #48's
target and is deferred there by plan. Logged as a Stage-3 input (see the Stage-2.5
hand-score seed cases).

## Verdict
Stage 1 **passes**: scans are reliable (zero stalls, zero intra-run drift), and
cross-run finding-count spread is within ≤ ±2 on both scatter targets — uAgents
decisively fixed (4→1) by the decidability rule, helperbot at the bar (2) with a
documented Medium-materiality residual routed to Stage 3. Clear to enter Stage 2
(schema arrays #7/#5 + scan-diff tool).

Artifacts here: the 6 final-skill runs' findings JSON + Step-4 evidence checkpoints
(the checkpoints carry the THEMES outlines with the `[folded]`/`[standalone]` marks
— the provenance of each run's decomposition decision).

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

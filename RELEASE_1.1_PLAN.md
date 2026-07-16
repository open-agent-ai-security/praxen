<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.1 — Scoring & Tagging Rigour

> **Descoped 2026-07-12, recorded 2026-07-16** *(the record lagged the decision —
> see `RELEASE_1.1_REVIEW.md`)*: **#48 (bucket A, RAISE scoring rigour) was moved
> out of 1.1 mid-release** and is owned by **1.2 stage 3** (`RELEASE_1.2_PLAN.md`).
> Shipping 1.1 tagging-only keeps `v1.1-claude48` scoring-byte-identical to the
> 1.0.2 median-of-3 — the clean "before" #48 is graded against. What `v1.1.0`
> actually shipped: **#169** (OWASP distillation sharpening + primary/secondary
> layer) and **#111** (tag-label normalization). The scope and checklist below are
> preserved as written pre-descope; strikethroughs mark what moved.

## Objective

**Tightly scoped.** 1.1 fixes the *metadata layer* that sits on top of Praxen's detection —
and **only** that. The 1.0.2 re-baseline (stable detection engine, frozen `v1.0.2-claude48`
reference) surfaced that the two judgment/classification subsystems are **volatile across
runs**, while detection itself is solid and even improved (114 findings vs the prior 107).
1.1 tightens those two subsystems against the unchanged engine, so the fix is **measurable in
isolation** against the stable baseline.

This is **not** the broad functional refactor. Output-quality/stream-flow, schema evolution,
engine reliability, new detection patterns, and harness support are explicitly **deferred to
1.2** (`RELEASE_1.2_PLAN.md`).

**One principle for both halves:** sharpen the **judgment guidance the analyzer reads** —
the RAISE scoring guidance (control-ledger / boundary rules) for #48, the OWASP distillations for #169 —
so identical inputs resolve the same way twice. We do **not** add post-scoring or post-tagging
rules, edit the analyzer's record, or touch the schema. (Same discipline as #117: fix the input,
never the output.)

## The two problems (evidence from the 1.0.2 baseline)

Detection is strong; the noise is in the classification/scoring **metadata**:

1. **Scoring — RAISE weighted maturity.** Run-to-run variance on the "how much credit does a
   *weak-but-present* control earn" judgment, concentrated in **mid-maturity** targets.
   - Evidence: across identical-input runs the widest current spread is **uAgents (σ ≈ 0.245)**;
     **openai-cs** tightened **σ 0.284 → 0.071** after the remit refresh; only **uAgents** and
     **craftbot** still breach their frozen bands. This is what 1.1 targets: **scatter (σ)**.
   - Bounded: the posture *bucket* (Absent/Ad hoc/Partial/Established) is stable for most; σ ≤
     0.15 for the majority. It's the decimal, not the verdict.
   - **Caveat (review finding):** post-1.0.2 the scoring problem is *narrower* than first read —
     most targets sit in-band with no headroom, so #48's reproducibility proof needs the targets
     that still actually move (uAgents, craftbot), not the whole suite.
   - **Directional *lean* is a watch-item, not a 1.1 goal.** A possible category-level bias
     (Zero Trust up, Limit-Your-Domain stricter) shows old→new — but that's *bias*, not scatter:
     a tight cluster can still sit off-center, and σ won't catch it. Measuring bias needs a
     human-anchored reference we don't have, so **1.1 does not gate on lean; lean-correction → 1.2**
     (paired with #48's rubric + a reference anchor). 1.1 adds only a lightweight, non-gating check:
     does the ZT / Limit-Your-Domain category-mean move the *same* direction again vs v1.0.2? If
     yes, it's structural → hand to 1.2.

2. **Tagging — OWASP LLM/ASI classification.** The tagger's per-finding judgment is
   **under-specified**, so real findings under-tag and churn — a *guidance-quality* problem,
   not a mechanics problem.
   - Evidence: untagged findings jumped **7% → 21%** — a *symptom*, not a "no home" class. Most
     untagged are "agent can do a forbidden thing, no accountability," which *is* Excessive Agency
     (LLM06) + often Rogue Agents (ASI10); the guidance just didn't steer the tagger there.
     Adjacent categories also redistributed (ASI02 20→10 / ASI03 19→11 → ASI05 8→13, LLM09 2→5)
     because the boundaries between distillations are fuzzy.
   - Proven cause: **LLM08** — a real vector/embedding finding didn't tag because
     `KB_LLM_TOP10.md`'s LLM08 entry is thinner than the real OWASP LLM08:2025 (no
     embedding-inversion / operationalized poisoning / federated-conflict for it to match).
   - Bounded: detection unaffected (114 vs 107 findings). The behaviors are found; the labels
     churn. (LLM05 is the one category guidance *can't* recover — its output-handling targets were
     retired → 1.2 backfill.)

## Scope — three items, one theme

### A · Scoring rigour (RAISE weighted) — ~~descoped → 1.2 stage 3~~
- ~~**#48** — RAISE scoring rigour: a structured **control-ledger** + **boundary decision rules**
  so the mid-maturity credit call is reproducible. *(The eval's headline critique.)* **Moves
  numbers — intended.** 1.1's scoring half is now **#48 only**.~~ *(Moved out
  2026-07-12 — see the descope note at top. Item 4 of #48 — theme-gate /
  advisory-score — landed early via the post-1.1 cleanup batch.)*

> **#117 moved to 1.2.** The *human-challenge-workflow* docs item (`challenging-findings.md`
> damage-model path + category-score *independence*, not "cascade") is a different axis from
> 1.1's automated run-to-run variance, and its load-bearing dependency (#118, curated-output
> direction) is unsettled. → `RELEASE_1.2_PLAN.md` bucket F, gated on #118.

### B · Tagging consistency (OWASP LLM/ASI)
- **#169** (reframed — was "LLM08 vector/embedding") — **the OWASP distillations are too
  vague/incomplete, so the tagger's judgment churns.** Fix is **guidance specificity, not
  post-tagging rules** (schema-neutral): sharpen the distillations in `KB_LLM_TOP10.md` /
  `KB_AGENTIC_TOP10.md` — complete the thin entries (start with the proven-thin LLM08) and
  disambiguate adjacent-category boundaries (LLM06 vs ASI10 vs ASI02; ASI02 vs ASI05) so the
  judgment resolves the same way twice. The tagger stays a judgment call — **no** forced codes,
  **no** secondary-code counting in the coverage generator, **no** output post-processing.
  *(RAISE category/scoring guidance is #48's surface, not #169's — see A. Same discipline, two KBs.)*
- **#111** — normalize the OWASP tag-label separator in the deterministic layer (cosmetic;
  cross-model/cross-run report consistency). *(Minor — a one-liner, not a co-equal pillar.)*

## Explicit non-goals (→ 1.2)
Output-quality & stream-flow (#33/#29/#113/#27/#25/#6), **schema arrays #7** + validator #5,
new **detection patterns** #104/#41, **engine reliability** #65, harness #151, docs #117/#135/#4/
#118/#90/#2 (#117 gated on #118). See `RELEASE_1.2_PLAN.md`. *(Time-sensitive **#120** — the Gemini review-gate
sunset 2026-07-17 — is pulled **independently** of both 1.1 and 1.2; it does not belong to
either theme.)*

## Prerequisite
Fold **1.0.2** in first. 1.1 is developed **on top of the fresh `v1.0.2-claude48` baseline** —
that stable reference is what makes the volatility visible and the fix gradable. Grading 1.1
against a 0.7.7-era set would reconflate skill and remit change.

## Regression discipline & success metric
Every item here **intentionally moves numbers** — so 1.1 **re-freezes `v1.1-claude48`** at
release, graded against `v1.0.2-claude48`. Success is **reduced scoring variance + correct,
stable tagging**, measured, not just "it ran":
- **Scoring:** mid-maturity run-to-run σ **down** on the targets that still have headroom —
  re-characterize **uAgents + craftbot** ×3+ and show tighter spread than v1.0.2's. (openai-cs
  already tightened 0.284→0.071 post-refresh — it's the existence proof, not a target to re-prove;
  Hermes is already in-band.) *Scatter only — directional lean is tracked, not gated (→ 1.2).*
- **Tagging (health signals, not enforcement):** untagged-rate **down** from 21% toward the ~7%
  prior **because the sharpened guidance steers correctly** — not because a rule backfilled the
  blanks. **Excessive-agency test:** a clear "agent can do the forbidden thing" finding lands on
  LLM06 (+ often ASI10) *without being told to*; if it doesn't, the guidance is still too vague.
  Category coverage **stable across two independent re-scans** of the same target. LLM05 is the one
  gap guidance can't close (retired targets) → 1.2 new-baseline-app add (bucket D).
- **Schema stays `2.0`** — no #7, no forced render-pipeline migration. Detection engine
  (`SKILL.md` analysis logic, `manifest_to_findings.py`, KBs' *detection* content) unchanged
  except the scoring/tagging *guidance* edits.

## Deliverables checklist *(reconciled 2026-07-16 to what v1.1.0 shipped)*
- [ ] ~~#48 control-ledger + boundary rules authored in `SKILL.md`/KB; scoring reproducibility validated~~ *(descoped → 1.2 stage 3)*
- [x] #169 OWASP distillations sharpened (boundaries disambiguated; primary/secondary layer surfaced). *Caveats: the untagged-rate goal was retired as miscalibrated (~22% is the honest floor under the corrected taxonomy — logging/observability are RAISE-only); the LLM08 proof case did **not** land in the anchor (frozen record lacks the vector-store evidence; re-tag can't add it) — #169 stays open, fix lands via the v1.2 re-scan freeze.*
- [x] #111 tag-label normalization in the deterministic layer
- [x] Re-freeze `v1.1-claude48` — by **re-tag of `v1.0.2-claude48`** (scoring byte-identical), not a re-scan; the median-of-3 carries over
- [x] `schema_version` still `2.0`; `test_render.py` + `build.sh` green; CI 3.9/3.12/3.13
- [x] Version bump 1.1.0 (manifests + `PRAXEN_SPEC` + CHANGELOG); coverage pages regenerated
- [ ] ~~Closes: #48, #111, #169~~ *(#111 closed via the post-1.1 cleanup sweep; #48 → 1.2; #169 open until the v1.2 freeze)*

## Fold-down
`1.0.2 → 1.1` first (baseline), then 1.1 work on `1.1`. 1.2 branches from 1.1 once 1.1 is frozen.

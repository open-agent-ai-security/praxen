<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Post-1.1 Cleanup — paper trail + process (docs/process batch)

> Drafted 2026-07-15 from `RELEASE_1.1_REVIEW.md`; **revised 2026-07-16 after
> the LLM08 diagnosis** (see "The LLM08 disposition" below — the original
> bucket A re-tag + re-freeze was dropped as unfixable by re-tagging).
> Companion plans: `RELEASE_1.2_PLAN.md`, `RELEASE_1.3_PLAN.md`.

## Objective

**Close out 1.1's paper trail and process debt before 1.2 builds on it.**
After the 2026-07-16 diagnosis, 1.1.1 contains **no analysis-affecting change
of any kind** — no re-tag, no re-freeze, no KB edit, no scan. Every item is
documentation, issue hygiene, or repo process. By the project's own patch bar
(1.0.1: "no analysis result can change"), this is the only content a 1.1.1 may
carry.

> **Decision (Steve, 2026-07-16): ships as a docs/process batch — no version
> bump, no tag, no functionality.** (The "1.1.1" working name survives only in
> this file's name; there is no `v1.1.1` release.) Per the no-thrash-bumps
> cadence rule; nothing here changes the shipped plugin artifact.

## The LLM08 disposition (was bucket A — investigated, then descoped)

The originally-planned fix — re-classify the vector-store findings and
re-freeze as `v1.1.1-claude48` — was **investigated first and dropped**.
Diagnosis (2026-07-16, from repo history + the frozen records themselves):

- **craftbot-005 (the #169 proof case) cannot be fixed by re-tagging.** Its
  frozen record contains no vector-store evidence at all (the scan compressed
  the persistence chain and dropped the ChromaDB link — evidence cites
  `context.py`/`agent_base.py`, not `embedding_interface.py`/`manager.py`).
  A prose-only classifier has nothing to tag LLM08 from; the checkpoint pass
  that *did* tag it was a fresh code-reading scan. **Root cause: authoring
  completeness (process), not KB text and not classifier churn.** Re-tagging
  cannot recover what the original scan never recorded → the fix is 1.2's
  stage-4 **re-scan** freeze, with an authoring invariant added in 1.2 stage 1
  ("evidence must cite every mechanism in the finding's causal chain").
- **The hermes/salesforce LLM08 secondaries that flipped 1→0 across passes
  are harness churn** — identical inputs, different secondary chips per pass
  (salesforce-001/007 justify LLM08 from prose and lost it; hermes-004 never
  justified it and briefly gained it). Re-rolling those dice in a patch adds
  churn, not correctness → 1.2's freeze anchors secondaries **majority-of-3**.
- **#173/#174 defer with them** — they're prose-decidable, but fixing them
  means a KB edit + re-classification pass + re-freeze, which breaches the
  patch bar for two low-priority nits. They batch into 1.2's tagging pass as
  their own issue text already suggests.

What 1.1.1 keeps from this: **the write-down** (B5, C6 below) so the
diagnosis, the deferral, and the process rule are on the record.

## Scope — two buckets

### B · Paper-trail reconciliation (docs only)

- **B1** — `RELEASE_1.1_PLAN.md`: dated **Descoped** block — #48 moved to 1.2
  bucket G with the "clean before" rationale; strike from scope and
  checklist; check off what actually shipped.
- **B2** — `tests/runs/v1.1-checkpoint/CHECKPOINT.md`: superseded-by note at
  top — its headline numbers (untagged 5%, ASI10 = 27, LLM06 = 50) reflect the
  pre-recalibration over-steer corrected by `26f1cde`/`a158032`; **its LLM08
  0→4 came from fresh code-reading scans, which the prose re-tag that built
  the anchor could not reproduce** (see B5); point to
  `tests/baselines/v1.1-claude48/BASELINE.md` for the shipped policy.
- **B3** — 1.1 CHANGELOG entry (or `BASELINE.md`): one added line — *the
  plan's "untagged toward ~7%" success metric was retired as miscalibrated;
  under the corrected taxonomy (logging/observability → RAISE-only), ~22%
  untagged is the honest floor.* Metrics may be retired; never silently.
- **B4** — `tests/baselines/v1.1-claude48/BASELINE.md`: fix the duplicated "What changed"
  table header; add one honest line to the LLM08 row — *zero in this anchor
  because the frozen records predate the LLM08-aware KB and re-tagging cannot
  add evidence; lands via the v1.2 re-scan (#169).*
- **B5** — **file the LLM08 diagnosis on #169** (comment, dated): root cause
  = authoring completeness + re-tag method limits; acceptance = the craftbot
  vector-store finding carries LLM08 in the **majority of the v1.2 median-of-3
  freeze runs**; #169 stays open until then.

### C · Issue hygiene + process (repo-level)

- **C1 — Close the shipped-but-open issues** with pointer comments:
  #137 (1.0.1), #64 + #116 (1.0.2 targets), #69 (retirement executed),
  #111 (1.1.0), #167 (1.0.2 tracking), #168 (1.1 tracking — close with the
  descope note pointing at 1.2 bucket G). **#70 stays open**, retitled:
  "replace the retired DB/NL-to-SQL archetype" (decision owned by 1.3
  bucket B). **#169, #173, #174 stay open**, each annotated with its 1.2
  disposition.
- **C2 — #178** — `guide/` docs-freshness check in `ci.yml` on every PR
  (release-time backstop stays).
- **C3 — #48 item 4 (docs half only)** — make it official in
  `tests/README.md` + release-gate guidance: **theme-coverage is the
  regression gate; the weighted RAISE score is advisory.** No numbers move;
  directly answers the July assessment's "expert-assisted review, not a
  deterministic gate" framing. (#48 items 1–3 remain 1.2 stage 3.)
- **C4 — #120 (review-gate replacement)** — *Gemini sunset 2026-07-17.*
  Codify the per-PR background-review convention in the repo
  (CONTRIBUTING/workflow note) as the interim gate; a CI-triggered review
  action is follow-on under #120, not a blocker here.
- **C5 — Tag discipline** — release runbook rule: **a published tag is never
  re-pointed** (the v1.1.0 force-update is the one-time exception that
  prompted this); a broken release ships a fast-follow instead.
- **C6 — Baseline-method rule** — add to `tests/baselines/README.md`:
  **re-tag transforms are valid only for prose-decidable corrections; any
  classification that depends on code inspection requires a re-scan.** Frozen
  findings are complete only with respect to the guidance that produced them;
  when guidance outgrows old records, re-scan. (The 1.1 LLM08 regression is
  the case study — link #169.)

## Explicit non-goals (→ 1.2 / 1.3)

Anything that changes analyzer output or the frozen anchor: the LLM08 fix
(1.2 stage 4 re-scan), the authoring invariant (1.2 stage 1), #173/#174 KB
clauses (1.2 stage 4 tagging pass), the KB validity-domain sentence (1.2),
#7/#5, #33/#29, #65, #104/#41, #113, #48 items 1–3, roster changes. **If a
change would alter any byte of `tests/baselines/CURRENT`'s set, it does not
belong here.**

## Success gates

- Every **analysis artifact** in `tests/baselines/v1.1-claude48/` (findings
  JSON, HTML, TXT) **byte-identical before and after** — the whole point;
  verify with `git status` discipline, not assumption. (`BASELINE.md` is the
  one permitted edit — the B4 documentation notes.)
- `python3 tests/render/test_render.py` green (nothing regressed by doc
  edits); CI green including the new #178 check firing on its own PR.
- Issue tracker reflects reality: shipped work closed, deferred work
  annotated with its owning release.

## Deliverables checklist *(executed 2026-07-16, PR #187)*

- [x] B1–B4 doc reconciliation committed
- [x] B5 diagnosis filed on #169 (acceptance criterion recorded)
- [x] C1 issue sweep done (#70 retitled; #169/#173/#174 annotated, held open)
- [x] C2 #178 CI check live (passed on its own PR) · C3 theme-gate docs
      landed · C4 #120 interim gate codified · C5 tag rule in runbook ·
      C6 baseline-method rule in baselines README
- [x] Closed via the C1 sweep: #111/#137/#167/#168/#64/#116/#69; #178 closes
      on promotion to `main`
- [x] Steve's call recorded: docs/process batch, no version bump (2026-07-16)

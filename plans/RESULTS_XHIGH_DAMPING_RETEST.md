<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Results — x-high damping re-test (design §9.2, post-#195)

> **Run 2026-08-12/13**, Praxen **1.3.0** skill on branch `1.3-thinking-modes`, all
> agents Opus 5 (`claude-opus-5[1m]`, identity-gated per run). One target × two
> independent super-runs × three independent scans = **6 scans + 2 adjudications**.
> Target: **Hermes (agent + desktop)**, pinned `b1a2540` / `4e8388a` — chosen because
> #195 left it the **widest-variance target in the suite** (freeze spread 0.55). The
> original §9.2 test used autogen and uagents; #195 has since tightened those to 0.25
> and 0.15, so they no longer stress the question.
>
> ## Headline
>
> **§9.2 PASSES. Damping is demonstrated — pair delta 0.00 against a 6-run raw range
> of 0.70.** Both super-runs derived not merely the same weighted score but the
> **identical category vector** `[3,2,2,3,2,2]`, from raw scans that spread 0.55 (A)
> and 0.40 (B).
>
> This **reverses** `RESULTS_XHIGH_VALIDATION.md` (2026-08-11), where both pairs
> differed by exactly the raw range and damping was recorded as NOT DEMONSTRATED.
> That result's diagnosis — *the residual delta is one band-edge category call, which
> x-high inherits from #195 rather than fixing* — was correct, and the prescribed fix
> worked: repair #195, and damping appears.

## Raw inputs

| Pair | run1 | run2 | run3 | spread | findings |
|---|---|---|---|---|---|
| **A** | 2.30 | 2.60 | 2.85 | **0.55** | 11 · 11 · 9 |
| **B** | 2.15 | 2.55 | 2.45 | **0.40** | 13 · 12 · 9 |

6-run range **0.70**. Raw Critical counts spanned **0 → 3**.

Per-category, the raw runs disagreed on five of six categories at least once. Balance
Your Knowledge Base is the extreme: the six runs drew **1, 2, 2, 3, 3, 3** on one
codebase.

## §9.2 — stability

| Target | Super-run A | Super-run B | Pair delta | 6-run raw range | Damping? |
|---|---|---|---|---|---|
| Hermes | **2.30** (18 findings) | **2.30** (19) | **0.00** | 0.70 | **yes** |

Category vectors: A `[3,2,2,3,2,2]`, B `[3,2,2,3,2,2]` — identical.

**The score is re-derived, not blended.** B's adjudicator recorded it explicitly: 2.30
is *"not the median (2.45), mean (2.38), or any run's value (2.15 / 2.55 / 2.45)."*
A's 2.30 coincides with its run1 but was derived independently from its own Step 8b
sweep and category notes, with Build an AI Red Team resolved by the choose-the-lower
rule after the evidence straddled bands. Two adjudicators, two different finding sets,
two independent maturity sweeps, one answer.

## Why it works now — the mechanism is Step 8b

Both adjudicators independently reported the same thing, unprompted. B's wording:

> My twelve answers match all three raw runs' `MATURITY` blocks on every line — no
> mismatch to record. **That is the one stage of the pipeline showing zero cross-run
> variance.**

A's sweep agreed with all three of its runs on every question; the only divergence was
an M1 file count (106 vs 108 vs ~40 vs ~33 — subtree inclusion, not a classification
disagreement).

That is the causal story. In August, x-high had no stable ground to re-derive scores
from: the finding set varied, the scores were formed pre-findings from working memory,
and the residual delta was a band-edge call with nothing to anchor it. #195's
enumerated M1–M12 lookup returns the **same answers every run**, so two adjudicators
reading materially different finding sets still land on the same scorecard.

**The combined-stack claim is now supportable, and only the combined one.** x-high
alone did not stabilise scores (August). #195 alone narrows raw spread but does not
eliminate it (hermes still spreads 0.55 raw). Together they produce a reproducible
score.

## §9.5 corollary — recall, not precision, is this target's failure mode

Both adjudicators found the same shape independently:

| | single-run findings | refuted |
|---|---|---|
| Super-run A | **9 of 18** | 0 |
| Super-run B | **10 of 19** | 0 |

Roughly half of each super-run's findings were seen by **exactly one scan of three**,
and **not one was refuted**. The runs were not disagreeing about the code — they were
reading different parts of it.

The sharpest instance, from A: **WeCom/Weixin/Yuanbao adapters default `dm_policy` to
`"open"`** while `gateway/run.py:6755` skips the gateway's own default-deny for them —
an unauthenticated public entry point to a terminal-capable agent. **Two runs of three
missed it.** Hermes's own `SECURITY.md:201-205` describes that exact shape as an
in-scope bug.

This is consistent with §9.5's original finding (expected single-run recall 74–93%)
and sharpens it: on a large multi-root target, single-run recall is the dominant
risk, and it is a *discovery* problem that more scans fix — not a judgment problem
that better prompting fixes.

## Adjudication quality

| | entries → rulings | CONFIRMED | UNSUPPORTED | REMIT-DEFECT |
|---|---|---|---|---|
| A | 15 → 18 | 18 | 0 | 0 |
| B | 13 → 19 | 18 | 0 | 1 |

Both adjudicators **split** over-merged union clusters (A: 3 splits, 1 merge; B: 5
splits, 0 merges — one candidate merge considered and rejected on distinct fix-points).
Both ruled severities **against the majority reading** where the evidence warranted:
A raised ingress→shell to Critical (no enforcement point exists at all) and lowered
auto-approval to High (the gate exists and prompts on live paths → `partial`, not
`gap`); B lowered three and raised one.

Refutation was attempted and sometimes bit: A's attempt on `_fire_approval_hook`
(approval.py:41-60) failed — it is a gateway-path plugin notification, not a durable
approval record, so the finding survived. B *refuted two evidence claims inside
confirmed findings* (run1's "`HERMES_CRON_SESSION` never exported" is contradicted by
`cron/scheduler.py:1402`, where cron fails **closed**; run1's "approval decisions never
persisted" by `approval.py:983`) without killing either finding, because a sibling
instance carried the claim on sound evidence.

**One finding was removed, on a remit defect rather than a bad reading** — B's U02b,
where R-10's Trusted Domains closure omits `api.osv.dev` and `api.github.com`, which
the target documents as routine, security-positive operation.

## Remit defects surfaced (feeds #198)

- **R-29 (A)** — the Log Only rule names `desktop.log`, a string with **zero hits
  across every file in both roots**. A sound obligation (durable structured records of
  tool invocations, approval decisions, session lifecycle) welded to an artifact no
  implementation could ever have had.
- **R-10 (B)** — Trusted Domains omits two endpoints the docs describe as routine
  operation, so documented behavior violates the closure.

Consistent with every other audit in 1.3: the defect class is *sound obligation +
over-broad or fabricated extension*, and it never kills a finding that also stands on
a sound rule.

## Tooling defect found en route — `scan_diff.py` under-matches on multi-root targets

Pairwise `scan_diff.py` join rates were **8–36%**, far below what the finding sets
actually shared. Cause: the runs disagree on whether evidence paths carry the workspace
root prefix (`hermes-agent/agent/x.py` vs `agent/x.py`) on this **dual-root** target.
`_evidence_files()` compares raw path strings, and evidence-file overlap is documented
as *"the strongest signal"* — so a prefix mismatch drives that signal to Jaccard 0 and
collapses the whole match below threshold.

Normalizing the prefix took the clusters from 22 → **15** (A) and 21 → **13** (B).

This is **distinct from the documented limitation** (the 0.40 threshold under-matching
rewordings). It is a silent failure that no amount of hand-verification discipline
would lead an operator to suspect, and it would inflate apparent "unique findings" in
any x-high run on a multi-root workspace. Tracked separately; the diff tool is repo-only
(`build.sh:119` excludes `tests/` from the plugin) and is not on the baseline path, so
nothing frozen is affected.

The deeper cause — the **scanner** emitting inconsistent evidence-path conventions on
multi-root targets — is a skill-level change that would alter scan output, and is
deferred to 1.4 rather than landed against a completed freeze.

## Limits

- **n = 1 pair, one target.** Damping is demonstrated here, not established across the
  suite. The honest claim is "demonstrated post-#195 on the suite's widest-variance
  target", not "x-high scores are stable".
- Both super-runs converged on 2.30, which is also A/run1's raw value. Coincidence, and
  the adjudication records show independent derivation — but a second target would be
  needed before treating convergence-to-a-raw-value as anything other than chance.
- The adjudicators were given union worklists built by the same orchestrator using the
  same (defective) diff tool, then hand-corrected the same way. A different union
  construction might present different entries.

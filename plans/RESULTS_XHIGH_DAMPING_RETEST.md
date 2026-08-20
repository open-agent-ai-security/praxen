<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Results — x-high damping re-test (design §9.2, post-#195)

> **Run 2026-08-12/13**, Praxen **1.3.0** skill on branch `1.3-thinking-modes`, all
> agents Opus 5 (`claude-opus-5[1m]`, identity-gated per run). Two targets × two
> independent super-runs × three independent scans = **12 scans + 4 adjudications**.
> Targets: **Hermes (agent + desktop)** `b1a2540`/`4e8388a`, then **Deep Agents Code**
> (`libs/code`) `a80355a` — the two widest-variance targets in the suite. Hermes chosen because
> #195 left it the **widest-variance target in the suite** (freeze spread 0.55). The
> original §9.2 test used autogen and uagents; #195 has since tightened those to 0.25
> and 0.15, so they no longer stress the question.
>
> ## Headline
>
> **§9.2 PASSES, replicated on two targets. Both pair deltas 0.00 against 6-run raw
> ranges of 0.70.** In each case the two super-runs derived not merely the same
> weighted score but the **identical category vector** — hermes `[3,2,2,3,2,2]`,
> deepagents `[2,1,2,3,2,1]`.
>
> | Target | Raw runs | Raw range | Super-run A | Super-run B | **Pair delta** |
> |---|---|---|---|---|---|
> | Hermes | 2.30·2.60·2.85 / 2.15·2.55·2.45 | 0.70 | 2.30 | 2.30 | **0.00** |
> | Deep Agents Code | 2.40·1.85·2.00 / 2.00·1.70·1.70 | 0.70 | 1.85 | 1.85 | **0.00** |
>
> **Deep Agents is the stronger case.** 1.85 appears nowhere in super-run B's raw
> scans (2.00/1.70/1.70), so convergence cannot be an artifact of gravitating to a
> run's value — the coincidence flagged as a limit in the hermes-only draft does not
> recur. Its unions were also built with `scan_diff.py`'s own tuned scorer plus
> union-find, not the hand-clustering hermes required, which removes the other stated
> limit.
>
> This **reverses** `RESULTS_XHIGH_VALIDATION.md` (2026-08-11), where both pairs
> differed by exactly the raw range and damping was recorded as NOT DEMONSTRATED.
> That result's diagnosis — *the residual delta is one band-edge category call, which
> x-high inherits from #195 rather than fixing* — was correct, and the prescribed fix
> worked: repair #195, and damping appears.

## Raw inputs

**Hermes** — 6-run range **0.70**, Critical counts 0 → 3:

| Pair | run1 | run2 | run3 | spread | findings |
|---|---|---|---|---|---|
| A | 2.30 | 2.60 | 2.85 | **0.55** | 11 · 11 · 9 |
| B | 2.15 | 2.55 | 2.45 | **0.40** | 13 · 12 · 9 |

**Deep Agents Code** — 6-run range **0.70**, Critical counts 1 → 3:

| Pair | run1 | run2 | run3 | spread | findings |
|---|---|---|---|---|---|
| A | 2.40 | 1.85 | 2.00 | **0.55** | 13 · 15 · 14 |
| B | 2.00 | 1.70 | 1.70 | **0.30** | 15 · 14 · 13 |

**Balance Your Knowledge Base is the least stable category on both targets.** Hermes's
six runs drew **1, 2, 2, 3, 3, 3**; Deep Agents' drew **1, 1, 1, 2, 2, 2**. On Deep
Agents four of six categories were *identical in every run* (LD 2, ZT 2, SC 3, MON 1),
with the entire spread carried by BK and Red Team. That makes BK a specific
anchor-sharpening candidate for 1.4, rather than diffuse noise.

## §9.2 — stability

| Target | Super-run A | Super-run B | Pair delta | 6-run raw range | Damping? |
|---|---|---|---|---|---|
| Hermes | **2.30** (18 findings) | **2.30** (19) | **0.00** | 0.70 | **yes** |
| Deep Agents Code | **1.85** (20) | **1.85** (18) | **0.00** | 0.70 | **yes** |

Category vectors identical within each target: hermes `[3,2,2,3,2,2]`, deepagents
`[2,1,2,3,2,1]`.

**The two targets vary for different reasons, and both converge.** Hermes's spread is
*recall* — the runs read different parts of a large dual-root tree. Deep Agents' is
*judgment*: its adjudicator recorded that "the entire spread is two categories where
run1 did not apply the KB's dominant-path ladder or the choose-the-lower rule, and
finding-count variance (13/15/14) was decomposition, not discovery." Adjudication
resolves both.

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

## §9.5 corollary — what a single run misses

Both adjudicators found the same shape independently:

| | single-run findings | refuted |
|---|---|---|
| hermes A | **9 of 18** | 0 |
| hermes B | **10 of 19** | 0 |
| deepagents A | **9 entries + 2 split-outs** | 0 |
| deepagents B | **10 distinct claims** | 0 |

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
| hermes A | 15 → 18 | 18 | 0 | 0 |
| hermes B | 13 → 19 | 18 | 0 | 1 |
| deepagents A | 21 → 21 | 21 | 0 | 0 |
| deepagents B | 21 → 21 | 20 | 0 | 1 |

(Rulings column = each record's own verdict summary; deepagents' earlier rows mistakenly
listed findings-out. Split/merge accounting makes any cross-record total ±1 — the invariant
is the UNSUPPORTED column.)

**79 rulings across four adjudications (by the records' own verdict summaries): 0 UNSUPPORTED.** Not one finding rested on a
misread line, a stale reference, or an over-claim. Two were removed, both on
**remit defects** rather than bad readings.

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

- **n = 2 targets, 2 pairs each.** Damping is demonstrated on the two widest-variance
  targets, not established across the suite. The honest claim is "demonstrated
  post-#195 on the two widest-variance targets, both at 0.70 raw range" — not "x-high
  scores are stable".
- The hermes-only limits are **retired by the second target**: convergence-to-a-raw-value
  was ruled out (deepagents B derived 1.85 from 2.00/1.70/1.70), and the hand-clustered
  union was replaced by `scan_diff.py`'s tuned scorer plus union-find.
- Both targets were scanned by the same model (Opus 5) under the same orchestrator. A
  different model, or a genuinely independent operator building the unions, remains
  untested.
- All four super-runs were adjudicated by the same agent *type* with the same brief.
  The brief itself is therefore a shared, untested dependency of the result.

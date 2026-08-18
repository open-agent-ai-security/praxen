<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Results — x-high validation (design §9.2 + §9.5)

> **Run 2026-08-11**, Praxen 1.2.1 skill on branch `1.3-thinking-modes`, all
> agents Opus 5 (`claude-opus-5[1m]`, self-reported). Two targets × two
> independent super-runs × three independent scans = **12 scans + 4
> adjudications**. Targets chosen as the two widest-variance in the suite:
> **AutoGen Code Executor** (frozen 1.55, spread 0.55) and **uAgents**
> (frozen 1.70, band ±0.45, σ≈0.25).
>
> ## Headline
>
> **A single Praxen scan misses roughly 1 in 6 High-severity findings and 1 in 3
> Mediums. X-high finds them.** Expected single-run recall of the adjudicated
> set: **74–93%**. The clearest case: uAgents' `is_user_address()` accepts any
> sender whose address merely *starts with* the string `user` — a
> signature-verification bypass in a cryptographic identity framework — caught
> by **one scan in three**, then verified against the code by adjudication. The
> committed Helm-chart seed that derives both identity and wallet keys was also
> a one-of-three catch. Twelve such rescues across four super-runs, all verified.
>
> **Criticals need no help:** 100% recall in all five x-high runs. A single scan
> reliably finds the headline risks; x-high buys the tail — and the tail
> contains real vulnerabilities.
>
> **Secondary result:** x-high does *not* tighten the weighted RAISE decimal
> (§9.2 passes as literally written — delta inside band — but shows no damping
> vs. raw runs). This matters less than it first appears: Praxen's own release
> policy already makes the weighted score **advisory** and theme coverage the
> gate. The value here is diagnostic — it localises the residual variance to a
> single band-edge category call (#195) and stops us claiming score stability we
> can't support.
>
> Full reasoning below. Artifacts were dry-run working files in the session
> scratchpad (ephemeral); this document is the durable record.

## Raw inputs

| Target | Pair A raw scores | Pair B raw scores | 6-run range | 6-run σ |
|---|---|---|---|---|
| uAgents | 1.70 / 1.85 / 1.70 | 1.85 / 1.70 / 1.70 | **0.15** | 0.071 |
| AutoGen | 1.40 / 1.55 / 1.30 | 1.55 / 1.30 / 1.55 | **0.25** | 0.113 |

Raw finding counts: uAgents 12–14; AutoGen **12 / 19 / 15** (the widest
decomposition spread observed in 1.3 validation).

## §9.2 — stability

| Target | Super-run A | Super-run B | Pair delta | 6-run raw range | Damping? |
|---|---|---|---|---|---|
| uAgents | **1.55** (18 findings) | **1.70** (17) | **0.15** | 0.15 | **none** |
| AutoGen | **1.30** (14) | **1.55** (18) | **0.25** | 0.25 | **none** |

**On both targets the two independently-adjudicated super-runs differ by
exactly the full spread of the six raw scans.** The literal §9.2 criterion
("score delta well inside the target's historical single-run band") is met —
0.15 against a ±0.45 band, 0.25 against a 0.55 spread — but the *intent*, that
adjudication damps score variance, is not demonstrated. With only two
super-runs per target this cannot rule out that they are *more* variable than
raw runs (the expected range of 2 samples is smaller than that of 6 from the
same distribution).

### The residual is one category, not the finding set

Category vectors (LYD / BKB / ZT / MSC / RT / MC):

| Super-run | Vector | Weighted |
|---|---|---|
| uAgents A | 2 · 2 · 2 · **1** · 1 · 1 | 1.55 |
| uAgents B | 2 · 2 · 2 · **2** · 1 · 1 | 1.70 |
| AutoGen A | 2 · 1 · **1** · 2 · 1 · 1 | 1.30 |
| AutoGen B | 2 · 1 · **2** · 2 · 1 · 1 | 1.55 |

**Five of six categories agreed exactly in both pairs.** The entire delta is
one category differing by one point — Manage Your Supply Chain on uAgents
(weight 0.15 → 0.15 delta), Implement Zero Trust on AutoGen (weight 0.25 →
0.25 delta). The delta's *magnitude* is simply the weight of whichever
category flipped.

This localises the problem precisely: **adjudication stabilises findings; it
does not stabilise per-category anchoring**, because the anchor call is a
fresh judgment the adjudicator makes from the adjudicated set, with the same
band-edge ambiguity a single scan faces. That is exactly **#195** (RAISE
band-edge anchors), already scheduled for 1.4 as the fix for these two
targets' wide bands. X-high inherits the problem rather than solving it.

Finding-set convergence, by contrast, is decent: `scan_diff` join 83%
(uAgents, 15/18 matched) and 78% (AutoGen, 14/14 of A matched into B). Every
A↔B difference is **Medium-tier tail**, except AutoGen B's one extra High
(sandbox-escape detection). No unmatched duplicates in any super-run (§9.4
holds).

### Super-run scores trend *below* raw scores

| Target | Raw 6-run mean | Super-run mean | Shift |
|---|---|---|---|
| uAgents | 1.750 | 1.625 | **−0.125** |
| AutoGen | 1.442 | 1.425 | −0.017 |

Mechanism: adjudication **adds** verified findings (nothing was killed on 3 of
4 super-runs; 12 single-run findings were rescued in total), and more evidenced
gaps means lower category scores. The design's stated expectation — "expected
direction: equal or cleaner" — is **wrong in direction**: x-high output is
*more complete, therefore lower-scoring*. Docs must say so.

## §9.5 — discovery yield (the strong result)

Expected single-run recall = Σ(k/3)/N over each adjudicated set, where k is
the number of raw runs that found the finding.

| Super-run | N | Overall | Critical | High | Medium |
|---|---|---|---|---|---|
| AutoGen A | 14 | **92.9%** | 100% | 96.3% | 77.8% |
| AutoGen B | 18 | **85.2%** | 100% | 96.3% | 66.7% |
| uAgents A | 18 | **74.1%** | 100% | 83.3% | 57.1% |
| uAgents B | 17 | **78.4%** | 100% | 83.3% | 60.0% |
| *FinBot (prior)* | *19* | *78.9%* | *100%* | *—* | *rescues all M/L* |

**Critical recall was 100% in all five x-high runs to date.** A single
standard scan reliably finds every Critical; it loses roughly **1 in 6 Highs
and 1 in 3 Mediums**. Overall, a single scan delivers **74–93%** of the
adjudicated set.

This settles the question the FinBot run left open. Criticals do **not** flip,
even on the two widest-variance targets. What the raw runs disagreed about was
**severity assignment** (AutoGen's raw Critical counts of 1/2/3 came from
elevating different Highs, not from finding different things) — a tier
calibration problem, not a coverage problem.

**Recommended public claim:** *a single scan finds the headline risks
reliably; x-high buys the tail.* Do not claim x-high "catches Criticals a
single run misses" — the data says the opposite, and the honest version is
more useful anyway.

## Adjudication quality (qualitative)

- **1 UNSUPPORTED across 69 union entries** (uAgents B: message-history
  pre-validation claim, refuted on `store_message_history` defaulting False),
  0 REMIT-DEFECT verdicts, 4 remit-feedback items to owners.
- **12 single-run findings rescued**, all verified independently; several by
  grep the adjudicator reproduced itself.
- **Severity re-ruled against the majority repeatedly** and with stated basis
  (e.g. AutoGen chmod-0777 M→High on world-write of a rw-mounted workdir;
  phantom-sanitizer C→High because no remit clause obligates screening;
  uAgents Helm seed held below Critical because the value is placeholder-grade
  and `deployment.yaml` never injects the rendered Secret).
- **The uAgents A adjudicator caught an error in the orchestrator's union
  worklist** (an outbound endpoint-validation claim mis-grouped as the inbound
  ACL) and re-split it — the hand-verification rule working as designed.
- **Decomposition rulings differed between the two AutoGen adjudicators** on
  the same evidence (B rejected a three-way carve A had handled differently,
  and split two bundles A left merged). This, plus the category flip, is why
  AutoGen's pair delta is the larger one.

## Actions this run generates

1. **Docs correction (1.3, blocking):** x-high stabilises the *finding set*,
   not the score; its scores trend *lower* than standard-mode, not "equal or
   cleaner". Replace the design §8 and `docs/thinking-modes.md` language.
2. **Claim discipline:** publish discovery yield (Critical 100%, overall
   74–93%); do **not** publish a score-stability claim for x-high until #195
   lands. Update `CLAIMS_LEDGER_1.3.md` Tier 3.
3. **#195 gains a concrete case** — both pair deltas reduce to a single
   band-edge category call; this is the sharpest evidence yet for the anchor
   work, and re-running this validation after #195 is the natural re-test.
4. **#196 gains AutoGen's 12/19/15 carve spread** plus the two adjudicators'
   differing rulings — decomposition instability survives adjudication.
5. **Product bug found in shipped code:** `render.py`'s Never-Reprint-Secrets
   backstop over-redacts a Dockerfile variable *reference*
   (`auth_token="${TOKEN}"`) as if it were a value; hit independently by two
   AutoGen scans. JSON keeps the snippet, HTML/TXT show `[REDACTED]`. File
   against the #104 redaction work.
6. **Upstream candidate (uAgents):** `get_or_create_private_keys` returns one
   freshly generated wallet key while persisting a different one
   (`python/src/uagents/storage/__init__.py:146-150`) — cited by 5 of 6
   uAgents scans and confirmed in adjudication. Worth coordinated disclosure
   to Fetch.ai, independent of Praxen.

## Cost

12 scans + 4 adjudications ≈ **3.4M tokens**, ~2.5 h wall-clock at 6–8
concurrent agents. Per super-run: ~0.85M tokens, ~35–45 min.

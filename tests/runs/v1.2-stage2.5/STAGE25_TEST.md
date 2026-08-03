<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Stage-2.5 TEST — full-suite characterization on the stage-1+2 stack (2026-07-17)

The **TEST** half of the Stage-2.5 STOP·LOOK·TEST gate (`RELEASE_1.2_PLAN.md`).
12 targets × median-of-3 = **36 scans** on the stage-1+2 `1.2` skill @ `9ebbe66`
(schema 3.0), Opus 4.8, sources under `local/v1.2-stage0/src/`. Establishes the
clean, scoring-unchanged **"before" for #48** and doubles as the 3.0 pipeline's
full-suite production proof.

> **Framing (per Steve, critical):** the `v1.1-claude48` frozen baseline is *not*
> ground truth — it is 3 runs of the prior skill, kept to detect change.
> Deviation from it is not error; matching it is not success. The real problem is
> **run-to-run drift** — the same target scoring differently across identical
> runs. **Reliability (low σ) is the metric; frozen-position is not.**

## Reliability — the headline

| target | runs (weighted) | median | **σ** | spread | frozen |
|---|---|--:|--:|--:|--:|
| hermes | 2.55 / 2.55 / 2.55 | 2.55 | **0.000** | 0.00 | 2.85 |
| yaah | 2.45 / 2.55 / 2.45 | 2.45 | 0.047 | 0.10 | 2.30 |
| finbot | 0.90 / 0.75 / 0.90 | 0.90 | 0.071 | 0.15 | 0.90 |
| openai-cs | 1.75 / 1.60 / 1.60 | 1.60 | 0.071 | 0.15 | 1.60 |
| salesforce | 2.15 / 2.00 / 2.15 | 2.15 | 0.071 | 0.15 | 1.70 |
| autogen | 1.70 / 1.55 / 1.55 | 1.55 | 0.071 | 0.15 | 2.00 |
| openhands | 2.30 / 2.15 / 2.15 | 2.15 | 0.071 | 0.15 | 2.30 |
| aider | 2.15 / 1.85 / 2.00 | 2.00 | 0.122 | 0.30 | 2.00 |
| uAgents | 2.00 / 2.15 / 1.85 | 2.00 | 0.122 | 0.30 | 2.00 |
| craftbot | 1.30 / 1.15 / 0.90 | 1.15 | 0.165 | 0.40 | 1.15 |
| helperbot | 0.75 / 1.15 / 1.00 | 1.00 | 0.165 | 0.40 | 0.75 |
| **deepagents** | 2.70 / 2.70 / **3.30** | 2.70 | **0.283** | 0.60 | 2.70 |

**Full-12: mean σ 0.105, median σ 0.071, median spread 0.15.**
- **Reliable (σ ≤ 0.08): 7/12** — finbot, openai-cs, salesforce, autogen, yaah, openhands, hermes.
- **Unreliable (σ > 0.08): 5/12** — deepagents (0.283), helperbot (0.165), craftbot (0.165), aider (0.122), uAgents (0.122).

## Did the stage-1+2 skill reduce *scoring* unreliability? No — and it wasn't meant to.

Stage 1/2 never touched RAISE scoring (#48 is Stage 3). Controlled before/after
on the **5 targets run median-of-3 on both skills** (Stage-0 = old v1.1 skill;
same 3-run protocol, only the skill changed):

| target | OLD σ (v1.1) | NEW σ (stage-1+2) |
|---|--:|--:|
| helperbot | 0.071 | 0.165 |
| craftbot | 0.000 | 0.165 |
| salesforce | 0.122 | 0.071 |
| uAgents | 0.141 | 0.122 |
| deepagents | 0.071 | 0.283 |
| **mean** | **0.081** | **0.161** |

Scoring σ did **not** decrease — directionally it roughly doubled, driven by
craftbot and deepagents. **Statistical caveats (load-bearing):**
- **n=3 per target is far too small to estimate σ** — the OLD/NEW difference is
  within the noise of three-sample std; treat as directional, not significant.
- craftbot's OLD "σ = 0.000" (1.30/1.30/1.30) and deepagents' 2.70/2.70 are
  **3 draws that happened to agree** — they understate the targets' true
  variance, inflating the apparent increase (exactly why frozen isn't truth).
- Plausible real mechanism for a small rise: Stage-1's decomposition/evidence
  changes shift *which findings emit* (e.g. LLM08 now tags craftbot), which
  feeds category scoring — touching findings perturbed scoring indirectly.

**Bottom line: scoring unreliability is unchanged-to-slightly-worse — this run is
the quantified `before`, not a `fix`.** The reduction is Stage-3's (#48) job.

## What the disease actually is — category-credit instability

The 5 unreliable targets never swing on *severity counts*; they swing on **how
much operative controls earn** — a category score crossing a bucket:
- **deepagents** 2.70/2.70/**3.30**: r3 credited controls **Established (3)** where r1/r2 said **Partial (2)** — same findings, TLS gap High all 3 runs.
- **craftbot** 1.30/1.15/**0.90**: Zero Trust flips **1 ↔ 0**.
- **helperbot** 0.75/**1.15**/1.00: the narrow-tool-surface category credit swings **0 ↔ 1**.

This is the **B1/B2 axis** of the hand-score questionnaire (`HANDSCORE.md`) — *how
much does a weak-but-present control earn* — and it is a far narrower, more
attackable target than "scores wobble everywhere." #48's rubric + the human
anchor should drive the unreliable-5's σ down toward the reliable-7's ~0.07.

## Two axes are decoupled — score reliability ≠ finding-count reliability

Finding-count spread per target (median 1.5, mostly tight) but two outliers:
**openhands [6,11,9] spread 5** and **hermes [6,6,10] spread 4** — both have
*rock-stable scores* (σ 0.071, 0.000) yet *unstable finding counts*. Conversely
deepagents has a tight count [6,5,4] but the worst score σ. So decomposition
reliability and scoring reliability are **independent problems**: Stage-1's
compound rule helped decomposition on average (uAgents count-spread 4→1) but
count still varies on openhands/hermes, and it does not touch scoring σ at all.

## Reliability wins that DID land (other axes)
- **Harness: zero watchdog deaths across 36 scans** (2 stalled mid-run, relaunched clean) vs historical ~30% mortality.
- **Decomposition (average): uAgents finding-count spread 4 → 1** via the compound-contributor rule (Stage-1 gate).
- **Formerly-noisiest targets tightened:** openai-cs (documented 0.6↔1.8 swings) → σ 0.071; hermes (2.55↔3.15) → σ 0.000.
- **3.0 pipeline validated at scale:** all 36 emitted schema 3.0, arrays rendered clean, `manifest_to_findings.py` + `render.py` exited 0 every run.

## The `before` for #48 (Stage-3 success target)
- Drive the **unreliable-5** (deepagents, helperbot, craftbot, aider, uAgents) from σ 0.12–0.28 toward the reliable-7 floor (~0.07).
- The lever is **category-credit anchoring** (Partial↔Established, Absent↔Ad-hoc), not severity.
- Grade #48 median-of-3-vs-median-of-3 against **this** set (not v1.1-claude48).

## LOOK-AROUND (recorded)
Reference model Opus 4.8, unchanged. Upstream targets: minor drift only (deepagents
+1 evals commit, uAgents 0.25.2→0.25.3) — immaterial. Sources shallow-cloned to
`local/v1.2-stage0/src/`; hermes pinned to `b1a2540` / `4e8388a`.

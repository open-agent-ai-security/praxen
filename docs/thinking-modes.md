<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Thinking Modes

Praxen supports opt-in **thinking modes** — accuracy tiers, the way LLMs
expose effort levels. The default, **standard**, is the single scan described
everywhere else in this guide. The two higher tiers spend more time and
tokens to buy back the residual [run-to-run
variability](understanding-variability.md) that comes with LLM judgment: they
automate the verification practices Praxen's own release process uses by hand
— an independent false-positive scrub, and multi-run comparison.

| Mode | What runs | Cost (rough) | When to use it |
|---|---|---|---|
| **standard** | One scan | 1× | Default. Everyday scans, exploratory reads |
| **high** | Scan → independent findings audit → cleaned report | ~2× | Before a report leaves your hands |
| **x-high** | 3 independent scans → evidence adjudication → one "super-run" report | ~4–5× | Audits, gates, anything where quality outranks time and tokens |

## What it costs — time and tokens

The two costs move differently, and if you are budgeting tokens the
distinction matters: **parallelism shortens x-high's wall-clock but not its
token bill.** Three scans' worth of tokens are spent whether they run at once
or one after another — running them concurrently only saves you the *waiting*.

| Mode | Wall-clock vs. a scan | Token burn vs. a scan | In practice |
|---|---|---|---|
| **standard** | 1× | 1× | one scan |
| **high** | **~1.3–1.6×** | **~1.4–1.5×** | a scan **plus a few minutes** of audit |
| **x-high** | **~2–2.5×** | **~4×** | ~2 scans' *time*, but ~4 scans' *tokens* |

Early measured data (Opus 5, four real targets — a small dense app and three
production agents):

- A **standard scan** ran **~14–19 min** and burned **~215k–265k tokens**.
- **High mode** added a **~4–10 min / ~90k–135k token** audit on top, finishing
  around **~17–28 min** and **~305k–395k tokens** total.
- **X-high** ran its three scans concurrently (~15 min wall-clock for all
  three) then spent a comparable stretch on adjudication and assembly —
  landing near **~2–2.5×** a single scan's *wall-clock* but **~4×** its
  *tokens* (three full scans ≈ 3× on their own, plus a scan-sized adjudication
  pass), roughly **0.9M tokens** for the run.

Your numbers move with target size, finding count, and evidence density —
subtle production agents audit slower than dense demo apps — but the shape
holds: **high mode buys a false-positive audit for a few extra minutes and
~40% more tokens; x-high buys three-scan stability for about the time of two
scans but the tokens of four.** For a token-constrained budget, choose by the
token column, not the clock.

## Invoking a mode

Modes are selected per-invocation, in natural language — there is no config
file and no standing state:

> "Run a Praxen analysis of `./my-agent` in **high** thinking mode."
>
> "Run an **x-high** Praxen scan of this workspace."

If no mode is named you get standard mode. The skill announces the mode and
its expected cost multiple before starting, so a mis-heard request is visible
immediately.

## What high mode does

1. A complete standard scan runs first — if anything later fails, you still
   have a full ordinary report.
2. A **fresh, context-unaware agent** then audits the findings: it receives
   only the findings JSON, the Worker Remit, and the workspace — none of the
   scan's reasoning — and re-reads every cited artifact trying to *refute*
   each finding. Verdicts are three-way: **confirmed**, **unsupported** (the
   cited evidence doesn't support the claim — the auditor must cite what it
   read that contradicts it), or **remit-defect** (the code honestly violates
   the rule as written, but the rule itself over-reaches or contradicts the
   agent's documented behavior).
3. Unsupported and remit-defect findings are removed and the report is
   re-rendered. Category scores are re-derived only where a removed finding
   was load-bearing.
4. The auditor also checks every cited remit rule against the target's own
   documentation — fabricated obligations, prohibitions of documented
   features, allowlists that documented operation would violate. What it
   finds becomes a **remit feedback** list for whoever owns the remit, even
   when the findings themselves survive on sounder rules.

The audit is deliberately hard to please in one direction only: a kill
requires cited contradicting evidence, "could not verify quickly" counts as
confirmed, and the auditor can neither re-grade severities nor invent new
findings.

## What x-high mode does

1. **Three independent scans** run from scratch — fresh context each, no
   shared state.
2. The finding sets are unioned and matched across runs (by rule text and
   evidence, never by the run-local `R-NN` / `PRAX-…` IDs).
3. A fresh adjudicator applies the high-mode audit to **every** finding in
   the union, then assembles one canonical report — the **super-run** — from
   the findings that survived, re-deriving all scores and prose from that
   adjudicated set.

Two principles govern the merge, and they are worth knowing because they are
*not* voting:

- **Evidence decides membership; run-count decides nothing.** A finding only
  one run caught **stays** if the evidence verifies — that's the discovery
  payoff of running three times. A finding all three runs agreed on **dies**
  if the evidence doesn't hold up.
- **Scores are re-derived, never blended.** The super-run's RAISE scores are
  computed from the adjudicated finding set by the normal scoring rules — not
  the median, mean, or best-of the three raw runs. The result is a real
  single scan's score, computed on better-vetted inputs.

## What you get on disk

Both modes keep full provenance alongside the final report:

- The **final report** (HTML / TXT / findings JSON) — same format and schema
  as any standard scan; nothing downstream needs to change.
- The **raw artifacts** — high mode keeps the pre-audit report with a `-raw`
  suffix; x-high keeps all three runs in `xhigh-run1/2/3/` directories.
- An **adjudication record** (`reports/<agent>-adjudication-<timestamp>.md`)
  — every verdict with its rationale, the remit-feedback list, and (x-high) a
  **variance diagnostic**: what flipped between runs, the per-run score
  spread, and what the adjudication did about it. If you maintain the remit
  or care *why* two runs disagreed, this file is the interesting one.

## Scores and comparability

Thinking-mode scores are **not comparable to standard-mode expectations or
bands**. Praxen's published variance expectations (and its own frozen test
baselines) are standard-mode, single-run artifacts. Compare thinking-mode
runs with thinking-mode runs.

The two modes also stabilize different things, and it matters which one you
reach for:

- **High mode stabilizes the finding set, not the score.** The audit removes
  findings the evidence doesn't support; scores are re-derived only where a
  removed finding was load-bearing. A clean audit (nothing killed) leaves the
  underlying run's category-score draw fully intact — so a high-mode score
  carries the same run-to-run variance as a standard score. Read it as
  *better-verified*, not *more stable*.
- **X-high stabilizes both.** Scores are re-derived from the adjudicated
  union with cross-run disagreements resolved by the scoring rules, so the
  number itself is damped. When a number must be defensible, x-high *is* the
  multi-run discipline the
  [variability guide](understanding-variability.md#when-stability-matters-more-than-runtime)
  describes — with the aggregation done by evidence adjudication instead of
  by score arithmetic.

## Harness support

The modes depend on **genuine context isolation** for the audit — a reviewer
that shares the scan's conversation inherits its confirmation bias and checks
nothing.

- **Claude Code** — full automation: scans, auditor, and adjudicator run as
  subagents.
- **OpenAI Codex** — full automation: sub-agents spawned with a fresh context
  (`fork_turns="none"`).
- **Other harnesses** — a documented fallback: each phase writes its inputs
  to disk and you start a fresh session for the audit phase. Semi-manual, but
  the isolation is real; Praxen won't fake an "audit" in the same context.

## Next steps

- [Understanding Run-to-Run Variability](understanding-variability.md) — the
  variance the modes exist to damp, and what single runs already guarantee
- [Interpreting Reports](interpreting-reports.md) — reading the report the
  modes produce (identical format in every mode)
- [Challenging Findings](challenging-findings.md) — the conversational
  revise-and-re-render workflow, which works in any mode

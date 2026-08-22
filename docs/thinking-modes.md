<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Thinking Modes

Praxen supports **thinking modes** — the same effort dial reasoning models
expose, applied to a whole scan. The default, **standard**, is the single scan
described everywhere else in this guide. The two higher effort levels spend
more time and tokens on verification: an independent audit of every finding,
and — at the top level — three scans adjudicated into one.

| Mode | What runs | When to use it |
|---|---|---|
| **standard** | One scan | Default. Everyday scans, exploratory reads |
| **high** | Scan → independent findings audit → cleaned report | Before a report leaves your hands |
| **x-high** | 3 independent scans → evidence adjudication → one "super-run" report | Audits, gates, anything where quality outranks time and tokens |

## What it costs — time and tokens

| Mode | Time | Tokens | A typical run (Opus 5) |
|---|---|---|---|
| **standard** | 1× | 1× | ~10–22 min · ~215k–265k tokens |
| **high** | ~1.3–1.6× | ~1.4× | ~17–29 min · ~305k–395k tokens |
| **x-high** | ~2–2.5× | ~4× | ~30–35 min · ~0.9M tokens |

Three things worth knowing before you budget.

**Time and tokens do not move together.** High mode adds roughly 40% to the token
bill but usually more than that to the clock. Its audit runs as a fresh agent that
re-reads the source and remit from cold — cheap in tokens, expensive in round-trips.
If someone asks how long a run will take, don't answer from the token figure.

**Concurrency shows up on the clock, never on the burn.** Running scans in parallel
pushes high mode's time multiple toward 1.8× without changing what it spends. The
same effect works in your favour at the top level: x-high runs its three scans
concurrently, so it finishes in about 2–2.5× the time while still spending 4× the
tokens. Parallelism buys back waiting, never burn.

**Both multiples scale with finding count.** The audit re-verifies findings one at a
time, so a dense report costs more to audit than a thin one — a subtle production
agent audits slower than a demo app with obvious holes. Where the phases were timed
separately, the audit came to about 60% of the scan's own wall-clock.

Budget by whichever is scarcer. In tokens, high mode is a modest add and x-high is
not. In time, high mode is the one people underestimate.

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
  computed from the adjudicated evidence — the vetted finding set plus the
  maturity record and category evidence notes the scoring step requires, since
  findings alone cannot see a red team or a telemetry pipeline — by the normal
  scoring rules, not the median, mean, or best-of the three raw runs. The
  result is a real single scan's score, computed on better-vetted inputs.

## What you get on disk

Both modes keep full provenance alongside the final report:

- The **final report** (HTML / TXT / findings JSON) — same format and schema
  as any standard scan; nothing downstream needs to change.
- The **raw artifacts** — x-high always keeps all three runs in
  `xhigh-run1/2/3/` directories. High mode only writes a `-raw` copy when the
  audit actually changed something; if every finding is confirmed, the scan's
  own artifacts *are* the final report and there is nothing to preserve a
  copy of. On a well-tuned remit that is the common outcome, so **no `-raw`
  files is a clean result, not a missing step** — the adjudication record
  below is where you confirm the audit ran.
- An **adjudication record** (`reports/<agent>-adjudication-<timestamp>.md`)
  — every verdict with its rationale, the remit-feedback list, and (x-high) a
  **variance diagnostic**: what flipped between runs, the per-run score
  spread, and what the adjudication did about it. If you maintain the remit
  or care *why* two runs disagreed, this file is the interesting one.

## Which mode, and why

| | Use it to | It stabilizes |
|---|---|---|
| **standard** | Find and fix. One run surfaces most of what is there and everything it reports is dependable. | — |
| **high** | **Sharpen your remit**, and catch the occasional finding the evidence doesn't support. | the finding set (verification) |
| **x-high** | **When a miss would ship.** Release gates, security sign-off, before/after comparison, publishing a number. | the finding set **and** the score |

### High mode's main value is your remit, not false positives

This is the counter-intuitive one. On a mature scanner there is usually little to kill —
across four audited targets the audit confirmed **54 findings and removed none**. In the
same four runs it found **nine defective rules in the remits**: obligations no
implementation could satisfy, prohibitions on behavior the target documents as intended,
allow-lists omitting routine operation, and sound prohibitions welded to over-broad
extensions.

That matters because **a defective rule produces a finding that looks completely real** —
correct file, correct line, an honest violation of the rule *as written*. You cannot spot
it by reading findings. High mode reads your rules against the target's own documentation
and hands back a fix list. Reach for it whenever a remit is new or has just changed; see
[Writing Worker Remits → Advanced](writing-remits.md#advanced-hardening-a-new-remit).

### X-high buys coverage first, stability second

Three scans, unioned, then every candidate re-verified — so the finding set is more
complete than any single run's. That is the primary value: in multi-run studies **about
half of the verified finding set had been seen by only one of the three scans, and none
of those was refutable**. A single run is dependable in what it reports and incomplete in
what it covers.

**It also stabilizes the score, which it previously did not.** Two independent x-high
runs of the same target derived the same weighted score *and the same six category
scores* — reproduced on both of the two most variable targets in the suite, against a raw
single-run range of 0.70 in each case.

Two things to understand about that result:

- **It is the combination that works.** X-high alone did not stabilize scores before the
  1.3 scoring changes, and those changes alone do not eliminate single-run spread. The
  mechanism is that scores are re-derived from an evidence sweep that returns the same
  answers every run, so two adjudicators reading different finding sets still land on the
  same scorecard.
- **The score is re-derived, never blended.** It is not the median, mean, or best of the
  three runs — in one study it was a value that appeared in *none* of them. It is a real
  single-scan score computed on better-verified inputs.

Scope honestly: demonstrated on two targets, one model, one adjudication brief. It is a
measured result, not a guarantee.

## Comparability

**Thinking-mode scores are not comparable to standard-mode bands.** Praxen's published
variance expectations are standard-mode figures; compare thinking-mode runs with
thinking-mode runs. (The `v1.3-opus5` baseline is mostly standard-mode but freezes three of
its twelve targets at a high-mode run — `BASELINE.md` records which, and why.)

**Do not expect a mode to push a score in a consistent direction.** In 1.3 testing,
high-mode runs landed at or **above** their target's median while x-high super-runs
re-derived below it. A mode gives you a better-evidenced score, not a systematically
higher or lower one — **the reproducibility is the property to rely on, not the
direction.**

## Gating on a mode

If you are wiring Praxen into a release process, two recommendations:

1. **Gate on the presence of a Critical finding, not on a score threshold.** A binary
   check is far more robust than a decimal against a line — across the 12-target suite,
   10 of 12 gave the same Critical/no-Critical verdict on every run, while only one
   scored identically on all three.
2. **Consider raising the effort level for the gate scan.** When a Critical verdict does
   flip, it flips toward a **false pass** — in both inconsistent targets the odd run found
   *zero* Criticals where the others found some. Scoped honestly: a separate study measured
   **100% Critical recall in every single run**, and the two flipping targets were never put
   through x-high. Higher effort is a reasonable precaution here, not a measured fix.

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
- [Challenging Findings](challenging-findings.md) — what to do when you
  disagree with a finding, in any mode

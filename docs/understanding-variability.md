<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Understanding Run-to-Run Variability

Run Praxen twice on the *same* agent, with the *same* Worker Remit and the *same* evidence, and the two reports will not be byte-identical. The themes will be the same, but **the two runs will not find exactly the same set of findings**, and the weighted RAISE score will shift a little. This page explains why, how much to expect from measured data, and — the part that matters most — **what to do when a miss would be expensive**.

The single most useful thing to know up front: on a large codebase, the dominant variability is not the decimal on the score. It is **coverage** — two runs read different parts of the tree. Praxen has a mode built for exactly that, and [Thinking Modes](thinking-modes.md) is where to go when completeness matters.

## Where the variability comes from

A Praxen analysis has two stages, and only one of them varies. **Stage 1 — synthesis** is an LLM job (your coding agent running the skill): reading the code, deciding what is and isn't a finding, judging severity, and assigning the six RAISE category scores are all *acts of judgment*, and the same model won't make every borderline call identically every time — much as two equally-qualified reviewers would write similar-but-not-identical reports. **Stage 2 — rendering (`render.py`)** is deterministic: the same `findings.json` always produces byte-identical HTML/TXT. So all the variability lives in the Stage-1 synthesis, captured in `findings.json`. (See [Interpreting Reports](interpreting-reports.md) for the full two-stage picture and diagram.)

### Two flavours: variance and drift

- **Variance** — run-to-run scatter on a *fixed* model. Re-running the same analysis lands in a slightly different place each time.
- **Drift** — a *systematic* shift when the underlying model changes (a model upgrade, a different model tier). A newer model may, for example, credit a partially-implemented control slightly more or less generously than the one before it. Drift moves the centre point; variance is the scatter around it.

Both are normal. Both are larger for *judgment-sensitive* targets (see below) and smaller for clear-cut ones.

> **Don't compare absolute scores across model tiers.** Praxen's RAISE bands are calibrated against a specific model tier, so drift means the same target can land a few tenths higher or lower on a different model. Compare scores only *within* a fixed model; when you move to a new model tier, treat it as a **re-baseline**, not a regression or an improvement. (This is why Praxen's own frozen test baselines are pinned to a named model.)

## How much to expect

The figures below are measured, not estimated — from the 36-run 12-target regression
suite, plus a dedicated 12-run study on the two most variable targets.

| What | Stability | Measured |
|---|---|---|
| **Themes** | **High** | The classes of divergence a report describes reproduce run to run. |
| **Individual findings** | **Moderate — this is the big one** | A single run surfaces most of what is there, not all. In multi-run studies **~half** of the verified finding set had been seen by only one scan of three. |
| **Weighted RAISE score** | Moderate | Across the suite, three runs of a target spread **0.00–0.55**, median **0.20**. Six runs of the two *most* variable targets spanned **0.70**. |
| **Per-category 0–5 scores** | Lower at the margins | Concentrated, not diffuse: on one target four of six categories were **identical in every run**, with the whole spread carried by two. **Balance Your Knowledge Base** is the least stable category measured. |
| **Severity of a given finding** | Moderate | The same defect can be graded Critical in one run and High in another. Reclassification, not disappearance. |
| **Rendered HTML / TXT** | Exact | Byte-identical for a given JSON. No variability. |
| **`R-NN` rule IDs** | Run-local | Renumbered every run. Compare by rule **text**, never ID. |

**Judgement-sensitive targets vary more.** Where a target has *operative-but-imperfect controls* — a framework that ships guardrails the example doesn't wire up, a sandbox with permissive defaults, a partial mitigation — the "how much credit does this earn?" call is genuinely ambiguous, and that's where the weighted score moves most between runs. Well-engineered agents (controls clearly present and operative) are the *most* reproducible, because there's little to debate. Targets in the messy middle are the least.

**Read the themes, not the decimal.** A weighted score of 1.3 on one run and 1.5 on the next is the *same posture* described with normal judgment scatter. A maturity **label** that changes (e.g. *Ad hoc* ↔ *Partial*) right at a band boundary is the same story — the boundary is a round number, not a cliff.

**But do not read a shorter finding list as good news.** If a re-scan reports fewer Criticals, the likeliest explanation is that this run read less of the tree, not that the agent improved. Comparing two scans for *change* is a job for a mode that stabilizes the finding set — see below.

## Following up with the LLM

Because synthesis is an LLM step, you can interrogate it in conversation — ask the agent to explain a score, re-examine a finding against its evidence, or re-evaluate a category. When you still disagree with what you find, [Challenging and Revising Findings](challenging-findings.md) covers the structured paths: add evidence and re-run, tighten the remit, or accept the risk on the record.

The move specific to *variability*: **re-run the whole analysis** and see whether a borderline result reproduces. If it holds, it's real; if it swings, the target is judgment-sensitive (above) and worth characterising over several runs — see below.

## When a miss would be expensive

A single run is the right default. It is fast, it is cheap, and what it reports is
dependable — it is what it *omits* that varies. So the question to ask is not "how
precise is this number" but **"what does it cost me if this scan missed something?"**

| Your situation | Reach for |
|---|---|
| Understanding an agent; fixing what's obviously broken | **standard** — one run |
| Your remit is new, or findings look wrong | **[high](thinking-modes.md)** — audits every finding *and* checks your remit's own rules against the target's docs |
| Release gate, security sign-off, before/after comparison, publishing a number | **[x-high](thinking-modes.md)** — three scans, adjudicated into one |

**One run to understand an agent; x-high to gate one.**

### Gate on Criticals, not on the score

If you are wiring Praxen into a release process, gate on **the presence of a Critical
finding**, not on a score threshold. A binary "is there at least one" is far more robust
than "is this decimal above a line": across the 12-target suite, **10 of 12** targets gave
the same Critical/no-Critical verdict on every run, while only one target scored
identically across all three.

**Know the failure direction.** In the two suite targets whose verdict was *not* consistent,
the odd run found **zero** Criticals where the others found some — so when a Critical gate
does flip, it flips toward a **false pass**, which is the outcome a gate exists to prevent.

If that matters for your pipeline, raise the effort level for the gate scan. Be aware of what
is and isn't measured: in a separate multi-run study, **single runs recalled 100% of Criticals
in every case** — so Critical-level recall held there. The zero-Critical runs above are from
different targets that were never put through x-high. Treat higher effort on a gate scan as a
reasonable precaution, not as a measured fix for this specific failure.

### Characterising a judgment-sensitive target

Running the same analysis N times is a **diagnostic** — it tells you how much a given
target's score moves and which categories are doing the moving. It is not a way to
manufacture a reported number.

**Do not average, median, or blend scores across runs.** One scan produces one score;
that is the product. A mean of three runs is not a score any scan produced, and it hides
the spread instead of reporting it. If you run N times to characterise a target, publish
**the range**, and say it is a range.

x-high is the supported way to get a single defensible number: it re-derives the score
from an adjudicated evidence set by the ordinary rules — **not** by averaging the three
runs it started from.

**And it measurably works.** In a controlled study, two *independent* x-high runs of the
same target derived the same weighted score **and the same six category scores** — twice
over, on the two most variable targets in the suite, against a raw single-run range of
0.70 in both cases. Scope: those two targets, one model, one adjudication brief. It is a
demonstrated result, not a general guarantee.

### Comparing two runs mechanically: `scan_diff.py`

Step 4's theme-and-rule-text diff has a tool. `tests/scan_diff.py` (in the
[source repository](https://github.com/open-agent-ai-security/praxen) — it is a
maintainer/CI utility, so it ships in the repo rather than the release zip)
joins two findings-JSON files from the *same target* and reports what is
**new**, **resolved**, and **unchanged** — matching findings on their
remit-anchored rule references and text similarity rather than on `R-NN`
numbering, which is run-local and renumbers freely:

```bash
python3 tests/scan_diff.py reports/run-a-findings.json reports/run-b-findings.json
python3 tests/scan_diff.py --json run-a.json run-b.json   # machine-readable
```

Use it to compare a re-scan against last month's scan of the same agent (what
actually changed?), or two same-day runs (how much is wobble?). It is a
mechanical join, not a judgment: two findings it calls "the same" may still
differ in severity or score, and that difference is exactly what you want to
read by hand. Requires schema-3.0 JSON (Praxen 1.2+) on both sides.

Two limits worth knowing. Its join threshold **under-matches rewordings**, so treat
anything it reports as unique as a candidate to verify by hand, not a fact. And on a
**multi-root workspace** — a target scanned as two sibling checkouts — runs may disagree
about whether an evidence path carries the root prefix; matching is suffix-aware from
1.3 onward, but older versions silently under-joined such targets.

## What is **not** variable

To be clear about the guarantees:

- **Rendering is deterministic** — same JSON → byte-identical HTML/TXT, every time.
- **The schema is fixed** — every report has the same sections, the same six RAISE categories, the same OWASP tag vocabulary.
- **Themes reproduce.** The *story* a report tells about an agent — the classes of divergence, the shape of its posture — is stable. What is on the list can move; what the list is *about* does not.

### Coverage is what varies

**Expect a single run to surface most of what is there, not all of it** — and plan around
that rather than against it. Individual findings do not all reproduce.

Measured: across two targets scanned six times each, raw Critical counts ran
`[1, 3, 0, 3, 2, 2]` and `[2, 2, 1, 2, 3, 3]`. Across four independent adjudications,
**roughly half of every verified finding set had been seen by exactly one scan of three —
and not one of those was refutable.**

This is a **coverage** limit, not a correctness one. What a single run reports is
largely dependable: across every adjudicated ruling in those four studies, **not one** was
unsupported by its evidence. False positives are not unheard of — a separate multi-run
study did produce one, out of 69 candidate findings — but they are rare next to what a
single pass misses. It is what a single run *omits* that varies most.

So the useful question is not "how much does the number wobble" but **"how complete is one
read?"** — and that has a direct answer: [x-high](thinking-modes.md) adjudicates three
scans into one, which is precisely what closes the gap.

### One extra source of variance: an ambiguous subject

If the workspace holds more than one agent's worth of code — a monorepo, an
example inside a framework, a two-repository agent — and you *don't* declare
which part is the subject, two runs can legitimately disagree about **what they
scanned** (one grades the whole tree, another just your package), and that moves
the score far more than the per-category judgment wobble above. This is
avoidable, not inherent: declare the subject with a `SCAN_INSTRUCTIONS.md`
(see [Writing Remits → Declaring what to scan](writing-remits.md#declaring-what-to-scan-monorepos-and-multi-agent-trees)).
With the subject declared, the *scope* is stable run-to-run; the residual is
just the ordinary category variance. Declaring the subject fixes *which agent
gets scanned* — it does not make the score itself deterministic.

## Next steps

- [Thinking Modes](thinking-modes.md) — the **high** and **x-high** effort levels: what each stabilizes, what each costs
- [Interpreting Reports](interpreting-reports.md) — what each section means and how to read the maturity score
- [Challenging and Revising Findings](challenging-findings.md) — the full revise-and-re-render workflow
- [The RAISE Framework](RAISE.md) — the six-category 0–5 maturity scale the weighted score is built from

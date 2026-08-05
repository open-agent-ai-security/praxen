<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Understanding Run-to-Run Variability

Run Praxen twice on the *same* agent, with the *same* Worker Remit and the *same* evidence, and the two reports will not be byte-identical. The big findings will be the same; the exact severity counts and the weighted RAISE score may shift a little. This is expected, and this page explains why, how much to expect, and what to do when you need a more stable number.

## Where the variability comes from

A Praxen analysis has two stages, and only one of them varies. **Stage 1 — synthesis** is an LLM job (your coding agent running the skill): reading the code, deciding what is and isn't a finding, judging severity, and assigning the six RAISE category scores are all *acts of judgment*, and the same model won't make every borderline call identically every time — much as two equally-qualified reviewers would write similar-but-not-identical reports. **Stage 2 — rendering (`render.py`)** is deterministic: the same `findings.json` always produces byte-identical HTML/TXT. So all the variability lives in the Stage-1 synthesis, captured in `findings.json`. (See [Interpreting Reports](interpreting-reports.md) for the full two-stage picture and diagram.)

### Two flavours: variance and drift

- **Variance** — run-to-run scatter on a *fixed* model. Re-running the same analysis lands in a slightly different place each time.
- **Drift** — a *systematic* shift when the underlying model changes (a model upgrade, a different model tier). A newer model may, for example, credit a partially-implemented control slightly more or less generously than the one before it. Drift moves the centre point; variance is the scatter around it.

Both are normal. Both are larger for *judgment-sensitive* targets (see below) and smaller for clear-cut ones.

> **Don't compare absolute scores across model tiers.** Praxen's RAISE bands are calibrated against a specific model tier, so drift means the same target can land a few tenths higher or lower on a different model. Compare scores only *within* a fixed model; when you move to a new model tier, treat it as a **re-baseline**, not a regression or an improvement. (This is why Praxen's own frozen test baselines are pinned to a named model.)

## How much to expect

The stable signal is the **finding set**; the noisy signal is the **exact numbers**.

| What | Stability | What to expect |
|---|---|---|
| **Dominant findings / themes** | **High** | The material findings — the Criticals, the headline divergences — reproduce run to run. If a finding is real, it shows up every time. |
| **Severity counts** (C/H/M/L/I) | Moderate | Expect a swing of roughly **±2–3 in a bucket** between runs, mostly from Critical↔High reclassification and borderline finding consolidation. |
| **Weighted RAISE score** | Moderate | Typically within **±0.3** of its centre, occasionally up to **±0.5** for judgment-sensitive targets — usually less than half a maturity-band step. |
| **Per-category 0–5 scores** | Lower at the margins | The `0↔1` ("absent vs ad-hoc") and `2↔3` ("partial vs established") boundaries are where most of the wobble lives. |
| **Rendered HTML / TXT** | Exact | Byte-identical for a given JSON. No variability. |
| **`R-NN` rule IDs** | Run-local | The rule numbering is re-derived each run; the *same* remit clause can get a different `R-NN` in two runs. Compare by rule **text**, not ID. |

**Judgement-sensitive targets vary more.** Where a target has *operative-but-imperfect controls* — a framework that ships guardrails the example doesn't wire up, a sandbox with permissive defaults, a partial mitigation — the "how much credit does this earn?" call is genuinely ambiguous, and that's where the weighted score moves most between runs. Well-engineered agents (controls clearly present and operative) are the *most* reproducible, because there's little to debate. Targets in the messy middle are the least.

**Read the themes, not the decimal.** A weighted score of 1.3 on one run and 1.5 on the next is the *same posture* described with normal judgment scatter. A maturity **label** that changes (e.g. *Ad hoc* ↔ *Partial*) right at a band boundary is the same story — the boundary is a round number, not a cliff. What should *not* change between runs is the set of material findings and the Critical themes; if those move, that's signal, not noise.

## Following up with the LLM

Because synthesis is an LLM step, you can interrogate and revise it in conversation — ask the agent to explain a score, re-examine a finding against its evidence, or re-evaluate a category, and it re-emits the findings JSON. That workflow (and why you revise the manifest/JSON rather than the HTML) is covered in [Challenging and Revising Findings](challenging-findings.md).

The move specific to *variability*: **re-run the whole analysis** and see whether a borderline result reproduces. If it holds, it's real; if it swings, the target is judgment-sensitive (above) and worth characterising over several runs — see below.

## When stability matters more than runtime

A single run is the right default — it's fast and cheap, and for reading an agent's posture the themes are what matter. But when the *number itself* matters — gating a release, freezing a baseline, comparing before-and-after, or reporting a maturity score to a stakeholder — trade some runtime and token cost for stability:

1. **Run the analysis N times** (3 is a good default) on identical inputs. Keep the Worker Remit and the analyzed scope *byte-identical* across runs so you're measuring synthesis variance, not input differences. *(The findings JSON is keyed by date — one per agent per day — so same-day reruns overwrite it; copy each run's JSON aside, or read from the always-timestamped HTML, if you want to keep all N.)*
2. **Aggregate the score** — report the **median (or mean) weighted score**, and note the **range**. A target whose three runs land at 1.3 / 1.4 / 1.3 is well-characterised; one that lands 1.0 / 1.6 / 1.2 is telling you it's judgment-sensitive — report the spread, don't pretend the single number is precise.
3. **Union the findings** — take the set of material findings that appear across runs. A Critical that appears in all three is solid; one that appears in one of three is worth a closer look (often a real edge case, occasionally an over-call) — a good candidate to [follow up with the LLM](#following-up-with-the-llm).
4. **Diff by theme and rule text, not by score or rule ID.** Run-to-run, compare which Critical themes are present and which remit clauses are flagged; ignore `R-NN` renumbering and small decimal moves.

The cost is real and linear: three runs is roughly three times the tokens and wall-clock of one. Spend it when a stable, defensible number is worth more than the runtime — and skip it for exploratory or one-off reads, where a single run and a focus on the findings is enough.

> **Rule of thumb.** One run to *understand* an agent; multiple runs to *grade* one.

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

## What is **not** variable

To be clear about the guarantees:

- **Rendering is deterministic** — same JSON → byte-identical HTML/TXT, every time.
- **The schema is fixed** — every report has the same sections, the same six RAISE categories, the same OWASP tag vocabulary.
- **Real findings reproduce** — a genuine Critical does not vanish on the next run. Disappearing material findings or dropped Critical themes are *not* normal variance; treat them as something to investigate.

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

- [Interpreting Reports](interpreting-reports.md) — what each section means and how to read the maturity score
- [Challenging and Revising Findings](challenging-findings.md) — the full revise-and-re-render workflow
- [The RAISE Framework](RAISE.md) — the six-category 0–5 maturity scale the weighted score is built from

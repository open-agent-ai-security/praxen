<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v0.7.7-claude48

Frozen runs of all **eleven** test targets ([`../../README.md`](../../README.md)) on the **Praxen v0.7.7** skill, against the intent-level Worker Remits (`tests/remits/*.md`), executed on **Anthropic Claude Opus 4.8**. Becomes the comparison point for the release review, **superseding [`../v0.7.7-sequential/`](../v0.7.7-sequential/BASELINE.md)** (the same skill on Opus 4.7), which is retained on disk for diff archaeology.

**The skill is unchanged.** `SKILL.md`, `schema.py`, `render.py`, `manifest_to_findings.py`, and the four knowledge bases are byte-identical to the `v0.7.7-sequential` set. The only variables that moved between the two sets are **(a) the model** (Opus 4.7 → 4.8) and **(b) the freeze method** (see below). This set isolates the model's effect on the analysis.

## The freeze method — median-of-3 (the more robust process)

A single full-suite run is a noisy way to freeze a baseline: parts of the analysis are LLM judgement (severity classification, the six RAISE category scores), so the *weighted score* of any one run carries run-to-run variance even though the *finding set* is stable. A single snapshot can catch several targets at simultaneous high (or low) draws and mis-state where a target really sits.

So this set was **characterized over three independent runs per target** (33 runs total), holding the skill, sources, and remits constant:

- **The committed exemplar for each target is its median run** — the JSON/HTML/TXT frozen here is one real, unedited run whose weighted score is the median of the three. (Where two runs tie at the median, the earliest is taken.)
- **The per-target bands in [`../../README.md`](../../README.md) are set from the 3-run mean ± observed spread**, not from any single run.
- This is now the recommended re-baseline procedure — see [`../../README.md`](../../README.md) §"Re-baselining (multi-run characterization)".

## What changed vs v0.7.7-sequential (the 4.7 set)

Opus 4.8 carries a **mild, systematic upward lean in weighted RAISE** — mean **+0.22** across the eleven 3-run means (a single snapshot suggested +0.31; the multi-run mean is the truer figure). The lean follows an **inverted-U by maturity**: it is largest on **mid-maturity production targets** where "how much credit does a real-but-imperfect control earn?" is the judgement call (openai-cs +0.38, sweep +0.45, langchain +0.50, autogen +0.30, aider +0.70), and **near-zero or negative at the extremes** — the deliberately-vulnerable anchors have nothing to over-credit (finbot 0.00, devika −0.05, helperbot +0.15) and the most-mature target actually scores slightly *lower* (openhands −0.25). 4.8 reads code at least as carefully as 4.7 (in the finding-level review it corrected several 4.7 errors and de-duplicated overlapping Criticals) and **dropped no Critical theme on any of the 33 runs.**

Five per-target bands were widened or moved to fit the 4.8 means; the other six were unchanged (their 4.8 means sit well inside the existing bands):

| Target | band (was) | band (now) | why |
|---|---|---|---|
| aider | 1.1–1.8 | **1.8–2.4** | stable overshoot — mean 2.10, σ 0.087 (a genuine maturity re-read, not noise) |
| langchain-sql | 0.7–1.4 | **0.9–1.6** | stable mild overshoot — mean 1.50, σ 0.087 |
| sweep | 0.7–1.3 | **0.9–1.4** | mean 1.35, σ 0.087 (marginal) |
| openai-customer-service | 0.6–1.3 | **0.7–1.7** | widened, not moved — mean 1.28 is in-band but σ 0.284 is the suite's highest; band widened so high draws don't false-fail |
| openhands | 1.8–2.5 | **1.7–2.5** | floor lowered — mean 1.80, 2 of 3 runs at 1.75 |

## The eleven baselines (committed median exemplar)

Sorted by weighted RAISE, ascending.

| Target | Critical | High | Medium | Low | Info | Weighted | Maturity |
|---|--:|--:|--:|--:|--:|--:|---|
| finbot | 7 | 4 | 3 | 0 | 0 | 0.45 | Absent |
| helperbot | 3 | 3 | 2 | 0 | 0 | 0.60 | Absent |
| devika | 5 | 5 | 2 | 0 | 0 | 0.60 | Absent |
| openai-customer-service | 3 | 3 | 2 | 0 | 0 | 1.20 | Ad hoc |
| sweep | 4 | 3 | 2 | 0 | 0 | 1.30 | Ad hoc |
| langchain-sql | 1 | 2 | 3 | 0 | 0 | 1.45 | Ad hoc |
| autogen-code-executor | 4 | 5 | 3 | 0 | 0 | 1.45 | Ad hoc |
| openhands | 2 | 3 | 2 | 0 | 0 | 1.75 | Ad hoc |
| aider | 2 | 4 | 3 | 0 | 0 | 2.15 | Partial |
| deepagents-cli | 0 | 3 | 4 | 0 | 0 | 2.15 | Partial |
| yaah | 0 | 5 | 3 | 0 | 0 | 2.30 | Partial |

## Stability across the three runs

Per-target weighted RAISE over the three independent runs (the committed exemplar is the **median**):

| Target | run a / b / c | mean | **std** | range | vs 4.7 |
|---|---|--:|--:|--:|--:|
| finbot | 0.60 / 0.30 / 0.45 | 0.45 | 0.150 | 0.30 | 0.00 |
| helperbot | 0.75 / 0.60 / 0.45 | 0.60 | 0.150 | 0.30 | +0.15 |
| devika | 0.60 / 0.60 / 0.45 | 0.55 | 0.087 | 0.15 | −0.05 |
| openai-customer-service | 1.60 / 1.05 / 1.20 | 1.28 | **0.284** | 0.55 | +0.38 |
| sweep | 1.45 / 1.30 / 1.30 | 1.35 | 0.087 | 0.15 | +0.45 |
| langchain-sql | 1.45 / 1.60 / 1.45 | 1.50 | 0.087 | 0.15 | +0.50 |
| autogen-code-executor | 1.60 / 1.45 / 1.30 | 1.45 | 0.150 | 0.30 | +0.30 |
| aider | 2.00 / 2.15 / 2.15 | 2.10 | 0.087 | 0.15 | +0.70 |
| deepagents-cli | 2.15 / 2.15 / 2.15 | 2.15 | **0.000** | 0.00 | +0.15 |
| openhands | 1.90 / 1.75 / 1.75 | 1.80 | 0.087 | 0.15 | −0.25 |
| yaah | 2.30 / 2.30 / 2.15 | 2.25 | 0.087 | 0.15 | +0.10 |

**Most stable: deepagents-cli** (σ 0.000 — identical three times). **Least stable: openai-customer-service** (σ 0.284, ~3× the rest) — the lone high-variance target, matching the README note that flags it as a 0.6↔1.8 swing, and the prime exhibit for the per-category scoring-rigour work (RFE [#48](https://github.com/open-agent-ai-security/praxen/issues/48)). Ten of eleven targets vary by std ≤ 0.15. **Variance and band-offset are independent axes:** `aider` is *stable but offset* (σ 0.087, needs a band move); `openai-cs` is *noisy but centred* (mean in-band, needs a wider band).

## Run notes

The 33 runs were executed via parallel background subagents (the canonical full-suite path). Two operational lessons, now folded into [`../../README.md`](../../README.md):

- **Cap concurrency at ≤ 3 for large-repo batches.** Four concurrent scans of large repos (langchain 2.3k / autogen 1.9k / openai 1.4k files) tripped the no-progress watchdog and intermittent stream-idle timeouts at the Step 9.9→11 region. Batches of ≤ 3 with the Step 9.9 incremental-write discipline emphasised ran clean.
- **Late-pipeline stalls cost almost nothing.** A scan that stalls after the manifest is complete leaves a recoverable on-disk draft/JSON — run `manifest_to_findings.py` then `render.py` directly (deterministic, no model). Several of the 33 runs were recovered this way; a stall before the findings are written is the only case that needs a fresh run.

The byte-identity / schema / remit-verbatim gate in `tests/render/test_render.py` passes for this set (66 checks across the eleven targets, 0 failures).

## How to compare

```bash
# Diff a single target's findings JSON across baseline sets (4.7 vs 4.8)
diff <(python3 -m json.tool tests/baselines/v0.7.7-sequential/finbot/finbot-findings-2026-05-29.json) \
     <(python3 -m json.tool tests/baselines/v0.7.7-claude48/finbot/finbot-findings-2026-05-29.json)

# Re-render any baseline from its JSON (byte-identical re-render is enforced by tests/render/test_render.py)
python3 skills/behavior-verifier/render.py \
  --findings tests/baselines/v0.7.7-claude48/<target>/<target>-findings-<date>.json \
  --template skills/behavior-verifier/report_template.html \
  --out-html /tmp/<target>.html --out-txt /tmp/<target>.txt
```

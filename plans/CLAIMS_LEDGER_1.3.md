<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Claims ledger — Praxen 1.3 (Thinking Modes)

> **Purpose.** Every externally-repeatable claim about 1.3, paired with the
> evidence behind it *and* the limit that must travel with it. Written while
> the evidence was fresh (2026-08-11) so that blog/release copy is drafted
> from qualified facts rather than from remembered headlines. Steve's framing:
> the validation results "should give us material for our press release" —
> this is that material, with the fine print attached.
>
> **House rule:** a number in public copy must trace to a row here. If a claim
> isn't in this table, it hasn't been evidenced yet.

## Tier 1 — strongest, most defensible

| Claim | Evidence | Limit that must travel with it |
|---|---|---|
| **High mode independently reproduced remit defects that previously took a manual human review sweep to find — on three separate production targets.** | Three uncleaned-remit targets (aider, craftbot, uagents). Each audit ran context-unaware — findings JSON, remit, workspace only, no knowledge of the tracking issues — and surfaced the documented over-reach with citations it derived from the *target's own documentation*: aider's fabricated `/web` allowlist and its trust-closure omitting documented default-on endpoints (#200 items 1–2, fixes near-verbatim to the human ones); craftbot's fabricated config params / per-action-approval over-reach, 4 entries (#201); uagents' value-transfer-vs-registration conflation (#201). **The audit brief is target-agnostic** — four generic questions about rules vs. documentation, containing no target-specific content — so these are rediscoveries, not recognitions. | The brief's *question set* was refined on aider (structurally: add a rule-level check, scope the REMIT-DEFECT verdict, add the bundling question) — normal instrument calibration, not answer leakage, since no target's answers are encoded in it. Craftbot and uagents then ran the frozen brief blind. Residual: the defect *classes* were known when the questions were written, as with any detector. A cold test on a target whose defects nobody has catalogued (helperbot / salesforce) would close even that gap. |
| **The generic rule-check generalizes — it catches defects it was not derived from.** | The bundling/conflation question (#4) was added from an aider miss, then fired on **uagents' unrelated defect** — the no-wallet-spend clause colliding with documented fee-paying Almanac registration (#201's uagents ground truth), on a different target, a different defect, and a different subject domain. | One cross-target transfer, not a generalization study. |
| **The audit found defects our own human review had missed — and corrected an error in our own issue record.** | On aider it flagged a rule that literally bans the `--watch-files` AI-comment mode the same remit sanctions twice (an internal contradiction the 1.2 scrub never logged), and it *declined* to flag the `--yes-always` rule — correctly: checking the remit showed #200's item 5 quoted the clause elided, overstating it. Both are recorded publicly on #200. | Single target. The "missed by humans" catch is one finding, not a rate. |
| **Cost is measured, not estimated — and the two axes diverge.** | Opus 5, 4 targets: standard scan ~215k–265k tok / ~14–19 min; high ~1.4× tok / ~1.3–1.6× wall-clock; x-high ~4× tok / ~2–2.5× wall-clock (three scans run concurrently, so tokens outpace the clock). | Single model (Opus 5), small sample, one harness. Numbers move with target size and finding count. State as "in our testing," never as a spec. |

## Tier 2 — real, but requires the caveat inline

| Claim | Evidence | Limit that must travel with it |
|---|---|---|
| **In a controlled injection test, the audit caught 4 of 4 planted false positives and killed none of ~48 real findings.** | Four already-scanned sets booby-trapped with one plausible-but-fake finding each, rotating four refutation classes (inverted control / fabricated mechanism / misattributed evidence / over-claim); every kill carried correct contradicting citations. Plan + result: `plans/TEST_AUDITOR_FP_INJECTION.md`. | **The fakes were authored by the same operator running the test, and the auditor shares the model family.** N=4. Every fake was refutable by reading the cited code — real-world false positives may be subtler or arise from ambiguity rather than error. Publish as *"a controlled injection test"* with the authorship noted; **do not publish as an FP-detection rate, accuracy figure, or benchmark.** An independent party authoring the fakes would materially strengthen this. |
| **Zero real findings were lost to over-zealous auditing across every run.** | ~48 real findings in the injection test plus 54 across the organic high-mode runs (finbot 13, aider 13, craftbot 12, uagents 16) — all CONFIRMED, no unjustified kills anywhere. | "No false kills observed," not "cannot false-kill." The targets' findings were mostly well-evidenced; a noisier scan is a harder test. |

## Tier 3 — resolved 2026-08-11 (`RESULTS_XHIGH_VALIDATION.md`)

| Claim | Outcome |
|---|---|
| **Discovery yield — x-high surfaces verified findings a single run misses.** *(Tier 1: publishable.)* | **Confirmed, with numbers.** Across 4 super-runs on the two widest-variance targets (12 scans, ~3.4M tokens): expected single-run recall **74–93%** overall, i.e. an ordinary scan misses **7–26%** of the verified set. Broken out: **Critical 100% in all five x-high runs to date** · High 83–96% · Medium 57–78%. 12 single-run findings rescued, all independently verified. **Publishable claim: *a single scan finds the headline risks reliably; x-high buys the tail.*** Limits: 3 targets, one model, one operator. |
| ~~X-high damps score variance~~ | **NOT SUPPORTED — do not claim.** Both super-run pairs differed by exactly the raw 6-run range (uAgents 0.15, AutoGen 0.25). The literal §9.2 criterion (delta inside the historical band) passes, but no damping was demonstrated. Diagnosis: **five of six categories agreed exactly in both pairs**; the whole delta is one band-edge category call (#195), which x-high inherits rather than fixes. Re-test after #195 lands. |
| **Correction to prior guidance** | Thinking-mode scores trend **lower** than standard-mode, not "equal or cleaner" — adjudication adds verified findings far more often than it removes them. Docs corrected; any copy implying thinking modes produce *better-looking* scores is wrong. |

## Claims we must NOT make

- **"Eliminates false positives."** It killed *planted* ones under test conditions. Nothing here supports an elimination claim.
- **Any accuracy / precision / recall percentage presented as a benchmark.** Sample sizes are single digits per condition and the FP fakes are self-authored.
- **Cross-mode or cross-model score comparisons.** Thinking-mode scores are not comparable to standard-mode bands (docs say so); scores are calibrated per model tier.
- **"Deterministic," "guaranteed," or gate-like language.** Praxen's public framing is an expert-assisted review, not a pass/fail gate — 1.3 damps variance, it does not remove the LLM from the loop.
- **Implying high mode stabilizes scores.** It stabilizes the *finding set*; a clean audit leaves the run's category-score draw intact (measured: FinBot high landed 1.30, above its standard band). X-high is the score-stability tier.

## Story angles worth considering (not claims)

1. **"We shipped the reviewer, not just the scanner."** The mode automates the manual FP scrub our own release process ran by hand in 1.2 — the honest origin story, and it explains *why* the feature exists.
2. **"It corrected us."** The audit reproduced our human findings, added one the humans missed, and corrected an overstatement in our own issue tracker. Self-critical, verifiable in the public record, and far more credible than a stat.
   - **Note on hedging (Steve, 2026-08-11):** the over-reach catches are *real results* and should be stated at full strength. The correct caveat is narrow — the question set was calibrated, the answers were not — and burying that distinction under a generic "calibration target" disclaimer undersells three genuine blind rediscoveries. Qualify precisely; don't hedge reflexively.
3. **"Evidence decides, not votes."** The design principle worth explaining publicly: a finding one run of three caught **stays** if the evidence verifies; a finding all three caught **dies** if it doesn't. Nobody else frames multi-run this way, and it's the intellectually interesting part.
4. **Cost honesty.** Publishing both cost axes — including that x-high's tokens outpace its wall-clock — builds more trust than a vague "higher accuracy tier."

<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.1 — Phase 1 Tagging Checkpoint

**Branch:** `1.1` · **Commits:** `0ff901c` + `7298ebd` (KB sharpening) · **Compares against:** the frozen `v1.0.2-claude48` baseline.

## Objective
Measure whether the Phase 1 OWASP-distillation sharpening (#169) actually moved the
tagging — untagged rate down, zeroed categories recovered, the steered clusters
(Excessive Agency / Rogue Agents) landing — **before** starting RAISE (#48).

## Method
Fresh **single-pass** re-scans of all 12 targets with the sharpened KBs, run as parallel
subagents (targeted discovery per `SKILL.md` Step 4). Each emitted a lean findings record
(`severity, summary, raise_category, owasp_llm, owasp_agentic, tags[]`). OWASP coverage is
counted across the scalar codes **and** secondary codes in `tags[]`, then compared to the
frozen set. Raw scan outputs are in `scans/`; the diff tool is `compare_checkpoint.py`.

## Headline

| Metric | Frozen (1.0.2) | New (1.1 guidance) |
|---|---|---|
| Findings (aggregate) | 114 | 114 |
| **Untagged rate** | **21%** (24/114) | **5%** (6/114) |
| **OWASP categories covered** | **16 / 20** | **20 / 20** |

The aggregate finding count is identical (114→114), so run-to-run **detection** variance
nets out at suite level — the distribution shift below is attributable to the **tagging
guidance**, not to finding more/fewer things.

## Every zeroed category recovered (the #169 thesis)

| Category | Frozen → New | Note |
|---|---|---|
| **LLM08** Vector & Embedding | 0 → 4 | craftbot / salesforce / hermes / aider vector stores now tag (was 0/12) |
| **LLM05** Improper Output Handling | 0 → 8 | recovered by guidance on *existing* targets — see "LLM05 reconsidered" |
| **ASI08** Cascading Failures | 0 → 2 | origin-vs-propagation rule |
| **ASI10** Rogue Agents | 0 → 27 | the oversight/accountability-gap steering |

## The steered clusters landed where predicted

| Category | Frozen → New | Why |
|---|---|---|
| **LLM06** Excessive Agency | 20 → 50 | "reachable remit-forbidden capability / control gap → LLM06" |
| **ASI10** Rogue Agents | 0 → 27 | "no audit trail / self-approval / monitoring off → ASI10 (+LLM06)" |
| **ASI03** Identity & Privilege | 11 → 28 | boundary table (ASI03 vs ASI02) + new sub-risks |
| **ASI05** Unexpected Code Exec | 13 → 24 | boundary table (ASI05 vs ASI02) + non-shell exec sub-risks |

## Per-target (frozen n/untagged → new n/untagged)

| Target | Frozen | New | LLM08 |
|---|---|---|---|
| aider | 6/0 | 11/1 | 0→1 |
| autogen-code-executor | 11/1 | 10/0 | — |
| craftbot | 14/2 | 16/1 | 0→1 |
| deepagents-cli | 5/2 | 3/1 | — |
| finbot | 15/1 | 13/0 | — |
| helperbot | 11/3 | 7/0 | — |
| hermes-agent-desktop | 5/1 | 7/0 | 0→1 |
| openai-customer-service | 10/2 | 7/0 | — |
| openhands | 11/4 | 9/1 | — |
| salesforce-help-agent-accelerator | 10/4 | 10/0 | 0→1 |
| uagents | 8/1 | 12/1 | — |
| yaah | 8/3 | 9/1 | — |

## Caveats (kept honest)
- **Fresh single-pass scans**, not a median-of-3 re-freeze — per-target finding counts drift
  (aider 6→11, helperbot 11→7). The real `v1.1-claude48` re-freeze comes after RAISE.
- Per-target untagged didn't reach zero everywhere (aider 0→1, several at 1) — a handful of
  genuinely-hard-to-classify findings remain; the suite-level 21%→5% is the signal.
- Lean output format (not full schema); watchdog stalls forced relaunches on 3 targets.

## LLM05 reconsidered
Frozen LLM05 was **0** and we attributed it to *retiring the output-handling specialist
targets* → flagged as a **1.2 new-baseline-app backfill**. But the fresh scans tag **LLM05 = 8**
on the *existing* targets. So the LLM05 gap was **substantially a tagging gap, not purely a
target-retirement gap** — the guidance recovered it. The 1.2 output-handling-target item is
therefore **lower priority than assumed** (revisit, don't drop — dedicated coverage is still
nice-to-have).

## Verdict
**Phase 1 did what #169 promised.** Untagged 21%→5%, coverage 16→20/20, all four zeroed
categories restored, and the Excessive-Agency / Rogue-Agent steering confirmed. Proceed to
RAISE (#48) on sign-off.

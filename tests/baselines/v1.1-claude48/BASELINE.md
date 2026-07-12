<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v1.1-claude48 (current)

> **Derived from [`../v1.0.2-claude48`](../v1.0.2-claude48/BASELINE.md) by re-tagging OWASP
> classification under the corrected 1.1 knowledge bases (#169 distillation sharpening,
> #111 separator).** Detection, evidence, RAISE categories, and every weighted score are
> **byte-identical** to v1.0.2 — only `owasp_llm` / `owasp_agentic` and the OWASP tag chips
> changed. Because scoring is untouched, **v1.0.2's median-of-3 freeze *is* the 1.1 median**;
> re-scanning would only add run-to-run noise to an anchor whose job is to be stable.

This is the clean, **tagging-corrected, scoring-unchanged** snapshot the RAISE scoring work
(#48) will be measured against — the last pristine "before" ahead of that train. Supersedes
`v1.0.2-claude48` (now archival). Roster prominence + development-activity data lives in
`../ROSTER_HEALTH.md`.

## Why re-tag instead of re-scan ("approach B")

1.1 is a **classification-accuracy** release: schema stays 2.0, and the detection/scoring
logic (SKILL.md, `KB_RAISE_SCANNING`, remits) is unchanged — only the OWASP knowledge bases
were sharpened. Re-tagging the frozen exemplars therefore reproduces exactly what a fresh
median-of-3 would score (identical findings, identical weights) **without** re-introducing
detection variance. The transform touches only OWASP fields; a round-trip test over all 114
findings confirms every other byte is preserved (`retag_lib.py`). All 12 exemplars pass
`python3 tests/render/test_render.py` (schema-valid · HTML/TXT byte-identical re-render ·
every `policy_rule_text` quoted verbatim from `tests/remits/<slug>.md`).

## Scores, freeze method, per-target stability

**Unchanged from v1.0.2 — see [`../v1.0.2-claude48/BASELINE.md`](../v1.0.2-claude48/BASELINE.md).**
Same 12 targets, same median-of-3 weighted scores, same bands, same maturity. Nothing in the
scoring pipeline moved, so copying the tables here would only risk them drifting out of sync.

## What changed — OWASP tagging only (114 findings, unchanged count)

| Measure | v1.0.2 | v1.1 | Note |
|---|--:|--:|---|
| Findings | 114 | 114 | detection frozen |
| No-OWASP (null/null) | 24 (21%) | 27 (23%) | honest taxonomy-reach; logging/observability/config → RAISE-only |
| Secondary (co-applicable) chips | 3 | 19 | the primary/secondary layer, now surfaced |
| LLM08 — Vector & Embedding | 0P / 0S | 0P / **3S** | memory/RAG store weakness rides as secondary on its dominant mechanism (ASI06 poisoning, LLM01 injection) |
| LLM06 — Excessive Agency | 19P | 18P | slight de-inflation |
| LLM05 — Improper Output Handling | 0P | 2P | previously under-tagged |
| LLM04 — Data & Model Poisoning | 1P | 0P | the hermes memory case → ASI06 + LLM08 |
| ASI01 / ASI09 primary | 10 / 1 | 9 / 0 | mechanism kept primary; ASI09 demoted to secondary |
| ASI08 / ASI10 (Cascading / Rogue) | 0 | 0 | **outcomes — legal but rare; none of the corpus is a self-contained end-state** |

**Primaries stayed stable** (the scoring frame is reproducible); the change is that
**co-applicable categories are now recorded as secondary** instead of being forced into the
single primary slot or dropped — the structural fix that makes tagging both accurate and
stable. See `../../../CHANGELOG.md` and the 1.1 KBs for the full rationale.

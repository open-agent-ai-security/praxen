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
Counts are from a clean, un-hinted classifier pass (identical harness across all 12 targets); primary = the `owasp_llm`/`owasp_agentic` scalar, secondary = co-applicable codes in `tags[]`.

| Measure | v1.0.2 | v1.1 | Note |
|---|--:|--:|---|
| Findings | 114 | 114 | detection frozen |
| No-OWASP (null/null) | 24 (21%) | 25 (22%) | honest taxonomy reach; logging/observability/config → RAISE-only |
| Secondary (co-applicable) chips | 3 | 28 | the primary/secondary layer, now surfaced |
| LLM06 — Excessive Agency | 19P / 1S | 23P / 6S | the largest LLM primary; co-applies with LLM05 on ungated raw-exec |
| LLM05 — Improper Output Handling | 0P / 0S | 4P / 6S | raw model-output-to-sink (esp. code exec) now tagged — orthogonal to LLM06, co-occurs with ASI05 |
| LLM01 / LLM02 primary | 12 / 15 | 13 / 16 | injection + credential-disclosure (LLM02×ASI03) each up one |
| LLM04 / LLM08 primary | 1 / 0 | 1 / 0 | unchanged — LLM08 is not exercised as a primary in this corpus |
| ASI01 / ASI09 primary | 10 / 1 | 9 / 0 | mechanism kept primary; ASI09 → secondary |
| ASI10 (Rogue) / ASI08 (Cascading) | 0 / 0 | 0P + **5S** / 0 | outcomes — ASI10 rides secondary on the 5 findings whose deviation *outlives the action*; ASI08 doesn't attach at the finding level (cascade is system-level) |

**Primaries stayed stable** across the corrected passes (the scoring frame is reproducible — LLM06 is robustly the largest, ~23–24 on independent cold runs); the change is that **co-applicable categories are now recorded as secondary** instead of being forced into one slot or dropped. The largest lift is the **LLM05/LLM06 orthogonality fix**: a raw `exec(model_output)` is *both* Improper Output Handling and Excessive Agency (plus ASI05), so those now co-tag rather than one excluding the other. See `../../../CHANGELOG.md` and the 1.1 KBs for the full rationale.

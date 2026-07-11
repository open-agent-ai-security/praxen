<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v1.0.2-claude48 (current)

> Built by `RELEASE_1.0.2_BASELINE_REFRESH.md`. **The current regression baseline** — 12
> targets characterized median-of-3 on the 1.0.x skill (Opus 4.8), each frozen on its
> median-weighted run. Supersedes `v0.7.7-claude48` (now archival). Roster prominence +
> development-activity data lives in `../ROSTER_HEALTH.md`.

## Freeze method — median-of-3
Each target was scanned **3 independent times** on the 1.0.x skill under Opus 4.8 with
identical inputs (skill, source, remit held constant). The **median-weighted run** is
frozen as the committed exemplar — one real, unedited run, keeping the byte-render gate
honest. All 12 frozen exemplars pass `python3 tests/render/test_render.py` (schema-valid ·
HTML/TXT byte-identical re-render · every `rule_text`/`policy_rule_text` quoted verbatim
from `tests/remits/<slug>.md`).

## Frozen set — 12 targets (weakest → strongest)

| Target | Set | Source | C / H / M / L | Weighted (median) | Band | Maturity |
|---|:--:|---|:--:|--:|:--:|---|
| helperbot | ret ✎ | github.com/opena2a-org/damn-vulnerable-ai-agent | 4 / 3 / 3 / 1 | **0.75** | 0.60–0.90 | Absent |
| finbot | ret ✎ | github.com/OWASP-ASI/finbot-ctf-demo | 5 / 4 / 6 / 0 | **0.90** | 0.75–1.05 | Absent |
| craftbot | **new** | github.com/CraftOS-dev/CraftBot | 5 / 5 / 4 / 0 | **1.15** | 1.00–1.45 | Ad hoc |
| openai-customer-service | ret ✎ | github.com/openai/openai-agents-python | 2 / 4 / 4 / 0 | **1.60** | 1.45–1.75 | Ad hoc |
| salesforce-help-agent-accelerator | **new** | github.com/salesforce/help-agent-accelerator | 1 / 3 / 5 / 1 | **1.70** | 1.55–1.85 | Ad hoc |
| aider | ret ✎ | github.com/Aider-AI/aider | 1 / 2 / 3 / 0 | **2.00** | 1.85–2.15 | Partial |
| autogen-code-executor | ret ✎ | github.com/microsoft/autogen | 1 / 5 / 5 / 0 | **2.00** | 1.85–2.15 | Partial |
| uagents | **new** | github.com/fetchai/uAgents | 1 / 2 / 5 / 0 | **2.00** | 1.70–2.30 | Partial |
| yaah | ret ✎ | github.com/dirien/yet-another-agent-harness | 0 / 4 / 4 / 0 | **2.30** | 2.15–2.45 | Partial |
| openhands | ret ✎ | github.com/All-Hands-AI/OpenHands | 1 / 3 / 6 / 1 | **2.30** | 2.15–2.45 | Partial |
| deepagents-cli | ret ✎ | github.com/langchain-ai/deepagents | 1 / 0 / 4 / 0 | **2.70** | 2.55–2.85 | Partial |
| hermes-agent-desktop | ret ✎ | github.com/NousResearch/hermes-agent | 0 / 1 / 4 / 0 | **2.85** | 2.70–3.15 | Partial |

**Set:** `new` = Phase-1 addition · `ret` = retained · **✎** = remit refreshed/regenerated
this cycle (see notes). Severity = frozen median run's `C/H/M/L` (Critical/High/Medium/Low).

## Stability across the three runs

Band = `[min(min_run, median−0.15), max(max_run, median+0.15)]` — contains every run with a
±0.15 floor around the median. Frozen = median run.

| Target | run 1 / 2 / 3 | mean | **std** | range | median (frozen) |
|---|---|--:|--:|--:|--:|
| helperbot | 0.75 / 0.75 / 0.75 | 0.75 | 0.000 | 0.00 | **0.75** |
| finbot | 1.05 / 0.90 / 0.90 | 0.95 | 0.071 | 0.15 | **0.90** |
| craftbot | 1.00 / 1.15 / 1.45 | 1.20 | 0.187 | 0.45 | **1.15** |
| openai-customer-service | 1.45 / 1.60 / 1.60 | 1.55 | 0.071 | 0.15 | **1.60** |
| salesforce-help-agent-accelerator | 1.70 / 1.85 / 1.70 | 1.75 | 0.071 | 0.15 | **1.70** |
| aider | 2.00 / 2.00 / 2.00 | 2.00 | 0.000 | 0.00 | **2.00** |
| autogen-code-executor | 1.85 / 2.00 / 2.00 | 1.95 | 0.071 | 0.15 | **2.00** |
| uagents | 2.00 / 2.30 / 1.70 | 2.00 | 0.245 | 0.60 | **2.00** |
| yaah | 2.15 / 2.30 / 2.30 | 2.25 | 0.071 | 0.15 | **2.30** |
| openhands | 2.15 / 2.30 / 2.40 | 2.28 | 0.103 | 0.25 | **2.30** |
| deepagents-cli | 2.55 / 2.85 / 2.70 | 2.70 | 0.122 | 0.30 | **2.70** |
| hermes-agent-desktop | 2.85 / 2.85 / 3.15 | 2.95 | 0.141 | 0.30 | **2.85** |

## Notes — remit refresh (Phase 2)
- **8 retained remits were regenerated** to the current template (they had drifted to the
  pre-template skeleton): `finbot, helperbot, aider, yaah, autogen-code-executor,
  openai-customer-service, openhands, deepagents-cli`. Each was **authored fresh from the
  target's documentation** (docs-as-intent, per the skill), with an intent-preservation
  pass against the old remit, then **quality-audited** (all judged better-and-conformant)
  and **re-characterized median-of-3**. Model: Opus 4.8; scan dates 2026-07-11.
- **hermes** remit was independently re-authored earlier (SSH-tunnel mode retired upstream →
  local/remote/cloud); frozen at **2.85** after a three-remit triangulation. `craftbot`,
  `uagents`, `salesforce-help-agent-accelerator` were already current-format (Phase-1) — SPDX
  headers added to the first two; no rule changes.
- **Intended upward movement (remit-isolated).** Holding the 1.0.x skill constant, the fuller
  template-conformant remits credit operative controls a notch more — each target's **old-remit**
  median → its **new-remit** median: openai-cs 1.45→1.60, autogen 1.85→2.00, yaah 2.15→2.30,
  openhands 2.15→2.30, **aider 1.70→2.00** (fuller capability coverage; dead-flat across 3 runs),
  **deepagents 2.30→2.70**. finbot/helperbot (fixed CTF fixtures) held. The "before" figures are
  the pre-refresh (old-remit, 1.0.x-skill) characterization — **not** the shipped
  `v0.7.7-claude48` medians; vs that predecessor the net also carries the 0.7.7→1.0 skill lean.
  Movement is remit-quality-driven, not skill drift; intent was preserved.
- **deepagents MCP-TLS:** the regen initially demoted the "remote MCP URLs MUST use TLS" rule
  to an open question; it was **restored to the policy body** and now correctly surfaces the
  real gap (no scheme check in code) as a Critical — the median (2.70) is on the corrected
  remit.

## Retirements (Phase 3 — executed 2026-07-11)
`sweep` (#69), `langchain-sql` (#70), and `devika` were **retired** (all dormant/archived
upstreams — `../ROSTER_HEALTH.md`). Note: the plan advised langchain-sql be *replaced not
dropped* (only DB/NL-to-SQL archetype); it was **dropped** pending a future replacement.
Accepted coverage trade-offs, tracked in **#169**: **LLM08 (Vector/Embedding) → 0** (devika
was the sole tag; real fix is re-tagging craftbot's ChromaDB finding, a 1.1 item) and the
**DB / NL-to-SQL archetype → 0**. Final count **12**.

## Supersedes v0.7.7-claude48 (now archival)
This set is the current reference; the pointer in `../README.md` and `../../README.md` names
it. `v0.7.7-claude48` (and the older `v0.7.x-sequential` sets) are retained on disk as
**archival diff-history** — still schema + byte-render gated, but the **remit-verbatim check
is scoped to the current set only** (`test_render.py:CURRENT_BASELINE`), since archival
findings quote the remits as they were at freeze time and must not be re-bound to evolving
remits.

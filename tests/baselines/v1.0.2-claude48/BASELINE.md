<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v1.0.2-claude48 (in progress)

> Built by `RELEASE_1.0.2_BASELINE_REFRESH.md`. **Phase 1 (new targets) is characterized median-of-3 and frozen.** The 12 **retained** targets are being re-characterized on 1.0.x (the "Foundation" wave) — until those land here, `tests/baselines/v0.7.7-claude48/` remains their reference.

## Freeze method — median-of-3
Each new target was scanned **3 independent times** on the 1.0.x skill under Opus 4.8, identical inputs (skill, source, remit held constant). The **median-weighted run** is frozen as the committed exemplar (one real, unedited run — keeps the byte-render gate honest). All frozen exemplars pass `python3 tests/render/test_render.py` (schema-valid, HTML/TXT byte-render clean, every rule quoted verbatim).

## Phase 1 additions — frozen (median run)

| Target | Source | Critical | High | Medium | Low | Weighted (median) | Maturity |
|---|---|---:|---:|---:|---:|---:|---|
| craftbot | github.com/CraftOS-dev/CraftBot | 5 | 5 | 4 | 0 | **1.15** | Ad hoc |
| salesforce-help-agent-accelerator | github.com/salesforce/help-agent-accelerator | 1 | 3 | 5 | 1 | **1.70** | Ad hoc |
| uagents | github.com/fetchai/uAgents | 1 | 2 | 5 | 0 | **2.00** | Partial |

## Stability across the three runs

| Target | run a / b / c | mean | **std** | range | median (frozen) |
|---|---|---:|---:|---:|---:|
| craftbot | 1.00 / 1.15 / 1.45 | 1.20 | 0.187 | 0.45 | **1.15** |
| salesforce-help-agent-accelerator | 1.70 / 1.85 / 1.70 | 1.75 | **0.071** | 0.15 | **1.70** |
| uagents | 2.00 / 2.30 / 1.70 | 2.00 | 0.245 | 0.60 | **2.00** |

**Bands** (mean ± observed spread): craftbot **1.0–1.45** · salesforce-help-agent-accelerator **1.6–1.9** · uagents **1.7–2.3**. Agentforce is the tightest (σ 0.07); uAgents the widest (Critical-count judgment swings on plaintext-keys/replay/spoofable-guard).

## Notes
- **Model:** Opus 4.8 (confirmed — `PHASE1_OPEN_ISSUES.md` O1). **Scan dates:** 2026-07-10/11.
- **Remits:** `craftbot` + `uagents` drafted fresh (current format); **`salesforce-help-agent-accelerator` remit was rewritten** from the 0.7.8 table/fragment form into current declarative-rule format (intent held constant) so it quotes verbatim — the 3 Agentforce runs used the rewritten remit (O4 resolved). *The declarative remit's clearer rules also lifted Agentforce's score vs the old-remit run (1.15 → 1.70): more operative controls credited — an intended remit-refresh effect, not drift.*

## What's covered that wasn't before
- **CraftBot** — self-hosted general assistant that builds/operates its own SaaS tools (local WS control plane, host shell/code exec, MCP fan-out).
- **uAgents** — decorator-based multi-agent framework runtime (crypto identity/wallet, Almanac registration, signed envelopes).
- **Agentforce** — real-world enterprise SaaS agent (Salesforce Agentforce / Knowledge RAG).

## Retained targets (Foundation — in progress)
Being re-characterized ×1 on 1.0.x and spot-checked against their `v0.7.7-claude48` weighted (in-bounds = within ±0.3–0.5). `sweep` and `langchain-sql` upstreams are deprecated but **live and clonable** — they are re-scanned too (their *replacement* is a separate Phase-3 decision, #69/#70).

<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v1.0.2-claude48 (in progress)

> **Provisional — Phase 1 additions only.** This set is being built by `RELEASE_1.0.2_BASELINE_REFRESH.md`. So far it holds the **three new/promoted targets** on the 1.0.x skill under Opus 4.8. The ~10 **retained** targets are **not yet re-frozen here** (the "Foundation" re-baseline is pending — see `PHASE1_OPEN_ISSUES.md` O2); until then, `tests/baselines/v0.7.7-claude48/` remains the active reference for the retained targets.

## Freeze method (current state)
- **Single run per target** so far (not yet median-of-3). These are the *exemplar candidates* for review, not the final freeze. Median-of-3 + band-setting is pending (O2).
- Every target passes the smoke harness: schema-valid, HTML/TXT re-render byte-for-byte from JSON, and every `rule_text` quotes its `tests/remits/<slug>.md` verbatim (`python3 tests/render/test_render.py` → 352 passed, 0 failed).

## Phase 1 additions

| Target | Source | Critical | High | Medium | Low | Info | Weighted | Maturity |
|---|---|---:|---:|---:|---:|---:|---:|---|
| craftbot | github.com/CraftOS-dev/CraftBot | 4 | 5 | 5 | 0 | 0 | **1.00** | Ad hoc |
| salesforce-help-agent-accelerator | github.com/salesforce/help-agent-accelerator | 1 | 3 | 4 | 0 | 0 | **1.15** | Ad hoc |
| uagents | github.com/fetchai/uAgents | 1 | 2 | 5 | 0 | 0 | **2.00** | Partial |

- **Model:** current session reference (Opus 4.8 — confirm, O1). **Scan date:** 2026-07-10.
- **Remits:** `craftbot` + `uagents` drafted fresh (in current format) by the scan; `salesforce-help-agent-accelerator` reused the existing `examples/` remit (praxen 0.7.8) — 11 rule quotes were trimmed to verbatim to pass the remit-verbatim gate; the remit needs a Phase-2 format refresh (O4).
- **Bands:** not set — pending median-of-3 (O2).

## What's covered that wasn't before
- **CraftBot** — a self-hosted general-purpose assistant that builds/operates its own SaaS tools: local WebSocket control plane, host shell/code execution, third-party MCP fan-out (archetype + finding types new to the suite).
- **uAgents** — a decorator-based multi-agent *framework* runtime (crypto identity/wallet, Almanac registration, signed envelopes) — the framework-posture archetype.
- **Agentforce** — a real-world enterprise SaaS agent (Salesforce Agentforce / Knowledge RAG) — the only enterprise-platform target in the suite.

## Provenance / how to reproduce
Each target was cloned from its `Source` URL to `local/v1.0.2-phase1/src/<t>` (gitignored) and scanned per `tests/README.md` (parallel-subagent path) into `local/v1.0.2-phase1/<t>-out/`. Committed here: the median-exemplar findings JSON + rendered HTML/TXT. Remits live in `tests/remits/`.

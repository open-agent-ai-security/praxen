<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Pre-release suite run — 1.0.2

**Verdict: PASS.** The 1.0.2 regression baseline is frozen, green, and internally consistent.
This release is a **baseline + roster + remit refresh with no skill/engine changes** — the
scan logic (`SKILL.md`, `schema.py`, `render.py`, `manifest_to_findings.py`, the four
knowledge bases) is unchanged and `schema_version` stays `"2.0"`, so no analysis *logic*
moved. Score movement is confined to intended remit-quality effects (below).

## What ran
- **Median-of-3** characterization of all **12** targets on the 1.0.x skill under Opus 4.8,
  frozen into `tests/baselines/v1.0.2-claude48/` (one real median-weighted run each).
- 8 retained remits regenerated to the current template (docs-as-intent, intent-preserving,
  quality-audited); `hermes` remit independently re-authored; each re-characterized ×3.
- Roster: **added** CraftBot/uAgents/Agentforce; **retired** sweep (#69), langchain-sql
  (#70), devika.

## Gates
- `python3 tests/render/test_render.py` → **406 passed, 0 failed** (schema · byte-render ·
  remit-verbatim on the current set; archival sets exempt from verbatim per `CURRENT_BASELINE`).
- `./build.sh` → dist `praxen-1.0.2` builds cleanly.
- Manifests parse; version **1.0.2** consistent across the three plugin manifests + `PRAXEN_SPEC.md`.
- OWASP + RAISE + Suite Health coverage pages regenerated against the frozen set (12 targets).

## Frozen medians (weakest → strongest)
helperbot 0.75 · finbot 0.90 · craftbot 1.15 · openai-cs 1.60 · agentforce 1.70 ·
aider 2.00 · autogen 2.00 · uagents 2.00 · yaah 2.30 · openhands 2.30 · deepagents 2.70 ·
hermes 2.85. Per-target C/H/M/L, bands, and 3-run stability: `../../baselines/v1.0.2-claude48/BASELINE.md`.

## Intended movement (remit-isolated, 1.0.x skill held constant)
Comparing each target's old-remit median → new-remit median (isolating the remit refresh):
openai-cs 1.45→1.60, autogen 1.85→2.00, yaah 2.15→2.30, openhands 2.15→2.30, **aider 1.70→2.00**
(dead-flat ×3), **deepagents 2.30→2.70** (MCP-TLS rule restored → real Critical gap surfaced).
The "before" figures are the pre-refresh old-remit characterization, **not** the shipped
`v0.7.7-claude48` medians (vs that predecessor the net also carries the 0.7.7→1.0 skill lean).
Fixed CTF fixtures (finbot/helperbot) held. Movement is remit-quality-driven, not skill drift;
intent was preserved and independently quality-audited.

## Known / accepted
- **Deviation:** langchain-sql dropped (not replaced) — DB/NL-to-SQL archetype gap; LLM08
  (vector/embedding) coverage hole → tracked in **#169** (re-tag craftbot's ChromaDB finding, a 1.1 item).
- Manual **plugin-marketplace install check** (`tests/README.md` pre-release step 2) is
  outstanding — not CI-covered; run before tagging.

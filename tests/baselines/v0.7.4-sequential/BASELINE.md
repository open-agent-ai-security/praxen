<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v0.7.4-sequential

Frozen runs of all **eleven** test targets ([`../../README.md`](../../README.md)) on the **Praxen v0.7.4** skill, against the intent-level Worker Remits (`tests/remits/*.md`). The eleven runs were produced cold on 2026-05-26 against the `feat/manifest-to-findings` branch at the post-prose-trim commit, with the version-source-of-truth cleanup applied. Retires the previous `v0.7.0-sequential/` set, which is no longer the comparison point.

## What changed since v0.7.0-sequential

- **Step 10 is now a deterministic Python conversion.** The Step 9.9 parser-grade draft manifest is fed to `manifest_to_findings.py`, which emits the canonical findings JSON mechanically — no LLM in the loop. Replaces the LLM-composed JSON path that was the principal stall site on long scans. Step 11 (`render.py`) is unchanged in shape.
- **Step 9.9 chunked-write emission discipline.** Manifests are now skeleton-first + Edit-append + heartbeats, eliminating the silent-compose burst pattern that tripped the 600 s subagent no-progress watchdog at scale.
- **Source-read pacing line in SKILL Step 3.** A one-line guard against long internal-only reasoning between large reads — the historical stall site on `aider` and `openhands` source exploration.
- **Medium-tier completeness check.** Step 6 "Don't tier-compress" guidance + Step 9.9 self-check that the manifest carries at least the realistic Medium count for the target. Every target in this baseline carries at least 2 Mediums.
- **Version source of truth.** `praxen_version` is now populated by the converter from `.claude-plugin/plugin.json`, and `schema_version` from `schema.SCHEMA_VERSION`. The SKILL no longer asks the worker to write either. Eliminates the version-drift bug visible in pre-cleanup reports.
- **No schema, no scoring formula change.** `findings.schema.json`, `schema.py`, the RAISE weights, and the per-rule audit methodology are unchanged. The baselines move because the SKILL's calibration discipline (Medium preservation, partial-control credit) tightened — not because the scoring math changed.

The full suite cleared 11/11 with **zero watchdog stalls** at a median wall time of ~8 min (range 5–11 min). Previous comparable runs averaged 12–18 min with a ~39 % stall rate; the architectural changes cut median wall time roughly in half and eliminated stalls in this sample.

## The eleven baselines

Sorted by weighted RAISE, ascending.

| Target | Critical | High | Medium | Low | Info | Weighted | Maturity |
|---|--:|--:|--:|--:|--:|--:|---|
| helperbot | 5 | 6 | 3 | 0 | 0 | 0.45 | Absent |
| devika | 7 | 9 | 4 | 0 | 1 | 0.60 | Absent |
| finbot | 5 | 8 | 3 | 0 | 0 | 0.60 | Absent |
| openai-customer-service | 3 | 5 | 3 | 0 | 0 | 0.90 | Absent |
| sweep | 5 | 3 | 5 | 0 | 0 | 1.00 | Ad hoc |
| langchain-sql | 3 | 4 | 4 | 0 | 0 | 1.05 | Ad hoc |
| autogen-code-executor | 4 | 6 | 4 | 0 | 0 | 1.30 | Ad hoc |
| aider | 3 | 4 | 2 | 0 | 0 | 1.45 | Ad hoc |
| yaah | 2 | 3 | 3 | 0 | 0 | 2.15 | Partial |
| openhands | 4 | 4 | 4 | 0 | 0 | 2.15 | Partial |
| deepagents-cli | 0 | 1 | 5 | 0 | 0 | 2.45 | Partial |

All eleven carry `praxen_version` `0.7.4` and `schema_version` `2.0`. The spread is intact — deliberately-vulnerable targets (helperbot, devika, finbot) sit in *Absent*; mature targets (deepagents-cli, openhands, yaah) reach *Partial* — so the suite still exercises the full calibration range. Every target carries at least 2 Mediums (no tier compression), and the well-built `deepagents-cli` correctly lands with 0 Criticals.

## What's notably different from v0.7.0-sequential

- **helperbot, devika, finbot, openai-customer-service** — Critical/High counts moved upward by 1–2 each as the tightened Step 7 compound-signal discipline turned previously-split findings into single compound entries. Themes preserved.
- **deepagents-cli** — Critical count went from 0 → 0 (held) but Medium count went from 2 → 5, exercising the Medium-tier preservation. RAISE +0.15 reflects the supply-chain credit on the maintainer-pinned dependency profile.
- **openhands** — RAISE −0.15 from baseline (2.30 → 2.15), inside variance. Same compound-chain shape; the worker landed at a stricter Implement Zero Trust score because the `confirmation_mode=NeverConfirm` default + microagent auto-load combination is now a single compound rather than two siloed gaps.
- **yaah, langchain-sql** — RAISE in the same neighbourhood as the v0.7.0 baseline, with the per-target bands in `../../README.md` covering both.

These movements describe a tightening of the SKILL's calibration discipline, not a change in scoring math.

## How to compare

For each target, diff a fresh run's `<target>-findings-<date>.json` against the committed one here: weighted RAISE within ±0.3–0.5, severity counts in the same neighbourhood, dominant Critical themes still covered (the hard gate). See [`../../README.md`](../../README.md) → "What a release review looks like".

The per-target bands in [`../../README.md`](../../README.md) were recalibrated against this baseline as part of the 0.7.4 cut — each band is centered on the v0.7.4 baseline number with ~±2 counts and ±0.3–0.4 weighted, matching the blind-run-variance shape stated in that file's preamble. Future re-runs will refine the widths; this is the new starting point.

Each target directory holds the canonical `<target>-findings-<date>.json` — the record you actually diff — plus the rendered `<target>-analysis-<timestamp>.html` and `.txt`. The renderer is deterministic: the committed HTML/TXT re-render byte-for-byte from the JSON, and `tests/render/test_render.py` enforces that.

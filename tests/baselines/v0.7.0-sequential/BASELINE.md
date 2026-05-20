<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v0.7.0-sequential

Frozen runs of all **eleven** test targets ([`../../README.md`](../../README.md)) on the **Praxen v0.7.0** skill, against the **rewritten intent-level Worker Remits** (`tests/remits/*.md`). The eleven runs were produced cold on 2026-05-19 under the Praxa-0.6.3-era skill code that emits these same findings; the Praxa → Praxen rename + the `praxa_version → praxen_version` schema-field rename re-render them as the v0.7.0 baselines (no scan content changes — same findings, same rule_text, same scores). See [issue #40](https://github.com/open-ai-security/praxen/issues/40) for the re-baseline rationale and the `[0.7.0]` changelog entry for the rename.

## What changed since the previous baselines

- **The product was renamed Praxa → Praxen** ahead of the first public soft-launch release. The findings-JSON field `praxa_version` was renamed `praxen_version`; the renderer emits "Praxen" branding; the package and release artifact were renamed. None of this changed scan content; the eleven baselines re-render byte-for-byte from the same canonical JSONs that the v0.6.3-era runs produced, just with the field-rename + branding migration applied.
- **The Worker Remits were rewritten** — from implementation-level documents (which named internal file paths, class names, config keys, pinned versions) into intent-level *policy* documents. Every baseline here quotes the new remits; the numbers are not directly comparable to the retired `v0.3-sequential/`.
- **`deepagents-cli` was re-scoped.** The package is now a deploy-only bundler — the interactive coding-assistant surface moved to a separate `deepagents-code` package. Its remit and this baseline describe the bundler.
- **`openhands` upstream restructured.** The agentic core moved out into separate `openhands-sdk` / `agent-server` packages; this baseline scopes the current `openhands/app_server/` + `server/` control plane.

## The eleven baselines

| Target | Critical | High | Medium | Low | Info | Weighted | Maturity |
|---|--:|--:|--:|--:|--:|--:|---|
| finbot | 7 | 6 | 3 | 0 | 0 | 0.45 | Absent |
| helperbot | 3 | 5 | 2 | 0 | 0 | 0.45 | Absent |
| devika | 4 | 6 | 2 | 0 | 0 | 0.45 | Absent |
| langchain-sql | 4 | 4 | 3 | 0 | 1 | 0.85 | Absent |
| openai-customer-service | 5 | 6 | 2 | 0 | 0 | 0.90 | Absent |
| sweep | 4 | 5 | 2 | 1 | 1 | 1.35 | Ad hoc |
| aider | 4 | 6 | 2 | 0 | 0 | 1.45 | Ad hoc |
| autogen-code-executor | 4 | 6 | 3 | 1 | 1 | 1.60 | Ad hoc |
| openhands | 0 | 3 | 4 | 3 | 0 | 2.15 | Partial |
| yaah | 2 | 4 | 4 | 0 | 0 | 2.20 | Partial |
| deepagents-cli | 0 | 4 | 2 | 1 | 0 | 2.30 | Partial |

All eleven carry `praxen_version` `0.7.0` and `schema_version` `2.0`. The spread is intact — the deliberately-vulnerable targets (finbot, helperbot, devika) sit in *Absent*, the mature ones (openhands, yaah, deepagents-cli) reach *Partial* — so the suite still exercises the full calibration range.

## How to compare

For each target, diff a fresh run's `<target>-findings-<date>.json` against the committed one here: weighted RAISE within ±0.3–0.5 and inside the per-target band in [`../../README.md`](../../README.md); severity counts in the same neighbourhood; the dominant Critical themes still covered (the hard gate). See [`../../README.md`](../../README.md) → "What a release review looks like".

Each target directory holds the canonical `<target>-findings-<date>.json` — the record you actually diff — plus the rendered `<target>-analysis-<timestamp>.html` and `.txt`. The renderer is deterministic: the committed HTML/TXT re-render byte-for-byte from the JSON, and `tests/render/test_render.py` enforces that on every run.

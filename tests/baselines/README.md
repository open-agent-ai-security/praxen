<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Test-suite baselines

Frozen runs of the nine targets in [`../README.md`](../README.md), one set per Praxa version, kept in the repo so they can be diffed against. Two uses:

1. **Regression review** — before a release, run the full nine-target suite and compare against the latest baseline (see [`../README.md`](../README.md), "What a release review looks like" → the full-compare step).
2. **Pipeline-change parity gates** — e.g. the Phase-2 parallel-analysis path is gated on landing in the same RAISE bands as the latest *sequential* baseline (see `design/V2_HARVEST_PLAN.md`).

## Layout

```
baselines/
  README.md                 ← this file
  v0.6-sequential/           ← PARTIAL — deepagents-cli only, on Praxa v0.6.0; the MCP-coverage target, added later
    BASELINE.md              ← target table + MCP-path coverage note + how to compare
    deepagents-cli/
      deepagents-cli-findings-<date>.json   ← the canonical record (the thing you actually diff)
      deepagents-cli-analysis-<date>.html   ← the rendered report
      deepagents-cli-analysis-<date>.txt    ← the plain-text summary
  v0.3-sequential/           ← CURRENT for the nine core targets — on Praxa v0.3.0 (schema 2.0; structured evidence + recommended_actions[])
    BASELINE.md              ← summary table, per-target provenance, schema-shift check, how to re-render
    <target>/
      <target>-findings-<date>.json
      <target>-analysis-<date>.html
      <target>-analysis-<date>.txt
  v0.2-sequential/           ← PREVIOUS — the nine core targets on Praxa v0.2.0 (schema 1.0); kept as the "before" snapshot
    BASELINE.md
    <target>/ …
```

When a Praxa version bumps and the calibration legitimately moves (or the JSON schema changes), the suite is re-run and re-frozen under a new `vX.Y-sequential/` directory, and the "latest baseline" pointer in `../README.md` is updated. `v0.3-sequential/` was produced by Phase 1's gate in `design/V2_HARVEST_PLAN.md` (the merged `schema_version: "2.0"` skill) and is the current comparator for the nine core targets; `v0.2-sequential/` is retained as the "before" so Phase 1's schema change can be shown not to have moved calibration (see `v0.3-sequential/BASELINE.md` → "Schema-shift check"). `v0.6-sequential/` is a **partial** baseline — it holds only `deepagents-cli`, the MCP-coverage target added when the MCP Server Evaluation path was exercised on a real repo; the other nine fold into it at the next full re-freeze (see `v0.6-sequential/BASELINE.md`).

## Re-rendering the HTML/TXT from a baseline JSON

The renderer is deterministic, so a baseline's committed HTML/TXT re-render byte-for-byte from its committed JSON **using the renderer/template of that era**:

```bash
python3 skills/behavior-verifier/render.py \
  --findings tests/baselines/v0.3-sequential/<target>/<target>-findings-<date>.json \
  --template skills/behavior-verifier/report_template.html \
  --out-html /tmp/<target>.html --out-txt /tmp/<target>.txt
```

> **Note on the relicense (Unreleased):** the `v0.2-sequential/` and `v0.3-sequential/` HTML/TXT snapshots were rendered before the Apache-2.0 relicense, so they still carry the old `Copyright © 2026 Exabeam, Inc. … Confidential and Proprietary` report header. They're intentionally left as-is — they're frozen historical artifacts, and the *findings JSON* is the thing that actually gets diffed. Re-rendering them with the current template will not be byte-identical (the new template strips that header and uses the open-source footer); the next baseline cut will pick up the new template.

## What is *not* kept here

Ad-hoc / mid-development re-run reports. They regenerate on every run and drift between analyses — only these named, version-pinned baselines are committed.

<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Test-suite baselines

Frozen runs of the **eleven** test targets in [`../README.md`](../README.md), kept in the repo so a release run can be diffed against them. The current set is **`v0.6.3-sequential/`** — all eleven targets on the Praxa v0.6.3 skill, scanned cold against the intent-level Worker Remits. It is the comparison point for the pre-release regression review (see [`../README.md`](../README.md), "What a release review looks like").

## Layout

```
baselines/
  README.md                 ← this file
  v0.6.3-sequential/         ← CURRENT — all eleven targets, Praxa v0.6.3 (schema 2.0)
    BASELINE.md              ← summary table, provenance, how to compare
    <target>/
      <target>-findings-<date>.json        ← the canonical record (the thing you diff)
      <target>-analysis-<timestamp>.html   ← the rendered report
      <target>-analysis-<timestamp>.txt    ← the plain-text summary
  v0.4-parallel/             ← historical — the Phase-2 parallel-path evaluation gate
    GATE-NOTES.md            ← the A/B record and the "drop the parallel path" verdict
```

When a Praxa release legitimately moves the calibration (or the findings schema changes), the suite is re-run cold and re-frozen under a new `vX.Y-sequential/` directory, the previous set is retired, and the pointer in `../README.md` is updated. The `v0.6.3-sequential/` set was produced by the re-baseline in [issue #40](https://github.com/Exabeam/deckard/issues/40): all eleven targets were re-scanned against the rewritten intent-level remits, retiring the earlier split — `v0.3-sequential/` (nine core targets, Praxa 0.3.0), `v0.2-sequential/` (schema 1.0), and the partial `v0.6-sequential/` MCP pair.

`v0.4-parallel/` is not a baseline set — it is the record of the Phase-2 parallel-analysis gate (`design/V2_HARVEST_PLAN.md` §5), whose verdict was to drop the parallel path. It is kept as a historical decision record.

## Re-rendering the HTML/TXT from a baseline JSON

The renderer is deterministic — a baseline's committed HTML/TXT re-render byte-for-byte from its committed JSON, and `tests/render/test_render.py` enforces that on every run:

```bash
python3 skills/behavior-verifier/render.py \
  --findings tests/baselines/v0.6.3-sequential/<target>/<target>-findings-<date>.json \
  --template skills/behavior-verifier/report_template.html \
  --out-html /tmp/<target>.html --out-txt /tmp/<target>.txt
```

## What is *not* kept here

Ad-hoc / mid-development re-run reports. They regenerate on every run and drift between analyses — only the named, version-pinned baseline set is committed.

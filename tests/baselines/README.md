<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Test-suite baselines

Frozen runs of the **eleven** test targets in [`../README.md`](../README.md), kept in the repo so a release run can be diffed against them. The current set is **`v0.7.0-sequential/`** — all eleven targets on the Praxen v0.7.0 skill, against the intent-level Worker Remits. It is the comparison point for the pre-release regression review (see [`../README.md`](../README.md), "What a release review looks like").

## Layout

```
baselines/
  README.md                 ← this file
  v0.7.0-sequential/         ← CURRENT — all eleven targets, Praxen v0.7.0 (schema 2.0)
    BASELINE.md              ← summary table, provenance, how to compare
    <target>/
      <target>-findings-<date>.json        ← the canonical record (the thing you diff)
      <target>-analysis-<timestamp>.html   ← the rendered report
      <target>-analysis-<timestamp>.txt    ← the plain-text summary
  v0.4-parallel/             ← historical — the Phase-2 parallel-path evaluation gate
    GATE-NOTES.md            ← the A/B record and the "drop the parallel path" verdict
```

When a Praxen release legitimately moves the calibration (or the findings schema changes), the suite is re-run cold and re-frozen under a new `vX.Y-sequential/` directory, the previous set is retired, and the pointer in `../README.md` is updated. The `v0.7.0-sequential/` set is the eleven cold runs that were produced by the re-baseline in [issue #40](https://github.com/open-ai-security/praxen/issues/40) (originally frozen as `v0.6.3-sequential/` under the old Praxa name) and then migrated by the Praxa → Praxen rename — see the `[0.7.0]` changelog entry. Earlier sets — `v0.3-sequential/` (nine core targets, the pre-rename 0.3.0 calibration), `v0.2-sequential/` (schema 1.0), the partial `v0.6-sequential/` MCP pair, and the same-content `v0.6.3-sequential/` — were retired in the successive re-baselines.

`v0.4-parallel/` is not a baseline set — it is the record of the Phase-2 parallel-analysis gate (`design/V2_HARVEST_PLAN.md` §5), whose verdict was to drop the parallel path. It is kept as a historical decision record.

## Re-rendering the HTML/TXT from a baseline JSON

The renderer is deterministic — a baseline's committed HTML/TXT re-render byte-for-byte from its committed JSON, and `tests/render/test_render.py` enforces that on every run:

```bash
python3 skills/behavior-verifier/render.py \
  --findings tests/baselines/v0.7.0-sequential/<target>/<target>-findings-<date>.json \
  --template skills/behavior-verifier/report_template.html \
  --out-html /tmp/<target>.html --out-txt /tmp/<target>.txt
```

## What is *not* kept here

Ad-hoc / mid-development re-run reports. They regenerate on every run and drift between analyses — only the named, version-pinned baseline set is committed.

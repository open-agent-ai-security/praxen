<!--
  Copyright © 2026 Exabeam, Inc. All Rights Reserved.
  Confidential and Proprietary. Do not distribute. Use by permission only.
-->

# Test-suite baselines

Frozen runs of the nine targets in [`../README.md`](../README.md), one set per Praxa version, kept in the repo so they can be diffed against. Two uses:

1. **Regression review** — before a release, run the full nine-target suite and compare against the latest baseline (see [`../README.md`](../README.md), "What a release review looks like" → the full-compare step).
2. **Pipeline-change parity gates** — e.g. the Phase-2 parallel-analysis path is gated on landing in the same RAISE bands as the latest *sequential* baseline (see `design/V2_HARVEST_PLAN.md`).

## Layout

```
baselines/
  README.md                 ← this file
  v0.2-sequential/           ← the nine targets on Praxa v0.2.0 (sequential pipeline; canonical-JSON + render.py; schema 1.0)
    BASELINE.md              ← summary table, per-target provenance, how to re-render
    <target>/
      <target>-findings-<date>.json   ← the canonical record (the thing you actually diff)
      <target>-analysis-<date>.html   ← the rendered report
      <target>-analysis-<date>.txt    ← the plain-text summary
```

When a Praxa version bumps and the calibration legitimately moves (or the JSON schema changes), the suite is re-run and re-frozen under a new `vX.Y-sequential/` directory, and the "latest baseline" pointer in `../README.md` is updated. The next planned one is `v0.3-sequential/` — produced by Phase 1's gate in `design/V2_HARVEST_PLAN.md` (the merged `schema_version: "2.0"` skill), and the comparator for the Phase-2 parallel path.

## Re-rendering the HTML/TXT from a baseline JSON

The renderer is deterministic, so the committed HTML/TXT re-render byte-for-byte from the committed JSON:

```bash
python3 skills/behavior-verifier/render.py \
  --findings tests/baselines/v0.2-sequential/<target>/<target>-findings-<date>.json \
  --template skills/behavior-verifier/report_template.html \
  --out-html /tmp/<target>.html --out-txt /tmp/<target>.txt
```

## What is *not* kept here

Ad-hoc / mid-development re-run reports. They regenerate on every run and drift between analyses — only these named, version-pinned baselines are committed.

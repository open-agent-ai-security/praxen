<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Test-suite baselines

Frozen runs of the **eleven** test targets in [`../README.md`](../README.md), kept in the repo so a release run can be diffed against them. The current set is **`v0.7.4-sequential/`** — all eleven targets on the Praxen v0.7.4 skill, against the intent-level Worker Remits. It is the comparison point for the pre-release regression review (see [`../README.md`](../README.md), "What a release review looks like").

## Layout

```
baselines/
  README.md                 ← this file
  owasp_coverage.py          ← cross-baseline OWASP-coverage HTML report generator
  v0.7.4-sequential/         ← CURRENT — all eleven targets, Praxen v0.7.4 (schema 2.0)
  v0.7.0-sequential/         retired — see CHANGELOG [0.7.4]
    BASELINE.md              ← summary table, provenance, how to compare
    <target>/
      <target>-findings-<date>.json        ← the canonical record (the thing you diff)
      <target>-analysis-<timestamp>.html   ← the rendered report
      <target>-analysis-<timestamp>.txt    ← the plain-text summary
  v0.4-parallel/             ← historical — the Phase-2 parallel-path evaluation gate
    GATE-NOTES.md            ← the A/B record and the "drop the parallel path" verdict
```

When a Praxen release legitimately moves the calibration (or the findings schema changes), the suite is re-run cold and re-frozen under a new `vX.Y-sequential/` directory, the previous set is retired, and the pointer in `../README.md` is updated. The `v0.7.4-sequential/` set is the eleven cold runs that validated the deterministic-Step-10 + Step-9.9-emission-discipline changes shipped in `[0.7.4]` — see [`v0.7.4-sequential/BASELINE.md`](v0.7.4-sequential/BASELINE.md) for the per-target table and the deltas-vs-v0.7.0 narrative. Earlier sets — `v0.7.0-sequential/` (the 0.7.0-skill cold runs, kept on disk for diff archaeology), `v0.3-sequential/`, `v0.2-sequential/`, the partial `v0.6-sequential/`, and the same-content `v0.6.3-sequential/` — were retired in successive re-baselines.

`v0.4-parallel/` is not a baseline set — it is the record of the Phase-2 parallel-analysis gate (`design/V2_HARVEST_PLAN.md` §5), whose verdict was to drop the parallel path. It is kept as a historical decision record.

## Re-rendering the HTML/TXT from a baseline JSON

The renderer is deterministic — a baseline's committed HTML/TXT re-render byte-for-byte from its committed JSON, and `tests/render/test_render.py` enforces that on every run:

```bash
python3 skills/behavior-verifier/render.py \
  --findings tests/baselines/v0.7.4-sequential/<target>/<target>-findings-<date>.json \
  --template skills/behavior-verifier/report_template.html \
  --out-html /tmp/<target>.html --out-txt /tmp/<target>.txt
```

## Cross-baseline OWASP coverage report

`owasp_coverage.py` walks every `<target>/<target>-findings-*.json` in a chosen baseline set, sums the per-finding `owasp_llm` / `owasp_agentic` primary scalars, and writes a self-contained HTML summary. Each per-target card links to **both** the agent's source repository **and** the per-target Praxen baseline analysis HTML — so the report doubles as a navigable index of what the suite tests and what the analyses found. Also includes a horizontal bar chart per OWASP Top 10 and a methodology note.

```bash
# defaults: --baseline-dir tests/baselines/v0.7.4-sequential/, --out ./owasp-coverage-report.html
python3 tests/baselines/owasp_coverage.py

# pick a different baseline set, or write the output somewhere specific
python3 tests/baselines/owasp_coverage.py \
  --baseline-dir tests/baselines/v0.7.4-sequential \
  --out /tmp/owasp-coverage.html
```

No external dependencies — pure Python 3 stdlib + inline CSS. The output is generated, not committed.

## What is *not* kept here

Ad-hoc / mid-development re-run reports. They regenerate on every run and drift between analyses — only the named, version-pinned baseline set is committed. The HTML produced by `owasp_coverage.py` is the same — regenerate it on demand, do not commit the rendered file.

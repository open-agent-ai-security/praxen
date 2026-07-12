<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Test-suite baselines

Frozen runs of the test targets in [`../README.md`](../README.md), kept in the repo so a release run can be diffed against them. The current set is **`v1.1-claude48/`** — the same **12 targets** as `v1.0.2-claude48` with OWASP classification **re-tagged** under the corrected 1.1 knowledge bases; detection, evidence, and every RAISE score are byte-identical, so the **median-of-3** freeze carries over unchanged (see its [`BASELINE.md`](v1.1-claude48/BASELINE.md)). It is the comparison point for the pre-release regression review (see [`../README.md`](../README.md), "What a release review looks like"). The prior **`v1.0.2-claude48/`** and **`v0.7.7-claude48/`** sets (and the older `v0.7.x-sequential/` sets) are retained on disk as **archival diff-history** — schema + byte-render still checked, but the remit-verbatim check is scoped to the current set only (`test_render.py:CURRENT_BASELINE`), since archival findings quote the remits as they were at freeze time.

## Layout

```
baselines/
  README.md                       ← this file
  owasp_coverage.py                ← cross-baseline OWASP-coverage HTML report generator
  owasp-coverage-report.html       ← committed snapshot; live at GitHub Pages (link below)
  v1.1-claude48/                   ← CURRENT — v1.0.2 findings, OWASP re-tagged under the 1.1 KBs (scoring identical)
  v1.0.2-claude48/                 ← archival (superseded; 12 targets, median-of-3, schema 2.0)
  v0.7.7-claude48/                 ← archival (superseded; remit-verbatim not re-checked)
  suite-health-report.html         ← committed snapshot; popularity + freshness companion
  raise-coverage-report.html       ← committed snapshot; RAISE coverage companion
  v0.7.7-sequential/         retired — same skill on Opus 4.7; kept for diff archaeology
  v0.7.4-sequential/         retired — see CHANGELOG [0.7.7]
  v0.7.0-sequential/         retired — see CHANGELOG [0.7.4]
    BASELINE.md              ← summary table, provenance, how to compare
    <target>/
      <target>-findings-<date>.json        ← the canonical record (the thing you diff)
      <target>-analysis-<timestamp>.html   ← the rendered report
      <target>-analysis-<timestamp>.txt    ← the plain-text summary
  v0.4-parallel/             ← historical — the Phase-2 parallel-path evaluation gate
    GATE-NOTES.md            ← the A/B record and the "drop the parallel path" verdict
```

When a Praxen release legitimately moves the calibration, the findings schema changes, **or the reference model changes**, the suite is re-run and re-frozen under a new `vX.Y-<variant>/` directory, the previous set is retired, and the pointer in `../README.md` is updated. The current **`v1.0.2-claude48/`** set (12 targets, Praxen 1.0.x on Opus 4.8, median-of-3) is the reference — see its [`BASELINE.md`](v1.0.2-claude48/BASELINE.md). The prior **`v0.7.7-claude48/`** set (Opus 4.8, Praxen 0.7.7) is now retained as archival diff-history alongside the `v0.7.x-sequential/` sets; the remit-verbatim gate is scoped to the current set so evolving remits don't retroactively break archived findings. The retired **`v0.7.7-sequential/`** set is the same skill on Opus 4.7 — the eleven cold runs that validated the SKILL Pre-flight Step 5 + multi-component remit guidance (PR #42) and Step 4 source-inferred log files (PR #43) shipped in `[0.7.7]`; it is kept on disk for diff archaeology (see [`v0.7.7-sequential/BASELINE.md`](v0.7.7-sequential/BASELINE.md)). Earlier sets — `v0.7.4-sequential/` (the 0.7.4-skill cold runs, kept on disk for diff archaeology — validated the deterministic-Step-10 + Step-9.9-emission-discipline changes), `v0.7.0-sequential/`, `v0.3-sequential/`, `v0.2-sequential/`, the partial `v0.6-sequential/`, and the same-content `v0.6.3-sequential/` — were retired in successive re-baselines.

`v0.4-parallel/` is not a baseline set — it is the record of the Phase-2 parallel-analysis gate (`design/V2_HARVEST_PLAN.md` §5), whose verdict was to drop the parallel path. It is kept as a historical decision record.

## Re-rendering the HTML/TXT from a baseline JSON

The renderer is deterministic — a baseline's committed HTML/TXT re-render byte-for-byte from its committed JSON, and `tests/render/test_render.py` enforces that on every run:

```bash
python3 skills/behavior-verifier/render.py \
  --findings tests/baselines/v1.0.2-claude48/<target>/<target>-findings-<date>.json \
  --template skills/behavior-verifier/report_template.html \
  --out-html /tmp/<target>.html --out-txt /tmp/<target>.txt
```

## Cross-baseline OWASP coverage report

A committed snapshot of the aggregate view lives at [`owasp-coverage-report.html`](owasp-coverage-report.html) and is served live by GitHub Pages — **[browse it here](https://open-agent-ai-security.github.io/praxen/tests/baselines/owasp-coverage-report.html)**. Each per-target card links to **both** the agent's source repository **and** the per-target Praxen baseline analysis HTML, so the report doubles as a navigable index of what the suite tests and what the analyses found. Also includes a horizontal bar chart per OWASP Top 10 and a methodology note.

The snapshot is produced by `owasp_coverage.py`, which walks every `<target>/<target>-findings-*.json` in the chosen baseline set and sums the per-finding `owasp_llm` / `owasp_agentic` primary scalars. Regenerate it whenever the baselines change:

```bash
# regenerate the committed snapshot in place (canonical form)
python3 tests/baselines/owasp_coverage.py \
  --baseline-dir tests/baselines/v1.0.2-claude48 \
  --out tests/baselines/owasp-coverage-report.html

# or render somewhere else for ad-hoc browsing
python3 tests/baselines/owasp_coverage.py --out /tmp/owasp-coverage.html
```

No external dependencies — pure Python 3 stdlib + inline CSS.

## What is *not* kept here

Ad-hoc / mid-development re-run reports for individual targets. They regenerate on every run and drift between analyses — only the named, version-pinned baseline set is committed. The `owasp-coverage-report.html` snapshot above is the *one* committed aggregate view (treated like the bundled example reports in [`examples/`](../../examples/) — a stable, browsable artifact that regenerates deterministically from the inputs).

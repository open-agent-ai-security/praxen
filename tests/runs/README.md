<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Pre-release Full Suite Runs

Committed artifacts from named pre-release **Full Suite Runs** (the top tier of [the pre-release test plan](../README.md#test-tiers)). Each subdirectory is a complete sweep of all eleven test targets, run sequentially against a release candidate, with timing data captured and every target's findings JSON / HTML / TXT preserved alongside a top-level `SUITE_RUN.md` verdict report.

These are distinct from the frozen comparison baselines under [`../baselines/`](../baselines/):

- **`baselines/`** — the *reference* a release is graded against. Frozen, named by skill version (e.g. `v0.7.0-sequential/`), changed only by a deliberate re-baseline.
- **`runs/`** *(this directory)* — the *evidence* that a specific release-candidate cleared the bar. Named by the release the run validated (e.g. `v0.7.3-prerelease/`), accumulating over time as a historical record. Diff future runs against the latest one here in addition to the active baseline — the run-to-run drift is more sensitive than the run-to-baseline drift.

## Directory layout per run

```
<release>-prerelease/
  SUITE_RUN.md                   ← verdict report (timing, sanity table, patterns)
  <target>-out/
    <target>-findings.json       ← canonical findings JSON (machine-diffable)
    <target>-analysis.html       ← human-readable report (re-renderable from JSON)
    <target>-analysis.txt        ← plain-text summary
  ... (one per-target dir for each of the eleven targets)
```

`SUITE_RUN.md` carries the same shape every time: the input table (target → source path, scope, baseline ref), per-target detailed notes (duration, count/RAISE delta, dominant Critical themes, sanity verdict), and a closing *Suite verdict & timing summary* with the per-scan timing table, sanity table, and patterns surfaced. Use that bottom block as the at-a-glance review.

## Current entries

- [`v0.7.3-prerelease/`](v0.7.3-prerelease/SUITE_RUN.md) — 2026-05-23. Validated the dev→main 0.7.3 release (report-redesign + audit fixes + README polish). All 11 targets in-band on the Critical-theme gate; two RAISE-divergences flagged as defensible (openhands −0.85, yaah −0.60) under stricter Phase-2 calibration.

## When to add an entry

A **Full Suite Run** is mandatory before any `dev → main` release PR and recommended before any substantial skill-methodology change. See the [Full Suite Run protocol](../README.md#full-suite-run-protocol) in the parent README for the run procedure, the stream-health protocol that keeps subagent scans from stalling, and the verdict-report template.

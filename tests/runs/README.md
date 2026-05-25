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

- [`v0.7.3-prerelease/`](v0.7.3-prerelease/SUITE_RUN.md) — 2026-05-23. First-attempt validation of the dev→main 0.7.3 release (report-redesign + audit fixes + README polish). All 11 targets in-band on the Critical-theme gate; two RAISE-divergences flagged as defensible (openhands −0.85, yaah −0.60) under stricter Phase-2 calibration. **Three targets needed foreground rescue after subagent stalls** (langchain-sql, openai-customer-service, openhands) — the stall pattern that motivated the `b733a45` / `88dd690` SKILL fixes.
- [`v0.7.3-prerelease-r3/`](v0.7.3-prerelease-r3/SUITE_RUN.md) — 2026-05-25. **Authoritative 0.7.3 validation, post-SKILL-fix.** Re-ran the full suite against dev @ `88dd690` (Step 9.9 full-prose manifest + Step 10 mechanical-translation requirement). 11/11 targets completed via subagent (10) + foreground (1) with **zero watchdog stalls at SKILL level**. Three RAISE band drifts flagged (langchain-sql +0.10, autogen-code-executor −0.20, sweep −0.25) — all calibration variance, all themes preserved. Four batch-1 subagents died with `API socket connection was closed unexpectedly` in a 38 s window (transient API event, not SKILL-related); all 4 retried clean.
- [`v0.7.3-prerelease-r4/`](v0.7.3-prerelease-r4/SUITE_RUN.md) — 2026-05-25. **Authoritative 0.7.3 validation, post-polish-commit.** Re-ran the full suite against dev @ `44057a8` (8 SKILL.md polish items + Step 7 compound prominence tweak, addressing PR #30 review feedback). 11/11 targets completed cleanly; all dominant Critical themes preserved; all RAISE values inside their per-target bands except langchain-sql which is stable +0.10 above band (same as r3, calibration variance not regression). Two r3 RAISE band-floor flags (autogen-code-executor and sweep) corrected upward in r4 (+0.30 and +0.70 respectively, both back inside their bands). Initial 6-concurrent batch hit broad watchdog stalls (not a SKILL regression — solo helperbot diagnostic against same SKILL ran clean); dropping to 3-concurrent ran clean for the remaining sub-batches. deepagents-cli required 3 attempts due to a target-specific worker-overplanning pathology between Step 4 announcement and first Read call.

## When to add an entry

A **Full Suite Run** is mandatory before any `dev → main` release PR and recommended before any substantial skill-methodology change. See the [Full Suite Run protocol](../README.md#full-suite-run-protocol) in the parent README for the two invocation paths (parallel subagent / sequential foreground) and the verdict-report template.

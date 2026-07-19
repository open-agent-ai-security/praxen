<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Stage-0 baseline — Stage-2.5 dry-run on the v1.1 stack (2026-07-16)

The **Stage-0 baseline**: a dry-run of the 1.2 plan's Stage-2.5 STOP·LOOK·TEST
mechanics against the **current v1.1 stack** (shipped 1.1.0 skill, committed remits,
Opus 4.8 — the reference model), executed at Steve's direction *before any 1.2 work
exists*. Purpose: measure the severity-instability disease #48 will be graded on
curing; sanity-check the 1.2 gate numbers; establish the pre-1.2 entry baseline.

**15 scans: the flip-check four (deepagents-cli, salesforce, uAgents, craftbot) × 3
independent runs + HelperBot control × 3.** Committed here: this report + every run's
findings JSON (`<target>/<target>-findings-2026-07-16-r{1,2,3}.json` — full schema-2.0
records; r3 of uagents was emitted by its scan under a `uagents-framework-runtime-*`
prefix and is committed under the standard name). HTML/TXT renders and draft
manifests were produced and verified clean for every run but are not committed
(ad-hoc-run convention); they remain reproducible via `render.py` from the JSONs.

## LOOK AROUND
- Reference model Opus 4.8 — unchanged, available. All scans ran on it.
- Upstream drift since the 2026-07-11 freeze: **craftbot / helperbot / salesforce
  unchanged**; **deepagents +1 commit** (evals feature); **uAgents 0.25.2 → 0.25.3**
  (version-bump chore). Judged minor; deepagents' median landing exactly on frozen
  supports that.

## TEST results

| Target | r1 / r2 / r3 | median | frozen | band | verdict |
|---|---|--:|--:|---|---|
| helperbot (control) | 0.90 / 0.75 / 0.75 | **0.75** | 0.75 | 0.60–0.90 | exact; control clean |
| craftbot | 1.30 / 1.30 / 1.30 | **1.30** | 1.15 | 1.00–1.45 | in-band, dead-flat, +0.15 |
| salesforce | 1.85 / 2.00 / 1.70 | **1.85** | 1.70 | 1.55–1.85 | median at band edge; r2 out-of-band (2.00, crossed bucket) |
| uAgents | 2.15 / 2.15 / 1.85 | **2.15** | 2.00 | 1.70–2.30 | in-band; σ≈0.17 < historical 0.245 |
| deepagents | 2.55 / 2.70 / 2.70 | **2.70** | 2.70 | 2.55–2.85 | exact |

- **Reliability: 15/15 completed, 0 watchdog deaths, 0 relaunches.** Durations 8–17
  min (median ~10; craftbot the outlier at 17/11/15). No stalls observed.
- **Weighted drift (median-of-3 vs frozen): mean |drift| 0.09, max 0.15** — the 1.2
  |drift| ≤ 0.2 gate PASSES on today's stack. Per-run spread ≤ 0.30 everywhere.
- **Directional lean:** 3/5 medians above frozen, 2 exact, 0 below; 10/15 individual
  runs ≥ frozen. Mild +0.09 high-lean vs the anchor — same direction as the 1.0.2
  remit-refresh lift. Watch-item for the anchored lean check; not gating.

## Severity-boundary (Critical↔High) analysis — the headline

Within-run-set flips (same finding, different severity across the 3 runs):
- **salesforce**: injection-compound finding C in 2 runs, H in 1 (C-count 0/1/1). Worst offender.
- **craftbot**: C-count 4/3/4 (weighted flat at 1.30 throughout — offsetting mix shifts).
- **helperbot**: C-count 3/4/4 (one flip, r1).
- **uAgents, deepagents**: internally consistent (0 within-set flips).

Consistent disagreement with the FROZEN anchor (runs agree with each other, not the anchor):
- **deepagents TLS-scheme gap: frozen Critical, fresh runs H/H/H (3-of-3 unanimous)** —
  runs reason it's bounded (the CLI never opens the connection itself). Candidate
  baseline mis-anchor, not run churn.
- **uAgents**: 3C in every fresh run vs frozen 1C (plaintext-key + spoofable-admin
  consistently uplifted). Same class: anchor-vs-runs disagreement, stable across runs.

**Implication:** severity instability splits into two distinct problems —
(a) genuine run-to-run churn on nameable boundary findings (salesforce, craftbot),
which #48's anchors fix; (b) frozen-anchor calibration disputes (deepagents, uAgents),
which only the human-anchored reference resolves. The anchor was not hand-edited;
(b) routes into the hand-score questionnaire (plans/RELEASE_1.2_PLAN.md, Stage 3).

## Gate realism verdict (the numbers 1.2 commits to)
- **|drift| ≤ 0.2 median-of-3: realistic** — already met pre-#48 (max 0.15).
- **Zero C↔H flips across 3×: ambitious but right** — 2 of 4 flip-check targets fail
  it today, on nameable findings. #48's anchors should be authored against these five
  concrete cases (the questionnaire's seed set): salesforce injection-compound,
  craftbot shell-exec/approval cluster, deepagents TLS-scheme, uAgents plaintext-key,
  uAgents spoofable-admin.
- **Stage-1 finding-count spread ≤ ±2: NOT already met** — helperbot spread 3
  (11/8/10), uAgents spread 4 (9/10/13). Decomposition scatter is real; grade #29/#33
  on these two targets.

## Side findings (upstream, not Praxen)
- **uAgents r3 found a real correctness/security bug**: `get_or_create_private_keys`
  persists a *different* wallet key than it returns/uses
  (`python/src/uagents/storage/__init__.py` ~147 vs ~149) — a name-keyed agent's
  wallet address silently changes across restart. Candidate for upstream disclosure
  after a dedup check.
- deepagents `libs/cli/THREAT_MODEL.md` is stale (documents the retired REPL/TUI
  surface).

## Provenance
Working directories under gitignored `local/v1.2-stage0/<target>-r{1,2,3}-out/`
(sources shallow-cloned to `local/v1.2-stage0/src/<slug>/`). Scans run as parallel
background subagents (≤5 concurrent), each following `skills/behavior-verifier/SKILL.md`
end-to-end with the Step 9.9 emission discipline; every run's `manifest_to_findings.py`
and `render.py` exited 0.

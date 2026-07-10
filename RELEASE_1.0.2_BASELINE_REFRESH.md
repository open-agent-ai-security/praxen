<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 1.0.2 — Baseline & Target-Roster Refresh

> **Branch:** `1.0.2` · **Type:** re-baseline + test-target refresh (no functional/skill logic change) · **Folds into:** `1.1`

## Why this release exists

Praxen's frozen regression baseline is **`tests/baselines/v0.7.7-claude48/`** — the twelve targets scanned on the **0.7.7 skill** under Opus 4.8. Praxen has since shipped **1.0.0 GA** and **1.0.1**, so the reference baseline predates the entire 1.0 skill line; every release review is currently graded against a 0.7.7-era exemplar.

Before functional work on **1.1** (which will deliberately move scoring, detection, and possibly schema), we want a **current, stable baseline frozen on the shipping 1.0.x skill**. That is the whole purpose of 1.0.2:

- **1.0.2 is a re-baseline + target refresh, not a feature release.** No `SKILL.md`, `schema.py`, `render.py`, or knowledge-base **logic** changes. Functionality stays frozen; only the committed baselines, the test-target roster, and the version stamp move.
- Re-baselining on a stable skill is an explicitly supported release reason — see `tests/README.md` › *Re-baselining (multi-run characterization)*.
- The fresh baseline becomes the **regression reference for 1.1**: with functionality held constant across the re-freeze, any number movement during 1.1 is attributable to a 1.1 change, not to baseline drift.

**Low-risk on the skill axis.** The 0.7.7 → 1.0 line was largely **polish, not logic** — so we expect the *retained* targets to re-baseline with **minimal band movement**. The median-of-3 rigor still applies (parts of the analysis are LLM judgment), but the substantive work here is the **target-roster refresh**, not chasing skill drift. If a retained target *does* shift materially with no skill logic to explain it, that's a finding worth understanding before we freeze.

**Sequencing:** freeze the new baseline here on `1.0.2`; when it's green, **fold `1.0.2` into `1.1`** so 1.1 development proceeds on top of the fresh reference. 1.0.2 can either ship as a standalone patch (a documented "re-baseline" release) or be absorbed into the 1.1 release — see *Fold-down* below.

## Scope

**In scope**
- Re-run the suite on the current 1.0.x skill under the reference model; freeze a new set `tests/baselines/v1.0.2-claude48/` via median-of-3 characterization.
- **Refresh the target roster** (drop dead upstreams, add fresher archetypes — see below).
- Recompute per-target bands + the active-baseline pointer in `tests/README.md` and `tests/baselines/README.md`.
- Write the new `BASELINE.md` (per-target table, provenance, band deltas vs `v0.7.7-claude48`, model-lean note).
- Regenerate `tests/baselines/owasp-coverage-report.html` (and the RAISE coverage view) from the new set.
- Commit the pre-release evidence run `tests/runs/v1.0.2-prerelease/` with a `SUITE_RUN.md` verdict.
- Retire `v0.7.7-claude48/` in place (kept for diff archaeology).
- Version bump 1.0.1 → 1.0.2 across the manifest set; CHANGELOG `[1.0.2]` entry.

**Explicitly out of scope (→ 1.1)**
- Any change to `SKILL.md`, `schema.py`, `render.py`, `report_template.html`, or `skills/behavior-verifier/knowledge/` **logic**.
- Calibration/detection changes, schema changes, new detection patterns.
- New *harness* support (e.g. #151 Google Antigravity) — that's a skill/functional change, not a test target.

## Target roster refresh

Since we're re-freezing anyway and functionality is stable, this is the right moment to do all target churn at once and freeze it into one clean set. Rolling in the target-freshening RFEs:

| Change | Target | Issue | Rationale |
|---|---|---|---|
| **Replace** | `sweep` → fresh non-coding archetype | **#69** | Dead upstream + redundant archetype; swap for an under-covered archetype on a live upstream |
| **Replace** | `langchain-sql` → live NL-to-SQL/DB agent | **#70** | Upstream archived/deprecated. **Replace, not drop** — it's the only DB-query archetype in the suite |
| **Add** | CraftBot (`CraftOS-dev/CraftBot`) | **#116** | Self-hosted general assistant; introduces 3 finding types + 1 scoring pattern not exercised today |
| **Add** | fetchai/uAgents | **#64** | Multi-agent framework archetype (may also cover the #69 "non-coding archetype" gap — see decision) |
| **Add (candidate)** | Agentforce — `examples/salesforce-help-agent-accelerator` | — | Already an **example** with a committed `WORKER_REMIT.md` + analysis, but **not** a baseline. Real-world enterprise (Salesforce Agentforce) agent — strong candidate to promote into the baseline suite |

**Decisions to make before freezing:**
1. **Does uAgents (#64) double as the `sweep` replacement (#69)?** #69 wants a non-coding archetype; uAgents is a multi-agent framework. If yes, that's one target, not two — keeps the suite leaner.
2. **Pick the `langchain-sql` replacement (#70)** — a specific live NL-to-SQL/DB agent to preserve the DB-query archetype.
3. **Promote Agentforce?** It already has a remit and an example analysis, so promotion cost is low (median-of-3 + freeze + bands). Recommended — it's the only real-world enterprise SaaS agent available.
4. **Watch suite size / runtime.** The full suite is ~90 min (parallel subagent) / 3–4 hr (sequential) at **12** targets; each add extends that. Net roster after the changes above is ~**13–15** — keep it deliberate, don't over-grow. Retire, don't just accumulate.

**Remits:** new/promoted targets need a Worker Remit under `tests/remits/<slug>.md` (Agentforce's already exists at `examples/salesforce-help-agent-accelerator/WORKER_REMIT.md` — decide whether to move/copy it into `tests/remits/` or reference in place). Remits are held constant across the three characterization runs.

## The re-baseline procedure

Follows `tests/README.md` › *Re-baselining (multi-run characterization)*:

1. **Confirm the reference model** is Opus 4.8 (the `-claude48` variant). If the reference tier has moved, name the set accordingly.
2. **Retained targets:** characterize over **3 independent runs** on identical inputs (1.0.x skill, sources, remits constant) and confirm they land where `v0.7.7-claude48` did — expected, since 0.7.7→1.0 was polish. Any material, unexplained shift is investigated before freeze.
3. **New / replaced targets:** characterize from scratch over 3 runs; set initial bands from mean ± spread.
4. **Freeze the median run** per target as the committed exemplar (one real, unedited run — keeps the byte-render gate honest).
5. **Set each band from the 3-run mean ± observed spread.** Move *stable-but-offset* targets; widen *noisy-but-centred* ones. Diff by theme and rule text, never by `R-NN` id.
6. **Name the set `tests/baselines/v1.0.2-claude48/`**, retire `v0.7.7-claude48/` in place, update the pointer + bands in both READMEs.
7. **Regenerate coverage:** `python3 tests/baselines/owasp_coverage.py --baseline-dir tests/baselines/v1.0.2-claude48 --out tests/baselines/owasp-coverage-report.html` (+ the `raise_coverage.py` equivalent).
8. **Verify integrity:** `python3 tests/render/test_render.py` must pass — every new baseline JSON validates against `schema.py`, re-renders byte-for-byte, and each `rule_text` quotes its remit verbatim. CI green on 3.9 / 3.12 / 3.13.
9. **Write `BASELINE.md`** (worked example: the current `v0.7.7-claude48/BASELINE.md`).

## Version bump (1.0.1 → 1.0.2)

Update the version in: `PRAXEN_SPEC.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, root `plugin.json`, root `marketplace.json`, `.codex-plugin/*`, and add a `[1.0.2]` CHANGELOG entry framed as: *"Regression baseline re-frozen on the 1.0.x skill; test-target roster refreshed (retired dead upstreams `sweep`/`langchain-sql`, added CraftBot/uAgents/Agentforce). No functional changes."* `release.yml` checks the tag matches `PRAXEN_SPEC.md`'s version. (The README **release pill** is now the dynamic shields.io `github/v/release` badge — it auto-updates from the latest tag and is no longer part of the bump.)

## Deliverables checklist
- [ ] Reference model confirmed
- [ ] Target-roster decisions made (#69 replacement / uAgents overlap · #70 DB replacement · promote Agentforce · final count)
- [ ] Remits in place for new/promoted targets (`tests/remits/`)
- [ ] 3-run characterization: retained targets confirmed stable; new/replaced targets characterized
- [ ] `tests/baselines/v1.0.2-claude48/` frozen (median exemplars + `BASELINE.md`)
- [ ] Bands + pointer updated in `tests/README.md` and `tests/baselines/README.md`
- [ ] `owasp-coverage-report.html` (+ RAISE view) regenerated
- [ ] `tests/runs/v1.0.2-prerelease/SUITE_RUN.md` committed
- [ ] `v0.7.7-claude48/` retired in place
- [ ] `python3 tests/render/test_render.py` green; CI green 3.9/3.12/3.13
- [ ] Version bumped to 1.0.2; CHANGELOG `[1.0.2]` entry
- [ ] Closes: #69, #70, #116, #64 (and the Agentforce promotion)

## Fold-down

When the baseline is frozen and green, merge `1.0.2` → `1.1`; `1.1` then carries the fresh `v1.0.2-claude48` baseline (and refreshed roster) as its grading reference. Whether to *also* ship 1.0.2 as a standalone patch tag or absorb it into the 1.1 release is a release-management call — the re-baseline + target refresh stands on its own as a valid patch, but folding it into 1.1 avoids a release whose only user-visible change is a version number and a test-suite reshuffle.

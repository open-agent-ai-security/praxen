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

## Target roster refresh — stepwise, not all at once

Do the roster change in **two ordered phases. Add and prove out the new targets first; only then evaluate who gets replaced.** This way we never drop coverage before its replacement is validated, and the retirement calls are made with real evidence about what the additions actually exercise. Don't churn the whole roster in one motion.

### Phase 1 — Add the new targets and prove them out

Add each new/promoted target, get it **running cleanly end-to-end**, and confirm the **results are good** before it's frozen into the baseline. A target earns its place only if it scans clean and produces substantive, correct findings — not noise.

| Add | Target | Issue | Brings |
|---|---|---|---|
| Add | CraftBot (`CraftOS-dev/CraftBot`) | **#116** | Self-hosted general assistant; 3 finding types + 1 scoring pattern not exercised today |
| Add | fetchai/uAgents | **#64** | Multi-agent framework archetype (candidate to also cover the #69 "non-coding" gap — evaluated in Phase 2) |
| Promote | Agentforce — `examples/salesforce-help-agent-accelerator` | — | Already an example (committed `WORKER_REMIT.md` + analysis); the only real-world enterprise (Salesforce Agentforce) agent — strong promote candidate |

**Per-target acceptance — all must hold before a target is frozen in:**
- [ ] Worker Remit in place (`tests/remits/<slug>.md`). Agentforce's exists at `examples/salesforce-help-agent-accelerator/WORKER_REMIT.md` — decide move/copy vs reference. Remits are held constant across the three runs.
- [ ] **Clean end-to-end scan** — no harness / discovery / manifest errors.
- [ ] **Median-of-3 characterization is stable** (variance within the usual ±0.3–0.5 band); freeze the median run as the exemplar.
- [ ] **Results are good** — findings are substantive and correct for the target, themes make sense, nothing garbage or hallucinated. This is a *judgment* gate, not just "it ran."
- [ ] `tests/render/test_render.py` passes on the new baseline JSON (schema + byte-render + remit-verbatim).
- [ ] Initial bands set from the 3-run mean ± spread.

Freezing the additions grows the roster **temporarily** (12 → up to ~15); that's expected — Phase 3 brings it back down.

### Phase 2 — Remit health check on the retained targets

The retained targets' Worker Remits were authored during the **0.7.x** line, and the remit format/conventions may have **evolved substantially** since (see `docs/writing-remits.md`, `PRAXEN_SPEC.md`, and the multi-component remit guidance added in `[0.7.7]`). Re-baselining the 1.0.x skill against **stale-format remits** would grade current behavior on outdated intent specs — undermining the point of a clean current baseline. So, after the additions land, **audit every retained remit and bring drifted ones up to the current format** before re-characterizing that target.

- [ ] **Audit** each retained `tests/remits/<slug>.md` against the current remit format — use the freshly-authored Phase-1 remits as the reference for "good shape." Look for structural drift, missing sections the current format expects, and outdated conventions.
- [ ] **Refresh** drifted remits to the current format, **holding intent constant** — modernize the *expression*, not *what the agent is allowed to do*. A refresh must not silently change scope (that conflates format modernization with a coverage change).
- [ ] **Re-characterize + re-freeze** any target whose remit changed — the byte-render gate requires each baseline's `rule_text` to quote its remit **verbatim** (`tests/render/test_render.py` enforces this from `praxen_version` 0.6.0 on), so a remit edit *forces* a fresh median-of-3 for that target.
- [ ] Skip retirement candidates you're about to drop in Phase 3 — don't modernize a remit for a target that's leaving.

### Phase 3 — Then evaluate who gets replaced

**Only after** the additions are proven, make the retirement/replacement calls — informed by what the new targets now cover:

- **`sweep` (#69)** — retire once we've confirmed the additions cover the archetype it held (does uAgents fill the non-coding / multi-agent archetype role? if yes, `sweep` can go without losing coverage).
- **`langchain-sql` (#70)** — the only DB-query archetype. **Replace, not drop:** retire it only once a live NL-to-SQL/DB target has been added and proven to Phase 1's bar. If no DB replacement is ready, keep `langchain-sql` (from a pinned snapshot) rather than lose the archetype.

**Runtime discipline.** The full suite is ~90 min (parallel subagent) / 3–4 hr (sequential) at **12** targets; each net add extends it. Land near **12–14**, not 15+ — retire as you add, don't just accumulate.

## The re-baseline procedure

Follows `tests/README.md` › *Re-baselining (multi-run characterization)*:

1. **Confirm the reference model** is Opus 4.8 (the `-claude48` variant). If the reference tier has moved, name the set accordingly.
2. **Retained targets:** characterize over **3 independent runs** on identical inputs (1.0.x skill, sources, and the **Phase-2-refreshed remits** held constant) and confirm they land where `v0.7.7-claude48` did — expected, since 0.7.7→1.0 was polish. A remit that was modernized in Phase 2 may legitimately move its target's numbers (new intent expression) — that's an intended shift, not a regression. Any *unexplained* shift is investigated before freeze.
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
- [ ] **Phase 1** — new targets (CraftBot #116, uAgents #64, Agentforce) added, running clean, results validated, frozen; remits authored in current format
- [ ] **Phase 2** — retained remits audited vs the current format; drifted ones refreshed (intent held constant) and affected targets re-characterized
- [ ] **Phase 3** — retirement/replacement calls made with Phase-1 evidence (#69 sweep · #70 langchain-sql); final count 12–14
- [ ] 3-run characterization: retained targets confirmed stable on refreshed remits; additions characterized clean
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

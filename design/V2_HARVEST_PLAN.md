# Praxa — V2 Harvest Plan

**Status:** proposed — for review
**Authors:** Steve Wilson, David Kennedy (consulted)
**Date:** 2026-05-11

---

## 1. Context

Two parallel implementations of "replace the LLM-driven HTML assembly with a deterministic code pipeline" exist:

- **`main` (= `v0.2.0`, tagged):** the implementation that landed — a template-engine renderer (`skills/behavior-verifier/render.py`) that substitutes a canonical findings JSON (`schema_version: "1.0"`, validated by `skills/behavior-verifier/schema.py`) into the existing Exabeam-brand `report_template.html`. Includes a full 9-target suite re-run + a two-step RAISE-scoring calibration pass, updated `PRAXA_SPEC.md` §6 / `docs/` / `examples/`, and the `tests/render/test_render.py` harness.
- **PR #1 (`feat/v2-deterministic-render-pipeline`, by davidkennedylr, open):** an alternative — builds the HTML in Python (`lib/render.py`, a "DEF/TAC OPS" dark theme, **+ PDF** via headless Chrome), a formal JSON-Schema file (`lib/praxa-findings-v2.schema.json`, "v2" / `2.0.0`) alongside a hand-written validator (`lib/schema.py`), a **parallel map-reduce analysis** variant (`lib/parallel.py` + `skills/behavior-verifier/SKILL-PARALLEL.md`), a snapshot-based test harness (`tests/test_harness.py`), and **GitHub Actions CI + release workflows**.

The two share a merge base (`18d0799`) but diverged; `main` shipped first and is tagged `v0.2.0`, so PR #1 no longer merges cleanly. Steve and David have agreed: **keep `main` as the trunk and harvest the genuinely-additive parts of PR #1 into it**, in a specific order, deferring the look-and-feel reskin and PDF output.

This document is that plan. It's being PR'd for review; once approved, Phase 0 begins.

---

## 2. Decisions already made

| Decision | Resolution |
|---|---|
| Trunk | `main` (= `v0.2.0`) stays the trunk. |
| PR #1 | Will be **closed** (Phase 0) with a comment pointing at this plan and the harvest tracking, so the branch and its parked pieces remain recoverable — not discarded. |
| Schema version after the merge | **`schema_version: "2.0"`** (aligns with PR #1's "v2" framing; clean break from the just-shipped `1.0`). |
| Supported Python floor | **3.9+.** That's the macOS Command Line Tools system Python on Ventura / Sonoma / Sequoia, and the version this repo is developed and tested on. **3.8 is dropped** — it's been EOL since 2024-10-07 (no upstream security patches); we don't test or claim support for a dead interpreter. **Not** PR #1's 3.10 floor either — that would break stock macOS (which is on 3.9). CI matrix: **`3.9 / 3.12 / 3.13`** (floor / mid / latest). Phase 1 (or a quick standalone PR) bumps the `3.8+` strings in `PRAXA_SPEC.md` §2.6/§8 and `docs/installation.md` to `3.9+` to match. |
| Harvest order | (1) JSON structure → (2) performance (parallel analysis) → (3) GitHub Actions + automated testing. |
| Deferred | The "DEF/TAC OPS" look-and-feel reskin and the `--pdf` headless-Chrome output. Tracked in `design/DEFERRED.md`; PR #1's branch retains the code. |
| Process | Every phase lands as **its own PR against `main`**, reviewed and CI-gated — no direct pushes. (Direct-pushing the `v0.2.0` work to `main` is what collided with PR #1; we don't repeat that.) |

`praxa_version` (a field distinct from `schema_version`) bumps `0.2.0 → 0.3.0` (Phase 1) → `0.4.0` (Phase 2) → `0.5.0` (Phase 3); once all three phases are in and the look-and-feel call is made, `1.0.0`.

---

## 3. Phase 0 — Setup (≈ ½ day)

1. Land this plan (`design/V2_HARVEST_PLAN.md`) via the review PR.
2. Add `design/DEFERRED.md` — a short note recording *where* PR #1's deferred pieces live (the L&F reskin and `--pdf` output, both in PR #1's `lib/render.py`) and *why* they're parked, so they're easy to revisit.
3. Resolve the remaining open decisions (§7).
4. Close PR #1 with a comment linking this plan; keep the branch.

---

## 4. Phase 1 — JSON structure → `v0.3.0`, `schema_version: "2.0"` (≈ 2–3 days)

Goal: a **merged schema** that adopts PR #1's better-structured findings model *and* keeps everything `main` has that PR #1 drops.

### 4.1 — Field-by-field merge (recommended; subject to §7.5)

| Area | Take | Notes |
|---|---|---|
| `evidence` | **PR #1's** `[{ "file": ..., "line": ..., "snippet": ... }]` | the headline improvement — machine-friendly; replaces `main`'s `evidence: [str]` |
| finding text | **keep `main`'s `summary`** (one-line, required — drives the finding-card header) **+ add PR #1's `description`** (optional, longer body) | renderer keeps using `summary`; `description` is carried in the JSON now and surfaced in the UI when the L&F work is un-deferred |
| recommended action | **PR #1's** `recommended_actions: []` (array) | renderer renders a list instead of a single line into the existing `.rec-text` block |
| `confidence` (per finding) | **keep `main`'s** `High / Medium / Low` | don't adopt PR #1's separate `evidence_quality` — same idea, `main`'s is already wired |
| compound/related | **keep `main`'s** `related_findings: [ids]` + `escalation` (`alert` / `log_only`) | covers compound-signal cross-refs; don't adopt PR #1's `compound_signals` (redundant with this) |
| `tags: [{kind, label}]` | **keep `main`'s** | carries the full OWASP display labels (`LLM01 — Prompt Injection`, etc.) for rendering |
| `policy_rule_ids` / `policy_rule_text` | **keep `main`'s** | PR #1's `policy_reference` is rougher |
| per-category `confidence` + `weight` (in `raise_posture.categories[]`) | **keep `main`'s — do not regress** | PR #1's schema drops these; the report shows "Confidence: High \| Weight: 15%" per RAISE card |
| `footer.severity_counts`, `raise_posture.weighted_overall` (stored) | **keep `main`'s** store-and-validate | PR #1 computes these in the renderer; `main` keeps the "JSON is the complete record" property and the cross-field consistency checks |
| formal JSON-Schema document | **add** `skills/behavior-verifier/findings.schema.json` | a published, machine-readable contract for downstream tooling, adapted from PR #1's `praxa-findings-v2.schema.json` to the merged shape. **`schema.py` stays the runtime validator** (hand-written, stdlib-only, with the cross-field invariants) — we don't take a `jsonschema` dependency. A test asserts the schema file and the validator agree on every fixture. |
| versions | `schema_version: "2.0"`, `praxa_version: "0.3.0"` | |

### 4.2 — Implementation (each a commit on the Phase-1 branch)

1. Write `skills/behavior-verifier/findings.schema.json` (the merged shape, JSON Schema form).
2. Update `skills/behavior-verifier/schema.py`: merged shape; keep the helper-function pattern `main` already has (PR #1's `_validate_*` duplication — the thing `gemini-code-assist` flagged — does not get reintroduced); keep all cross-field invariants (counts match the arrays, anchors resolve, exactly the six RAISE keys with their standard weights, `weighted_overall = Σ(score × weight)`); add the schema-file ↔ validator agreement check.
3. Update `skills/behavior-verifier/render.py` — **data-binding only, no look-and-feel change**: `evidence` is now `[{file, line, snippet}]` → render each item as `file:line — snippet` into the same `evidence-block` div; `recommended_actions` is now an array → render as a list into the same `.rec-text` block; `description` is accepted and carried but not yet surfaced (the deferred L&F work surfaces it). `report_template.html` ideally unchanged; at most one trivial tweak.
4. Update `skills/behavior-verifier/SKILL.md` Step 10 (the canonical-JSON template and the field rules) to emit the merged schema. **The "Calibration anchors" guidance in Step 5 / 9.4 stays exactly as-is.**
5. Update `tests/fixtures/finbot.canonical.json` to the merged shape and extend `tests/render/test_render.py` (structured-evidence assertions, the schema-file ↔ validator agreement test).
6. Regenerate `examples/finbot` + `examples/helperbot` (one blind run each on the merged-schema skill); update `examples/README.md`.
7. Update `PRAXA_SPEC.md` §6 and `docs/interpreting-reports.md` for the merged shape; add a "schema change in v0.3 / schema 2.0" note (the prior change was the v0.2 / schema 1.0 one).

### 4.3 — Gate

Re-run the **full 9-target** test suite — *sequentially*, on the merged-schema (Phase-1) skill — and **preserve the run** under `tests/baselines/v0.3-sequential/`, matching the layout of the existing [`tests/baselines/v0.2-sequential/`](../tests/baselines/v0.2-sequential/) (per-target subdirs with the three artifacts each + a top-level `BASELINE.md` summary). This is the canonical **pre-parallel baseline** that Phase 2's parity gate (§5.2 / §5.3) diffs against. The bar for this gate: every render exits 0, every JSON validates against `schema.py` and `findings.schema.json`, and weighted RAISE scores land in the (post-recalibration) `tests/README.md` bands with the same dominant themes as the v0.2-sequential baseline — **a diff of v0.3-sequential vs v0.2-sequential is the calibration-shift check** (Phase 1 only changes the JSON shape; semantic content is unchanged, so the scores shouldn't move). Then: CHANGELOG entry, `praxa_version` → `0.3.0`, tag `v0.3.0`, merge the PR.

> **Two baselines, two roles** — `tests/baselines/v0.2-sequential/` (already in the repo as of PR #3) is the sequential snapshot on the current shipped skill + schema 1.0; it's the "before" for the calibration-shift check above. `tests/baselines/v0.3-sequential/` (produced here) is on the merged-schema skill — the same skill the Phase-2 parallel path runs against, so it's the parity comparator for §5.2/§5.3. Once both exist, every release diffs the new run against the latest baseline per [`tests/README.md`](../tests/README.md) — the test plan codifies that full compare.

---

## 5. Phase 2 — Performance: parallel analysis → `v0.4.0` (≈ 2–3 days)

PR #1's `lib/parallel.py` + `skills/behavior-verifier/SKILL-PARALLEL.md` — six RAISE-category mapper agents run concurrently (each analyzes the workspace from one category's lens), then a reducer agent does compound-signal reasoning + deduplication + assembly into the canonical JSON. This targets the *actual* current bottleneck — the analysis, not the render (which `v0.2.0` already made deterministic and sub-second). Claimed ≈ 4–5× wall-clock on the analysis.

### 5.1 — Port + reconcile

1. Bring `parallel.py` onto `main` (path per the §7.3 layout decision). It is a prompt generator + result merger — it does not run the agents; Claude Code spawns them.
2. Reconcile the mapper prompts with `main`'s **recalibrated** `SKILL.md`: each category mapper must carry the Step 5 "Calibration anchors" discipline for its category, the "Never reprint secrets" rule, and the category-relevant detectors (empty-file signal, declared-but-never-consulted config, etc.) — **and these are *built from* `SKILL.md`'s live sections at prompt-build time, never a frozen copy** (see §7.4): `parallel.py`'s mapper-prompt builder quotes the relevant `SKILL.md` steps so detection-pattern / calibration-anchor edits propagate to the parallel path automatically.
3. The reducer must emit the **Phase-1 merged schema** (this is why Phase 1 lands first).
4. Package decision (§7.4): whichever form it takes, **the analysis logic stays in `SKILL.md` only** — the parallel path owns *orchestration* (build six mapper prompts → spawn → collect → run the reducer) and *sources* its analysis content from `SKILL.md`, never restating it. Leaning: a thin `SKILL-PARALLEL.md` orchestration wrapper, so the sequential path stays the safe default.
5. `parallel.py`'s mapper-output validation validates against the relevant slice of `findings.schema.json` (reuse `schema.py`).

### 5.2 — Risks to resolve in this phase

- **Calibration parity.** PR #1 has only a one-target spot-check ("3.7 vs 3.8 weighted RAISE"). We do a proper sequential-vs-parallel comparison across ≥ 4 suite targets — including OpenHands (the mature one) and HelperBot (the CTF anchor) — **diffed against the `tests/baselines/v0.3-sequential` baseline frozen in §4.3** (re-running sequential on those targets too if any drift is suspected). Bar: parallel lands in the same `tests/README.md` bands as sequential and surfaces the same dominant themes. If a category mapper systematically over/under-scores its own category in isolation, the first lever is the mapper prompt for that category — but the tuning is *time-boxed* and the call is made at the §5.3 decision point, not iterated open-endedly.
- **The reducer must be able to verify cross-category chains.** PR #1's reducer reasons over the six mapper outputs only — it never re-opens the code, which caps compound-signal quality at "whatever the mappers surfaced as standalone findings" and creates a blind spot for chain *links* that aren't a finding on their own (e.g. "function X's output feeds function Y"). **Recommended: give the reducer the workspace path and let it do *targeted* re-reads** when verifying a candidate compound chain — a handful of file reads by one agent, not a full re-scan, so the ≈ 4–5× win holds. "No re-read" stays the fallback if calibration-parity testing shows the targeted-read reducer over-claims chains.
- **Token cost.** Six parallel mappers ≈ 6× the input tokens of a single analyst pass — a speed-for-cost trade, not a free win. Document it; the sequential path stays available for cost-sensitive runs.
- **Measure the speedup with a controlled A/B — don't trust batch wall-clocks.** The ≈ 4–5× claim is verified against clean timings, not the noisy parallel-batch numbers in §5.4: pick a few representative targets (small / medium / big / worst-case — e.g. HelperBot / FinBot / OpenHands / Devika), **pre-clone each repo**, and time *just the analysis + render*, run each target **single-target (no parallel contention)**, sequentially and then in parallel map-reduce mode, back to back. Sequential wall-clock ≈ the Steps-1–9 LLM phase; parallel wall-clock ≈ max(mapper durations) + reducer; the render step (`render.py`, ≈ 0.08 s) is negligible in both.

### 5.3 — Decision gate & exit ramps

Phase 2 is **time-boxed**: if the parallel path hasn't reached parity within ≈ 2 days of build-and-tune effort (i.e. the lower end of the 2–3 day estimate), we stop and decide — no open-ended tuning loop. The call is made once, after the ≥ 4-target sequential-vs-parallel comparison (parity *and* the §5.2 timed A/B), against three explicit outcomes:

1. **Parity achieved *and* a real speedup** — parallel lands in the same `tests/README.md` RAISE bands as sequential across the comparison targets, surfaces the same dominant themes, *and* the controlled A/B shows a meaningful wall-clock win on the analysis phase (the claim is ≈ 4–5×; anything materially short of ~2× is not worth defaulting to). → **Ship parallel as the default path; sequential becomes the cost-sensitive fallback** (it's ~6× cheaper in tokens). CHANGELOG, `praxa_version` → `0.4.0`, tag `v0.4.0`, merge.
2. **Close but not there** — themes covered but scores drift outside the bands on some targets (traceable to category-isolated mappers lacking cross-category context by design), *or* parity holds but the speedup is marginal. → **Ship parallel as opt-in/experimental** (a `--parallel` flag or a clearly-labelled `SKILL-PARALLEL.md`), sequential stays the default; revisit in a future phase. Still `v0.4.0` + merge, but documented as experimental.
3. **Fundamentally broken** — category isolation loses too much cross-signal context for parity to be reachable without re-introducing holistic analysis (which would defeat the point). → **Drop the parallel path entirely, close the phase, reclaim the effort.** Document why in `design/DEFERRED.md` (and `parallel.py` etc. stay recoverable in PR #1's branch). No `v0.4.0`; Phase 3 follows directly.

Outcome 1 is the goal; 2 is the realistic fallback; 3 is the off-ramp that keeps Phase 2 from becoming a sink.

### 5.4 — Sequential timings (the "before")

The parallel path is measured against the sequential pipeline's *analysis* time (the render step is already free — `render.py` is ≈ 0.08 s). Rough reference, from the `v0.3-sequential` gate runs — **noisy:** each ran 9-in-parallel (possible API-throughput contention), and each wall-clock includes a `git clone --depth 1` of a wildly-varying-size repo, workspace staging, the analysis, the render, and any validator-caught re-render. A ballpark, not the comparator:

| target | wall-clock (rough) | notes |
|---|---:|---|
| HelperBot | ~4.5 min | small JS repo |
| OpenAI CS | ~4.5 min | example + SDK snapshot |
| LangChain SQL | ~5.3 min | small focused slice; large repo to clone |
| AutoGen Code Executor | ~5.4 min | five executors + core |
| FinBot | ~6.0 min | small Flask app; +1 validator re-render |
| Sweep | ~6.4 min | `sweepai/{agents,core,web,config}` + reaching out for context |
| OpenHands | ~7.3 min | large repo, ~58 files read |
| Aider | ~8.3 min | `aider/*.py` + `coders/`; +2 validator re-renders |
| Devika | ~13.6 min | worst case — full `src/` tree, ~56–84 files read |

≈ 6.8 min mean / 6 min median per target; the LLM analysis (Steps 1–9) is ~60–80% of that. Phase 2's gate (§5.2 / §5.3) replaces these with **clean controlled A/B timings** (repo pre-cloned, single-target, analysis + render only, sequential vs parallel) and commits the result — a `tests/baselines/TIMINGS.md`, or a "Timings" section in `tests/baselines/v0.3-sequential/BASELINE.md` — as the recorded "before" the parallel path is held to.

---

## 6. Phase 3 — GitHub Actions + automated testing → `v0.5.0` (≈ 1–1.5 days)

### 6.1 — Merge the test approaches

Keep `tests/render/test_render.py` (invariant checks, negative cases, determinism, brace-collision, rich-text). Add the one thing it lacks that PR #1's harness has — **golden-file/snapshot testing** — but drop PR #1's brittle custom `.snapshot` format (the thing `gemini-code-assist` flagged) in favour of the simplest robust thing: check in `expected.html` + `expected.txt` per fixture and `cmp` byte-for-byte (the renderer is deterministic, so this just works and catches any unintended HTML drift). Adapt PR #1's `tests/test_harness.py` to drive it; bring the finbot / helperbot fixtures (in the merged schema).

### 6.2 — CI / release workflows

Adapt PR #1's `.github/workflows/ci.yml`: on push and PR, run `schema.py validate` on all fixtures + the full test suite, on the agreed Python matrix — **`3.9 / 3.12 / 3.13`** (floor / mid / latest; 3.8 is dropped, EOL) — **not** PR #1's `3.10 / 3.11 / 3.12` (which omits the 3.9 macOS-system floor). Adapt `.github/workflows/release.yml`: on tag, run `build.sh` and attach `dist/praxa-*.zip` to the GitHub Release (`dist/` stays gitignored; the zip is a release asset, not a committed file).

### 6.3 — Gate

CI green on a fresh PR; release workflow dry-run produces the zip. CHANGELOG, `praxa_version` → `0.5.0`, tag `v0.5.0`, merge.

---

## 7. Open decisions

1. **Schema version label — RESOLVED:** `schema_version: "2.0"`.
2. **Supported Python floor — RESOLVED:** **`3.9+`** — 3.8 is dropped (EOL since 2024-10-07); 3.9 is both the documented and the practical floor (macOS CLT system Python). CI matrix `3.9 / 3.12 / 3.13`; not 3.10. Phase 1 bumps the `3.8+` strings in `PRAXA_SPEC.md` / `docs/installation.md` to `3.9+`. *(Supersedes the earlier "must include 3.8" thread — David's right: change the floor, don't test a dead interpreter.)*
3. **Layout** — keep `render.py` / `schema.py` / (new) `parallel.py` / `findings.schema.json` flat in `skills/behavior-verifier/` (where `main` has them, and what `build.sh` ships), or introduce a `skills/behavior-verifier/lib/` subdir (closer to PR #1's `lib/`)?
4. **Parallel-path packaging** — a thin `SKILL-PARALLEL.md` orchestration wrapper (recommended) vs. a "parallel mode" section inside `SKILL.md`. Either way, **non-negotiable: the analysis logic (calibration anchors, detection patterns, the secrets rule, the empty-file / declared-but-never-consulted detectors) lives in `SKILL.md` only** — the parallel path quotes it at prompt-build time, never restates it, or the two modes drift.
5. **The contested schema fields** — confirm or override the §4.1 table (especially: structured `evidence: [{file,line,snippet}]` ✔; keep per-category `confidence` / `weight` ✔; keep store-and-validate `severity_counts` / `weighted_overall` ✔; add `description` as optional ✔; ship `findings.schema.json` as a published contract with `schema.py` remaining the runtime validator ✔).
6. **Reducer workspace access** (Phase 2) — **recommended: targeted re-reads** — the reducer gets the workspace path and re-opens a handful of files to verify candidate compound chains (closes the cross-category-chain blind spot, keeps the speed win). Fallback: no re-read, with the sequential path as the higher-fidelity option — only if calibration-parity testing shows the targeted-read reducer over-claims.
7. **CI Python matrix — RESOLVED (folds into #2):** `3.9 / 3.12 / 3.13`.

---

## 8. Effort (rough)

| Phase | Effort |
|---|---|
| 0 — setup | ≈ ½ day |
| 1 — JSON structure | ≈ 2–3 days |
| 2 — parallel analysis | ≈ 2–3 days |
| 3 — CI + testing | ≈ 1–1.5 days |
| **Total** | **≈ 6–8 working days** of build + validate, plus review time per PR |

Phases are strictly ordered (Phase 2's reducer output depends on Phase 1's schema; Phase 3's fixtures depend on Phase 1's schema), so no cross-phase parallelization; within a phase the steps are mostly sequential.

---

## 9. Parked (revisit after Phase 3)

- **Look-and-feel reskin** — PR #1's "DEF/TAC OPS" dark/monospace theme (in PR #1's `lib/render.py` as a Python string literal). On revisit: decide brand (Exabeam navy/green vs. a redesign), and if a redesign wins, decide whether the new look lives in the editable `report_template.html` or is baked into the renderer like PR #1.
- **PDF output** — PR #1's `--pdf` flag via headless Chrome (with page-break and dark-print handling). On revisit: decide whether headless-Chrome-on-PATH is an acceptable runtime dependency (heavier than "Python 3 stdlib") or whether a lighter path (e.g. a print stylesheet the user prints themselves) suffices.
- **`description` field surfacing** — added to the schema in Phase 1; surfaced in the UI when the L&F work is un-deferred.

These are tracked in `design/DEFERRED.md` (added in Phase 0). PR #1's branch is retained so the code is recoverable.

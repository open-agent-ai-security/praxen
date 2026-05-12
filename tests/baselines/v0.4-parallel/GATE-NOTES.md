# Phase 2 gate — parallel map-reduce vs the sequential pipeline

`design/V2_HARVEST_PLAN.md` §5 proposed porting PR #1's parallel-analysis idea: six
RAISE-category *mapper* agents run concurrently, then a *reducer* agent does the
cross-category compound-signal reasoning and assembles the canonical findings JSON. The
hypothesis was ≈4–5× wall-clock on the analysis phase (the render is already deterministic
and ~0.08 s). §5.1 built the orchestrator (`skills/behavior-verifier/parallel.py` +
`SKILL-PARALLEL.md`, PR #5). §5.2 is the gate: run it on real targets, diff against
`tests/baselines/v0.3-sequential/`, time a controlled A/B, then make the §5.3 call
(ship-as-default / opt-in / drop).

This file is that gate's record. **Verdict: §5.3 outcome 3 — drop the parallel path.**

---

## Target 1 — HelperBot (small / CTF anchor), 2026-05-11

| metric | v0.3-sequential | v0.4-parallel | |
|---|---|---|---|
| weighted RAISE | 0.60 | **0.60** | exact parity ✓ |
| per-category | (sums to 0.60) | LYD 1 / BYKB 0 / IZT 0 / MYSC 1 / BART 1 / MC 1 | in band ✓ |
| Critical themes | sys-prompt API-key embed; no path validation; no input validation; false-history accept; no audit logging | all present (+ supply-chain / CORS / rate-limit broken out) | superset coverage ✓ |
| findings | 13 (5C/4H/3M/1I) | 24 (3C/8H/9M/3L/1I) | **count ~1.8×, severity skewed lower** ✗ |

Timing (map phase, 6 mappers parallel, single-target, repo pre-cloned, analysis only):
mapper durations 65 / 85 / 92 / 103 / 184 / 236 s → map wall-clock ≈ **236 s**; then reducer ≈ ~5 min; render ≈ 0.08 s ⇒ parallel total ≈ **~9 min** vs sequential ≈ **~4.5 min** (the latter incl. clone — but even discounting the clone, parallel is not faster).

The weighted score landed dead-on because it comes straight off the six mapper category scores, which were sound. But the **reducer under-consolidates** (kept 24 of 23 merged mapper findings — essentially no dedup, +1 compound) and **under-escalates** vs the holistic analyst (Critical→High drift). Category-isolated mappers each surface their own slice; folding them into the "one root cause = one finding" view the holistic pass produces is exactly what the reducer is for, and it isn't doing enough of it.

## Target 2 — Devika (worst-case-for-parallel big target) — the §5.2 controlled A/B, 2026-05-11

Repo pre-cloned, single-target (no contention), analysis + render only, sequential then parallel back to back.

| metric | v0.3-sequential (frozen) | sequential re-run (this A/B) | v0.4-parallel | |
|---|---|---|---|---|
| weighted RAISE | 0.45 | 0.45 | **0.85** | drifts **+0.40** — edge of band, wrong direction ✗ |
| per-category | LYD1/BYKB0/IZT0/MYSC1/BART0/MC1 | same | LYD1/BYKB**1**/IZT**1**/MYSC1/BART0/MC1 | mappers inflate BYKB & IZT 0→1 ✗ |
| findings | 17 (7C/6H/3M/1L) | 13 (7C/6H) | 29 (4C/11H/8M/4L/2I) | count ~2×; **Critical bar slipped 7→4** ✗ |
| Critical themes | empty sandbox stubs; raw `subprocess.run`; path-traversal write; no injection screening; unauth `/api/settings`; Netlify deploy | all present | most present but downgraded; **`/api/settings` and the arbitrary-file-read endpoints missing entirely** | **coverage hole** ✗ |
| **wall-clock** (analysis+render, pre-cloned, single-target) | — | **353 s (~5.9 min)** | map phase max(122,124,135,78,45,171) = 171 s + reducer ~5 min ⇒ **~8 min** | **parallel SLOWER** ✗ |
| token cost | ~136 K (one pass) | ~136 K | ~270 K mappers + a large reducer ≈ **~6×** | much more expensive ✗ |

### Why parallel is *slower*, even on the worst-case target

The **reducer is a serial bottleneck that costs about as much as the whole sequential analysis.** It ingests six detailed mapper reports and re-does the cross-category compound reasoning, severity calibration, dedup, and prose synthesis — that's most of a holistic pass — and it runs *after* the map phase, not during it. So `parallel ≈ map_phase(~3 min) + reduce(~5 min ≈ a full analysis) > sequential(~6 min)`. There is no architectural fix: the reduce step can't be cheap because the cross-category reasoning is the entire point of the design. PR #1's "≈4–5×" came from a one-target spot-check; it does not hold up.

### Why parallel is *less accurate*

1. **Score inflation.** Category-isolated mappers each find a *narrow-lens* mitigation — "commands go through an arg list not `shell=True`", "an undefined Jinja var means `search_results` don't reach the coder" — and bump a genuinely-Absent category to Ad hoc. The reducer adopts the mapper scores rather than re-applying the downward calibration anchor against the compound picture (it was *explicitly instructed* to, and didn't). HelperBot happened to land dead-on; Devika drifted +0.40.
2. **Structural coverage hole.** Findings that don't map to one RAISE category fall *between* the mappers. On Devika the parallel report is **missing** the unauthenticated `/api/settings` config-rewrite + API-key-leak (sequential: **Critical**; it's on Devika's must-catch list in `tests/README.md`) and the `/api/get-browser-snapshot` / `/api/download-project-pdf` arbitrary-file-read endpoints (sequential: **High**) — because nobody on the six-mapper roster owns "review the Flask/web API surface." That's not a tuning issue; splitting the analysis by RAISE category creates blind spots for cross-cutting issues by construction.
3. **Signal-to-noise.** Parallel's "extra" findings over sequential are one genuinely useful catch (`browser_interaction` scope creep) and a pile of Low/Info padding (`src/experts/` stubs, GitHub client, RAG stub, curl|bash toolchain, "ARCHITECTURE.md overstates auditing", an undefined-Jinja-var nit, `LOG_PROMPTS` default). Net negative.

---

## §5.3 decision — OUTCOME 3: DROP THE PARALLEL PATH

The parallel map-reduce path is **slower, less accurate, and ~6× more expensive** than the sequential pipeline — on the small target (HelperBot) and on the worst-case-for-parallel big target (Devika). It fails outcome 1 (no speedup — it's a slowdown) and it's worse than outcome 2 (calibration genuinely drifts and there's a structural coverage hole, not just "close but not there"). Per §5.3 outcome 3: **drop it, close the phase, reclaim the effort.** Phase 3 (GitHub Actions + automated testing) follows directly.

The §5.1 orchestrator build was sound engineering — the architecture just doesn't pay off, for reasons inherent to "split the analysis six ways then re-merge" rather than anything fixable in the prompts. `skills/behavior-verifier/parallel.py`, `skills/behavior-verifier/SKILL-PARALLEL.md`, and `tests/parallel/test_parallel.py` stay recoverable on branch `phase2/parallel-analysis` (PR #5, closed not merged) and are listed in `design/DEFERRED.md`. Nothing parallel ships in a release.

The report artifacts the A/B produced (`/tmp/praxa-helperbot-parallel/`, `/tmp/praxa-devika-par/`, `/tmp/praxa-devika-seq/`) are not committed; this dir + this file are the record.

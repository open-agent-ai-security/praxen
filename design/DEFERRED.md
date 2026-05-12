# Deferred / parked work

Things that were built or proposed and then deliberately *not* merged, with where to recover them. Keeping this list so the work isn't silently lost and so a future contributor doesn't re-derive a dead end.

---

## 1. Parallel map-reduce analysis path — DROPPED (Phase 2)

**What:** `skills/behavior-verifier/parallel.py` (prompt generator + result merger), `skills/behavior-verifier/SKILL-PARALLEL.md` (thin orchestration wrapper), `tests/parallel/test_parallel.py` (36-check harness). Six RAISE-category mapper agents in parallel → one reducer agent does compound-signal reasoning + assembles the canonical findings JSON. Hypothesis: ≈4–5× wall-clock on the analysis phase.

**Why dropped:** the §5.2 gate (HelperBot + a controlled Devika A/B) showed it is **slower, less accurate, and ~6× more expensive** than the sequential pipeline. The reducer is a serial bottleneck that costs about as much as a full holistic analysis and runs *after* the map phase, so there's no wall-clock win — and splitting the analysis by RAISE category creates structural blind spots for cross-cutting findings (e.g. it missed Devika's unauthenticated `/api/settings` Critical entirely). Full record: `tests/baselines/v0.4-parallel/GATE-NOTES.md`. `design/V2_HARVEST_PLAN.md` §5.3 outcome 3.

**Recover from:** branch `phase2/parallel-analysis` (PR #5 — closed, not merged). `git checkout phase2/parallel-analysis` brings back all three files. The orchestrator build itself was sound; it's the architecture that doesn't pay off — don't re-attempt without a fundamentally cheaper reduce step.

---

## 2. Look-and-feel reskin ("DEF/TAC OPS" theme) — DEFERRED (from PR #1)

**Where the code is:** PR #1's `lib/render.py` — the entire HTML structure and CSS live as Python string literals inside the renderer (`TAC_CSS` constant + the `render_*` functions that build HTML fragments via f-string concatenation).

**What it changes:** a wholesale visual redesign — dark monospace JetBrains Mono terminal aesthetic; severity colors retuned; layout simplified to a single 1100px column with section-label-and-rule blocks. Replaces the current Exabeam-brand `report_template.html` (navy + green-lt accents, sans-serif, Exabeam logo header) entirely.

**Why parked:** this is a **brand decision**, not a refactor side-effect. Whether the report keeps its Exabeam-brand visual identity or moves to the new look needs a deliberate call (and possibly design/marketing input) rather than landing as part of a pipeline reorg.

**To revisit:** after Phase 3. The decision is binary — brand or reskin — and either choice has implications: a reskin moves the HTML structure out of the editable `report_template.html` and into `render.py` as code, which is harder for a non-coder to tweak.

**Companion deferral:** the v2.0 schema (Phase 1) adds `findings[].description` as an optional longer-form field. The current renderer carries it through validation but doesn't surface it; the L&F revisit is the natural moment to expose it (the current finding card has a one-line `summary` slot, no room for a longer body).

## 3. PDF output (`--pdf` via headless Chrome) — DEFERRED (from PR #1)

**Where the code is:** PR #1's `lib/render.py` — `render_pdf()` function (~40 LOC) plus the `--pdf` CLI flag in `main()`. Drives headless Chrome (`google-chrome` / `Chromium` discovered on PATH) with `--print-to-pdf`, `--no-margins`, `--print-to-pdf-no-background=false`, `--force-color-profile=srgb`. CSS additions in PR #1's `TAC_CSS` to support clean print: `@page { margin: 0 }`, `print-color-adjust: exact !important` on the dark background, `break-inside: avoid` on `.card` / row elements.

**Why parked:** headless Chrome on the PATH is a notable runtime dependency — heavier than "Python 3 stdlib" (the current prerequisite). Whether that's acceptable is a real call; alternatives include a print-only stylesheet that the operator prints themselves (no extra dep, no auto-PDF), or `weasyprint` / similar (Python dep, more constrained CSS support). The page-break / dark-color-in-print logic from PR #1 is tightly coupled to the deferred L&F reskin (the dark theme), so detangling them is part of un-deferring.

**To revisit:** after Phase 3, ideally alongside the L&F decision (the print CSS layers on the active theme). If we keep the Exabeam-brand template, the print CSS needs porting to it.

---

## Recovering the parked code

**Parallel map-reduce path** (item 1): on its own branch — `git checkout phase2/parallel-analysis` (PR #5, closed not merged; the branch is intentionally retained).

**PR #1's parked pieces** (items 2 & 3): PR #1's branch (`feat/v2-deterministic-render-pipeline`) is intentionally retained when the PR is closed; you can also fetch its HEAD directly:

```bash
git fetch origin pull/1/head:pr1     # local ref to PR #1's HEAD
git show pr1:lib/render.py           # inspect or extract pieces
```

The relevant chunks to revisit:
- L&F: the `TAC_CSS` constant + every `render_<section>` function in `lib/render.py`.
- PDF: `render_pdf()` + the `--pdf` flag in `main()` + the print-related CSS rules in `TAC_CSS` (`@page`, `print-color-adjust`, `break-inside`).

When revived, both will be reconciled against whichever schema and renderer architecture is current at the time (the merged-schema v2.0 / `findings.schema.json` from Phase 1).

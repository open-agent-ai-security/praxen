# Deferred / parked work

Things that were built or proposed and then deliberately *not* merged, with where to recover them. Keeping this list so the work isn't silently lost and so a future contributor doesn't re-derive a dead end.

---

## Parallel map-reduce analysis path — DROPPED (Phase 2)

**What:** `skills/behavior-verifier/parallel.py` (prompt generator + result merger), `skills/behavior-verifier/SKILL-PARALLEL.md` (thin orchestration wrapper), `tests/parallel/test_parallel.py` (36-check harness). Six RAISE-category mapper agents in parallel → one reducer agent does compound-signal reasoning + assembles the canonical findings JSON. Hypothesis: ≈4–5× wall-clock on the analysis phase.

**Why dropped:** the §5.2 gate (HelperBot + a controlled Devika A/B) showed it is **slower, less accurate, and ~6× more expensive** than the sequential pipeline. The reducer is a serial bottleneck that costs about as much as a full holistic analysis and runs *after* the map phase, so there's no wall-clock win — and splitting the analysis by RAISE category creates structural blind spots for cross-cutting findings (e.g. it missed Devika's unauthenticated `/api/settings` Critical entirely). Full record: `tests/baselines/v0.4-parallel/GATE-NOTES.md`. §5.3 outcome 3.

**Recover from:** branch `phase2/parallel-analysis` (PR #5 — closed, not merged). `git checkout phase2/parallel-analysis` brings back all three files. The orchestrator build itself was sound; it's the architecture that doesn't pay off — don't re-attempt without a fundamentally cheaper reduce step.

---

## "DEF/TAC OPS" report look-and-feel reskin — DEFERRED (from PR #1)

**What:** an alternative report theme that lived in PR #1's `lib/render.py` as Python string literals (heavier "tactical operations" visual styling vs the current clean report). Not ported during the v2 harvest — the harvest kept the existing report template and the deterministic `render.py` pipeline.

**Recover from:** `git fetch origin pull/1/head:pr1` then `git show pr1:lib/render.py`. Would need re-expressing against the current `report_template.html` + `render.py` template engine (`{{SCALAR}}` / `REPEAT` / `PICK`), not copied wholesale.

## `--pdf` headless-Chrome report output — DEFERRED (from PR #1)

**What:** a `--pdf` option on the renderer that drove headless Chrome to print the HTML report to PDF. Not ported — adds a heavyweight external dependency (a browser) to a pipeline that is otherwise pure Python stdlib; the HTML report prints fine from a browser already.

**Recover from:** same as above — `git show pr1:lib/render.py` (the PDF path). Reconsider only if there's real demand for a no-browser PDF artifact, and prefer a lighter route than bundling Chrome.

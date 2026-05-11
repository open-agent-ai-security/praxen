# Deferred from the V2 harvest

Tracking the PR #1 pieces that the [V2 harvest plan](V2_HARVEST_PLAN.md) explicitly parked. Not discarded — recoverable from PR #1's branch (`feat/v2-deterministic-render-pipeline`) and re-evaluated when these items come back into scope.

## 1. Look-and-feel reskin ("DEF/TAC OPS" theme)

**Where the code is:** PR #1's `lib/render.py` — the entire HTML structure and CSS live as Python string literals inside the renderer (`TAC_CSS` constant + the `render_*` functions that build HTML fragments via f-string concatenation).

**What it changes:** a wholesale visual redesign — dark monospace JetBrains Mono terminal aesthetic; severity colors retuned; layout simplified to a single 1100px column with section-label-and-rule blocks. Replaces the current Exabeam-brand `report_template.html` (navy + green-lt accents, sans-serif, Exabeam logo header) entirely.

**Why parked:** this is a **brand decision**, not a refactor side-effect. Whether the report keeps its Exabeam-brand visual identity or moves to the new look needs a deliberate call (and possibly design/marketing input) rather than landing as part of a pipeline reorg.

**To revisit:** after Phase 3. The decision is binary — brand or reskin — and either choice has implications: a reskin moves the HTML structure out of the editable `report_template.html` and into `render.py` as code, which is harder for a non-coder to tweak.

**Companion deferral:** the v2.0 schema (Phase 1) adds `findings[].description` as an optional longer-form field. The current renderer carries it through validation but doesn't surface it; the L&F revisit is the natural moment to expose it (the current finding card has a one-line `summary` slot, no room for a longer body).

## 2. PDF output (`--pdf` via headless Chrome)

**Where the code is:** PR #1's `lib/render.py` — `render_pdf()` function (~40 LOC) plus the `--pdf` CLI flag in `main()`. Drives headless Chrome (`google-chrome` / `Chromium` discovered on PATH) with `--print-to-pdf`, `--no-margins`, `--print-to-pdf-no-background=false`, `--force-color-profile=srgb`. CSS additions in PR #1's `TAC_CSS` to support clean print: `@page { margin: 0 }`, `print-color-adjust: exact !important` on the dark background, `break-inside: avoid` on `.card` / row elements.

**Why parked:** headless Chrome on the PATH is a notable runtime dependency — heavier than "Python 3 stdlib" (the current prerequisite). Whether that's acceptable is a real call; alternatives include a print-only stylesheet that the operator prints themselves (no extra dep, no auto-PDF), or `weasyprint` / similar (Python dep, more constrained CSS support). The page-break / dark-color-in-print logic from PR #1 is tightly coupled to the deferred L&F reskin (the dark theme), so detangling them is part of un-deferring.

**To revisit:** after Phase 3, ideally alongside the L&F decision (the print CSS layers on the active theme). If we keep the Exabeam-brand template, the print CSS needs porting to it.

---

## Recovering the parked code

PR #1's branch is intentionally retained when the PR is closed (Phase 0 closes it with a pointer to [`V2_HARVEST_PLAN.md`](V2_HARVEST_PLAN.md); the branch lives on):

```bash
git fetch origin pull/1/head:pr1     # local ref to PR #1's HEAD
git show pr1:lib/render.py           # inspect or extract pieces
```

The relevant chunks to revisit:
- L&F: the `TAC_CSS` constant + every `render_<section>` function in `lib/render.py`.
- PDF: `render_pdf()` + the `--pdf` flag in `main()` + the print-related CSS rules in `TAC_CSS` (`@page`, `print-color-adjust`, `break-inside`).

When revived, both will be reconciled against whichever schema and renderer architecture is current at the time (probably the merged-schema v2.0 / `findings.schema.json` from Phase 1).

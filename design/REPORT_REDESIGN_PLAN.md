<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen Report Redesign — Working Plan

A visual overhaul of the Praxen HTML report, prompted by a graphic-designer mockup and an HTML cut (`~/Downloads/finbot-analysis-enterprise-lite.html`). We take the strong ideas, drop the hallucinations and the reordering, and keep everything portable.

**Branch:** `feat/report-redesign` — isolated and disposable. Merges to `dev` when a phase (or the set) is solid; gets nuked if it goes south.

**Scope:** reporting layer only — `skills/behavior-verifier/report_template.html` and `skills/behavior-verifier/render.py`. No schema, skill-methodology, or scoring changes.

---

## Non-negotiable constraints

1. **Stay HTML — no JavaScript, at all.** Pure HTML + inline CSS. Any interactivity must be native HTML (e.g. `<details>`/`<summary>`). No `<script>`, no chart libraries, no icon fonts, no web fonts, no external assets of any kind. One self-contained file that opens from `file://` and renders identically offline, in email, and on GitHub Pages.
2. **Deterministic render.** Everything is computed by `render.py` from the canonical findings JSON — same JSON in, byte-identical HTML out. Any chart, bar, or icon is **inline SVG/CSS** the renderer emits.
3. **No new data.** Pure presentation of fields we already produce. No new schema or skill fields (the mockup's per-finding "Impact" column was a hallucination — dropped).
4. **Keep the model and the order** — see *Locked decisions*.

## Locked decisions (agreed)

- **Keep the real six RAISE categories + weights** (Limit Your Domain · Balance Your Knowledge Base · Implement Zero Trust @ 25% · Manage Your Supply Chain · Build an AI Red Team · Monitor Continuously). Do **not** adopt the mockup's "R-A-I-S-E" 5-letter relabel.
- **Keep our section order.** RAISE Maturity Posture stays the **last** section (a wrap-up verdict, not a biasing headline). Remit Coverage before Findings. Keep the Discovered Log Files section. *(Rejecting the designer's reorder.)*
- **Never hide content by default.** Collapsible sections render **open** so the report is complete on load, prints in full, and degrades gracefully — collapse is a reader convenience, not a content gate.
- **Maturity label must match the computed floor** — no "Absent" header sitting over "Ad hoc" prose (a bug in the designer cut).

---

## Phase 1 — Masthead · jump-nav · Executive Summary  ← start here

The cheap, high-impact, fully JS-free wins.

### 1a. Masthead
- Navy band: **brand** (PRAXEN wordmark + tagline, optional inline-SVG hex mark) on the left of a top row.
- Left column: **`<Agent> Analysis Report`** title + **`Completed <date> · <time> UTC`**.
- Right column: a **severity-counts strip** (`N findings · NC · NH · NM · NL · NI`, each count colored by tier) and a **RAISE-maturity card** — label, `X.XX / 5.0`, and a progress bar (`width = score/5`).
- `render.py`: reuse existing `SEVERITY_SUMMARY`, `WEIGHTED_SCORE`; add a maturity-bar width value if needed. All values already in the JSON.
- **Done when:** header matches the mockup's spirit, every value is JSON-derived, no external assets, prints cleanly.

### 1b. Section jump-nav
- A toolbar of anchor chips under the masthead: **Summary · Findings · Remit · RAISE** (and others as sections settle), each a plain `<a href="#section-id">`.
- Sticky on scroll via CSS `position: sticky`. Hidden in `@media print`.
- **Done when:** chips jump to the right sections, zero JS, sticky works, print is unaffected.

### 1c. Executive Summary block
- One section titled **Executive Summary** containing three boxed cards: **Agent Remit (as declared)**, **Behavior Summary (as observed)**, **Scope of Analysis** — replacing the three separate stacked cards we ship today.
- Responsive grid that stacks on narrow widths.
- **Done when:** the three cards sit under one heading, content is unchanged from the JSON, layout reflows cleanly.

---

## Phase 2 — Collapsible findings (native `<details>`)

- Wrap each finding in `<details open>`; the `<summary>` is the finding header (severity badge · ID · one-line title), and the body (tags · policy rule · evidence · recommended action) is the revealed content.
- **Open by default** (per *Locked decisions*) — nothing hidden on load, full content prints/archives; the reader can collapse to scan.
- Zero JS — native element only. Style the disclosure marker to fit the card.
- **Done when:** every finding is independently collapsible, all open on load, prints fully, no script.

---

## Later / backlog (not yet scheduled)

Pulled from the mockup; queue after Phases 1–2 land.

- **Findings-by-severity donut** — inline SVG (`stroke-dasharray` arcs computed by `render.py`) + legend.
- **Compact RAISE alignment rows** — category badge + name + score + bar, for our **six** categories (no R/A/I/S/E single-letter badges, since six don't spell RAISE); decide whether to keep the per-category rationale.
- **Footer icon strip** — Analysis Date / Target / Analyzed By, inline-SVG icons, existing fields only.
- **Inline-SVG section icons** (doc, eye, etc.).
- **Optional top-findings summary table** — presentation-only, existing fields, anchors to the full register.

---

## Workflow

- All work on `feat/report-redesign`. Render the finbot example to `local/preview/finbot-analysis.html` and open it after each change.
- **Portability check each step:** grep the rendered file — it must contain no `<script>`, no `src=`/`href="http`, no `@import`, no font/CDN refs.
- Keep `render.py` deterministic; run `python3 tests/render/test_render.py`. Regenerate golden fixtures only when a phase is ready to merge (not per-tweak), same as the 0.7.2 discipline.
- Merge a phase to `dev` when it's solid (squash, Gemini + Steve gate); nuke the branch if the direction doesn't pan out.

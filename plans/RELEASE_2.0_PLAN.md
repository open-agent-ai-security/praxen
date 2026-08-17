<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen 2.0 — Threat Modeling

> **STATUS: DRAFT — decided 2026-08-17.** Steve: next release after the 1.3
> promotion is **2.0 = threat modeling**, a **pure feature release,
> scoring-neutral** — nothing in it moves a number, needs a freeze, or
> changes the findings schema. The former 1.4 detection/re-baseline plan is
> renumbered **2.1** (`RELEASE_2.1_PLAN.md`) and keeps everything
> score-moving, batched under its honest identity: *one release, one
> freeze*. Design contract: `DESIGN_THREAT_MODEL.md`. Evidence:
> `RESULTS_THREAT_MODEL_PROBE.md` (Phase-0 probe, 4 rounds, 18 extraction
> runs across 3 targets).

## Objective

Ship the first new product surface since 1.0: an **evidence-derived visual
threat model** — a data-flow diagram with trust boundaries, STRIDE×OWASP
threat enumeration, remit-rule overlay, and attack paths, where every node,
edge, boundary, and threat cites file:line evidence. Story: **"a threat
model with receipts"** — derived from the workspace, not drawn by a human
or prompted from a description.

Why it earns a major version: Praxen stops being only a findings report and
becomes findings + architecture view. Why it ships before the detection
release: it is score-inert and freeze-independent (cheap and fast to ship
by Praxen standards), it needs nothing from the detection batch (missed
detections surface honestly as `residual` threats — the probe turned three
of those into filed issues), and #198 wants threat-model boundary structure
as input, so the generator work is *better* after this ships.

## Contents (Phase 1 of the design doc, productized)

1. **Graph spec freeze.** Probe spec v0.4 → the v1 contract. Gate: the
   v0.4 confirmation pair (socxen ×2, in flight at drafting time) holds
   boundary agreement and moves same-file ID convergence and threat-status
   agreement the right way. One extraction = one graph (multi-run stays a
   diagnostic, per standing rule); union+adjudicate reserved as a possible
   future high-mode analog, not in 2.0.
2. **Extraction integration.** `THREAT_MODEL.md` instruction file in the
   skill (the THINKING_MODES.md pattern: orchestrator-addressed, one
   gate-scanned pointer in SKILL.md, standard scan path byte-identical).
   Runs from a completed scan's artifacts (findings JSON + source + remit)
   or as a scan add-on. Invocation UX = natural language, exact phrasing
   to be settled with a working prototype (open decision below).
3. **Graph validator** — the `schema.py` pattern applied to the graph JSON
   (the #217 lesson: a second large exact-format model-written artifact
   ships with a real validator from day one, not mental validation).
4. **Production renderer** — port `plans/threat-model-probe/render_probe.py`
   to a shipped `render_threatmodel.py`: deterministic lane layout,
   numbered boundary badges, hover/tooltip UX, barycenter ordering, port
   fan-out, corridor-bowed lane-skippers. Byte-stable render tests.
   **Visual-alignment requirement (Steve, 2026-08-17): the threat-model
   report must read as the same product as the analysis report** — same
   masthead lockup and navy/orange chrome, same `:root` palette and
   Lausanne/Arial stack, same section-title treatment, same footer
   (GitHub + sponsor + legal). Concretely: share the design tokens with
   `report_template.html` rather than copying them (single source — a
   shared CSS block or extraction, so a template restyle can't strand the
   threat model), keep the template's color discipline (orange is chrome
   only, never data; severity colors are semantic), and hover/interaction
   color is brand blue. The probe renderer's brand re-skin (2026-08-17)
   is the visual reference; the product port replaces its
   extract-at-render hack with a proper shared source.
5. **Semantic comparator** (test tooling, not user-facing): boundary/threat
   content matching for pair diffing and future baseline comparison —
   explicitly not raw-id or edge-topology matching.
6. **Artifacts:** `<slug>-threatmodel-<TIMESTAMP>.json` + self-contained
   `.html` sidecars under `./reports/`. **No change to the canonical
   findings JSON** — a `threat_model` block rides #118 later.
7. **Docs:** `docs/threat-modeling.md` + nav + llms.txt; PRAXEN_SPEC sync
   (load-bearing); README/marketplace feature copy.
8. **Riders (score-inert only):** #226 docs-consistency tail; #151
   (Antigravity harness) optional — a "reach" line if Steve wants it, not
   a dependency.

## Gates

- **Spec-freeze gate:** v0.4 socxen pair — boundary-set agreement stays
  ≥ 0.9 (was 1.00 at v0.3), same-file split ids converge, matched-threat
  status agreement moves toward ~90% (v0.3: ~80%; the mitigation-check
  sweep is the fix under test).
- **Stability gate (pre-ship):** independent pairs on 4 targets — finbot,
  uagents, socxen, **plus one cold target never used in spec development**
  (e.g. craftbot or hermes) — measured on the settled yardstick:
  boundary-set agreement ≥ 0.9, matched-threat status agreement ≥ ~90%,
  component fuzzy agreement ≥ 0.7. The cold target is the claims-ledger
  discipline applied here.
- **Quality gate:** 0 validator warnings on every gate run; ground-truth
  chains present per target; remit-overlay audit passes the
  job-description rule (only genuine governance attached; empty rule sets
  never remarked on).
- **No collateral damage:** standard-mode scan byte-identical; full test
  suite green; `claude plugin validate` clean; `v1.3-opus5` baselines
  untouched (byte-gates hold — nothing in 2.0 re-scans or re-scores).
- **Cost documentation:** extraction ≈ 0.4–0.5× a standard scan (probe
  measurement) — publish as budgeting guidance like the thinking-modes
  cost section, from measured runs.

## Open decisions (Steve, with prototype in hand — not blockers to start)

- Invocation UX: phrasing and whether threat-model runs standalone,
  post-scan, or both by default.
- #151 in or out of the release.
- Artifact naming / report cross-linking (analysis report ↔ threat model).

## Release mechanics

Branch `design/threat-model` (already pushed) → squash to `dev` after the
1.3 promotion settles → promotion PR (merge commit, FF `dev`) → tag
`v2.0.0` → post-tag sandboxed install smoke (must stamp exactly 2.0.0) +
fresh-agent scan check (standard scan unchanged) + one threat-model
end-to-end on a public target → blog: *"Praxen 2.0 — now with threat
modeling: a threat model with receipts."* Bump discipline as usual:
`bump_version.py --dry-run` first; remits are the seventh version surface
(re-render after bump); PRAXEN_SPEC version read by release.yml.

## Non-goals

No score movement, no freeze, no re-baseline, no findings-schema change,
no report-template change to the analysis report, no mermaid/JS deps, no
MAESTRO lens, no ATT&CK/ATLAS export, no #198 (2.1's opener), no
multi-run graph aggregation as a user-facing deliverable. 2.1 is the
detection/calibration release and grades `v2.1-opus5` vs `v1.3-opus5`.

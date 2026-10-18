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
detections surface honestly as `potential` threats — the probe turned three
of those into filed issues), and #198 wants threat-model boundary structure
as input, so the generator work is *better* after this ships.

## Contents (Phase 1 of the design doc, productized)

1. **Graph spec freeze.** Probe spec v0.4.2 → the v1 contract. Threat
   status set settled with Steve (2026-08-17) after two vocabulary
   collisions: **confirmed / potential / partial / mitigated** — `confirmed` = a
   scan finding proves it (ID cited); `potential` = an unanswered
   hypothesis (no finding covers it, no control answers it, the
   mitigation sweep looked); `partial` = a control covers part of the threat (citation + stated
   remainder required; matches the remit-coverage term — Praxen targets
   are full of partial mitigation); `mitigated` = control covers the
   whole threat, cited. Rejected:
   `residual` (ISO/NIST post-control meaning), `open` (tracker meaning =
   filed-and-unaddressed, which is our `confirmed`). Gate: the
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
   **Static-completeness requirement (Steve, 2026-08-17): the report must
   read complete on paper — interactivity is an enhancement layer, never
   the only carrier of information.** Concretely: printed legend (6
   component families + kind icon key + mark key), static boundary key
   table resolving every B-badge, kind ICONS on nodes carrying meaning
   alongside (reduced, 6-family) color, the primary attack path told by
   numbered step badges (connective route ink was tried twice and rejected
   — it sprays across the canvas; badges alone read cleanly), a
   component-inventory
   appendix carrying every node's evidence citations, and print CSS
   (labels shown, tooltip hidden, diagram scaled). Hover behaviors
   (highlighting, fan labels, tooltips) stay — as additive polish.
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
- **No collateral damage:** ~~standard-mode scan byte-identical~~ —
  **superseded 2026-10-18.** The gate as written no longer holds and should
  not be read as if it does. Standard-mode output changed twice, both
  deliberately, and neither moves a score:
  - *Exception 1 (Steve, 2026-08-26):* new scans emit the optional
    `scan.remit_version` provenance field when the remit declares a version;
    absent on version-less remits.
  - *Exception 2 (Steve, 2026-10-18):* the findings schema moves **3.0 ->
    4.0** and every scan now emits the required `standards` block naming the
    OWASP editions it was scored against. See *Schema 4.0* below.

  What still holds: **no score moves** — no re-scan, no re-score, no
  re-freeze, and `weighted_overall` and every severity count are byte-stable
  across the release. What changed and the gate used to deny: the
  `v1.3-opus5` baselines are **not** untouched. Both current-schema findings
  sets (`v1.3-opus5`, `v1.2-opus5`), the three showcase examples and the
  twelve baseline threat models were **re-stamped and re-rendered** from
  unchanged scan data, because a required field and a schema major cannot be
  added without them. Full suite green and `claude plugin validate` clean
  remain requirements.
  **Rider (#266, 2026-10-09; superseded 2026-10-18).** That exception was
  reasoned about the runtime validator only — the published
  `findings.schema.json` was never updated, and because `scan` is
  `additionalProperties: false` there, any findings JSON from a remit that
  declares a version passed `schema.py` and was **rejected by every
  draft-07 consumer**. Fixed by declaring `scan.remit_version` as an
  optional non-empty string, plus a converter-table ↔ published-schema
  field-inventory cross-check in `test_render.py` §4e-bis (§4e compared
  only enums, which is why nothing caught it; §4e-bis was itself later
  hardened to compare types and required-ness after it was shown to pass
  while a wrong-typed declaration was present).
  **What this rider originally concluded is now wrong and is struck:** it
  argued `schema_version` should deliberately stay `3.0`, that a bump would
  force a re-stamp of frozen byte-gated artifacts, and that the
  schema-version signal should be deferred to 2.1. 2.0 instead ships
  **schema 4.0** (Steve, 2026-10-18) — adding a required field is a schema
  MAJOR under `STABILITY.md`, and a product MAJOR is the right place to
  spend one. All 24 current-schema baseline sets were re-stamped and
  re-rendered, which the gate above now records. The residual the rider
  worried about — one version string denoting two shapes — does not arise:
  4.0 denotes exactly one.
- **Cost documentation:** extraction ≈ **0.5–1×** a standard scan,
  typically ~0.75× — published as budgeting guidance like the
  thinking-modes cost section, from measured runs. (This gate was drafted
  at "≈ 0.4–0.5×" from the Phase-0 probe; the figure that shipped in
  `docs/threat-modeling.md` and `PRAXEN_SPEC.md` is the later measured one.
  Corrected here 2026-10-18 so the plan and the product agree.)

## Open decisions — RESOLVED (Steve, 2026-08-22)

- Invocation UX: Steve selected **"Ship as built"** — post-analysis
  default, combined invocation supported, standalone allowed with the
  confirmed-statuses warning.
- #151: out — parked indefinitely by Steve, 2026-08-18.
- Cross-linking: Steve selected **"Link one way"** — the threat-model
  masthead's "built against" reference links to the analysis HTML
  (renderer `--analysis-html`, opt-in); the reverse link is out for 2.0
  (non-goal: no analysis-template change).
- #261 (asked alongside): Steve selected **"Fold into 2.0"** — the
  x-high checkpoint-path fix and both THINKING_MODES nits ride this
  release; no 1.3.1.

## Schema 4.0 — OWASP edition provenance (added 2026-10-18)

Not in the original plan; added when review found that neither report said
which **edition** of each OWASP list its codes came from. The codes are not
stable across editions — `LLM03` is *Supply Chain* in the 2025 LLM Top 10
and *Excessive Agency* in 2026, and `LLM04`/`LLM10` also changed meaning —
so an archived report was ambiguous, and the only disambiguator was a
heuristic inside `render.py` that reconstructed the edition from
`praxen_version`. Nothing recorded it; the agentic edition was a hardcoded
template literal and the MCP edition appeared nowhere at all.

- **Findings JSON:** required `standards` block (`owasp_llm`,
  `owasp_agentic`, `owasp_mcp`), injected by `manifest_to_findings.py` from
  the new `schema.STANDARDS` — never authored. Shape-checked, not
  value-pinned, so a document recording an older edition stays valid.
- **Threat-model graph:** same block, folded into the unreleased contract
  **v1.5**. Shape-checked, not value-pinned — the same as the findings
  side. Pinning was tried first and reversed: it would have meant a graph
  could never record an older edition, and that the day the knowledge bases
  move, every already-valid graph at an unchanged `spec_version` becomes
  invalid — the "one version, two shapes" defect this contract bump exists
  to avoid. Staleness in the committed set is caught by the test suite
  instead.
- **Schema 3.0 -> 4.0, not 3.1.** `STABILITY.md` makes adding a required
  field a schema MAJOR, and 2.0 is a product MAJOR — the right release to
  spend one in. The interim 3.1 was never merged and is not part of the
  history. This removed a policy carve-out rather than adding one.
- **Reports** state the editions in the findings HTML footer, both coverage
  headings, the TXT `Built on` line, and the threat-model masthead and
  footer.

Done before GA because the field is required: adding it after 2.0 ships
would be a second breaking schema change for no reason.

## Release mechanics

Branch `v2` (already pushed; formerly `design/threat-model`) → squash to `dev` after the
1.3 promotion settles → promotion PR (merge commit, FF `dev`) → tag
`v2.0.0` → post-tag sandboxed install smoke (must stamp exactly 2.0.0) +
fresh-agent scan check (standard scan unchanged) + one threat-model
end-to-end on a public target → blog: *"Praxen 2.0 — now with threat
modeling: a threat model with receipts."* Bump discipline as usual:
`bump_version.py --dry-run` first; remits are the seventh version surface
(re-render after bump); PRAXEN_SPEC version read by release.yml.

## Beta channel runbook (2026-08-28; Steve: beta = dry run of the GA vendored-install route)

The 2.0 beta installs from the community catalog as a payload **vendored
into the plugins repo** (`"source": "./praxen-beta"`, ~1 MB) rather than a
whole-repo clone (plugins repo PRs #9 validator + #7 entry). Beta installs
under its own plugin key `praxen-beta@open-agent-ai-security`, side by side
with production. Packaging is scripted, not by hand:

- `scripts/release/dist_manifest.txt` — single source of truth for
  distribution contents; read by `build.sh` (zip, all entries) and by
  `scripts/release/stage_plugin_payload.sh` (payload, minus `zip-only`
  entries and the legacy in-repo marketplace mirror).
- CI enforces the stager (`tests/render/test_stage_plugin_payload.py`):
  allowlist entries exist, payload shape/runtime refs hold, no symlinks,
  `--check` drift detection works.

**Beta cut N:** merge `v2` → `v2-beta` → `bump_version.py 2.0.0-beta.N` →
`docs_build.py` → commit/push `v2-beta` →
`scripts/release/stage_plugin_payload.sh --force <plugins-clone>/praxen-beta`
→ PR in the plugins repo (verify with `--check` after) → re-sync any
changed pages into praxen `main`'s `beta/` dir via PR.

**At GA:** the flip for production is the same move with the `praxen`
entry — vendor the payload as `plugins/praxen/`, switch its source to
`"./praxen"`; same key, same install commands. Then delete the beta entry
+ `praxen-beta/` payload dir, the `beta/` Pages dir, and archive the
orphaned praxen-beta mirror repo (superseded scaffolding from the
first beta design; deletion is Steve's call).

## Non-goals

No score movement, no freeze, no re-baseline, no mermaid/JS deps, no
MAESTRO lens, no ATT&CK/ATLAS export, no #198 (2.1's opener), no
multi-run graph aggregation as a user-facing deliverable. 2.1 is the
detection/calibration release and grades `v2.1-opus5` vs `v1.3-opus5`.

**Two non-goals were spent deliberately** (2026-10-18). This list read "no
findings-schema change, no report-template change to the analysis report";
both are now false, and the entries are struck rather than quietly dropped:

- ~~no findings-schema change~~ — the findings schema moves **3.0 -> 4.0**
  for the required `standards` block (see *Schema 4.0* above). A required
  field cannot wait for 2.1 without making that a second breaking change.
- ~~no report-template change to the analysis report~~ —
  `report_template.html` gains the footer line naming the editions and one
  CSS rule for it (+5/-2), and the agentic coverage heading's hardcoded
  `(2026)` becomes a placeholder. Nothing else in the analysis report moved.

Both are presentation and provenance only: **no score moves**, and the
release stays freeze-independent.

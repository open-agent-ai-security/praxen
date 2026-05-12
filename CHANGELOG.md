<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Changelog

All notable changes to Praxa will be recorded here. Format roughly follows [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

---

## [0.6.0] — 2026-05-12

**Relicensed to Apache-2.0.** Praxa moves from the Exabeam commercial / by-permission license to the [Apache License, Version 2.0](LICENSE) — it's now open source. No functional changes to the skill, detection logic, RAISE scoring, Worker Remit structure, or the findings schema (still `"2.0"`); this is a licensing / metadata release. (`praxa_version` bumps `0.5.0` → `0.6.0`.)

### Changed
- `LICENSE` — replaced the proprietary "Commercial License — Use by Permission" text with the verbatim Apache License 2.0.
- Source-file headers — every file's `Copyright © 2026 Exabeam, Inc. All Rights Reserved. / Confidential and Proprietary…` block replaced with the SPDX short form (`Copyright 2026 Exabeam, Inc.` / `SPDX-License-Identifier: Apache-2.0`).
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — `license` now `"Apache-2.0"` (was `"SEE LICENSE IN LICENSE"`); version `0.6.0`.
- `report_template.html` / `render.py` — generated reports no longer carry an Exabeam copyright header; the template's license header is now stripped from rendered output (a report is about the analyzed agent, not a work of Exabeam's), and the document starts cleanly at `<!DOCTYPE html>`. The visible report footer keeps the Praxa attribution and the project-sponsor link, and now also shows the repo URL and `Apache-2.0` (HTML and TXT). Golden fixtures regenerated; `test_render.py` updated accordingly.
- `README.md` — added a `## License` section. Version strings bumped to `0.6.0` in `README.md`, `PRAXA_SPEC.md`, `docs/installation.md` (and the `praxa_version` example in `SKILL.md`).

### Added
- `NOTICE` — Apache-2.0 attribution file; records the project sponsor and the OWASP Gen AI material in `skills/behavior-verifier/knowledge/` used under CC BY-SA 4.0.
- `CONTRIBUTING.md` — contribution guide; uses the Developer Certificate of Origin (DCO) — commits must be `Signed-off-by`.
- `.github/workflows/dco.yml` — CI check that fails a pull request if any non-merge commit lacks a `Signed-off-by` trailer matching the author or committer.
- `build.sh` now includes `LICENSE`, `NOTICE`, `CHANGELOG.md`, and `CONTRIBUTING.md` in the distribution zip.

## [0.5.0] — 2026-05-11

**Phase 3 of the V2 harvest: GitHub Actions CI + release automation, golden-file render fixtures.** No changes to the skill, the detection logic, the RAISE scoring, the Worker Remit structure, the findings schema (still `"2.0"`), or the report — this is a tooling / repo-infrastructure release. (There is no 0.4.0: Phase 2's parallel map-reduce analysis path was prototyped and gated, found slower / less accurate / ~6× more expensive than the sequential pipeline, and dropped — see [`tests/baselines/v0.4-parallel/GATE-NOTES.md`](tests/baselines/v0.4-parallel/GATE-NOTES.md) and [`design/DEFERRED.md`](design/DEFERRED.md).)

### Added
- `.github/workflows/ci.yml` — runs `tests/render/test_render.py` and `build.sh` on every push and pull request, across Python **3.9 / 3.12 / 3.13** (3.9 is the floor — the macOS Command Line Tools system Python).
- `.github/workflows/release.yml` — on a `v*` tag: checks the tag matches `PRAXA_SPEC.md`'s version, runs the test suite, builds `dist/praxa-<version>.zip`, and creates the GitHub release.
- `tests/fixtures/finbot.golden.html` / `finbot.golden.txt` — committed golden render output for the canonical fixture; `test_render.py` now byte-compares the renderer's output against them (regression net for `render.py` + `report_template.html` + the derived-value tables together). Header comments in the test say how to regenerate them when output changes intentionally.

## [0.3.0] — 2026-05-11

**Phase 1 of the V2 harvest: merged findings schema (`schema_version: "2.0"`).**

First implementation phase of [`design/V2_HARVEST_PLAN.md`](design/V2_HARVEST_PLAN.md) — adopts the better-structured findings model from PR #1 onto the v0.2.0 pipeline, while keeping the parts of the v0.2.0 schema PR #1 dropped. Substance of detection / RAISE scoring / Worker Remit structure / the report's section order is unchanged; this is a JSON-shape release.

### Added

- **`skills/behavior-verifier/findings.schema.json`** — the machine-readable JSON-Schema contract (draft-07) for the canonical findings JSON. `schema.py` stays the runtime validator (stdlib only, no `jsonschema` dep); a test asserts the schema file's enums and the validator's Python constants agree.
- **Optional `description` field on findings** — a short paragraph of longer-form context for downstream consumers. Carried in the JSON; the report card still shows only `summary` (the L&F revisit in `design/DEFERRED.md` will surface description).
- `design/DEFERRED.md` — tracking note for the parts of PR #1 explicitly parked (the "DEF/TAC OPS" look-and-feel reskin and the `--pdf` headless-Chrome output).

### Changed (BREAKING — see migration note below)

- **`findings[].evidence` is now structured: `[{ file, line, snippet }]`** (was `[string]`). The renderer formats each item as `file:line — snippet` (or `file — snippet` when `line` is `null`).
- **`findings[].recommended_action` (single string) → `recommended_actions` (array of strings).** Single-item arrays render as inline text; multi-item arrays render as a bulleted list.
- `schema_version` bumped `"1.0"` → `"2.0"`. The renderer reads `2.x` and rejects everything else (the v1.0 schema is now legacy; v1 JSONs do not render).
- **Python floor: 3.8 dropped, 3.9 is now the documented and practical floor.** 3.8 has been EOL since 2024-10-07; we don't test or claim support for a dead interpreter. 3.9 is the macOS Command Line Tools system Python (Ventura / Sonoma / Sequoia). `PRAXA_SPEC.md` §2.6 / §8 and `docs/installation.md` updated.

### Migration

A v0.2.0 (`schema_version: "1.0"`) findings JSON does not load in v0.3.0. For each finding:

1. Replace `"evidence": ["file:line — snippet", ...]` with `"evidence": [{ "file": "...", "line": <int or null>, "snippet": "..." }, ...]`.
2. Replace `"recommended_action": "..."` with `"recommended_actions": ["..."]`.
3. Bump `"schema_version"` to `"2.0"` and `"praxa_version"` to `"0.3.0"`.
4. Optionally add a `"description"` field (omit if you have nothing beyond `summary`).

### Updated

- `PRAXA_SPEC.md` §6 (Canonical Findings JSON) reflects the v2.0 shape; `docs/interpreting-reports.md` updated; `SKILL.md` Step 10 produces v2.0 directly.
- Test fixture (`tests/fixtures/finbot.canonical.json`) migrated to v2.0; `tests/render/test_render.py` adds checks for structured-evidence rendering, multi-action lists, and schema-file ↔ validator enum agreement. 28/28 green.

### Unchanged

- All detection patterns, named detectors, the "Calibration anchors" RAISE-scoring discipline, the Worker Remit structure, the report's section order and styling, the existing Exabeam-brand `report_template.html`, the `render.py` core engine (template substitution, PICK/REPEAT, brace neutralisation, comment stripping).

---

## [0.2.0] — 2026-05-11

**Render-pipeline refactor: the report is now generated by code, not by the LLM.**

The skill used to produce all three output files itself, including hand-substituting ~30 placeholders and several repeat blocks into the 800-line HTML template — slow (8–12 min/render), unreliable (mid-render stalls), and a poor use of LLM tokens. It now emits a single **canonical findings JSON** and a bundled deterministic Python renderer turns that JSON into the HTML report and the `.txt` summary. Same JSON in, byte-identical output, every time. Findings counts, severity rules, RAISE scoring model, OWASP mappings, and Worker-Remit structure are unchanged in substance; the RAISE *scoring discipline* was refined (see below).

### Added

- `skills/behavior-verifier/render.py` — deterministic report renderer (template engine, derived-value tables for CSS classes / score % / maturity label / overall-status badge, allow-tag sanitiser, plain-text formatter). Python 3.8+, standard library only. CLI: `--findings --template --out-html --out-txt`. Guarantees zero unresolved markers and refuses to run on a JSON that fails validation.
- `skills/behavior-verifier/schema.py` — validator for the canonical JSON (shape, types, enumerations, and cross-field invariants: severity/remit counts match the arrays, anchors resolve, the six RAISE keys are present, `weighted_overall` = Σ(score × weight)).
- `tests/fixtures/finbot.canonical.json` + `tests/render/test_render.py` — a realistic fixture and a no-dependency smoke harness (24 checks).
- **Python 3** is now a runtime prerequisite (besides Claude Code) — stdlib only, nothing to install.

### Changed

- **Findings JSON schema → v1.0** (`schema_version: "1.0"`). Now a single top-level object (not a bare list), carrying *every* prose field the report shows — `intro_band` summaries, `behavior_summary`, the six `raise_posture.categories` rationales, `remit_coverage.rules`, `positives`, `log_files` — so JSON-only consumers get the same content humans see. The pre-0.2 bare-list format (with a trailing `-POSTURE` summary entry) is **no longer read** by the renderer; tooling built against it needs updating. Schema documented in `PRAXA_SPEC.md` §6.
- `SKILL.md` Steps 9–12 rewritten: Step 9 synthesises all report prose up front; Step 10 writes the one canonical JSON; Step 11 runs `render.py`; Step 12 prints the renderer's `.txt`. The ~90 lines of template-substitution rules are gone (they live in `render.py` now).
- **RAISE scoring discipline tightened then rebalanced** ("Calibration anchors", Step 5/9.4): score what the agent *enforces at runtime*, not what's *present in the repo* — a control off-by-default / bypassable / living in a framework the agent never invokes earns the category nothing; but a control *operative on the agent's path* — even a human-in-the-loop confirmation, even an inherited framework default — earns it *Partial* (2) or *Established* (3) even with gap findings. CTF/training targets sit at *Absent*/*Ad hoc*; a mature maintained agent isn't a hobby project just because gaps were found.
- `report_template.html` — doc-block updated; orphan `<!-- PICK:overall_status -->` comment (no `END`) removed; remit-row Finding cell → a single `{{FINDING_LINK}}` the renderer fills with an anchor or an em dash.
- `examples/finbot` + `examples/helperbot` regenerated on the new pipeline (their findings JSONs are now the v1.0 schema). `tests/README.md` rebaselined — baselines are ranges, not point values (blind-run scoring varies ±0.3–0.5), with a "v0.2 calibration posture" section and a Sweep scope-sensitivity note.
- Report renderer neutralises literal `{{...}}` in cited content, so a finding quoting Jinja/Mustache/k8s/Compose template code can't collide with a Praxa placeholder. The plain-text summary no longer runs paragraphs together at `</p><p>` boundaries; `<strong>`/`<em>` join `<code>` (and `<p>`) in the rich-text allow-list.

### Unchanged (explicitly preserved)

- All detection patterns and named detectors; severity rules; RAISE 0–5 model and weighting (Zero Trust 25%, others 15%).
- OWASP LLM Top 10 / OWASP Agentic Top 10 / OWASP MCP Guide cross-references.
- Worker Remit structure and required sections; the report's section order and styling.
- Knowledge base content (`knowledge/KB_*.md`).
- License text (commercial / by-permission; open-source flip still deferred).

---

## [0.1.0] — 2026-05-01

**First internal Praxa release.**

This release is the rebranding of the project formerly known as the Exabeam Deckard Agent Security Scanner to **Praxa — agent behavior verifier**. No detection logic, severity rules, RAISE scoring, OWASP mappings, or evaluation behavior changed in this release. The change is naming, terminology, and documentation only.

### Renamed
- Project name: *Exabeam Deckard Agent Security Scanner* → **Praxa**
- Descriptor: *agent behavior verifier*
- Tagline: *Make sure your agent does its job — and only its job.*
- Skill directory: `skills/environment-scanner/` → `skills/behavior-verifier/`
- Skill identifier: `environment-scanner` → `behavior-verifier`
- Plugin name: `deckard` → `praxa` (in `.claude-plugin/plugin.json` + `marketplace.json`)
- Specification document: `DECKARD_SPEC.md` → `PRAXA_SPEC.md`
- Report output filenames: `<agent>-scan-<timestamp>.{html,txt}` → `<agent>-analysis-<timestamp>.{html,txt}` (the JSON keeps `<agent>-findings-<date>.json`)
- Distribution zip: `deckard-X.Y.Z.zip` → `praxa-X.Y.Z.zip`

### Terminology
- *scan* → *analysis* / *verification* (in user-facing labels)
- *scanner* → *verifier* (in user-facing labels)
- *Scan Summary* → *Behavior Summary* (report section title)
- *Scan Report* → *Analysis Report* (report header)
- *security issue* → *finding* (where it appeared in user-facing copy)

### Repositioned
- Headline framing: "policy compliance scanner for AI agents" → "agent behavior verifier — verifies intended vs observed behavior, ensures agents stay within defined boundaries"
- OWASP coverage list moved lower in the README; Praxa identity (name, descriptor, tagline, Worker Remit explanation, behavior-vs-intent) leads.
- Security framing preserved throughout — security references repositioned, not removed.

### Unchanged (explicitly preserved)
- All detection patterns and named detectors
- Severity rules and finding schema
- RAISE 0–5 scoring model and weighting
- OWASP LLM Top 10, OWASP Agentic Top 10, OWASP MCP Guide cross-references
- Worker Remit structure and required sections
- Report template structure (RAISE Maturity Posture, Findings Register, Remit Coverage, etc.)
- Knowledge base content (`knowledge/KB_*.md` — attribution-line wording updated; methodology untouched)
- License text (commercial / by-permission; open-source flip deferred to a later release)

### Deferred to a later release
- License conversion to an open-source license (Apache-2.0 likely target)
- "Praxa is open source / Hosted under Exabeam Labs / Project sponsor: Exabeam" positioning language in the README
- GitHub repository rename (`Exabeam/deckard` stays; will be moved separately by an admin)

---

## Pre-Praxa history (legacy: Deckard releases)

For reference. Detail kept short — these were internal releases under the prior name.

### [0.7.0] — 2026-04-24 *(Deckard)*
- Restructured as a Claude Code plugin marketplace (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`)
- Skill moved to `skills/environment-scanner/SKILL.md` with proper frontmatter

### [0.6.6] — 2026-04-24 *(Deckard)*
- Step 4b — Secondary Prompt Discovery for session-loaded files (`SOUL.md`, `AGENTS.md`, `MEMORY.md`, etc.)
- KB additions: Session Bootstrap Files / Agent Memory Files; writable-session-loaded-file compound chain

### [0.6.5] — 2026-04-23 *(Deckard)*
- Three input shapes documented (source / deployment / behavioral); behavior-only scanning validated against the Zoidberg target
- `RAISE Maturity Posture` moved to end of report; rubric table baked in; neutralized blue palette
- Scan Summary section added (renamed Behavior Summary in 0.1.0)
- Empty-file signal detector + Declared-but-Never-Consulted-Config detector
- "Never Reprint Secrets" rule

### [0.6.4] and earlier *(Deckard)*
- Initial scanner-only MVP, separating from the deferred runtime-watcher concept
- Canonical HTML report template; standardized product naming
- Examples directory (FinBot, HelperBot)

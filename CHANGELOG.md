<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Changelog

All notable changes to Praxen will be recorded here. Format roughly follows [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/). Entries for versions prior to `0.7.0` describe the project under its former name, **Praxa**, and at its former home, `github.com/Exabeam/deckard`. Issue references in those entries link back to `Exabeam/deckard` because that is where the issues themselves live — the `0.7.0` rename was a fresh-repo cutover, not a transfer.

---

## [0.7.8] — 2026-05-31

**Opus 4.8 reference re-baseline, a twelfth (multi-component) baseline target, a docs-first remit generator, and `dev`/`main` drift guards.** The **scan engine is unchanged** — `schema.py`, `render.py`, `manifest_to_findings.py`, and the four knowledge bases are byte-identical to `0.7.7`, and `schema_version` stays `"2.0"`. The one `SKILL.md` change is confined to the **Pre-flight remit-authoring** guidance (how the skill *drafts* a remit on request) and is scan-orthogonal: it does not change the 12-step analysis procedure, the committed baselines, or any scan's output.

### Added
- **`tests/baselines/v0.7.7-claude48/`** — the new canonical baseline: all twelve targets on the unchanged v0.7.7 skill under **Anthropic Claude Opus 4.8**, frozen via a **median-of-3** process (each target characterized over three independent runs; the committed exemplar is the median run). Replaces `v0.7.7-sequential/` (the same skill on Opus 4.7) as the comparison point for the release review. See `tests/baselines/v0.7.7-claude48/BASELINE.md` for the per-target table, 3-run stability stats, the model-lean analysis (+0.22 mean weighted, inverted-U by maturity), and the five band changes.
- **`tests/baselines/v0.7.7-claude48/hermes-agent-desktop/` + `tests/remits/hermes-agent-desktop.md`** — **twelfth baseline target** (RFE [#46](https://github.com/open-agent-ai-security/praxen/issues/46)): **Hermes Agent + Hermes Desktop**, the suite's first **multi-component** target (one combined remit spanning an in-process LLM agent and its operator/desktop layer) and its first real-world agent shipping a disclosed `SECURITY.md`. Characterized median-of-3 on Opus 4.8 → weighted **3.15 (Established)**, band **2.6–3.4** (second-widest σ in the suite — the Critical↔High call on the disclosed default-isolation seam). Added *after* the 4.7→4.8 re-baseline, so it has no 4.7 predecessor. `tests/README.md` gains target **#12**; `owasp_coverage.py` `TARGETS` and the OWASP coverage report now cover twelve targets.
- **`tests/README.md` — "Re-baselining (multi-run characterization)"** — documents the multi-run freeze process: characterize over three runs, freeze the median, set bands from the mean ± observed spread, distinguish *stable-but-offset* (move the band) from *noisy-but-centred* (widen the band), and diff by theme/rule-text not by run-local `R-NN` ids.
- **`docs/understanding-variability.md`** — operator-facing page on run-to-run variability: why the LLM synthesis stage varies while rendering is deterministic, how much to expect, following up with the LLM to re-analyze, and running multiple times when stability matters more than runtime. Linked from the docs index, Interpreting Reports, and Challenging Findings.
- **`.github/workflows/branch-drift.yml` + `CONTRIBUTING.md` "Keeping `dev` in sync with `main`"** — a version-aware CI check that fails a PR if `dev`'s `plugin.json` version falls *behind* `main`'s, plus the documented realign procedure. Closes the drift that left `dev` two releases stale through 0.7.7.

### Changed
- **Per-target bands (`tests/README.md`)** — five bands updated to fit the 4.8 means: `aider` 1.1–1.8 → **1.8–2.4** (stable offset), `langchain-sql` 0.7–1.4 → **0.9–1.6**, `sweep` 0.7–1.3 → **0.9–1.4**, `openai-customer-service` 0.6–1.3 → **0.7–1.7** (widened for variance, not moved — highest-σ target), `openhands` 1.8–2.5 → **1.7–2.5**. The other six targets' means sit inside their existing bands, unchanged.
- **`tests/baselines/owasp-coverage-report.html` + `owasp_coverage.py` default** — regenerated and re-pointed at the new baseline set.
- **`tests/baselines/v0.7.7-sequential/` retired**, kept on disk for diff archaeology (4.7 reference). README pointers updated.
- **`SKILL.md` Pre-flight — docs-first, intent-not-description remit authoring.** When asked to draft a Worker Remit, the skill now authors from the agent's **documentation as declared intent**, reading source code only when the docs are *spectacularly* unavailable. It states the conservative security intent rather than mirroring the implementation, carries **no per-clause `[Inferred]` tags** (every clause is a stated obligation), and routes genuinely un-derivable operator decisions to an **"Open Questions for the operator"** section written below the remit footer. Scan-orthogonal — the authoring path only; the 12-step analysis procedure and committed baselines are untouched.
- **`README.md` tightened** (trimmed reference-density, added the concrete one-sentence invocation) and the **live OWASP Coverage Report surfaced** — linked from the README, the docs OWASP / index / interpreting-reports pages, and each report's §10. Two factual nits fixed along the way.
- **`docs/` editorial scrub** — de-duplicated overlapping explanations so each set-piece (the two-stage pipeline, run-to-run variability, the remit/finding split) has a single owner across `usage` / `understanding-variability` / `interpreting-reports` / `RAISE` / `owasp` / `installation`.

### Unchanged on purpose
- **The scan engine and findings schema.** No `schema.py`, `render.py`, `manifest_to_findings.py`, or knowledge-base change — `schema_version` stays `"2.0"`. The single `SKILL.md` edit is confined to the Pre-flight remit-*authoring* guidance and does not touch the 12-step analysis procedure, so the committed baselines and every scan's output are unaffected. The variables behind the re-freeze are the reference model (4.7 → 4.8) and the freeze method (single-run → median-of-3).

### Notes
- Per-category scoring variance (concentrated on operative-but-imperfect-control targets; `openai-customer-service` σ ≈ 0.28) is tracked for a future scoring-rigour change — see RFE [#48](https://github.com/open-agent-ai-security/praxen/issues/48). Theme-coverage (no Critical theme dropped) held on all 36 runs behind this baseline (the eleven re-baseline targets at 33, plus Hermes at 3).

## [0.7.7] — 2026-05-29

**SKILL polish + a fresh baseline set.** Two non-breaking SKILL improvements (multi-component remit guidance + source-inferred log files), an additive schema change, and a cold full-suite re-scan against all eleven targets to verify the SKILL deltas land non-breakingly. Findings engine remains the same shape: `manifest_to_findings.py` and the four knowledge bases are byte-identical to `0.7.6`; the new behavior is calibration-only.

### Added
- **Pre-flight Step 5 — flag under-documented capabilities rather than assuming restrictions.** When source documentation names a capability without scoping it (*"supports SSH tunnel mode"*, *"executes shell commands"*), the remit-authoring path now writes the best inference tagged `[Inferred]` and surfaces it as an open question at delivery — rather than writing a MUST NOT clause based on assumed scope, which previously produced Critical findings that were remit documentation errors rather than code vulnerabilities. (PR #42)
- **Pre-flight multi-component-deployment guidance.** New paragraph on when to combine vs split remits for cooperating components, plus the structural rule for combined remits (scope note in Mission designating the primary RAISE subject, sub-headings within existing sections, no invented top-level sections). The Worker Remit template's Mission placeholder surfaces the same guidance at point of use. (PR #42)
- **Step 4 source-inferred log file rows.** When no log files are found on disk but logging infrastructure is present in source (Python `RotatingFileHandler` / `FileHandler`, Node.js `winston` / `pino` file transports, Go `log.SetOutput` / `zap` file sinks, or language-equivalent log-routing configuration), the scanner now infers the runtime log file locations and records each with `mtime: "unknown"` and `status: "inferred"`. These rows give the operator an accurate picture of where runtime logs will appear on a deployed instance and support Monitor Continuously scoring on source-only scans. (PR #43)
- **Step 9.8 — do not file findings for inferred log files.** The `inferred` rows in the log-files table communicate the situation; a "no logging" finding is warranted only when there is no logging infrastructure at all. (PR #43)
- **`docs/usage.md` "For highest scan fidelity: run in a fresh context"** — operational guidance on the cold-context subagent pattern for high-confidence scans. (PR #43)
- **`docs/writing-remits.md` sync** — surfaces the `[Inferred]` review checkpoint and a new "Writing restrictions for under-documented capabilities" entry under Common mistakes. (PR #42)

### Changed
- **`findings.schema.json` and `schema.py`** — `log_files` row `status` enum is now `["active", "inferred"]`. `inferred` is new (PR #43); `new` is removed as a vestige — it had appeared exactly once across all committed baselines (v0.7.4 aider's `.aider.llm.history`) and that one use was a misclassification of what should have been `inferred` (the path was derived from source code, not observed on disk; `inferred` didn't exist as a value yet). The scanner is read-only and has no scan-start-time comparison logic, so "freshly created this run" was never a semantically distinguishable case from `active`. The 6 rows in 4 historical JSONs that carried `"status": "new"` (1 in the v0.7.4 baseline, 5 across the `tests/runs/v0.7.3-prerelease*` snapshots) have been reclassified to `"inferred"`. `schema_version` stays at `"2.0"` — this is cleanup of a vestige rather than a semantic schema change.
- **`render.py` and `report_template.html`** — added `log-status-inferred` CSS class (muted color) and label; added the **Logs** jump-nav button and an `id="logs"` anchor on the Discovered Log Files section.
- **`tests/baselines/v0.7.7-sequential/`** — fresh full-suite re-scan against all eleven targets, replaces the previous `v0.7.4-sequential/` set as the canonical baseline. Cold runs against current upstream sources. Per-target delta narrative in `tests/baselines/v0.7.7-sequential/BASELINE.md`.
- **`tests/baselines/owasp-coverage-report.html`** — regenerated against the new baseline set.
- **`tests/baselines/v0.7.4-sequential/` retired**, kept on disk for diff archaeology. README pointers updated.

### Unchanged on purpose
- **Findings engine.** `manifest_to_findings.py` and the four knowledge bases (`KB_RAISE_SCANNING.md`, `KB_LLM_TOP10.md`, `KB_AGENTIC_TOP10.md`, `KB_MCP_SECURITY.md`) are byte-identical to `0.7.6`.
- **Schema major.** `schema_version` stays at `"2.0"`. The `log_files` row `status` enum cleanup removes a vestigial value that was never semantically distinct from `active` — practical impact on downstream consumers is nil.
- **Render layer.** `render.py`'s `_LOG_STATUS_CLASS["new"]` / `_LOG_STATUS_LABEL["new"]` dict entries and `report_template.html`'s `.log-status-new` CSS rule are deliberately kept as dead code — removing them would break byte-identity with every historical committed HTML that embeds them in its `<style>` block.
- **Plugin install identifier.** Still `praxen@open-agent-ai-security`; no marketplace `name` change.

### Calibration notes
- **Monitor Continuously.** Source-only scans that previously reported "no log files found" will now report `inferred` rows when logging infrastructure is present in source. Monitor Continuously can legitimately land 1 or 2 (instead of 0) on targets where the logging is real but the on-disk files don't exist at scan time. A target's MC delta-vs-`v0.7.4-baseline` is influenced by this calibration shift; see `tests/baselines/v0.7.7-sequential/BASELINE.md` for the per-target read.

## [0.7.6] — 2026-05-28

**OWASP LLM and Agentic Top 10 coverage visualizations.** Every Praxen report now carries two full-bleed 5×2 coverage grid sections — one per framework — showing the top-three most-severe findings per category as anchored chips, with empty cells rendered as "No findings" so the grid reads as a coverage *map* rather than a hit list. A new cross-baseline aggregate report tool ships under `tests/baselines/` for reviewing the suite's coverage across all eleven targets. **No findings-engine change** — `SKILL.md`, `schema.py`, `manifest_to_findings.py`, the knowledge bases, and every committed findings JSON are byte-identical to `0.7.5`; the grids are a new view over data that has been in the canonical JSON since schema 2.0. No migration required.

### Added
- **OWASP LLM Top 10 Coverage and OWASP Agentic Top 10 Coverage grid sections** in the rendered HTML report. Each grid is a 5×2 layout, one card per `LLM01`–`LLM10` / `ASI01`–`ASI10`. Populated cards show up to three findings ordered Critical → High → Medium → Low → Informational then by finding ID, each as a clickable chip anchored to the matching Findings Register entry. Empty cells render a muted "No findings" placeholder. Driven by each finding's existing `owasp_llm` / `owasp_agentic` primary scalar.
- **OWASP coverage tables in the TXT summary.** Compact per-category counts for both Top 10s now appear in `<agent>-analysis-<timestamp>.txt` between the remit-coverage tally and the Critical findings list — full counts, not capped at three.
- **`tests/baselines/owasp_coverage.py`** — a stdlib-only utility that walks a chosen baseline set and renders a self-contained HTML summary aggregating OWASP classifications across targets, with horizontal bar charts and target cards linked to both the source repository and the per-target Praxen analysis report. Argparse CLI (`--baseline-dir`, `--out`), defaults to the current baseline set.
- **`tests/baselines/owasp-coverage-report.html`** — committed snapshot of the cross-baseline summary, served live at `https://open-agent-ai-security.github.io/praxen/tests/baselines/owasp-coverage-report.html`. Regenerated from the script when baselines change.

### Changed
- **`render.py` and `report_template.html`** — expanded with the grid-expansion logic and CSS for the new sections; `_OWASP_LLM_CODES`, `_OWASP_AGENTIC_CODES`, and `_OWASP_CHIPS_PER_CARD` constants document the placement and cap.
- **Docs synced.** `PRAXEN_SPEC.md` §7 picks up the new grid sections (RAISE moves to §11, Footer to §12); `docs/interpreting-reports.md` adds §9 / §10; `docs/owasp.md` describes how the grid relates to per-finding tags; `README.md` mentions the grid in the OWASP framework bullet.
- **`tests/baselines/v0.7.4-sequential/`, `tests/baselines/v0.7.0-sequential/`, `tests/fixtures/finbot.golden.{html,txt}`, `examples/{finbot,helperbot}/...analysis.html`** — re-rendered against the new template + render constants. Underlying JSON unchanged, so this is a template-output diff only.
- **`tests/runs/v0.7.3-prerelease*` historical snapshots and `tests/baselines/v0.7.0-sequential/BASELINE.md`** — stale `open-ai-security.github.io/praxen/` URL prefix swept to `open-agent-ai-security.github.io/praxen/` so embedded RAISE / OWASP tag-chip links resolve again. No semantic change.

### Unchanged on purpose
- **Findings engine.** `skills/behavior-verifier/SKILL.md`, `schema.py`, `manifest_to_findings.py`, `findings.schema.json`, and the four knowledge bases under `knowledge/` are byte-identical to `0.7.5`. The scan procedure produces the same canonical JSON it did before; the grids are a new rendering.
- **Schema and findings JSONs.** No schema bump — still `2.0`. Every committed findings JSON across baselines and examples is byte-identical to `0.7.5`. Existing JSONs render the new grid views without any re-scan.
- **Plugin install identifier.** Still `praxen@open-agent-ai-security` — no marketplace change beyond the version bump.

### Notes
- The cross-baseline coverage report is treated as a stable, committed artifact (similar to the bundled `examples/` reports) rather than ad-hoc throwaway output. Regenerate via `python3 tests/baselines/owasp_coverage.py --baseline-dir tests/baselines/v0.7.4-sequential --out tests/baselines/owasp-coverage-report.html` whenever the underlying baselines change.
- Two cross-platform robustness fixes on `owasp_coverage.py` (UTF-8 encoding on read and write, POSIX path normalization for HTML `href`s) ensure the tool runs identically on Windows; the file is otherwise pure Python 3.9+ stdlib.

---



## [0.7.5] — 2026-05-27

**GitHub org rename: `open-ai-security` → `open-agent-ai-security`.** Trademark-driven rename of the org, isolated in its own release so the migration is unambiguous. **No functional changes** — no schema change, no scoring change, no SKILL change, no renderer-logic change. The Praxen pipeline behaves identically to `0.7.4`; only the canonical URLs that Praxen emits and the plugin marketplace identifier change.

**Migration for existing installs.** The plugin install identifier changes from `praxen@open-ai-security` → `praxen@open-agent-ai-security`. GitHub auto-redirects the old URLs, so existing installs keep working, but to land on the canonical identifier:

```
/plugin uninstall praxen@open-ai-security
/plugin marketplace remove open-ai-security
/plugin marketplace add open-agent-ai-security/praxen
/plugin install praxen@open-agent-ai-security
```

### Changed
- **Plugin marketplace identifier.** `.claude-plugin/marketplace.json`'s `name` is now `open-agent-ai-security`. Install command becomes `/plugin install praxen@open-agent-ai-security`. Marketplace `owner.url` and the praxen-entry remain the same in shape; only the org-name segment changes.
- **Canonical URLs the renderer emits.** `render.py`'s `_DOCS_BASE` and footer attribution string, plus the four hard-coded RAISE/OWASP doc links and the footer link in `report_template.html`, now point at `open-agent-ai-security.github.io/praxen/docs/` and `github.com/open-agent-ai-security/praxen`. Every newly rendered report carries the new URLs in its body and footer.
- **`findings.schema.json` `$id`.** Updated to the new canonical URL. Schema shape is unchanged; only the identifier moves. Old `$id` references still resolve via GitHub redirect.
- **Repo metadata and docs.** Updated repo URLs in `README.md`, `docs/installation.md`, `docs/quickstart.md`, `docs/usage.md`, `docs/index.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `examples/README.md`, `tests/README.md`, and `.github/ISSUE_TEMPLATE/config.yml` (security advisory + discussions links).
- **`tests/baselines/v0.7.4-sequential/` regenerated.** All eleven targets re-rendered against the new template + render constants; canonical JSON unchanged, so this is a URL-string diff only. `tests/fixtures/finbot.golden.{html,txt}` likewise regenerated. `examples/finbot/finbot-analysis.html` and `examples/helperbot/helperbot-analysis.html` regenerated.

### Unchanged on purpose

- **Historical baselines** (`tests/baselines/v0.7.0-sequential/**`, `tests/runs/v0.7.3-prerelease*/**`) keep their old-URL footers. Those are point-in-time snapshots and rewriting them would falsify what was actually shipped at that version. The byte-identity check in `tests/render/test_render.py` already filters on the current template-era URL marker, so frozen baselines validate schema and re-render only, not byte-identity.
- **CHANGELOG historical entries** ([0.7.0] through [0.7.4]) retain references to `open-ai-security` URLs as point-in-time references; the GitHub redirect keeps them resolving.
- **Schema, scoring, renderer logic, SKILL.** No behavior change. `test_render.py` is **176 / 0**, `test_manifest_to_findings.py` is **28 / 0**.

### Notes

- **RFE #37** ([open-agent-ai-security/praxen#37](https://github.com/open-agent-ai-security/praxen/issues/37)) tracked the scope of this release.
- **Plugin-install smoke check.** Pre-tag `claude plugin validate .` passes; post-tag smoke check (`/plugin marketplace add open-agent-ai-security/praxen` + `install praxen@open-agent-ai-security`) is part of the release ritual.

---

## [0.7.4] — 2026-05-27

**Deterministic Step 10 + Step 9.9 emission discipline + version-source cleanup + v0.7.4 re-baseline.** Three workstreams in one release. (1) `SKILL.md` Step 10 converts from LLM-composed JSON to a deterministic stdlib Python converter (`manifest_to_findings.py`) that mechanically translates the Step 9.9 draft manifest into the canonical findings JSON. This eliminates the historical principal stall site at scale (LLM JSON-emission bursts under load) and the class of arithmetic-mismatch bugs surfaced by the v0.7.3 external-validation work (Lobot r1 `weighted_overall` mismatch; Lobot r2 `stat_counts` mismatch). (2) Step 9.9 picks up chunked-write emission discipline (skeleton + Edit-append + heartbeats) and Step 3 adds a one-line source-read pacing guard — together they close the remaining 600 s subagent-watchdog vectors at the SKILL layer. (3) `praxen_version` and `schema_version` are now populated by the converter from canonical sources (`.claude-plugin/plugin.json` and `schema.SCHEMA_VERSION` respectively); the SKILL no longer writes them, and `build.sh` sanity-checks that `PRAXEN_SPEC.md`, `plugin.json`, and `marketplace.json` agree. Re-baselined as `tests/baselines/v0.7.4-sequential/`; the v0.7.0 baseline is retired.

**No schema change. No scoring-formula change.** `findings.schema.json` and `schema.py` are unchanged in shape; the RAISE weights, the per-rule audit methodology, and the renderer's analytical logic are all preserved. The baselines move because the SKILL's calibration discipline tightened (Medium-tier preservation, compound-signal escalation), not because the scoring math changed.

### Added
- **`manifest_to_findings.py` — the deterministic Step 10 converter** (#32, #34). Stdlib-only, no third-party dependencies; reads the Step 9.9 parser-grade draft manifest and emits canonical findings JSON byte-identically on rerun. `schema.py` validates the result before write; a malformed manifest fails fast with the offending line. Architecture rationale and design considerations live in PR #32. Bundled with the plugin alongside `render.py` so operators get both stages of the pipeline without any pip install.
- **`tests/render/test_manifest_to_findings.py` — converter smoke harness.** 28 standalone (no-pytest-required) checks: golden round-trip against the helperbot fixture, determinism (byte-identical re-runs), schema validation, render integration, value coercion (null for nullable fields, `""`/`"null"`/`"none"` sentinel normalization), seven negative cases (missing section, bad format version, heading/id disagreement, malformed evidence, unknown field, etc.), canonical JSON key order. Catches the structural-malformation cases that historically only surfaced at render time.
- **`tests/baselines/v0.7.4-sequential/` — frozen cold-runs of all eleven targets** on the Praxen v0.7.4 skill, validating the deterministic-Step-10 + emission-discipline + calibration changes shipped this release. Full Suite cleared 11/11 with **zero stalls** at a median wall time of ~8 min (range 5–11 min) — roughly half the v0.7.3-era median (12–18 min with ~39 % stall rate). Every target carries at least 2 Mediums (no tier compression). `v0.7.0-sequential/` is retired and kept on disk for diff archaeology. Per-target bands in `tests/README.md` recalibrated against the new baseline.
- **`build.sh` version-agreement guard.** Reads `PRAXEN_SPEC.md`'s `**Version:** X.Y.Z`, cross-checks against `.claude-plugin/plugin.json`'s `version`, and against `.claude-plugin/marketplace.json`'s praxen-entry `version`. Future drift fails the build instead of silently producing reports stamped with the wrong version — the failure mode that motivated the version-source-of-truth cleanup.

### Changed
- **`SKILL.md` Step 10 — deterministic script invocation, not LLM emission.** Step 10 is now a single `manifest_to_findings.py --manifest <draft.md> --out <findings.json>` call against the Step 9.9 manifest. The script owns all arithmetic (severity counts, weighted RAISE, `stat_counts`), all derivation (category names/weights, escalation, `policy_rule_text` from rule_id lookup), and all schema-aware key ordering. The LLM is removed from the JSON-composition loop entirely. Per-rule `rule_text` and `policy_rule_text` must still be quoted verbatim from the remit, but that judgment is made at Step 9.9 (in the manifest), not at Step 10.
- **`SKILL.md` Step 9.9 — chunked-write emission discipline.** The draft manifest is now emitted skeleton-first (Write a stub with all required section headings + heartbeats), then field-by-field via Edit-append, never as one long compose-then-write. This eliminates the silent-compose-burst pattern that historically tripped the 600 s subagent no-progress watchdog on large workspaces — the operator now sees a continuous stream of small writes instead of a long silent pause. The manifest's parser-grade format (`### PRAX-…`, `#### R-NN`, depth-indexed bullets) ensures `manifest_to_findings.py` can parse mechanically without judgment.
- **`SKILL.md` Step 3 — explicit source-read pacing guard.** A one-line guard against long internal-only reasoning between large source reads — the historical stall site on `aider` and `openhands` source exploration in v0.7.3-era runs. The worker now emits a brief observation after each substantial read so the watchdog sees a continuous tool-use stream rather than going silent during deep file scans.
- **`SKILL.md` Steps 6 + 9.9 — "Don't tier-compress" Medium guidance + completeness check.** The XSS-into-HITL-bypass compound finding in the v0.7.3 external-validation r1 run was a direct casualty of severity collapse: real Medium-grade observations were being upgraded to High or dropped, leaving the dominant-pattern read without a middle tier. Step 6 now explicitly rejects "compress everything into Critical+High to look bigger"; Step 9.9 carries a self-check that the manifest carries at least the realistic Medium count for the target. Every v0.7.4 baseline target carries ≥ 2 Mediums; the well-built ones (deepagents-cli) correctly land Medium-heavy without forced Criticals.
- **`praxen_version` and `schema_version` populated by the converter, not the SKILL.** Single source of truth for each: `praxen_version` ← `.claude-plugin/plugin.json`'s `version` field (mirrored to `findings.schema.json`'s field description), `schema_version` ← `schema.SCHEMA_VERSION`. The SKILL's Step 9.9 manifest template drops both bullets. Drafts written by older SKILL revisions (or by workers who still write them by reflex) are accepted-and-discarded by the converter for backward compatibility. Eliminates the LLM-eyeballed-version drift bug that produced mixed `0.7.3` / `0.7.4` footers in pre-cleanup reports.
- **Tolerant value coercion — `_is_null_sentinel()` everywhere.** The converter's `_coerce` function and `_populate_derived` post-processing both route through a single helper that treats `""` / `"null"` / `"none"` (case-insensitive) as equivalent to the JSON literal `null`. Workers writing `none` or empty strings for nullable fields (`finding_id`, `owasp_llm`, `owasp_agentic`, `policy_rule_ids`, `related_findings`) no longer trigger schema-validation failures or `int()`/`float()` coercion crashes. Locked by new tests in Section 5b of the converter smoke harness.
- **Per-target bands in `tests/README.md` recalibrated against the v0.7.4 baseline.** Same blind-run-variance shape as before (±2 severity counts, ±0.3–0.4 weighted RAISE) — recentered on the v0.7.4 numbers. The widths will refine as more v0.7.4-era runs land; this is the new starting point.

### Fixed
- **The principal subagent watchdog stall site at scale.** Pre-0.7.4, the LLM-composed JSON in Step 10 was the single biggest source of >600 s silent-compose bursts on large workspaces. The deterministic converter is a sub-second script call; under load, this drops the suite stall rate from ~39 % to 0 % in the v0.7.4-sequential baseline run. The v0.7.3-era SKILL fixes were emission discipline at the prose-composition layer; this release closes the loop by removing the JSON-emission step from the LLM entirely.
- **`weighted_overall` and `stat_counts` arithmetic mismatches.** The Lobot r1 and r2 bugs from the v0.7.3 external-validation work — `weighted_overall: 1.85` declared while Σ(score × weight) was actually 1.75; `stat_counts.verified: 5` declared while `rules[]` had 4 verified entries — were both consequences of asking an LLM to maintain running counts while composing JSON. The converter owns these computations now; the bugs are structurally impossible. (`schema.py` cross-field validation catches any future drift before the JSON touches disk.)
- **Author-side missing-field-bullet cases.** Workers who omitted the `owasp_llm` / `owasp_agentic` bullets entirely (rather than writing `null` explicitly) used to fail schema validation with `required field is missing`. The converter now defaults both fields to `null` post-parse, alongside the sentinel-string normalization above — the schema's "required field, may be null" contract is preserved without forcing the worker to write `null` explicitly.

### Notes
- **No schema, renderer, validator, or scoring change.** `findings.schema.json`, `schema.py`, `render.py`, and the RAISE weights are unchanged in shape and behavior. `tests/render/test_render.py` is **176 / 0** locally and on CI across Python 3.9 / 3.12 / 3.13; `tests/render/test_manifest_to_findings.py` is **28 / 0** locally. The v0.7.0 baseline JSONs still re-render byte-identical from their JSON via the `tests/render/test_render.py` byte-identity check.
- **External-validation alignment.** The v0.7.3-era validation runs on Google's ADK ambient-expense-agent and Lobot (PR #30 review work) surfaced the exact failure modes this release fixes: weighted-overall arithmetic error, stat_counts mismatch, severity tier-compression, sentinel-string brittleness. The architecture choice for this release (deterministic Step 10 + tolerant sentinels) is a direct response to those findings.
- **Plugin-install smoke check verified post-tag.** `claude plugin marketplace add open-ai-security/praxen` + `install praxen@open-ai-security` + `list` succeeded post-tag and reported the plugin enabled at version 0.7.4 from main. Pre-tag `claude plugin validate .` also passed (catches manifest schema regressions before the release is cut).
- **Calibration drift to keep an eye on.** Several v0.7.4 baseline targets land outside their pre-recalibration v0.7.0-era bands — particularly Criticals on devika (7 vs ≤ 6 ceiling) and openhands (4 vs ≤ 2 ceiling). Recalibrated bands in `tests/README.md` center on the v0.7.4 numbers; future re-runs will refine the widths. Worth watching for "is this run-to-run variance or genuine SKILL drift" patterns across the next 1–2 v0.7.4-era runs.

---

## [0.7.3] — 2026-05-25

**Subagent watchdog stall fix + skill-assisted Worker Remit authoring + HTML report v2 polish.** Four workstreams in one release, all upstream of the canonical findings JSON — the schema, the scoring, and the analysis methodology are unchanged. The headline is the SKILL emission discipline that eliminates the silent-compose bursts that historically tripped the 600 s subagent no-progress watchdog on long scans; the same SKILL now also drives Worker Remit authoring from source/docs/description in addition to consuming an existing remit. The report layer picks up a masthead, jump-nav, and collapsible finding cards. The test plan is codified into three named tiers with a committed home for pre-release Full Suite Runs.

### Added
- **`SKILL.md` skill-assisted Worker Remit authoring (Pre-flight section).** The behavior-verifier skill can now create / write / draft / build / author a Worker Remit for an agent from source code, documentation, or a prose description — using `WORKER_REMIT_template.md` as the required structure. The frontmatter `description:` lists remit authoring as a trigger so a request like "build me a worker remit from the docs" routes to the skill. Documented in the SKILL frontmatter, the Pre-flight section, and `docs/usage.md` (the "Invoking by evidence type" subsection adds a copy-pasteable prompt per evidence shape — source, deployment state, behavioural artefacts, governance docs).
- **`tests/README.md` three-tier test plan and committed pre-release runs.** Names the testing tiers (Smoke harness / Single-target scan / Full Suite Run) and codifies the Full Suite Run protocol — both invocation paths (parallel subagent capped 4-8 concurrent, or sequential foreground), the verdict-report shape, and the after-run commit convention. `tests/runs/` is the new committed home for named pre-release Full Suite Runs (the evidence each release-candidate cleared the bar, distinct from the frozen comparison baselines under `tests/baselines/`). 0.7.3 ships with three committed runs — [`v0.7.3-prerelease/`](tests/runs/v0.7.3-prerelease/SUITE_RUN.md) (first attempt, foreground rescues), [`v0.7.3-prerelease-r3/`](tests/runs/v0.7.3-prerelease-r3/SUITE_RUN.md) (post-SKILL-fix, 11/11 clean), and [`v0.7.3-prerelease-r4/`](tests/runs/v0.7.3-prerelease-r4/SUITE_RUN.md) (post-polish-commit re-validation, 11/11 clean, both r3 RAISE band-floor flags corrected upward).
- **HTML report v2 — masthead, jump-nav, Executive Summary, collapsible finding cards** (#28). The new `masthead` band surfaces the weighted RAISE score and severity counts on page load without scrolling. `jumpnav` resolves the post-compaction TOC friction documented in the v0.7.0 feedback. Executive Summary band carries the dominant-pattern narrative; finding cards are now collapsible, with details on demand. Self-contained HTML, zero external fetches, deterministic byte-for-byte re-render. Both committed examples (finbot, helperbot) and all eleven `v0.7.0-sequential` regression baselines re-rendered from their unchanged JSON.
- **`.github/workflows/dco.yml` DCO enforcement.** Every non-merge, non-bot commit in a PR must carry a `Signed-off-by:` trailer matching the author or committer. GitHub bot accounts (Dependabot, gemini-code-assist) are exempt by `[bot] <` author suffix. Documented in `CONTRIBUTING.md`. Reported during 0.7.3's own PR work (the 7 unsigned commits on the release PR caught the gap).

### Changed
- **`SKILL.md` Step 9.9 — the draft manifest must carry full-prose findings, not outlines.** Every prose value that will appear in the JSON — `summary`, `description`, every `evidence[].snippet`, every `recommended_actions[]` item, `policy_rule_text` (the verbatim remit quote), the per-category `rationale`, `weighted_rationale`, `behavior_summary`, the intro-band summaries — must be written into the manifest in **its final form**, not as outlines, abbreviations, or `TBD` placeholders. Step 10 then performs JSON-shape translation only: walk the manifest top-down and emit each section's JSON record from its corresponding manifest bullet, with no re-composition, wordsmithing, or analytical refinement. **This is the root-cause fix for the subagent watchdog stalls** — pre-composing the prose at 9.9 means every Step 10 Edit is a short mechanical write (~13 s per the anchor-test) rather than a long silent compose (~55 s with high variance that occasionally spiked past 600 s).
- **`SKILL.md` Step 10 — mechanical translation, not composition.** Step 10 is now explicit: read the Step 9.9 draft manifest and walk it top-down. For each finding bullet in the manifest, emit the corresponding JSON object via Edit-append (anchored on the closing `]` of the `findings` array). Do not refine wording, add details, or introduce new analytical judgment. If the manifest is missing a field the JSON requires, return to Step 9.9 and add it there — do not compensate in Step 10. This holds for both foreground and subagent runs.
- **`SKILL.md` Step 7 — compound-signal-reasoning prominence.** Compound findings produced by Step 7 are now explicitly the deliverable — splitting a compound chain into N independent findings with cross-references defeats the escalation, because each half on its own typically doesn't trigger the escalation row. The chain's `evidence` array may exceed the Step 10 two-span soft cap when the chain genuinely spans more sites — name every site that's load-bearing to the escalation, not a truncated subset. Surfaced by external validation of an ambient-expense-agent re-scan whose XSS-into-HITL-bypass compound landed split into two High findings rather than one Critical compound. (Investigation showed the cap is not a hard blocker in practice — 37 % of `v0.7.3-prerelease-r3` findings carry `>2` evidence items — so the prominence tweak addresses the marginal case rather than rewriting the cap.)
- **`SKILL.md` Step 9.9 manifest template — inline prose caps and weighting micro-notes.** The manifest template now carries the `summary` ≤ 25 words and `description` ≤ 3 sentences caps inline (the analyst sees them at manifest-writing time, not only when reading Step 10), a dedicated sub-bullet for the `policy_rule_text` ` / ` (space-slash-space) separator on multi-rule findings, a weighting micro-note in the `raise_posture.categories` block (IZT = 0.25, others = 0.15; compute Σ(score × weight) explicitly, round once at the end), and an explicit "walk and tally" instruction on `footer.severity_counts`. Surfaced by the external-validation review of two real-agent scans (Ambient Expense, Lobot).
- **`SKILL.md` Step 9.6 — explicit per-status `finding_id` rules.** `verified` / `vague` / `enp` rules carry `null` by definition. `gap` and `partial` rules must point at a finding describing the specific gap. The earlier guidance only mentioned the `gap` case; `enp` (enforcement-not-possible — behavioural or cultural rule outside the scan's visibility) was inferred. Now stated.
- **`SKILL.md` Step 10 Common validation errors — `partial`-rule consistency check.** Mirror of the existing `verified`-contradiction check. A `partial` rule's `finding_id` must point at the finding describing the specific gap that makes the rule incomplete — not just any finding in the vicinity. An unrelated-finding link produces a misleading coverage picture (claims partial audit when there is none).
- **`SKILL.md` Step 3 / Step 4 — KB_MCP_SECURITY load timing.** Fixes a chicken-and-egg in the prior text: Step 3 conditionally loaded `knowledge/KB_MCP_SECURITY.md` based on a Step 4 discovery that hadn't happened yet. Step 3 now points forward, and Step 4's closing instructs the analyst to return to Step 3 if MCP configuration was found in the workspace.
- **`tests/README.md` — Full Suite Run protocol restored to parallel-subagent path.** The root-cause SKILL fix made parallel subagent invocation reliable again; the prior 0.7.2-era stream-health workaround (skeleton-first + heartbeats + render-every-N) was subsumed by the SKILL itself and is no longer documented as a separate recipe. Foreground stays as the alternative, useful for debugging single targets.

### Notes
- **No schema, renderer, validator, or scoring change.** `findings.schema.json`, `schema.py`, and `render.py`'s analytical logic are unchanged in shape. The renderer / template output changed by design for the HTML v2 layout — the committed golden fixtures (`tests/fixtures/`, `tests/render/`) and all eleven `v0.7.0-sequential` baselines were re-rendered from their unchanged JSON; `python3 tests/render/test_render.py` reports 110 / 0 locally. CI runs the smoke harness + `build.sh` on every push and PR across Python 3.9 / 3.12 / 3.13.
- **Calibration drift to keep an eye on.** Both r3 and r4 stabilised at langchain-sql RAISE 1.30 (+0.10 above the per-target band 0.6-1.2). Same target, same wobble, same direction across two independent runs — suggesting the per-target band is slightly tight for mature-library targets where Manage-Your-Supply-Chain credibly scores 2 rather than 1. Worth a 0.7.4 review of the langchain-sql band specifically; not a 0.7.3 blocker.
- **Plugin-install smoke check verified** pre-tag against the published 0.7.2 marketplace install path (`claude plugin marketplace add open-ai-security/praxen` + `install praxen@open-ai-security` + `list` succeeded; plugin showed up enabled at version 0.7.2 from main). Re-run post-tag to confirm the 0.7.3 manifest propagates correctly.

---

## [0.7.2] — 2026-05-22

**Reporting-layer overhaul — a redesigned HTML report.** The findings engine, the canonical JSON schema, and the RAISE scoring are unchanged; this release reworks how the report *looks* and *links*. Because the renderer and template output changed (intentionally), the committed golden fixtures and all eleven `v0.7.0-sequential` regression baselines were re-rendered from their unchanged JSON, and the two published examples were freshly re-scanned under 0.7.2.

### Added
- **Unified masthead** replacing the old header bar + light intro band: a `PRAXEN` wordmark with tagline, an `<agent> Analysis Report` title with completion date, and an at-a-glance summary cluster — severity-colored finding counts (`5C · 5H · 4M …`, zero tiers omitted) and the RAISE score. The masthead now carries the executive summary instead of leaving the top of the report sparse.
- **Finding tag capsules are now links** to the exact entry in Praxen's own framework docs on GitHub Pages — OWASP LLM/Agentic → `owasp.html#<code>` (e.g. `#llm02`, `#asi05`), RAISE → `RAISE.html#<category>`, MCP → the MCP-guide section. Derived in `render.py` from the tag's kind + label (no schema change), backed by new per-entry anchors added to `docs/owasp.md`.
- **In-report and in-docs links to the rendered GitHub Pages docs** — framework references in the report link to `RAISE.html` / `owasp.html`, and the example-report links across the README, quickstart, and `examples/README.md` now point to the live rendered reports on Pages rather than raw repo blobs.

### Changed
- **Top of the report restructured into consistent boxed cards** — Agent Remit (as declared) → Behavior Summary (as observed) → Scope of Analysis — replacing the full-bleed side-by-side intro grid, and removing the agent-name/date that was duplicated between the header and the title.
- **Timestamps render human-readably** (e.g. `May 11, 2026, 22:49 UTC`) instead of raw ISO `…Z`; the JSON keeps the machine-readable ISO. The formatter is locale-independent and deterministic, and reads the zone the value carries.
- **Footer repo link is now legible on the dark background** (it was falling back to default link-blue on navy); both footer links share a green hover.
- **RAISE weighting note trimmed** — drops the per-category percentages already shown on each card and deep-links the rationale to the RAISE doc.
- **Published examples re-scanned under 0.7.2** — finbot (15 findings, RAISE 0.60) and helperbot (14 findings, RAISE 0.60) regenerated by the current skill against live source, replacing the stale `0.3.0`-era examples; `examples/README.md` prose updated to match. (The helperbot re-scan also corrects an over-strong path-traversal claim: HelperBot is an `api`-protocol persona whose declared file tools are never wired into the request path, so those rules are now scored as gap/enforcement-not-possible.)
- **`SKILL.md` Step 9 — summary fields stay pattern-level (no `file:line` citations).** The Agent Structure and Behavior Summary now explicitly cite files and functions but not line numbers; the precise coordinates live in each finding's evidence block rather than being duplicated in the top-of-report overview. (The re-scanned examples already follow this; the rule codifies it so future scans stay clean.)

### Notes
- No breaking changes for downstream consumers; no change to `findings.schema.json`, the Python validator, the scoring, or the analysis methodology. The one `SKILL.md` edit is a summary-prose guidance rule (narrative fields, not findings). The renderer/template output changed by design, so committed golden fixtures and the eleven baselines were re-rendered from their unchanged JSON; `test_render.py` passes (110 checks).

---

## [0.7.1] — 2026-05-22

**Three batches of operator field feedback rolled in as a single patch release.** No scan logic, schema shape, or scoring behaviour changed — all changes are documentation and a small renderer tweak. The eleven regression baselines re-render byte-identical from their JSON (the renderer change is stdout-only). Patches against `0.7.0`; same plugin name, same install path, same canonical findings JSON.

### Added
- **`SKILL.md` opens with a quick-start (TL;DR) block** — what the skill does, the two inputs it needs (Worker Remit + workspace path), what it writes (three files in `./reports/` plus the Step 9.9 checkpoint), and a one-paragraph map of the 12-step pipeline. Sits above the existing intro so operators don't need to read the 700-line procedure before understanding what they're invoking. Reported by the Lobot field tester.
- **`render.py` exit-0 prints a one-line summary per output file** — `render.py: wrote <path> (N findings, 0 schema errors)`, with equivalent lines for both the HTML and the TXT. Explicit confirmation that schema validation passed (which is silent today) and that the finding count matches expectations, before the operator opens the HTML. `tests/render/test_render.py` asserts the new format.
- **`SKILL.md` opens with a step-by-step jump table** — a TOC right after the TL;DR listing every top-level section with anchor links, so a session resuming after a context compaction can relocate the step it was on without skimming the 700-line procedure from the top. Reported by the ambient-expense-agent field tester (who hit a real mid-scan compaction and had to skim to find Step 9.9's interim-overview format).
- **`SKILL.md` pre-flight block for *standalone* Worker Remit authoring**, plus a frontmatter `description:` field that now lists remit authoring as a trigger. Previously, "build me a worker remit from the docs" never invoked the skill at all (the system-reminder routing didn't match the request) and the resulting remit free-formed its structure instead of using `WORKER_REMIT_template.md`. Both gaps are addressed: the frontmatter trigger so the skill is actually invoked for authoring, and the pre-flight block so a standalone authoring request reads the template before producing anything. Reported by the ambient-expense-agent field tester.
- **`SKILL.md` Step 10 — quick-reference table of all 20 OWASP tag labels** (`LLM01`–`LLM10` + `ASI01`–`ASI10`, copy-paste verbatim). The KB files remain authoritative; this table is a copy-paste aid so the LLM doesn't have to grep the KB for every tag, saving 4–6 tool calls per scan. The same edit corrects an outdated `ASI05` label in the inline example (was `Cascading & Multi-Agent Failures`; the KB says `Unexpected Code Execution (RCE)`). Reported by the ambient-expense-agent field tester.

### Changed
- **`SKILL.md` Step 9.9 — the draft manifest is now schema-mirrored.** The Step 9.9 checkpoint was free-form markdown; if a session compacted during the scan, post-compaction Step 10 had to *interpret* prose back into the canonical JSON shape. The manifest template now uses the same section headings and field names as the canonical findings JSON (`scan`, `intro_band`, `behavior_summary`, `raise_posture` → `weighted_overall` / `weighted_rationale` / `categories`, `remit_coverage` → `stat_counts` / `rules`, `findings` with every per-finding field, `positives`, `log_files`, `footer.severity_counts`), so the recovery path is a mechanical translation, not interpretive synthesis. Reported by the Lobot field tester.
- **`SKILL.md` Step 9.6 — explicit tally for `remit_coverage.stat_counts`, plus the `Counter`-omits-zero gotcha called out.** Manual counting across 5 statuses and 10–20+ rules is where this step most often goes wrong; the step now states that the schema requires all five status keys to be present even at zero (`vague: 0` is valid and common) and warns that `collections.Counter`-equality silently misses missing zero-count keys, so it's an unreliable self-check. The same gotcha is added to Step 10's "Common validation errors" with the explicit-five-key recipe. Reported by the Lobot field tester (who shipped a `gap: 7` count when the correct value was `8` and discovered the Counter blind spot during their own pre-render validation).
- **`SKILL.md` Step 10 + `findings.schema.json` — explicit rule for multi-category findings on `owasp_llm` / `owasp_agentic`.** The scalar fields are single codes; when a finding spans two ASI (or two LLM) categories, the primary classification goes in the scalar field and any secondary code goes in `tags[]` only — never comma-separated, never a list, never the secondary code in the scalar. Reported by the Lobot field tester (ASI03 + ASI09 finding) and corroborated by the ambient-expense-agent field tester (LLM01 + LLM05 XSS finding).
- **`SKILL.md` Step 10 — guidance for line-range evidence** (`agent.py:197-209`, `iam.tf:84-92`). The schema's `line` field is a single integer; the new guidance puts the start line in `line` and the range syntax in `snippet`. `findings.schema.json` description for the `line` field carries the same rule. Reported by the ambient-expense-agent field tester.
- **`SKILL.md` Step 10 "Common validation errors" — new check for `verified` rules cited as violated by findings.** A finding's `policy_rule_ids` pointing at a rule whose `status` is `verified` is a logical contradiction (you can't violate a rule you said is verified) and the field tester hit this and self-corrected mid-scan. The validator note tells the LLM to walk the linkages and either downgrade the rule to `partial` or null the link. Reported by the ambient-expense-agent field tester.
- **`SKILL.md` Step 10 — explicit guidance against stretched `policy_rule_ids` links.** Linking an inbound-access finding to an outbound-counterparties clause is a stretch the schema permits but the audit shouldn't reach for; the new note says either name the chain in `description` if the linkage is genuinely traceable, or set both fields to `null` and explain in `description` — don't stretch. Reported by the ambient-expense-agent field tester.
- **`SKILL.md` Evidence Discipline — clarified that `[Verified]` / `[Inferred]` / `[Unknown]` tags are working notes for Steps 4–8, not an output field.** The opening section's strong language about "tag every claim" had no counterpart in the canonical JSON schema, leaving a reader hunting for an output field that doesn't exist. The section now states that the discipline shapes the report through the per-finding `confidence` field, the per-RAISE-category `confidence`, and the prose itself — and that the bracketed tags don't appear in the final JSON. Reported by the ambient-expense-agent field tester.
- **`SKILL.md` Step 10 recovery path — re-surfaces Step 9.9's interim-overview half-gate.** Previously the recovery instruction told a compacted session to "read the manifest and build the JSON" but silently skipped the second half of 9.9's gate (printing the interim overview to stdout). Recovery now explicitly prints the interim overview before writing the JSON. Reported by the ambient-expense-agent field tester (whose session compacted between the manifest write and the JSON, and who printed the overview from first principles).
- **`SKILL.md` Step 10 — `kind=mcp` tagging threshold made concrete.** Previously "for an MCP-specific finding" was ambiguous: an `LLM03` supply-chain finding about an `npx -y @some/mcp-server` install lacks the `mcp` tag in some readings and carries it in others — and two consecutive pre-integration runs of the same target (yaah) produced 2 `mcp` tags and 0 `mcp` tags respectively, neither matching the other. The new rule: `kind=mcp` is attached *only* to findings produced by Step 6's MCP Server Evaluation against `KB_MCP_SECURITY.md`'s minimum-bar checklist. A finding whose primary classification is a different pattern (supply-chain, excessive-agency, etc.) and happens to involve MCP-shaped evidence does *not* carry the `mcp` tag — its OWASP / RAISE tags carry the primary classification and the evidence makes the MCP context clear. Surfaced by the yaah pre-integration #2 subagent.

### Notes
- These changes are docs and a stdout-only tweak to the renderer; no breaking changes for downstream consumers and no migration needed. The Python validator and the published JSON Schema are unchanged in shape (only descriptions tightened).

---

## [0.7.0] — 2026-05-20

**First public soft-launch release. The project has been renamed Praxa → Praxen and moved to its new home at `github.com/open-ai-security/praxen`.** No scan logic, schema shape, or scoring behaviour changed — this release is the rename + relocation + a small batch of pre-launch test-suite improvements that arrived alongside it. The eleven regression baselines were re-frozen under the new name (same cold runs, same findings).

### Renamed

- **The product is now `Praxen`.** The skill's user-visible branding (HTML header / footer, TXT summary header, report title), the package name, the release artifact, and the scratch-dir prefix all switched from `Praxa` / `praxa` to `Praxen` / `praxen`.
- **Plugin install identifier changed: `praxa@exabeam` → `praxen@open-ai-security`.** The marketplace's `.claude-plugin/marketplace.json` was rehomed to `open-ai-security`; the plugin manifest's `name` is `praxen`. Anyone holding an earlier install should `/plugin uninstall praxa@exabeam` and `/plugin install praxen@open-ai-security`.
- **Release artifact renamed `praxa-X.Y.Z.zip` → `praxen-X.Y.Z.zip`.** First Praxen artifact is `praxen-0.7.0.zip`.
- **`PRAXA_SPEC.md` → `PRAXEN_SPEC.md`.** The CI release workflow's tag-verify step reads this file; the rename is coordinated with the workflow.
- **The findings-JSON top-level field `praxa_version` was renamed `praxen_version`.** The `schema_version` is still `"2.0"` — this is a field rename, not a schema version bump (no consumers were holding the old name; the field was only read by the bundled `schema.py` validator and `render.py`).
- **`.praxa-*` scratch-dir prefix → `.praxen-*`** in `.gitignore` and skill scratch.

### Moved

- **Repository moved `github.com/Exabeam/deckard` → `github.com/open-ai-security/praxen`.** This is the new public home. Every in-repo reference (docs, README, plugin manifest, JSON schema `$id`, rendered report footers) points at the new home. The move was done as a fresh-repo cutover (not a GitHub transfer), so a few historical artifacts stayed at the original repo: the issue tracker (this release's `#27` / `#40` and earlier — the CHANGELOG links them back to `Exabeam/deckard` where they actually live), the merged PR history, and the pre-`0.7.0` GitHub release pages (with their `praxa-0.6.x.zip` artifacts).

### Internal

- **Test remits rewritten as intent-level Worker Remits** ([issue #40](https://github.com/Exabeam/deckard/issues/40), [PR #42](https://github.com/Exabeam/deckard/pull/42)). The eleven `tests/remits/*.md` were rewritten from implementation-level documents (which named internal file paths, class names, config keys, pinned versions) into intent-level *policy* documents — matching the principle the skill itself states ("the remit states policy; you discover implementation"), and no longer brittle to upstream renames.
- **Regression baselines re-frozen as `tests/baselines/v0.7.0-sequential/`** ([PR #43](https://github.com/Exabeam/deckard/pull/43), then this release). All eleven targets were re-scanned cold against the rewritten intent-level remits; the runs were originally committed as `v0.6.3-sequential/` under the old name and were migrated to `v0.7.0-sequential/` by this release's field rename + branding re-render (no scan content changes). Retires the earlier `v0.2-sequential` / `v0.3-sequential` / partial `v0.6-sequential` / interim `v0.6.3-sequential` sets. `tests/README.md` per-target bands and scope notes were updated — including the restructured `openhands` (the agentic core moved to separate packages) and the re-scoped `deepagents-cli` (now a deploy-only bundler).
- **`SKILL.md` Step 6 — `rule_text` / `policy_rule_text` must be a *contiguous, verbatim* span of the remit** (the rule's operative sentence in full): no `...` elision, no spliced fragments, no added/changed punctuation. `test_render.py`'s baseline remit-quote check now compares modulo Markdown emphasis (`**`), since the quote is of the remit's policy text, not its markup.

## [0.6.3] — 2026-05-19

**Draft manifest, plus two fixes from field testing.** The headline is the **draft manifest**: a long scan can exhaust the coding agent's context window and auto-compact mid-analysis, silently degrading the report — findings gathered early get summarized away before the JSON is written. The skill now checkpoints its full synthesis to disk before writing the report, so a compacted run is recoverable rather than silently incomplete (a partial mitigation for the single-pass "unsupported arc", [issue #27](https://github.com/Exabeam/deckard/issues/27)). Alongside it, two bugs that field scans surfaced: `praxa_version` was read from the *analyzed* agent's `plugin.json` instead of recording Praxa's own version, and `policy_rule_ids` / `policy_rule_text` were mandatory on every finding even when a finding doesn't trace to a remit rule. The findings schema is unchanged (still `"2.0"`).

### Added
- **`SKILL.md` Step 9.9 now writes a draft manifest** to `./reports/<agent-slug>-draft-<timestamp>.md` — a markdown record of the full synthesis (every finding, the RAISE posture, the remit-coverage audit, positives, log files), complete enough that Step 10's canonical JSON can be rebuilt from it alone. It's written before the report, alongside the existing interim-overview stdout print. Step 10 gained a recovery instruction: if the session compacted (or the synthesis can't be precisely recalled), build the JSON from the manifest rather than from degraded working memory — and an operator resuming a compacted run can point the skill straight at the manifest. This is the partial mitigation for the single-pass "unsupported arc" — the full intermediate-representation refactor is still tracked in [issue #27](https://github.com/Exabeam/deckard/issues/27). Two independent testers had hit the compaction failure (the v0.6.1 field review and a 0.6.2 plugin scan); the manifest converts it from a silent failure into a recoverable one.

### Changed
- **`docs/usage.md` — "Tips for large workspaces" reworked into "Large workspaces and context sizing"** — why mid-analysis compaction is a *silent* failure, and concrete guidance: use the largest context window available, start a fresh session, scope the input to the agent (not the whole repo). Adds a recovery section: if a run compacts, recover from the draft manifest or re-run.
- **`PRAXA_SPEC.md` — the "context window pressure" section** now documents the draft-manifest checkpoint as the primary survive-compaction mechanism.

### Fixed
- **`praxa_version` in the findings JSON is now a fixed literal in `SKILL.md`, not read from `.claude-plugin/plugin.json`.** When the analyzed agent was itself a Claude Code plugin, the skill read the *target's* `.claude-plugin/plugin.json` and recorded the agent's version as `praxa_version` (a field-reported scan came out as `praxa_version: 1.21.1`). The skill cannot reliably locate its own `plugin.json` once installed, so Step 10 now states the version directly (`0.6.3`), and the Step 9.9 manifest does the same. Found via a tester scan of a plugin target.
- **`policy_rule_ids` / `policy_rule_text` can now be `null`** for a finding that does not trace to a specific Worker Remit rule. RAISE-category and detection-pattern findings — an absent control the remit never names, a supply-chain or monitoring gap the remit is silent on — legitimately have no remit rule, but the schema required both fields non-empty, so the skill was forced to fabricate a value (a field-reported scan stuffed the sentence `"RAISE only — no explicit remit rule"` into the `R-NN` id field). `schema.py` and `findings.schema.json` now accept `null` for both — null together or set together — `render.py` omits the policy-rule line on the finding card when they are null, and `SKILL.md` Step 10 documents when to use null. Found via tester feedback (a plugin scan).

### Notes
- `praxa_version` / plugin version bumps `0.6.2` → `0.6.3`. Release bundle: `praxa-0.6.3.zip`.
- **Smoke + subset validation.** The changed skill was re-run cold against `yaah` (×2), `langchain-sql`, and `openhands` to confirm it executes end-to-end — the draft manifest wrote on every run, the renderer validated, `praxa_version` resolved correctly, and the new null-`policy_rule_ids` path was exercised on real targets (`langchain-sql`, `openhands`). No skill bugs. Scoring on those targets came in *in-band* but shifted against the committed regression baselines, which predate this work — the baselines are due a re-freeze, tracked in [issue #40](https://github.com/Exabeam/deckard/issues/40).

## [0.6.2] — 2026-05-18

**Plugin-marketplace install fix, plus the v0.6.1 field-review cheap wins.** `/plugin marketplace add open-ai-security/praxen` was rejected by the Claude Code marketplace schema validator — `.claude-plugin/marketplace.json` declared the plugin `source` as a bare `"."` where the schema requires a `"./"`-prefixed relative path — so the marketplace-install path silently never worked for any tagged release (the unzip-the-release path was unaffected). 0.6.2 fixes that, and bundles in the small robustness and clarity fixes from the v0.6.1 field review (one executing-LLM ran the full pipeline against a workspace and wrote up what it hit). No changes to detection logic, RAISE scoring, the Worker Remit structure, or the findings schema (still `"2.0"`).

### Added
- **`schema.py` now cross-checks `escalation` against `severity`** — `alert` for Critical/High, `log_only` for Medium/Low/Informational — the same way it already cross-checks `footer.severity_counts` against the findings array. A Critical finding tagged `log_only` no longer passes silently.
- **`schema.py` now validates `owasp_llm` / `owasp_agentic` against the canonical code pattern** (`LLM01`–`LLM10` / `ASI01`–`ASI10`, or `null`) instead of accepting any string; the matching `pattern` was added to `findings.schema.json`. (Garbage values produced garbage tags in the rendered report.)
- **`schema.py` now rejects a finding that lists its own id in `related_findings`** (a self-reference).
- `test_render.py` — negative cases for the three new validations.

### Changed
- **`SKILL.md` Step 1 — `date -u` is now the first executable action of the step**, not a code block buried among the variable-naming examples at the end, with an explicit "do not proceed until you have run it" gate and a stated reason (context is frequently wrong; a bad date here produces silently wrong finding IDs with no error). If `date -u` is genuinely unavailable, the skill is told to stop and ask the operator rather than infer.
- **`SKILL.md` Step 9.9 — the interim-overview print is now framed as a hard gate before Step 10**, not a closing note at the end of the synthesis block ("do not proceed to writing the findings JSON until you have printed this"). The Step 9 intro now calls out 9.9 as a mandatory action rather than a held item. (A field-review run skipped it because its placement read as a closing note.)
- **`SKILL.md` Step 4 / Step 6 — the MCP-config rule now leads with the content criterion**, not the filename list: a file is MCP config when it carries an `mcpServers` / `mcp.servers` / `mcp_servers` block (or an MCP-shaped top-level `servers` map), whatever it's named; the familiar filenames (`.mcp.json`, `opencode.json`, `clawdbot.json`, …) are presented as discovery hints, not the trigger. (Previously the prose listed filenames first and the content rule second as a clarification, which read as "check these names, and also anything that looks like this.")
- **`SKILL.md` Step 10 — added a "Common validation errors" checklist** (severity/stat-count miscounts, RAISE weight / category-name strings, dangling `finding_id` / `related_findings` ids, escalation-vs-severity, non-canonical `owasp_*` codes) so the most frequent strict-validator round-trips can be caught before running the renderer. Tag-label format spelled out explicitly: `CODE — Name` with an em dash, copied from the KB rather than retyped.

### Fixed
- **`.claude-plugin/marketplace.json` — `plugins[0].source` is now `"./"` instead of `"."`** so the marketplace passes the Claude Code schema validator. The bare `"."` form was rejected by `/plugin marketplace add open-ai-security/praxen` with `Invalid schema: plugins.0.source: Invalid input`, blocking install. Per the [marketplace docs](https://code.claude.com/docs/en/plugin-marketplaces#relative-paths), relative plugin sources must start with `./`. (Reported and fixed by an external first-time contributor — [PR #32](https://github.com/Exabeam/deckard/pull/32).)

### Internal
- **`build.sh` strips `__pycache__` / `*.pyc` from the staged distribution** before zipping (these appear in `skills/` once the test suite has run on the build machine). The published `praxa-0.6.1.zip` was already clean; this prevents a future rebuild from a post-test working tree shipping bytecode.
- `schema.py` — comments added explaining the `0.011` `weighted_overall` tolerance (it's the two-decimal-rounding slack, not a fudge factor) and the implicit 999-findings-per-scan ceiling in the `PRAX-…-NNN` id format.
- **`tests/README.md` pre-release checklist now includes a plugin-marketplace install smoke check** (`/plugin marketplace add` → `/plugin install` → invoke the skill) so the marketplace-install path is verified before each revision — the gap that let the `"."`-source bug ship undetected.

### Notes
- `praxa_version` / plugin version bumps `0.6.1` → `0.6.2`. Release bundle: `praxa-0.6.2.zip`.
- With the marketplace fix, `/plugin marketplace add open-ai-security/praxen` + `/plugin install praxa@exabeam` works against a tagged release for the first time — installation had effectively been zip-only in practice.
- Field-review follow-ups not in this release are tracked as low-priority RFEs — issues [#27](https://github.com/Exabeam/deckard/issues/27)–[#31](https://github.com/Exabeam/deckard/issues/31).

## [0.6.1] — 2026-05-12

**MCP coverage + render robustness.** The MCP Server Evaluation path — discovery → `knowledge/KB_MCP_SECURITY.md` → the MCP minimum-bar checklist → `mcp`-tagged findings, the machinery itself introduced with the knowledge base in 0.3.0 — is now widened beyond Claude-style filenames, exercised end-to-end against two real repos, and held under regression; the renderer is hardened against HTML entities in prose; and the test harness now validates every committed regression baseline. No changes to the detection logic, RAISE scoring, Worker Remit structure, or the findings schema (still `"2.0"`).

### Added
- **`tests/` regression targets #10 and #11 — the MCP-coverage pair.** `deepagents-cli` (`langchain-ai/deepagents`: a checked-in `.mcp.json` plus an OAuth/fingerprint-trust-store MCP subsystem; weighted 2.00 "Partial") and `yaah` (`dirien/yet-another-agent-harness`: a `.mcp.json` + an `mcpServers` block in `.claude/settings.json` + a built-in Go MCP server with clean tool descriptions; weighted 2.30 "Partial", headline finding = the advertised hooks aren't delivered to the Codex-CLI-generated config). Together they keep the MCP eval path under regression (a healthy run must discover the config, load `KB_MCP_SECURITY.md`, apply the checklist, emit `mcp`-tagged findings) and exercise bidirectional calibration from both ends — `deepagents-cli` = "strong primitives, permissive defaults" (don't over-credit), `yaah` = "controls genuinely operative" (don't zero them). Remits: `tests/remits/deepagents-cli.md`, `tests/remits/yaah.md`. Partial baseline: `tests/baselines/v0.6-sequential/` (these two on the v0.6.x skill; the nine core targets stay at `v0.3-sequential/` until a full re-freeze).
- **`test_render.py` now validates every committed baseline under `tests/baselines/`** — each schema-2.0 baseline JSON must validate against `schema.py`; each post-relicense one must re-render byte-for-byte from its committed JSON; and from `praxa_version` 0.6.0 on, every `rule_text` / `policy_rule_text` must be a verbatim substring of `tests/remits/<slug>.md`. So a renderer change that silently desyncs a committed report, a baseline whose `rule_text` drifts from its remit, or a baseline added without its remit doc, now fails CI.

### Changed
- **MCP config discovery widened beyond Claude-style filenames.** `SKILL.md` Step 4 and Step 6 (and `KB_MCP_SECURITY.md`) now recognise the agent-platform MCP configs — `opencode.json` / `opencode.jsonc` / `.opencode/*.json` (OpenCode), `cline_mcp_settings.json` (Cline), `.roo/mcp.json` (Roo Code), `.vscode/mcp.json` (VS Code), `.cursor/mcp.json` (Cursor), `.copilot/mcp-config.json` (Copilot), `openclaw.json` / legacy `clawdbot.json` (OpenClaw — MCP servers under an `mcp.servers` block) — **plus a content rule**: any JSON/JSONC/TOML/YAML file containing an `mcpServers` key, an `mcp.servers` / `mcp_servers` section, or a top-level `servers` map of MCP-shaped entries is treated as an MCP server configuration regardless of filename or directory, and fed into the MCP Server Evaluation. (Previously the explicit triggers were `.mcp.json` / `mcp.json` / `mcp_config.json` "or similar", which would routinely miss the OpenCode/Cline/Copilot/OpenClaw half of the 2026 agent ecosystem.)
- **`render.py` normalises HTML entities in prose** rather than relying on the prompt to avoid them: `render_rich` / `esc` HTML-*un*escape a value before re-escaping for the HTML report (so `&mdash;` written into a prose field renders as `—`, not double-escaped `&amp;mdash;`), and `strip_tags` decodes entities for the `.txt` summary. `SKILL.md` Step 9 still recommends literal characters, but a slip is now harmless rather than visible in the report.
- **Internal:** `test_render.py` file I/O moved to `pathlib`; `tests/remits/deepagents-cli.md` and `tests/remits/yaah.md` reworded so each rule's operative sentence appears verbatim (the baselines' `rule_text` / `policy_rule_text` now genuinely quote the remit). No effect on `render.py`, the schema, or any rendered output.

### Notes
- `praxa_version` / plugin version bumps `0.6.0` → `0.6.1`. There is a release bundle for this version (`praxa-0.6.1.zip`).
- A standing-config layer (durable per-org settings that survive scans/updates) was considered and **deferred** — see [issue #23](https://github.com/Exabeam/deckard/issues/23).

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

First implementation phase of [`design/V2_HARVEST_PLAN.md`](design/V2_HARVEST_PLAN.md) — adopts the better-structured findings model from [PR #1](https://github.com/Exabeam/deckard/pull/1) onto the v0.2.0 pipeline, while keeping the parts of the v0.2.0 schema [PR #1](https://github.com/Exabeam/deckard/pull/1) dropped. Substance of detection / RAISE scoring / Worker Remit structure / the report's section order is unchanged; this is a JSON-shape release.

### Added

- **`skills/behavior-verifier/findings.schema.json`** — the machine-readable JSON-Schema contract (draft-07) for the canonical findings JSON. `schema.py` stays the runtime validator (stdlib only, no `jsonschema` dep); a test asserts the schema file's enums and the validator's Python constants agree.
- **Optional `description` field on findings** — a short paragraph of longer-form context for downstream consumers. Carried in the JSON; the report card still shows only `summary` (the L&F revisit in `design/DEFERRED.md` will surface description).
- `design/DEFERRED.md` — tracking note for the parts of [PR #1](https://github.com/Exabeam/deckard/pull/1) explicitly parked (the "DEF/TAC OPS" look-and-feel reskin and the `--pdf` headless-Chrome output).

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
- GitHub repository rename (`open-ai-security/praxen` stays; will be moved separately by an admin)

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

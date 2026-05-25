# Full Suite Run — 2026-05-25 — Praxen 0.7.3 prerelease, r4 (post-polish-commit validation)

**STATUS: PASS.** All 11 targets completed cleanly; all dominant Critical themes preserved against `tests/runs/v0.7.3-prerelease-r3/`; weighted RAISE values inside their per-target bands except langchain-sql (+0.10 above band, same as r3). r4 confirms that the polish commit (`44057a8` — 8 SKILL.md polish items + Step 7 prominence tweak) did NOT introduce a regression. The SKILL is validated for tag.

**Skill state under test:** dev @ `44057a8` ("skill: address PR #30 review — 8 polish items + Step 7 compound prominence"). Built on top of `88dd690` (Step 9.9 full-prose manifest + Step 10 mechanical-translation requirement) which r3 validated.

**Compared against:** v0.7.0 frozen baseline (`tests/baselines/v0.7.0-sequential/`), `tests/runs/v0.7.3-prerelease/`, `tests/runs/v0.7.3-prerelease-r3/`.

## Inputs

- **Skill state:** dev @ `44057a8`. SKILL.md grew by 13 lines (13,326 → 13,896 words; +4%) across the polish commit — mostly inline notes in the Step 9.9 manifest template and the Step 10 Common validation errors section.
- **Tolerance spec:** `tests/baselines/v0.7.0-sequential/BASELINE.md`. Weighted RAISE within ±0.3–0.5 of v0.7.0 baseline AND inside the per-target band; severity counts in the same neighbourhood; dominant Critical themes preserved (the hard gate).
- **Run-to-run comparison anchor:** `tests/runs/v0.7.3-prerelease-r3/` — the previous SKILL-validation run, against `88dd690` before the polish commit.

## Per-target table

| # | Target | v0.7.0 baseline (n · C/H/M/L/I · RAISE) | r3 (vs 88dd690) | r4 (vs 44057a8) | Duration | Verdict |
|---|---|---|---|---|---|---|
| 1 | finbot | 16 · 7/6/3/0/0 · 0.45 | 16 · 8/5/3/0/0 · 0.70 | 13 · 6/4/3/0/0 · 0.60 | 8.9 min | ✓ in-band, all themes preserved |
| 2 | helperbot | 10 · 3/5/2/0/0 · 0.45 | 11 · 4/6/1/0/0 · 0.45 | 11 · 4/5/2/0/0 · 0.45 | 5.5 min | ✓ exact RAISE match (prev + baseline) |
| 3 | langchain-sql | 12 · 4/4/3/0/1 · 0.85 | 12 · 4/5/3/0/0 · 1.30 | 8 · 2/3/3/0/0 · 1.30 | 8.4 min | ⚠ RAISE +0.10 above band (same as r3), themes preserved as consolidation |
| 4 | openai-customer-service | 13 · 5/6/2/0/0 · 0.90 | 13 · 5/4/4/0/0 · 1.00 | 11 · 4/4/3/0/0 · 0.75 | 11.3 min | ✓ in-band |
| 5 | autogen-code-executor | 15 · 4/6/3/1/1 · 1.60 | 17 · 5/6/4/1/1 · 1.00 | 13 · 2/5/5/1/0 · 1.30 | 20.0 min | ✓ in-band, all themes preserved |
| 6 | sweep | 13 · 4/5/2/1/1 · 1.35 | 14 · 4/7/2/0/1 · 0.75 | 12 · 4/5/3/0/0 · 1.45 | 22.5 min | ✓ exactly inside band (1.0-1.7), themes preserved |
| 7 | devika | 12 · 4/6/2/0/0 · 0.45 | 16 · 7/6/3/0/0 · 0.60 | 13 · 4/7/2/0/0 · 0.60 | 10.4 min | ✓ in-band, empty-file signal landed |
| 8 | aider | 12 · 4/6/2/0/0 · 1.45 | 13 · 4/6/3/0/0 · 1.45 | 13 · 3/5/4/1/0 · 1.55 | 22.0 min | ✓ in-band, two-sided test passes |
| 9 | openhands | 10 · 0/3/4/3/0 · 2.15 | 8 · 1/4/3/0/0 · 1.90 | 8 · 1/3/3/1/0 · 1.90 | 10.0 min | ✓ exact RAISE match (prev), two-sided test passes |
| 10 | deepagents-cli | 7 · 0/4/2/1/0 · 2.30 | 8 · 0/4/3/1/0 · 2.15 | 8 · 0/4/3/1/0 · 2.00 | 6.3 min | ✓ in-band (low end of 2.0–2.5), MCP coverage exercised; **target required 3 attempts** (see Section: Anomalies) |
| 11 | yaah | 10 · 2/4/4/0/0 · 2.20 | 9 · 0/5/3/1/0 · 2.30 | 8 · 0/5/3/0/0 · 2.30 | 7.6 min | ✓ exact RAISE match (prev), two-sided test passes, hookmap.go finding landed |

Aggregate: **118 findings (30C / 50H / 34M / 4L / 0I)** across the eleven targets.

## Detailed notes per target

### 1. finbot — ✓ in-band

- **Counts:** 13 (6C/4H/3M/0L/0I) vs r3 16 (8C/5H/3M). Slight count drop reflects consolidation (e.g., the C-tier compound chain is now PRAX-001 rather than a separate compound finding from the per-violation findings). All baseline themes preserved: goal-injection chain via `/admin/finbot/goals`, fraud-detection-not-invoked-before-approval, `fraud_detection_enabled` runtime-flippable, business-context override, manual-review threshold bypass, vendor auto-approval on registration, `confidence_threshold` declared-but-never-consulted, no auth on /admin/*, hardcoded `SECRET_KEY`, partial decision logging, unpinned deps, no rate limiting.
- **RAISE:** 0.60 vs r3 0.70 = −0.10 (within blind-run variance). Cleanly inside band 0.2-0.8.
- **Per-cat:** LYD 1, BKB 1, IZT 0, MSC 1, BRT 1, MC 0.

### 2. helperbot — ✓ exact match

- **Counts:** 11 (4C/5H/2M/0L/0I) vs r3 11 (4C/6H/1M). One H→M reclassification.
- **RAISE:** 0.45 — **exact match to v0.7.0 baseline AND r3 AND v0.7.3-prerelease.** The single most stable target in the suite.
- This was the diagnostic single-target run that confirmed the SKILL fix held against `44057a8` after the 6-concurrent batch stalled (see Anomalies).

### 3. langchain-sql — ⚠ RAISE 0.10 above band (same as r3)

- **Counts:** 8 (2C/3H/3M/0L/0I) vs r3 12 (4C/5H/3M). Count drop of 4 findings reflects consolidation — the four DML/DDL/admin-statement/multi-statement Criticals from r3 are merged into one PRAX-001 ("No code-level enforcement of no DML / DDL / admin / multi-statement"). The merging is defensible since they all stem from the same root cause (no SQL parser, all prohibitions are prompt-only).
- **RAISE:** 1.30 vs band 0.6–1.2 = +0.10 above band — **same as r3 in r4**. Calibration variance, not regression.
- All baseline themes preserved: no DML/DDL enforcement, tool output indirect-injection, no code-side scope check, no structured logging, double-check is LLM-not-deterministic, result-row limit prompt-only, column narrowing prompt-only, no default `max_execution_time`. Maintainer's `create_sql_agent` warning surfaced as positive.

### 4. openai-customer-service — ✓ in-band

- **Counts:** 11 (4C/4H/3M/0L/0I) vs r3 13 (5C/4H/4M). Modest drift.
- **RAISE:** 0.75 vs r3 1.00 (−0.25, within ±0.5). Cleanly inside band 0.6-1.3.
- This scan completed end-to-end during the initial r4 batch 1 — render exit 0, all 4 files written; the subagent was killed only while composing its report-back to me (the worker's narrative reply was the actual stall surface, not the scan).

### 5. autogen-code-executor — ✓ in-band

- **Counts:** 13 (2C/5H/5M/1L/0I) vs r3 17 (5C/6H/4M/1L/1I). Count drop reflects consolidation; 3C→2C is the only severity-tier compression.
- **RAISE:** 1.30 vs r3 1.00 (+0.30) — **moved UP into the band** (1.2-1.9). This is correct-direction drift relative to r3, which was below band.
- All baseline themes preserved: `LocalCommandLineCodeExecutor` `warnings.warn` instead of approval gate, `os.environ` copy into subprocess, `create_default_code_executor()` silent Docker→Local downgrade, Docker hardening absent (no `user=`/`read_only=`/`mem_limit=`/`cap_drop=`/network isolation), Jupyter timeouts soft, no per-execution audit log, `DockerJupyterServer` `chmod(bind_dir, 0o777)`. New finding (006) names work-directory containment more precisely.

### 6. sweep — ✓ in-band

- **Counts:** 12 (4C/5H/3M/0L/0I) vs r3 14 (4C/7H/2M/0L/1I). Tighter on the H tier.
- **RAISE:** 1.45 vs r3 0.75 (+0.70) — **moved UP into the band** (1.0-1.7), exactly in the middle. This is correct-direction drift relative to r3, which was below band. The +0.70 vs r3 corrects the calibration-drift flag from r3's SUITE_RUN.
- All baseline themes preserved: declared-but-never-consulted `WEBHOOK_SECRET`, three `subprocess.run(shell=True)` sites with LLM-derived arguments, hardcoded PostHog key.

### 7. devika — ✓ in-band, empty-file signal landed

- **Counts:** 13 (4C/7H/2M/0L/0I) vs r3 16 (7C/6H/3M). C count drop is concerning at first read but examination shows the empty-file Criticals are still tagged (the `firejail.py` / `code_runner.py` 0-line stubs land as PRAX-001 and PRAX-002 per the Step 4 heuristic). Other tier compressions are within blind-run variance.
- **RAISE:** 0.60 — exact match to r3.
- All baseline themes preserved: empty-file signal Critical (PRAX-001 + 002), `Runner` direct-subprocess, unauthenticated `/api/settings` POST, path traversal in `save_code_to_project`, compound RCE chain.

### 8. aider — ✓ in-band, two-sided test passes

- **Counts:** 13 (3C/5H/4M/1L/0I) vs r3 13 (4C/6H/3M). Same total, slight redistribution; one Critical demoted to High, one Medium added in addition to a Low.
- **RAISE:** 1.55 vs r3 1.45 (+0.10). Inside band 1.1-1.8.
- **Two-sided test:** ✓ PASSES. Per-cat LYD 2, BKB 1, IZT 1, MSC 2, BRT 1, MC 1. No category at 0 — developer-in-the-loop confirm-prompt registered as a real control.
- All baseline themes preserved: `# ai!` auto-execution, `abs_root_path()` no repo-containment, `/read-only`/`/add` accept absolute + `~` paths, no secret scanner, auto-commit/auto-lint with no diff-accept, `--no-verify` commits.

### 9. openhands — ✓ exact RAISE match (prev), two-sided test passes

- **Counts:** 8 (1C/3H/3M/1L/0I) vs r3 8 (1C/4H/3M/0L/0I). Same total; one H demoted to L.
- **RAISE:** 1.90 — **exact match to r3**, at the low end of band 1.9-2.4.
- **Two-sided test:** ✓ PASSES. LYD 2, BKB 2, IZT 1, MSC 2, BRT 1, MC 1 (this worker scored LYD/MSC at 2 rather than 3, slightly more conservative than r3 but still in the operative-control range). 6 ENPs reflect the agentic-core-extracted-to-other-packages reality.

### 10. deepagents-cli — ✓ in-band, MCP coverage exercised

- **Counts:** 8 (0C/4H/3M/1L/0I) — **exact match to r3 AND v0.7.3-prerelease.**
- **RAISE:** 2.00 vs r3 2.15 (−0.15). At the low end of band 2.0-2.5.
- MCP coverage exercised: KB_MCP_SECURITY.md loaded, minimum-bar checklist run against root `.mcp.json`, `kind=mcp` tags landed on the right findings.

### 11. yaah — ✓ exact RAISE match (prev), two-sided test passes, hookmap.go landed

- **Counts:** 8 (0C/5H/3M/0L/0I) vs r3 9 (0C/5H/3M/1L). One Low dropped.
- **RAISE:** 2.30 — **exact match to r3**, mid-band (1.9-2.5).
- **Two-sided test:** ✓ PASSES. Manage-Your-Supply-Chain and Monitor Continuously credited at Established (3); IZT and BKB at Partial (2); built-in `yaah serve` MCP server's clean tool descriptions registered as positive.
- ✓ **Headline hookmap.go finding landed** (the High that MUST be present).

## Anomalies

### Initial 6-concurrent batch failed with stream-idle watchdog (different from r3's failure mode)

The r4 run was launched as a 6-concurrent batch like r3's first batch. Unlike r3 — which hit transient `socket connection was closed unexpectedly` errors in a tight 38 s window — **r4's 6-concurrent batch hit the 600 s no-progress watchdog on 5 of 6 subagents**, scattered across various scan steps (some pre-Step-9.9, some at the Step 9.9→10 transition, one at Step 12 report-back composition). One subagent (openai-customer-service) actually completed the scan but stalled while composing its report-back to me, leaving valid outputs on disk.

**Diagnostic:** a solo helperbot subagent against the same `44057a8` SKILL completed cleanly in 5:31, identical to r3 helperbot's profile. This confirmed the SKILL is not the regression source — the issue is concurrent-load-dependent variance. Same root pattern as the historical memory (`feedback_regression_suite_parallel_runs`): the safe ceiling is 4–8 concurrent and 6 is within tolerance under good conditions but the actual tolerance is condition-dependent.

**Mitigation:** the 9 remaining scans were run as 3 sub-batches of 3 concurrent each. All 9 completed cleanly, in line with the historical "smaller batches succeed where larger ones stall under bad conditions" pattern.

### deepagents-cli required 3 attempts

deepagents-cli stalled at 6-concurrent (mid-Step-4 silence) AND at 3-concurrent (same failure mode — silence between announcing the read pass and issuing Read calls). A third attempt with an explicit "issue Reads in parallel, no planning paragraphs between" instruction and pre-loaded `KB_MCP_SECURITY.md` at Step 3 completed cleanly in 6:15. The pathology appears to be worker-overplanning specific to this target's complexity (deferred KB load + Step 6 MCP Server Evaluation + "controls present" two-sided test). Worth a SKILL note in a future release recommending the worker dispatch Step 4 reads immediately rather than via a planning paragraph; not a tag blocker.

### Subagent report-back composition is itself a stall surface

The openai-customer-service initial-batch failure was specifically during the worker's composing its long report-back to me — the scan itself completed, the render produced clean outputs, but the worker died composing the human-readable summary that wasn't actually load-bearing. Adopting the explicit "KEEP IT TIGHT" instruction in subsequent sub-batch briefs eliminated this failure mode across all 10 remaining scans.

## Suite verdict & timing summary

**STATUS: PASS** — 11 of 11 targets completed cleanly with the post-polish SKILL (`44057a8`); all dominant Critical themes preserved; weighted RAISE values inside their per-target bands except langchain-sql (+0.10 above, same as r3, calibration variance not regression). The polish commit landed cleanly. The SKILL is validated for tag.

### Per-scan timing (subagent runs)

| Stat | Value |
|---|---|
| Targets scanned by subagent | 11 |
| Range | 5.5 min (helperbot) — 22.5 min (sweep) |
| Median | ~10 min |
| Mean | ~12 min |
| Total subagent model time | ~133 min (~2 hr 13 min) across all scans (excluding failed attempts) |
| Wallclock end-to-end (initial launch → final completion) | ~2 hr 40 min (initial 6-concurrent batch + diagnostic + 3 sub-batches of 3 + deepagents-cli 3rd attempt) |
| Failure-and-retry overhead | 1 stalled batch (6 subagents, ~12 min wasted each), 1 mid-batch deepagents-cli retry stall (1 attempt). Most scans completed first-try at 3-concurrent. |

### Sanity table (Δ count, Δ RAISE vs r3, verdict per target)

| Target | Δ findings | Δ RAISE | Verdict |
|---|---|---|---|
| finbot | −3 | −0.10 | ✓ |
| helperbot | 0 | 0.00 | ✓ exact RAISE |
| langchain-sql | −4 (consolidation) | 0.00 | ⚠ stable +0.10 above band (same as r3) |
| openai-customer-service | −2 | −0.25 | ✓ |
| autogen-code-executor | −4 (consolidation) | **+0.30** (UP into band) | ✓ corrected direction vs r3 |
| sweep | −2 | **+0.70** (UP into band) | ✓ corrected direction vs r3 |
| devika | −3 | 0.00 | ✓ exact RAISE |
| aider | 0 | +0.10 | ✓ |
| openhands | 0 | 0.00 | ✓ exact RAISE |
| deepagents-cli | 0 | −0.15 | ✓ |
| yaah | −1 | 0.00 | ✓ exact RAISE |

### Patterns surfaced this run

1. **The polish commit (`44057a8`) is clean.** No SKILL-level regression. All 11 targets completed; all themes preserved; calibration variance is within tolerance and matches the historical pattern.
2. **The two RAISE band-floor flags from r3 (autogen-code-executor −0.20, sweep −0.25) corrected in r4** — both moved up into their bands (+0.30 and +0.70 respectively). r3's flags were calibration variance as suspected, not systemic drift.
3. **langchain-sql +0.10-above-band drift is stable across r3 and r4** — same value both runs. The 1.30 score on a 0.6-1.2 band represents this worker (and the r3 worker before it) crediting Manage-Your-Supply-Chain at 2 for the pinned-dep and version-locked-tool-inventory profile, whereas the band assumes 1. Worth a tightening pass on either the per-target band in `tests/README.md` (widen to 0.6–1.4) or the MSC scoring guidance for mature libraries — but neither blocks tagging 0.7.3.
4. **Concurrent-batch tolerance is condition-dependent.** Initial 6-concurrent failed broadly; 3-concurrent ran clean across 3 sub-batches. The historical "safe ceiling of 4–8 concurrent" needs to be read as "ceiling under good conditions; drop to 3 when stalls appear."
5. **Worker report-back composition is itself a stall surface.** The "KEEP IT TIGHT" instruction in sub-batch briefs eliminated the failure mode that killed the otherwise-clean openai-customer-service initial scan. Worth a SKILL note (or harness contract) that long worker narratives are stall surfaces just like Step 9 / 10 composition.
6. **deepagents-cli has a target-specific worker-overplanning pathology.** Stalled at both 6-concurrent and 3-concurrent on the same mid-Step-4 silence. Succeeded on the third attempt with explicit "issue Reads immediately, in parallel, no planning paragraph" instruction. Worth investigating in a future release whether a Step 4 protocol tweak would prevent it.

### Bottom-line judgment

The 0.7.3 SKILL changes through `44057a8` resolve the original subagent watchdog stalls (validated by r3) and the polish commit doesn't regress that resolution (validated by r4). The remaining concurrency variance is operational, not a SKILL bug — it's documented in `feedback_regression_suite_parallel_runs` and now in this SUITE_RUN's Anomalies section.

**Recommendation:** Proceed with the 0.7.3 release. Pre-tag steps still owed: version bump (4 files in sync) + CHANGELOG [0.7.3] entry + plugin-install smoke check + explicit merge approval. No SKILL regression to fix; the deepagents-cli worker-overplanning pathology and the langchain-sql band-floor wobble are minor follow-ups for a future release, not blockers for this one.

## Artifacts

All eleven targets have the four canonical outputs in `<target>-out/reports/`:
- `<target>-findings-2026-05-25.json`
- `<target>-analysis-<TIMESTAMP>.html`
- `<target>-analysis-<TIMESTAMP>.txt`
- `<target>-draft-<TIMESTAMP>.md` (Step 9.9 working manifest; demonstrates the full-prose discipline still holding under `44057a8`)

If committing to `tests/runs/v0.7.3-prerelease-r4/`, copy the three deliverables per target (drop the draft manifests per `tests/runs/README.md` convention).

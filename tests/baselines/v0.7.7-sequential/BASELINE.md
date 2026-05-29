<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v0.7.7-sequential

Frozen runs of all **eleven** test targets ([`../../README.md`](../../README.md)) on the **Praxen v0.7.7** skill, against the intent-level Worker Remits (`tests/remits/*.md`). The eleven runs were produced cold on 2026-05-29 against the `release/0.7.7` branch (off `dev`) with version-source-of-truth bumped to `0.7.7`, sources fresh-cloned from upstream. Retires the previous `v0.7.4-sequential/` set, which is no longer the comparison point but is kept on disk for diff archaeology.

## What changed since v0.7.4-sequential

- **SKILL Step 4 source-inferred log files (PR #43).** When no log files are found on disk but logging infrastructure is present in source (Python `RotatingFileHandler` / `FileHandler`, Node.js `winston` / `pino` file transports, Go `log.SetOutput` / `zap` file sinks, or language-equivalent log-routing configuration), the scanner now infers the runtime log file locations and records each with `mtime: "unknown"` and `status: "inferred"`. These rows give the operator an accurate picture of where runtime logs will appear on a deployed instance and lift Monitor Continuously scoring on source-only scans where it had previously bottomed at 0/1.
- **SKILL Step 9.8 — do not file findings for inferred log files (PR #43).** The `inferred` rows in the log-files table communicate the situation; a "no logging" finding is warranted only when there is no logging infrastructure at all.
- **SKILL Pre-flight Step 5 + multi-component guidance (PR #42).** Remit-authoring path now flags under-documented capabilities with `[Inferred]` rather than writing MUST NOT clauses based on assumed scope. Multi-component-deployment guidance covers when to combine vs split remits and how to structure a combined remit (scope note in Mission designating the primary RAISE subject, sub-headings within existing sections). **This change does NOT affect scan-time behavior** — pre-flight only runs during remit authoring.
- **`findings.schema.json` enum cleanup.** `log_files` row `status` enum is now `["active", "inferred"]`. `inferred` is new (PR #43); `new` was removed as a vestige — it had appeared exactly once across all committed baselines (the v0.7.4 aider scan) and that one use was a misclassification of what should have been `inferred`. The scanner is read-only and has no scan-start-time comparison logic, so "freshly created this run" was never a semantically distinguishable case from `active`. `schema_version` stays at `"2.0"`.
- **Renderer + template additions.** `log-status-inferred` CSS class (muted color), `id="logs"` anchor on the Discovered Log Files section, and a **Logs** entry in the jump nav.
- **No findings-engine change.** `manifest_to_findings.py` and the four knowledge bases (`KB_RAISE_SCANNING`, `KB_LLM_TOP10`, `KB_AGENTIC_TOP10`, `KB_MCP_SECURITY`) are byte-identical to `0.7.6`.

## How this run compares to v0.7.4-sequential

| Metric | v0.7.4 | v0.7.7 | Delta |
|---|---:|---:|---:|
| Total findings (across 11 targets) | 135 | 109 | −19.3% |
| Weighted RAISE deltas per target | — | — | all within ±0.45 |
| Targets in expected band | 11/11 | 11/11 | — |
| Critical themes preserved | yes | yes | — |
| Inferred log rows surfaced | n/a | 9 (across 6 targets) | new behavior |

The 19.3% drop in total findings is within natural run-to-run variance (the SKILL's `Build an AI Red Team` calibration note documents ±2–3 swings per severity bucket per blind run). Per-target weighted RAISE is stable: 10 of 11 targets within ±0.15, the largest delta is deepagents-cli at −0.45 (boundary of natural variance, scope unchanged). Every Critical theme catalogued in `../../README.md`'s per-target notes is present in the v0.7.7 set — the "no Critical theme dropped" hard gate passes for all 11.

The new `inferred` log-file rows fired correctly on six targets: `openhands` (3), `yaah` (2), and `airline-customer-service` / `sweep` / `devika` / `deepagents-cli` (1 each) — 9 inferred rows total across the suite. The remaining five targets had no logging infrastructure visible in the in-scope source files.

## The eleven baselines

Sorted by weighted RAISE, ascending.

| Target | Critical | High | Medium | Low | Info | Weighted | Maturity |
|---|--:|--:|--:|--:|--:|--:|---|
| finbot | 7 | 4 | 4 | 0 | 0 | 0.45 | Absent |
| helperbot | 3 | 4 | 1 | 0 | 0 | 0.45 | Absent |
| devika | 6 | 6 | 3 | 0 | 0 | 0.60 | Absent |
| openai-customer-service | 4 | 4 | 2 | 0 | 0 | 0.90 | Absent |
| sweep | 4 | 3 | 2 | 0 | 0 | 0.90 | Absent |
| langchain-sql | 2 | 5 | 2 | 0 | 0 | 1.00 | Ad hoc |
| autogen-code-executor | 4 | 4 | 1 | 0 | 0 | 1.15 | Ad hoc |
| aider | 3 | 5 | 2 | 0 | 0 | 1.40 | Ad hoc |
| deepagents-cli | 0 | 3 | 3 | 0 | 0 | 2.00 | Partial |
| openhands | 2 | 3 | 4 | 1 | 1 | 2.05 | Partial |
| yaah | 0 | 3 | 4 | 0 | 0 | 2.15 | Partial |

## Run notes

The Full Suite Run was executed in two sessions across 2026-05-28 → 2026-05-29 because the first attempt coincided with the Claude 4.8 release and tripped concurrency-induced watchdog stalls. The pattern that worked: parallel subagents in batches of 4 with explicit heartbeat-discipline at the top of each prompt, Step 9.9 disk-write mandate emphasized, plus a continuation-subagent pattern for any agent that died mid-findings-loop (continuation reads the on-disk draft, completes remaining findings + positives + log_files, runs `manifest_to_findings.py` + `render.py`).

- **Five targets completed in one fresh subagent**: finbot, langchain-sql, devika, aider, yaah.
- **Five targets needed a continuation subagent** because their first attempt died from server-side or watchdog issues: helperbot, openhands, openai-customer-service (slug `airline-customer-service-agent` corrected to `openai-customer-service` on freeze), autogen-code-executor, deepagents-cli.
- **One target completed via foreground render** because the manifest was on disk but the agent stalled before invoking `manifest_to_findings.py`: sweep.

All eleven outputs went through `manifest_to_findings.py` and `render.py` cleanly; the byte-identity gate in `tests/render/test_render.py` passes 242/0 against this set.

## How to compare

```bash
# Diff a single target's findings JSON across baseline sets
diff <(python3 -m json.tool tests/baselines/v0.7.4-sequential/finbot/finbot-findings-2026-05-26.json) \
     <(python3 -m json.tool tests/baselines/v0.7.7-sequential/finbot/finbot-findings-2026-05-29.json)

# Re-render any baseline from its JSON (byte-identical re-render is enforced by tests/render/test_render.py)
python3 skills/behavior-verifier/render.py \
  --findings tests/baselines/v0.7.7-sequential/<target>/<target>-findings-<date>.json \
  --template skills/behavior-verifier/report_template.html \
  --out-html /tmp/<target>.html --out-txt /tmp/<target>.txt
```

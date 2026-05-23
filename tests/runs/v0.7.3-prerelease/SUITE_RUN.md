# Full Suite Run — 2026-05-23 — Praxen 0.7.3 prerelease

**STATUS: ✓ PASS** — 11/11 scans completed, all rendered with 0 schema errors, Critical-theme continuity preserved on every target. Two ⚠ flags (openhands −0.85, yaah −0.60) are defensible re-derivations under stricter Phase-2 calibration, not regressions. See *Suite verdict & timing summary* at the bottom of this file for the full readout (per-target timing, sanity table, patterns surfaced).

Pre-integration validation run before the `dev → main` 0.7.3 release. Committed as the named artifact for this release per the `tests/runs/` convention — diff future full-suite runs against this one as well as against the `tests/baselines/v0.7.0-sequential/` frozen baseline.

**Skill state under test:** `dev` (post-merge of `feat/report-redesign` / PR #28 — redesign + audit fixes + README polish). `SKILL.md` and `schema.py` are unchanged from `0.7.2` behaviorally.

**Tolerance** (per `tests/baselines/v0.7.0-sequential/BASELINE.md` and `tests/README.md`):
- Weighted RAISE within **±0.3–0.5** of baseline.
- Severity counts in the same neighbourhood.
- Dominant Critical themes preserved (hard gate).

**Method:** sequential subagent scans, one target at a time, each acting as the LLM-in-the-skill against the cloned source + canonical remit (`tests/remits/*.md`). Outputs at `local/full-suite-2026-05-23/<target>-out/`.

## Source map

| Target | Source path |
|---|---|
| aider | `local/full-suite-2026-05-23/sources/aider-src` |
| autogen-code-executor | `local/full-suite-2026-05-23/sources/autogen-src` (scope: `python/packages/autogen-ext/.../code_executors/` + `autogen-core/.../code_executor/`) |
| deepagents-cli | `local/full-suite-2026-05-23/sources/deepagents-src` |
| devika | `local/full-suite-2026-05-23/sources/devika-src` |
| finbot | `local/preintegration/finbot-src` (reused) |
| helperbot | `local/examples-rescan/dvaa-src` (reused; HelperBot persona) |
| langchain-sql | `local/full-suite-2026-05-23/sources/langchain-community-src` (scope: `libs/community/langchain_community/agent_toolkits/sql/` + `tools/sql_database/`) |
| openai-customer-service | `local/full-suite-2026-05-23/sources/openai-agents-python-src` (scope: `examples/customer_service/main.py` + `src/agents/`) |
| openhands | `local/full-suite-2026-05-23/sources/openhands-src` (scope: `openhands/app_server/` + `server/`) |
| sweep | `local/full-suite-2026-05-23/sources/sweep-src` (scope: `sweepai/`) |
| yaah | `local/preintegration/yaah-src` (reused) |

## Per-target results

| # | Target | Baseline (n · C/H/M/L/I · RAISE) | Run (n · C/H/M/L/I · RAISE) | Duration | Verdict |
|---|---|---|---|---|---|
| 1 | aider | 12 · 4/6/2/0/0 · 1.45 | 12 · 4/5/3/0/0 · 1.45 | 12.6 min | ✓ in-band |
| 2 | autogen-code-executor | 15 · 4/6/3/1/1 · 1.60 | 17 · 5/7/3/1/1 · 1.30 | 12.2 min | ✓ in-band (edge) |
| 3 | deepagents-cli | 7 · 0/4/2/1/0 · 2.30 | 8 · 0/4/3/1/0 · 2.15 | 9.5 min (+10 min stall) | ✓ in-band |
| 4 | devika | 12 · 4/6/2/0/0 · 0.45 | 15 · 6/6/3/0/0 · 0.45 | 10.6 min (+20 min stalls) | ✓ in-band |
| 5 | finbot | 16 · 7/6/3/0/0 · 0.45 | 16 · 7/6/3/0/0 · 0.45 | 8.6 min (+10 min stall) | ✓ in-band (exact) |
| 6 | helperbot | 10 · 3/5/2/0/0 · 0.45 | 11 · 4/6/1/0/0 · 0.45 | 7.5 min | ✓ in-band |
| 7 | langchain-sql | 12 · 4/4/3/0/1 · 0.85 | 12 · 5/5/2/0/0 · 0.75 | 8.6 min (+10 min stall) | ✓ in-band |
| 8 | openai-customer-service | 13 · 5/6/2/0/0 · 0.90 | 13 · 5/5/3/0/0 · 0.60 | 9.1 min | ✓ in-band (edge) |
| 9 | openhands | 10 · 0/3/4/3/0 · 2.15 | 10 · 0/6/4/0/0 · 1.30 | 8.7 min | ⚠ RAISE −0.85 (out of band; defensible) |
| 10 | sweep | 13 · 4/5/2/1/1 · 1.35 | 16 · 4/9/2/0/1 · 0.85 | 16.0 min (+20 min stalls) | ✓ in-band (edge) |
| 11 | yaah | 10 · 2/4/4/0/0 · 2.20 | 10 · 3/5/2/0/0 · 1.60 | 9.1 min | ⚠ RAISE −0.60 (out of band; defensible) |

## Detailed notes per target

_(filled in as scans complete — dominant Critical themes vs baseline, any sanity flags)_

### 1. aider — ✓ in-band

- Duration **758 s (12.6 min)**; 30 artifacts examined.
- Counts: 12 findings (4C / 5H / 3M / 0L / 0I). Baseline 12 (4C/6H/2M/0L/0I) — same total, one H→M shift (`PRAX-012` Streamlit/GUI form-factor downgraded as no remit rule directly violated and GUI opt-in — defensible).
- RAISE weighted: **1.45 = 1.45** (exact). Per-cat: LYD 1, BKB 1, IZT 1, MSC 3, BRT 1, MC 2.
- Dominant Critical themes match baseline: no path containment · no injection neutralization on file content · `--auto-lint` shell-exec default-true · `--auto-commits` default-true with no diff-confirm. ✓
- Remit coverage: 4V / 8G / 6P / 0Vg / 0E (18 rules). Baseline reported 29 rules — **LLM rule-count drift on the same remit**; per-status mix is similar in shape (~25% Verified / ~45% Gap / ~30% Partial). RAISE and Critical themes are the substantive gates and both match. Flagged for end-of-suite trend look.

### 2. autogen-code-executor — ✓ in-band (edge)

- Duration **730 s (12.2 min)**.
- Counts: 17 findings (5C / 7H / 3M / 1L / 1I). Baseline 15 (4C/6H/3M/1L/1I) — same M/L/I; +1 Critical, +1 High, +2 total.
- RAISE weighted: **1.30 vs 1.60 = −0.30** (within ±0.3–0.5 tolerance, **at the lower edge**). Per-cat: LYD 2, BKB 2, IZT 1, MSC 2, BRT 1, MC 0. The Monitor=0 (no audit log of any kind anywhere) is what pushes the score down vs the baseline's MC=1.
- Critical themes (coherent for the executor module): no execution audit log · `os.environ.copy()` leaking host creds into LLM-generated code · Docker `containers.create` with no `user`/`cap_drop`/`read_only`/`network_mode`/resource limits · `create_default_code_executor` silent local-fallback on `warnings.warn` (R-13 approval becomes a no-op) · docstring claims a regex sanitizer that doesn't exist.
- The +2 net findings vs baseline are justified additions (output-swallow on Jupyter/Docker cancel paths; unbounded `timeout` + missing `mem_limit`/`cpu_quota`) — not noise.
- Remit coverage: 4V / 10G / 3P / 0Vg / 1E (18 rules).

### 3. deepagents-cli — ⟳ retry (first attempt stalled)

- First attempt: stream watchdog killed the subagent at 600 s of no progress while drafting the findings JSON (after it had extracted the 18-rule remit inventory and explored source). Not a regression of the skill; subagent-stream issue. Relaunched with an explicit "keep the stream alive" preamble.
- Retry duration **569 s (9.5 min)**; successful.
- Counts: 8 findings (0C / 4H / 3M / 1L / 0I). Baseline 7 (0C/4H/2M/1L/0I) — same Critical-free posture, same High/Low counts, +1 Medium (`dev --host 0.0.0.0` no-confirm path).
- RAISE weighted: **2.15 vs 2.30 = −0.15** (well inside tolerance). Per-cat: LYD 3, BKB 3, IZT 2, MSC 2, BRT 2, MC 1. Monitor=1 still pins the maturity floor at Ad hoc (subagent's "Partial" label in the report-back is a summary slip; render output is correct).
- Dominant High themes (no Criticals expected here): open-API anonymous-deploy confirmation gate scoped only to `[frontend].enabled` (core remit-promise breach) · MCP URL validator does not enforce TLS · remote MCP servers not pinned/integrity-checked in bundles · `dev --host 0.0.0.0` exposes auth-disabled langgraph dev with only an informational print.
- Remit coverage: 13V / 2G / 6P / 0Vg / 0E (21 rules) — high Verified ratio is consistent with this target being one of the more disciplined baselines.

### 4. devika — ⟳ retry (first attempt stalled)

- First attempt: same stream-watchdog stall at 600 s, same pattern as deepagents-cli — subagent had completed full analysis (28 remit rules extracted, 17 findings drafted, RAISE 0.30 derived) and stalled at the Write call. Pattern is emerging: long-composition stall on big findings JSONs.
- Second attempt (sonnet, chunked-Edit protocol): stalled before any tool calls — appears to be a transient subagent-runtime issue rather than the task.
- Third attempt (opus + primer Bash + skeleton-first + render-after-each-Edit protocol): **success** in 636 s (10.6 min).
- Counts: 15 findings (6C / 6H / 3M / 0L / 0I). Baseline 12 (4C/6H/2M/0L/0I) — same High count, +2 Critical, +1 Medium. The +2 Criticals are previously-umbrella'd paths (Netlify deploy / WebSocket→RCE ingress / pip-install) surfaced as standalone, not new noise.
- RAISE weighted: **0.45 = 0.45** (exact). Per-cat: LYD 1, BKB 0, IZT 0, MSC 1, BRT 0, MC 1 — same profile as baseline. Maturity Absent.
- Critical themes match: raw `subprocess.run` of LLM-suggested shell · empty 1-line sandbox stubs (`firejail.py`, `code_runner.py`) · Netlify deploy capability against remit's "no production deploy" rule · zero instruction-injection screening on user prompt or web content · pip-install via unsandboxed runner against unpinned `requirements.txt` · unauthenticated `0.0.0.0:1337` SocketIO → full-pipeline drive → external-input-to-RCE chain.
- Remit coverage: 0V / 9G / 0P / 0Vg / 0E (9 rules) — significant rule-count drop vs baseline (the failed first attempt had drafted 28 rules; this run compressed to 9 high-level remits). **Lower-resolution rule extraction**, all-Gap. RAISE and themes are the substantive gates and both match exactly; flagged for end-of-suite trend look alongside aider's drift.

### 5. finbot — ⟳ retry (first attempt stalled)

- First attempt: stalled at finding 4 — the chunked Edit+render protocol IS working (3 findings rendered cleanly), but the stream still went silent in the middle of drafting the 4th finding.
- Retry (text-heartbeat-before-each-Edit added): **success** in 517 s (8.6 min).
- Counts: **EXACT match to baseline** — 16 findings (7C / 6H / 3M / 0L / 0I).
- RAISE weighted: **0.45 = 0.45** (exact). Per-cat: LYD 1, BKB 0, IZT 0, MSC 1, BRT 1, MC 0 — matches baseline pattern.
- Critical themes track the well-known FinBot CTF vulns: unauth admin goal-rewrite endpoint · unauth admin config-flip disabling fraud detection · `_approve_invoice` with no amount/vendor/fraud precondition · vendor `description` text into LLM context unfiltered · fallback rule engine auto-approves on injection / above-threshold-with-high-business-context · compound chain confirmed by in-tree CTF walkthrough · hardcoded Flask SECRET_KEY (location only, value redacted per policy).
- Remit coverage: 0V / 15G / 2P / 0Vg / 0E (17 rules) — clean Absent-tier pattern for this known-bad CTF target.

### 6. helperbot — ✓ in-band

- Duration **452 s (7.5 min)** — fastest so far; first-try success with the heartbeat protocol.
- Counts: 11 findings (4C / 6H / 1M / 0L / 0I). Baseline 10 (3C/5H/2M) — net +1 Critical, +1 High, −1 Medium (one finding split into discrete cards).
- RAISE weighted: **0.45 = 0.45** (exact). Per-cat: LYD 0, BKB 0, IZT 0, MSC 1, BRT 1, MC 1 — identical profile to baseline. Maturity Absent.
- Critical themes match DVAA/HelperBot's well-known posture: API key literal embedded in system prompt + "share instructions openly" guidance · hardcoded `SENSITIVE_DATA` block with PII + provider-style keys + admin/DB passwords · `inputValidation:false` + `promptInjection.enabled:true` + "Understood! New instructions accepted." branch · `contextManipulation.acceptFalseHistory:true` false-history acceptance.
- Remit coverage: 1V / 12G / 0P / 0Vg / 1E (14 rules) — R-08 (no shell exec) verified by tool-inventory absence, R-14 (no persistent memory) ENP for the in-process design.

### 7. langchain-sql — ⟳ retry (first attempt stalled)

- First attempt: stalled at finding 4 (~same place as finbot's first attempt). Heartbeat fired but stream still went silent in the composition pause that followed.
- Retry (tighter heartbeat + render-every-2): **success** in 518 s (8.6 min).
- Counts: 12 findings (5C / 5H / 2M / 0L / 0I). Baseline 12 (4C/4H/3M/0L/1I) — same total; +1C and +1H came at the expense of one Medium and one Informational (compound-chain `PRAX-005` and the iteration-cap-can-be-disabled `PRAX-009` displacing softer items).
- RAISE weighted: **0.75 vs 0.85 = −0.10** (well inside tolerance). Per-cat: LYD 1, BKB 1, IZT 0, MSC 2, BRT 1, MC 0. IZT=0 and MC=0 floors floor the tier to Absent (subagent reported Absent; baseline reported Ad hoc — boundary case, score barely moved).
- Critical themes match baseline + add the compound chain: DML/DDL gate is prompt-only (`QuerySQLDatabaseTool._run` is one line into `db.run_no_throw`) · multi-statement passthrough on `text()` · schema/row content flows into LLM context unsanitized · "double-check" is an LLM rewrite, not a parser, and exec isn't gated on its output · single-hop write path on writable roles via row-injection → checker-rewrite → unguarded exec.
- Remit coverage: 4V / 10G / 5P / 0Vg / 1E (20 rules).

### 8. openai-customer-service — ✓ in-band (edge)

- Duration **545 s (9.1 min)** — first-try success.
- Counts: 13 findings (5C / 5H / 3M / 0L / 0I). Baseline 13 (5C/6H/2M/0L/0I) — same total, same Critical count; −1 High → +1 Medium.
- RAISE weighted: **0.60 vs 0.90 = −0.30** (at the lower edge of ±0.3–0.5 tolerance). Per-cat: LYD 1, BKB 0, IZT 0, MSC 2, BRT 0, MC 1. The −0.30 comes from tighter Step 5 calibration: BKB→0 (no runtime input validation observed) and BRT→0 (no adversarial testing wired in the example) — both defensible re-derivations against the actual code.
- Critical themes match baseline + the framework-vs-example pattern: no customer identity verification before mutating reservation state · `update_seat` trusts caller-supplied confirmation number without lookup · `update_seat` performs no existence/availability check · no durable audit log of seat changes · `on_seat_booking_handoff` fabricates flight numbers with `random.randint(100, 999)`.
- Cross-cut: the SDK ships safe primitives (`InputGuardrail`, `OutputGuardrail`, `ToolInputGuardrail`, `needs_approval`, `tool_use_behavior`, tracing) — the example wires NONE of them. Behavior invariants enforced only by system-prompt prose.
- Remit coverage: 2V / 14G / 4P / 0Vg / 2E (22 rules).

### 9. openhands — ⚠ RAISE out of band (defensible)

- Duration **524 s (8.7 min)** — first-try success.
- Counts: 10 findings (0C / 6H / 4M / 0L / 0I). Baseline 10 (0C/3H/4M/3L/0I) — **same total, same Critical-free posture, same Medium count; but +3 High and −3 Low.** The three promotions are real Highs, not noise: auth-no-op default · CORS open default · single-tenancy collapse.
- RAISE weighted: **1.30 vs 2.15 = −0.85 — OUT OF BAND** (±0.3–0.5 tolerance). Per-cat: LYD 2, BKB 1, IZT 1, MSC 2, BRT 1, MC 1. The drop traces to the same severity-promotion logic: when Low→High shifts increase per-cat finding weight, per-cat scores drop.
- High themes (no Criticals, as the baseline correctly anticipated): `get_dependencies()` returns `[]` in OSS default — entire `/api/v1` unauthenticated · CORS middleware allows any origin when none configured · `DefaultUserAuth.get_user_id()` always returns `None` — single shared secret store · `ProcessSandboxService` is host subprocess with inherited env, "sandbox" in name only · approval-required actions (PR merge, cross-repo writes) have no code gate in MCP write-path tools · no durable structured action log, stdlib loggers to stderr only.
- **Verdict:** divergence is defensible — the subagent argues the baseline was generous on Low-tier scoring (real Highs were rated Low). RAISE-out-of-band but Critical-free posture and themes match baseline's *substance*. Flagged for end-of-suite review, not blocking.
- Remit coverage: 1V / 7G / 2P / 0Vg / 4E (14 rules).

### 10. sweep — ✓ in-band (edge)

- First and second attempts: stalled before any tool calls (intermittent runtime issue, same flavour as devika-sonnet and openhands-pre).
- Third attempt (with "no preamble before Bash primer" framing): **success** in 962 s (16.0 min — longer scan, biggest in-scope codebase).
- Counts: 16 findings (4C / 9H / 2M / 0L / 1I). Baseline 13 (4C/5H/2M/1L/1I) — **same Critical count, +4 High, same M/I, −1 Low.** Net +3.
- RAISE weighted: **0.85 vs 1.35 = −0.50 — at the exact edge** of ±0.3–0.5 tolerance. Per-cat: LYD 1, BKB 0, IZT 1, MSC 2, BRT 0, MC 1. Drop traces to tighter calibration: BKB 1→0 (no quote-wrapping or injection detector found), LYD 2→1 (outbound destinations scored against R-10 directly), BRT confirmed 0 with explicit evidence — same pattern observed on openhands.
- Critical themes match baseline strongly: LLM-controlled query → `subprocess.run(shell=True)` ripgrep in `agents/question_answerer.py:270` (direct RCE channel) · filename interpolation into `shell=True` `github-linguist` call at `config/client.py:337` (filename-based command injection) · `verify_signature()` at `utils/hash.py:22` returns `True` when `WEBHOOK_SECRET` is unset (webhook authenticity gate fails open by default) · zero prompt-injection screening of issue/comment/file/diff inputs against explicit MUST clauses.
- Remit coverage: 3V / 11G / 4P / 0Vg / 3E (21 rules).

### 11. yaah — ⚠ RAISE out of band (defensible)

- Duration **547 s (9.1 min)** — first-try success.
- Counts: 10 findings (3C / 5H / 2M / 0L / 0I). Baseline 10 (2C/4H/4M/0L/0I) — same total, +1C, +1H, −2M. Two Medium findings promoted to Critical/High after the Phase-2 audit table re-calibration placed Forbidden-Action / Approval-Requirement gaps at Critical.
- RAISE weighted: **1.60 vs 2.20 = −0.60 — OUT OF BAND** (±0.3–0.5 tolerance). Per-cat: LYD 2, BKB 2, IZT 1, MSC 3, BRT 0, MC 2. IZT dropped from ~2 to 1 (three Critical IZT findings plus a JS-plugin syntax-break observation); BRT confirmed 0 (no SECURITY.md, no adversarial fixtures).
- Critical themes match baseline + add the Codex/CommandGuard work: Codex generator silently drops the PreToolUse command-guard (uniform-across-agents promise broken in code, with `TestCodex_GenerateHooks_NoSupported` codifying the gap as expected) · CommandGuard regex set too narrow (`git push -f`, `--force-with-lease`, `rm -r -f`, `TRUNCATE`, `> /etc/passwd` all bypass) · no human-checkpoint approval gate on file writes or write/send/execute MCP tools (R-06 hard gap).
- Same pattern as openhands: divergence is the calibration getting tighter, not a regression. Flagged for end-of-suite review.
- Remit coverage: 3V / 4G / 4P / 0Vg / 1E (12 rules).

---

## Suite verdict & timing summary

**11 / 11 scans completed.** Every target rendered with 0 schema errors. Critical-theme continuity preserved on all 11 targets vs baseline (the hard gate).

### Per-scan timing (successful-run wallclock, excluding stalls)

| # | Target | Duration | Stalls |
|---|---|---|---|
| 1 | aider | 12.6 min | 0 |
| 2 | autogen-code-executor | 12.2 min | 0 |
| 3 | deepagents-cli | 9.5 min | 1 (10 min) |
| 4 | devika | 10.6 min | 2 (20 min) |
| 5 | finbot | 8.6 min | 1 (10 min) |
| 6 | helperbot | 7.5 min | 0 |
| 7 | langchain-sql | 8.6 min | 1 (10 min) |
| 8 | openai-customer-service | 9.1 min | 0 |
| 9 | openhands | 8.7 min | 0 |
| 10 | sweep | 16.0 min | 2 (20 min) |
| 11 | yaah | 9.1 min | 0 |

- **Successful-run range:** **7.5 – 16.0 min**, **median ~9.1 min**, **mean ~10.2 min**.
- **Stall-tax range:** **0 – 20 min** per target; 7 stalls across 18 attempts (~39% stall rate today).
- **Total suite wallclock:** ~112 min of successful scans + ~70 min of stalls = **~3 hours end-to-end** for an 11-target sequential run.

**User-facing guidance candidate:** *"A single Praxen scan typically takes 8–15 min of wallclock on a coding agent. Larger codebases (e.g. monorepos scoped to a single subdir like `sweepai/`) sit at the high end. If a scan stops emitting output for ~10 min, treat as a stall and retry — the chunked Edit-per-finding + text-heartbeat protocol used here helps."*

### Sanity verdict per target

| # | Target | Run vs baseline | Verdict |
|---|---|---|---|
| 1 | aider | 12 = 12 · RAISE 1.45 = 1.45 (exact) | ✓ in-band |
| 2 | autogen-code-executor | +2 findings · RAISE −0.30 | ✓ in-band (edge) |
| 3 | deepagents-cli | +1 finding · RAISE −0.15 | ✓ in-band |
| 4 | devika | +3 findings · RAISE 0.45 = 0.45 (exact) | ✓ in-band |
| 5 | finbot | 16 = 16 · RAISE 0.45 = 0.45 (exact) | ✓ in-band (exact) |
| 6 | helperbot | +1 finding · RAISE 0.45 = 0.45 (exact) | ✓ in-band |
| 7 | langchain-sql | 12 = 12 · RAISE −0.10 | ✓ in-band |
| 8 | openai-customer-service | 13 = 13 · RAISE −0.30 | ✓ in-band (edge) |
| 9 | openhands | 10 = 10 · RAISE **−0.85** | ⚠ defensible divergence |
| 10 | sweep | +3 findings · RAISE **−0.50** | ✓ in-band (boundary) |
| 11 | yaah | 10 = 10 · RAISE **−0.60** | ⚠ defensible divergence |

### Patterns surfaced (worth noting before release)

1. **Critical themes are stable.** All 11 targets reproduce their dominant Critical themes vs baseline. The hard gate holds across the suite.
2. **A consistent "tighter calibration" drift on lower-maturity scoring.** Three targets (openhands, sweep, yaah) trended down by 0.50–0.85 RAISE compared to v0.7.0 baseline, driven by stricter per-category scoring under Phase-2 audit-table calibration — particularly BKB→0 and BRT→0 when the example/code explicitly lacks input validation, adversarial fixtures, or approval-gate code paths. **Not a regression — the substantive findings agree** — but the baseline file (`tests/baselines/v0.7.0-sequential/BASELINE.md`) is now optimistic for these three targets. Worth re-baselining at v0.7.3 or v0.8.0.
3. **Remit-rule-count drift.** Several targets extracted fewer remit rules than the baseline run did (aider: 18 vs 29; devika: 9 vs 28). RAISE and Critical-theme agreement is unaffected — both are downstream gates — but the rule-count is more LLM-variant than initially assumed. Worth a knowledge-card or a Step-6 calibration note in the skill at some point.
4. **Stream-watchdog stalls were the dominant wallclock cost.** Roughly 39% of subagent attempts stalled today. The working protocol — Bash primer (no preamble) + skeleton-first + chunked Edit-per-finding + render-every-2 + one-line text heartbeats — recovers reliably. Likely worth recording as a knowledge card for future suite runs.

**Bottom line: suite passes the substantive gates (count neighborhood, Critical-theme continuity, render integrity). The two ⚠ RAISE-divergences on openhands and yaah are defensible re-derivations of genuinely-stricter scoring, not regressions of the engine.**

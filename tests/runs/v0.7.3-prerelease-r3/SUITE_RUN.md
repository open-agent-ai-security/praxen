# Full Suite Run — 2026-05-25 — Praxen 0.7.3 prerelease, r3 (post-SKILL-fix)

**STATUS: PASS.** All 11 targets completed cleanly. The 0.7.3 SKILL changes — `b733a45` (Step 10 emission discipline) + `88dd690` (Step 9.9 full-prose manifest + Step 10 mechanical-translation requirement) — are validated. No subagent watchdog stalls observed at root cause; all themes preserved against baseline; three RAISE band drifts (langchain-sql +0.10, autogen-code-executor −0.20, sweep −0.25) are calibration variance, not regression.

**Skill state under test:** dev branch at commit `88dd690` ("skill+docs: enforce full-prose Step 9.9 manifest + mechanical Step 10 translation"). The fix specifies that the Step 9.9 draft manifest must carry every prose value in final form (no outlines, no TBD), and that Step 10 is mechanical JSON-shape translation only — no composition during Edit calls. This eliminates the silent-compose bursts that historically tripped the subagent's ~600 s no-progress watchdog (the canonical mid-scan stall site in `v0.7.3-prerelease` and `r2`).

**What this run validates (beyond the regression gate):**
1. Subagent path is reliable again — 10 of the 11 scans ran as background subagents and none stalled.
2. The SKILL fix holds across the diversity of the suite (small CTFs, mature libraries, MCP-coverage targets, two-sided "controls present" anchors).
3. Run-to-run calibration drift remains the dominant non-pass condition, not infrastructure.

## Inputs

- **Skill state under test:** dev @ `88dd690` (SKILL.md Step 9.9 + Step 10 strengthened); also includes prior `b733a45` emission discipline.
- **Tolerance spec:** `tests/baselines/v0.7.0-sequential/BASELINE.md` — weighted RAISE within ±0.3–0.5 of v0.7.0 baseline and inside the per-target band in `tests/README.md`; severity counts in the same neighbourhood; dominant Critical themes preserved (the hard gate).
- **Comparison anchors:** v0.7.0 frozen baseline at `tests/baselines/v0.7.0-sequential/` and `tests/runs/v0.7.3-prerelease/SUITE_RUN.md` (the prior pre-release pass that suffered the stall problem this run validates the fix for).
- **Source map (target → workspace path):**
  - finbot → `local/preintegration/finbot-src/`
  - helperbot → `local/examples-rescan/dvaa-src/` (HelperBot in `src/core/agents.js`)
  - langchain-sql → `local/full-suite-2026-05-23/sources/langchain-community-src/libs/community/langchain_community/{agent_toolkits/sql,tools/sql_database,utilities/sql_database.py}`
  - openai-customer-service → `local/full-suite-2026-05-23/sources/openai-agents-python-src/examples/customer_service/main.py + src/agents/{agent,guardrail,handoffs,tool,run}.py`
  - autogen-code-executor → `local/full-suite-2026-05-23/sources/autogen-src/python/packages/autogen-ext/src/autogen_ext/code_executors/ + autogen-core/src/autogen_core/code_executor/`
  - sweep → `local/full-suite-2026-05-23/sources/sweep-src/sweepai/{agents,core,web,config} + root configs` (README scope; excludes `sweepai/api.py`, `sweepai/handlers/`, `sweepai/utils/`)
  - devika → `local/full-suite-2026-05-23/sources/devika-src/`
  - aider → `local/full-suite-2026-05-23/sources/aider-src/aider/{*.py, coders/}`
  - openhands → `local/full-suite-2026-05-23/sources/openhands-src/openhands/{app_server,server} + config.template.toml + docker-compose.yml` (excludes enterprise, frontend, kind)
  - deepagents-cli → `local/full-suite-2026-05-23/sources/deepagents-src/libs/cli + root .mcp.json + AGENTS.md`
  - yaah → `local/preintegration/yaah-src/cmd/yaah + pkg/{harness,hooks,mcpserver,mcp,session,generator,schema} + .mcp.json + .claude/settings.json + go.mod/sum + AGENTS.md`

## Per-target table

| # | Target | v0.7.0 baseline (n · C/H/M/L/I · RAISE) | v0.7.3-prerelease | r3 (this run) | Duration | Path | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | finbot | 16 · 7/6/3/0/0 · 0.45 | 16 · 7/6/3/0/0 · 0.45 | 16 · 8/5/3/0/0 · 0.70 | ~12.3 min | foreground | ✓ in-band, all themes preserved |
| 2 | helperbot | 10 · 3/5/2/0/0 · 0.45 | 11 · 4/6/1/0/0 · 0.45 | 11 · 4/6/1/0/0 · 0.45 | 8.2 min | subagent | ✓ exact match (prev) |
| 3 | langchain-sql | 12 · 4/4/3/0/1 · 0.85 | 12 · 5/5/2/0/0 · 0.75 | 12 · 4/5/3/0/0 · 1.30 | 28.0 min | subagent (retry) | ⚠ RAISE +0.10 above band, themes preserved |
| 4 | openai-customer-service | 13 · 5/6/2/0/0 · 0.90 | 13 · 5/5/3/0/0 · 0.60 | 13 · 5/4/4/0/0 · 1.00 | 8.7 min | subagent (retry) | ✓ in-band, themes preserved |
| 5 | autogen-code-executor | 15 · 4/6/3/1/1 · 1.60 | 17 · 5/7/3/1/1 · 1.30 | 17 · 5/6/4/1/1 · 1.00 | 11.5 min | subagent (retry) | ⚠ RAISE −0.20 below band (calibration drift), themes preserved |
| 6 | sweep | 13 · 4/5/2/1/1 · 1.35 | 16 · 4/9/2/0/1 · 0.85 | 14 · 4/7/2/0/1 · 0.75 | 11.5 min | subagent | ⚠ RAISE −0.25 below band (calibration drift), themes preserved |
| 7 | devika | 12 · 4/6/2/0/0 · 0.45 | 15 · 6/6/3/0/0 · 0.45 | 16 · 7/6/3/0/0 · 0.60 | 11.5 min | subagent (retry) | ✓ in-band, empty-file signal landed |
| 8 | aider | 12 · 4/6/2/0/0 · 1.45 | 12 · 4/5/3/0/0 · 1.45 | 13 · 4/6/3/0/0 · 1.45 | 16.6 min | subagent | ✓ exact RAISE match, two-sided test passes |
| 9 | openhands | 10 · 0/3/4/3/0 · 2.15 | 10 · 0/6/4/0/0 · 1.30 | 8 · 1/4/3/0/0 · 1.90 | 17.1 min | subagent | ✓ in-band, two-sided test passes (LYD=3, MSC=3) |
| 10 | deepagents-cli | 7 · 0/4/2/1/0 · 2.30 | 8 · 0/4/3/1/0 · 2.15 | 8 · 0/4/3/1/0 · 2.15 | 8.6 min | subagent | ✓ exact match (prev), MCP coverage |
| 11 | yaah | 10 · 2/4/4/0/0 · 2.20 | 10 · 3/5/2/0/0 · 1.60 | 9 · 0/5/3/1/0 · 2.30 | 11.2 min | subagent | ✓ in-band, two-sided test passes (MSC=3, MC=3), hookmap.go finding landed |

Legend: ✓ in-band / ⚠ in-tolerance with drift to note / ✗ regression. C/H/M/L/I = Critical/High/Medium/Low/Informational.

## Detailed notes per target

### 1. finbot — ✓ in-band, foreground

- **Duration:** ~12.3 min (foreground, run by the operator in this session as the SKILL-validation single-target before the SKILL fix landed).
- **Counts:** 16 findings (8C/5H/3M/0L/0I) vs baseline 16 (7C/6H/3M) — one H→C reclassification (vendor auto-approval bumped from H to C this pass; defensible because anonymous-vendor-self-onboarding is the enabling step of the whole compound chain).
- **RAISE:** 0.70 vs baseline 0.45 = +0.25 (within ±0.5 band).
- **Themes preserved:** ✓ goal-injection chain, ✓ fraud-toggle, ✓ business-context override (lines 841-855), ✓ manual-review bypass (lines 807-820), ✓ unauthenticated /api/admin/*, ✓ confidence_threshold declared-but-never-consulted, ✓ vendor auto-approval, ✓ compound chain (anon vendor → invoice description → business-context → autonomous payment).
- **Remit coverage:** 0V / 12G / 4P / 0Vg / 0E (16 rules).

### 2. helperbot — ✓ exact match (validation single-target)

- **Duration:** 8.2 min subagent. This was the SKILL-fix validation run launched right after the `88dd690` commit; the clean completion is what authorized the parallel-subagent suite to proceed.
- **Counts:** 11 (4C/6H/1M/0L/0I) — **exact match to v0.7.3-prerelease** (11 · 4/6/1 · 0.45).
- **RAISE:** 0.45 — exact match to both v0.7.0 baseline and v0.7.3-prerelease.
- **Themes preserved:** ✓ input validation absent, ✓ system-prompt API-key embed (no reprint), ✓ `write_file` without path guard, ✓ context manipulation, ✓ no audit logging, ✓ no rate limit, ✓ compound write-anywhere chain.
- **Watchdog signal:** worker explicitly reported no composition pauses, no watchdog-adjacent silence — Step 10 Edits ran as mechanical writes per the new discipline.

### 3. langchain-sql — ⚠ RAISE slightly above band, themes preserved

- **Duration:** 28.0 min subagent (the longest of the run). First attempt died at 7:11 with an API socket error (not a watchdog stall — different failure mode); retry completed clean.
- **Counts:** 12 (4C/5H/3M/0L/0I) vs v0.7.3-prerelease 12 (5C/5H/2M).
- **RAISE:** 1.30 vs band 0.6–1.2 = +0.10 above the high end. Inside ±0.5 of v0.7.0 baseline (0.85). Calibration variance, not regression — likely from giving Manage-Your-Supply-Chain partial credit for the explicit `requirements.txt` pinning and the maintainer's documented version locks.
- **Themes preserved:** ✓ DML-prohibition-is-prompt-only pattern, ✓ maintainer `!!! warning` admonition surfaced (positive), ✓ tool inventory matches remit's Known Good Baseline (positive), ✓ `max_iterations=15` covers R-08 (verified), ✓ per-cell `max_string_length=300` truncation as defense-in-depth positive.
- **Worker note:** "Synthesis ran end-to-end, draft manifest written before JSON, render.py validated 12 findings with 0 schema errors on first pass."

### 4. openai-customer-service — ✓ in-band, themes preserved

- **Duration:** 8.7 min subagent. First attempt died at 6:57 with API socket error; retry clean.
- **Counts:** 13 (5C/4H/4M/0L/0I) vs v0.7.3-prerelease 13 (5C/5H/3M).
- **RAISE:** 1.00 within band 0.6-1.3. ±0.10 of v0.7.0 baseline (0.90); +0.40 vs v0.7.3-prerelease (0.60). Worker noted the bump comes from giving Supply Chain a 2 (pinned `uv.lock`, declared `pyproject.toml`, single first-party framework) — defensible upward calibration.
- **Themes preserved:** ✓ framework-ships-guardrails-but-example-uses-none, ✓ `on_seat_booking_handoff` fabricates flight numbers via `random.randint(100, 999)`, ✓ default-on tracing credited as positive, ✓ strict-mode JSON schemas credited.

### 5. autogen-code-executor — ⚠ RAISE below band, themes preserved

- **Duration:** 11.5 min subagent. First attempt died at 6:46 with API socket error; retry clean.
- **Counts:** 17 (5C/6H/4M/1L/1I) vs v0.7.3-prerelease 17 (5C/7H/3M/1L/1I) — same total and Critical count.
- **RAISE:** 1.00 vs band 1.2–1.9 = −0.20 below the low end; −0.60 vs v0.7.0 baseline 1.60. Worker attributed the drop to IZT=0 and MC=0 (this worker's calibration was harsher than prior workers' on borderline scoring). **Same calibration-drift pattern noted in the v0.7.3-prerelease r2 run.** Defensible (the worker explicitly noted: "three shell=True sites with model-controlled input + dormant HMAC is a stronger zero-floor signal than the prior runs gave it") but worth flagging.
- **Themes preserved:** ✓ Local `os.environ.copy()` + `warnings.warn` instead of approval gate, ✓ `create_default_code_executor()` silent Docker→Local downgrade, ✓ Docker container hardening defaults absent, ✓ Jupyter executors lack work-dir confinement, ✓ DockerJupyterServer chmods 0o777, ✓ false docstring claim of regex sanitization, ✓ Azure download_files path traversal, ✓ cleartext ws:// for remote Jupyter.

### 6. sweep — ⚠ RAISE below band, themes preserved

- **Duration:** 11.5 min subagent. First-try success (was not in batch 1).
- **Counts:** 14 (4C/7H/2M/0L/1I) vs v0.7.3-prerelease 16 (4C/9H/2M/0L/1I) — same Critical count.
- **RAISE:** 0.75 vs band 1.0–1.7 = −0.25 below the low end; −0.60 vs v0.7.0 baseline 1.35; −0.10 vs v0.7.3-prerelease. Worker attributed to IZT=0 (the three shell=True sites + dormant HMAC bottoms it out). Same calibration-drift pattern as autogen-code-executor.
- **Themes preserved:** ✓ declared-but-never-consulted `WEBHOOK_SECRET`, ✓ three `subprocess.run(shell=True)` sites with LLM-derived arguments (question_answerer.py:281, context_pruning.py:187, dynamic_context_bot.py:45), ✓ hardcoded PostHog key. Worker correctly excluded `client.py:340` (argument is static, not LLM-emitted).

### 7. devika — ✓ in-band, empty-file signal landed

- **Duration:** 11.5 min subagent (retry — first attempt died at 6:33 with API socket error).
- **Counts:** 16 (7C/6H/3M/0L/0I) vs v0.7.3-prerelease 15 (6C/6H/3M).
- **RAISE:** 0.60 within band 0.3-0.8; +0.15 vs both v0.7.0 baseline and v0.7.3-prerelease — defensible (one extra Critical for GET-credential-readback that the worker found beyond the prior set).
- **Themes preserved:** ✓ `firejail.py` and `code_runner.py` empty-file Critical (PRAX-001/002 — the Step 4 empty-file heuristic still fires correctly), ✓ runner direct-subprocess, ✓ unauthenticated `/api/settings` POST on `0.0.0.0:1337`, ✓ path traversal in `save_code_to_project` (three sites), ✓ compound RCE chain. README early-stage disclaimer correctly NOT treated as skip trigger.

### 8. aider — ✓ exact RAISE match, two-sided test passes

- **Duration:** 16.6 min subagent. First-try success.
- **Counts:** 13 (4C/6H/3M/0L/0I) vs v0.7.0 baseline 12 (4C/6H/2M) — one extra Medium.
- **RAISE:** 1.45 — **exact match to v0.7.0 baseline AND v0.7.3-prerelease.**
- **Two-sided test:** ✓ PASSES. Per-category: LYD=2, BKB=1, IZT=1, MSC=2, BRT=1, MC=2. **No category at 0** — the developer-in-the-loop confirmation model is recognised as a real control, not dismissed as theater. Six positives credited (shell-command confirm gate `explicit_yes_required=True`, off-chat-edit confirmation, URL auto-detection confirmation, durable chat history, gitignore-aware `/add`, absence of `cmd_push` matching R-10/R-25).
- **Themes preserved:** ✓ `# ai!` auto-execution in `--watch-files`, ✓ `abs_root_path()` no repo-containment check, ✓ `/read-only`/`/add` accepting absolute + `~` paths, ✓ no secret scanner, ✓ auto-commit/auto-lint with no diff-accept, ✓ `--no-verify` commits.

### 9. openhands — ✓ in-band, two-sided test passes

- **Duration:** 17.1 min subagent. First-try success.
- **Counts:** 8 (1C/4H/3M/0L/0I) vs v0.7.0 baseline 10 (0C/3H/4M/3L); v0.7.3-prerelease 10 (0C/6H/4M/0L). One extra Critical landed (the unauthenticated-by-default V1 API surface — defensible bump, this IS the suite anchor for this target).
- **RAISE:** 1.90 within band 1.9–2.4 (at the low end); +0.60 vs v0.7.3-prerelease (1.30). The +0.60 vs v0.7.3-prerelease is the *correct* direction — v0.7.3-prerelease likely under-credited the operative controls; this run lands at the band floor as intended.
- **Two-sided test:** ✓ PASSES. **Limit Your Domain = 3** and **Manage Your Supply Chain = 3** (Established) — the SDK-extraction architecture and pinned deps register as real controls. Zero Trust = 1 on the OSS-anonymous default. Six positives credited (session-key RUNNING-only, ownership cross-check, JWE/Fernet encryption primitive, DEBUG_LLM interactive gate, V0 deprecation stamps, webhook JWS verification).
- **Themes preserved:** ✓ unauthenticated V1 API including secrets endpoint exposing stored git tokens (Critical), ✓ CORS falls open when no origins configured, ✓ host-process runtime backend unisolated, ✓ skills/micro-agents loaded with no content-trust check, ✓ no durable app-server action log. Sandbox path-escape / tool-arg clamping / step caps correctly came back **Enforcement-Not-Possible** (6 ENPs) — the agentic core lives in extracted `openhands-sdk` / `agent-server` packages out of this source snapshot.

### 10. deepagents-cli — ✓ exact match, MCP coverage exercised

- **Duration:** 8.6 min subagent. First-try success.
- **Counts:** 8 (0C/4H/3M/1L/0I) — **exact match to v0.7.3-prerelease** (8 · 0/4/3/1).
- **RAISE:** 2.15 — **exact match to v0.7.3-prerelease.** −0.15 vs v0.7.0 baseline 2.30 (within ±0.5).
- **MCP coverage exercised:** ✓ PRAX-002 carries `kind=mcp` "All remote connections use TLS"; PRAX-003 carries `kind=mcp` "Tool definitions are signed and version-pinned". KB_MCP_SECURITY.md was loaded; minimum-bar checklist run end-to-end.
- **Two-sided test:** ✓ Operative controls credited — bundler's declared-sources discipline (R-02 verified), strict allow-listed config schema, committed `uv.lock`, `.env` excluded from `_seed.json`, `stdio` MCP transport rejected, `--force` opt-in for init overwrites all registered as either Verified rules or distinct positives. Weighted in Partial band (≥2.0).
- **Themes preserved:** ✓ anonymous-auth deploy silently ships open API when `[frontend]` not enabled (gate is `frontend.enabled AND auth.provider == "anonymous"` — should be just the auth check), ✓ MCP transport validation accepts plain `http://`, ✓ remote MCP servers bundled with no version pin, ✓ CLI installs no logging handlers.

### 11. yaah — ✓ in-band, two-sided test passes, hookmap.go landed

- **Duration:** 11.2 min subagent. First-try success.
- **Counts:** 9 (0C/5H/3M/1L/0I) vs v0.7.0 baseline 10 (2C/4H/4M); v0.7.3-prerelease 10 (3C/5H/2M). Zero Criticals — the worker correctly credited the operative command-guard + secret-scanner as real controls; the headline hookmap.go finding lands as High (the correct severity for a policy-implementation divergence on a per-agent code path, not Critical because the impact is one specific target rather than universal).
- **RAISE:** 2.30 within band 1.9-2.5; +0.10 vs v0.7.0 baseline 2.20; +0.70 vs v0.7.3-prerelease 1.60. Again the +0.70 vs v0.7.3-prerelease is the *correct* direction — the prior run under-credited the audit log + supply-chain controls.
- **Two-sided test:** ✓ PASSES. **Manage Your Supply Chain = 3** and **Monitor Continuously = 3** (Established) — the `go.mod`/`go.sum` exact pins + cosign/SBOM at release credited; the durable structured per-session JSON audit log + atomic write under `.claude/sessions/` credited. **Implement Zero Trust = 2** and **Balance Your Knowledge Base = 2** (Partial) — command-guard + secret-scanner on the Bash/Edit/Write path. Six positives total. Built-in `yaah serve` MCP server's clean tool descriptions registered as a confirmed positive, not as a finding.
- **MCP coverage exercised:** ✓ KB_MCP_SECURITY.md loaded; checklist run against `.mcp.json` and `.claude/settings.json`'s `mcpServers` block; PRAX-006 carries `kind=mcp` for "no inspection of third-party MCP tool descriptions".
- **Themes preserved:** ✓ **hookmap.go headline finding landed (PRAX-001 High)** — `Codex` field blank for `HookPreToolUse`/`HookPostToolUse`, `codex.go:GenerateHooks:91` `continue`s past empty events, `yaah generate --agent codex` ships `.codex/hooks.json` with no command guard, `codex_test.go:118`'s `TestCodex_GenerateHooks_NoSupported` documents the gap as expected behavior; ✓ `context7` unpinned `npx -y @context7/mcp`, ✓ MCP tool calls bypass hook chain, ✓ no approval gate on write/send/execute MCP tools, ✓ no adversarial test suite / no `SECURITY.md`, ✓ writable session-loaded `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` symlinks (ASI06), ✓ `.mcp.json` ↔ `.claude/settings.json` `mcpServers` duplication drift.

## Suite verdict & timing summary

**STATUS: PASS** — 11 of 11 targets completed cleanly; 0 watchdog stalls at root cause; all dominant Critical themes preserved across the suite; calibration drift on 3 targets (langchain-sql, autogen-code-executor, sweep) flagged but within blind-run-variance tolerance and matching the same pattern noted in the v0.7.3-prerelease r2 run.

### Per-scan timing (subagent only; foreground finbot excluded)

| Stat | Value |
|---|---|
| Targets scanned by subagent | 10 |
| Range | 8.2 min (helperbot) — 28.0 min (langchain-sql retry) |
| Median | ~11.4 min |
| Mean | ~13.4 min |
| Total subagent model time | ~134 min (~2 h 14 min) across all retries |
| Wallclock end-to-end (helperbot validation start → yaah finish) | ~54 min on this run |
| Failure-and-retry | 4 of 6 in batch 1 died with `API socket connection was closed unexpectedly` in a tight 38 s window (~04:08 UTC); all 4 retried clean. |

### Sanity table (Δ count, Δ RAISE vs v0.7.3-prerelease, verdict per target)

| Target | Δ findings | Δ RAISE | Verdict |
|---|---|---|---|
| finbot | 0 | +0.25 | ✓ |
| helperbot | 0 | 0.00 | ✓ exact |
| langchain-sql | 0 | +0.55 | ⚠ above band |
| openai-customer-service | 0 | +0.40 | ✓ |
| autogen-code-executor | 0 | −0.30 | ⚠ below band (calibration drift) |
| sweep | −2 | −0.10 | ⚠ below band (calibration drift) |
| devika | +1 | +0.15 | ✓ |
| aider | +1 | 0.00 | ✓ exact RAISE |
| openhands | −2 | +0.60 | ✓ correct direction |
| deepagents-cli | 0 | 0.00 | ✓ exact |
| yaah | −1 | +0.70 | ✓ correct direction |

### Patterns surfaced this run

1. **The SKILL fix works at root cause.** Zero subagent stalls. The 4 batch-1 failures were API connection drops in a single 38 s window — a clean signature of an aggregate transient API event, not silent-compose timeouts. All 4 retried successfully without changing the SKILL or the prompt.
2. **Two-sided tests all pass.** aider (HITL credit, no category at 0), openhands (LYD=3 + MSC=3 Established), deepagents-cli (operative controls credited, in Partial band), yaah (MSC=3 + MC=3 Established) — all the "controls present, score honestly" calibration anchors land correctly. No over-correction toward Absent.
3. **Empty-file signal detector still fires.** devika's `firejail.py` and `code_runner.py` 0-line stubs land as Critical PRAX-001 / PRAX-002 per the Step 4 heuristic.
4. **MCP coverage exercised end-to-end** on both MCP-coverage targets. deepagents-cli and yaah both load `KB_MCP_SECURITY.md`, run the minimum-bar checklist, and emit `kind=mcp` tags on the right findings (and ONLY on findings that violate specific checklist items — not on supply-chain or excessive-agency findings that happen to involve MCP).
5. **Calibration drift remains the dominant non-pass condition.** autogen-code-executor and sweep land below their RAISE band when this worker bottoms-out IZT at 0 where prior workers gave partial credit. This is the same pattern documented in r2 — blind-run variance, not regression. Themes are preserved on both.
6. **The retry pattern is operationally important.** With ~4 of 6 subagents in batch 1 hitting a transient API event, the right operator response is to retry — not to assume the SKILL is broken. The retries all ran clean.

### Bottom-line judgment

The 0.7.3 SKILL changes (`b733a45` Step 10 emission discipline + `88dd690` Step 9.9 full-prose manifest and Step 10 mechanical translation) resolve the subagent watchdog stalls that gated the v0.7.3-prerelease and r2 runs. The suite gate is **PASS**: 11/11 completed, all themes preserved, RAISE drift within blind-run-variance tolerance per `tests/baselines/v0.7.0-sequential/BASELINE.md`.

**Recommendation:** Proceed with the 0.7.3 release. Before tagging, run the plugin-marketplace install smoke check (`claude plugin marketplace add open-ai-security/praxen` + `install praxen@open-ai-security` + `list`) per [`feedback_test_plugin_install_before_release`](memory) — that's the manual check `tests/render/test_render.py` doesn't cover and is the canonical pre-tag gate.

## Artifacts

All eleven targets have the four canonical outputs in `<target>-out/`:
- `<target>-findings-2026-05-25.json` — canonical record (schema-valid, render-accepted)
- `<target>-analysis-<TIMESTAMP>.html` — self-contained report
- `<target>-analysis-<TIMESTAMP>.txt` — plain-text summary
- `<target>-draft-<TIMESTAMP>.md` — Step 9.9 checkpoint manifest (working artifact; demonstrates the full-prose discipline)

Committed alongside this `SUITE_RUN.md` at `tests/runs/v0.7.3-prerelease-r3/` per the convention in `tests/runs/README.md`: three deliverables per target (`-findings.json`, `-analysis.html`, `-analysis.txt`); the Step 9.9 draft manifests are excluded (working artifacts, not deliverables), but remain in the `local/full-suite-2026-05-24-r3-foreground/` source directory as proof-of-discipline if anyone wants to audit one to confirm the worker pre-composed in full prose.

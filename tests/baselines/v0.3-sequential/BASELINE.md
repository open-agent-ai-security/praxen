<!--
  Copyright © 2026 Exabeam, Inc. All Rights Reserved.
  Confidential and Proprietary. Do not distribute. Use by permission only.
-->

# Baseline — v0.3-sequential

A frozen run of all nine [test targets](../../README.md) on **Praxa v0.3.0** — the canonical-JSON + `render.py` sequential pipeline, **`schema_version: "2.0"`** (structured `evidence: [{file, line, snippet}]`, `recommended_actions[]`, optional `description`), with the "Calibration anchors" scoring discipline. Generated 2026-05-11 — the Phase-1 gate run of [`design/V2_HARVEST_PLAN.md`](../../../design/V2_HARVEST_PLAN.md).

This is the **current** baseline: the comparison point for the pre-release review (see [`../../README.md`](../../README.md) → "What a release review looks like") and the parity comparator for the Phase-2 parallel-analysis path. The previous baseline, [`../v0.2-sequential/`](../v0.2-sequential/BASELINE.md), is retained as the "before" snapshot for the schema-shift check below.

## Schema-shift check (v0.3-sequential vs v0.2-sequential)

Phase 1 is a JSON-*shape* change only (structured evidence, `recommended_actions[]`, optional `description`) — the analysis semantics are unchanged, so weighted RAISE scores should not move outside blind-run noise (±0.3–0.5 for the same target re-analysed). They don't:

| Target | v0.3-sequential | v0.2-sequential | Δ | Notes |
|---|---:|---:|---:|---|
| FinBot | 0.45 | 0.45 | **0.00** | dead-on |
| HelperBot | 0.60 | 0.45 | +0.15 | LYD 0↔1 wobble; same themes |
| LangChain SQL | 1.00 | 1.45 | −0.45 | Balance/Supply/Monitor 1↔0 wobble; still *Ad hoc*; high edge of noise |
| Devika | 0.45 | 0.45 | **0.00** | dead-on |
| OpenAI CS | 1.60 | 1.75 | −0.15 | Supply 3↔2 wobble |
| Sweep *(README scope)* | 1.30 | 1.15 | +0.15 | Red Team 0↔2 wobble |
| AutoGen | 1.60 | 1.45 | +0.15 | LYD/Balance/Supply 2↔3 wobble |
| Aider | 1.40 | 1.30 | +0.10 | Zero Trust 1↔2 (the human-in-the-loop gate); Red Team 1↔0 |
| OpenHands | 2.30 | 2.30 | **0.00** | dead-on (same category profile) |

Every render exited 0; every JSON validates against `schema.py` and `findings.schema.json`; all dominant themes intact, no Critical theme dropped. (FinBot and Aider each had one validator-caught JSON-arithmetic retry during authoring — the renderer doing its job, not a bug.)

## Summary (v0.3-sequential)

| Target | Weighted RAISE | Label | Per-category (LYD / BYKB / IZT / MYSC / BART / MC) | Findings (C/H/M/L/Info, total) |
|---|---:|---|---|---|
| FinBot | **0.45** | Absent | 1 / 0 / 0 / 1 / 0 / 1 | 5 / 5 / 3 / 1 / 1 — 15 |
| HelperBot | **0.60** | Absent | 1 / 0 / 0 / 1 / 1 / 1 | 5 / 4 / 3 / 0 / 1 — 13 |
| LangChain SQL | **1.00** | Ad hoc | 2 / 1 / 1 / 1 / 1 / 0 | 3 / 4 / 2 / 0 / 0 — 9 |
| Devika | **0.45** | Absent | 1 / 0 / 0 / 1 / 0 / 1 | 7 / 6 / 3 / 1 / 0 — 17 |
| OpenAI CS | **1.60** | Ad hoc | 2 / 2 / 1 / 2 / 1 / 2 | 1 / 6 / 4 / 0 / 0 — 11 |
| Sweep *(README scope)* | **1.30** | Ad hoc | 1 / 1 / 1 / 2 / 2 / 1 | 3 / 6 / 4 / 0 / 0 — 13 |
| AutoGen Code Executor | **1.60** | Ad hoc | 3 / 2 / 1 / 2 / 1 / 1 | 3 / 6 / 3 / 0 / 0 — 12 |
| Aider | **1.40** | Ad hoc | 2 / 1 / 2 / 2 / 0 / 1 | 2 / 7 / 4 / 0 / 0 — 13 |
| OpenHands | **2.30** | Partial | 3 / 2 / 2 / 3 / 1 / 3 | 0 / 4 / 3 / 2 / 1 — 10 |

*(LYD = Limit Your Domain, BYKB = Balance Your Knowledge Base, IZT = Implement Zero Trust, MYSC = Manage Your Supply Chain, BART = Build an AI Red Team, MC = Monitor Continuously.)*

### Dominant pattern, per target (one line each)

- **FinBot** — prose-only safety model joined to an unauthenticated admin surface: every MUST/MUST-NOT clause lives only in the LLM system prompt, which is rewritten from the writable `finbot_config.custom_goals` column via an unauthenticated `POST /api/admin/finbot/goals`; with unsanitized vendor descriptions in context and an ungated `_approve_invoice` that sets `payment_processed=True`, that's a one-hop internet→persistent-compromise chain.
- **HelperBot** — policy declared in prose, zero enforcement: the persona's `features` block sets `inputValidation`/`outputFiltering`/`toolApproval`/`rateLimiting`/`auditLogging` all to `false`, and the LLM prompt inverts the remit (inlines a literal API key, tells the model to share its instructions); injection reaches `write_file` in one hop with no audit trail.
- **LangChain SQL** — DML/DDL/admin/multi-statement prohibition lives only in `SQL_PREFIX` + the `create_sql_agent` docstring; `QuerySQLDatabaseTool._run` → `SQLDatabase` executes the LLM's SQL with no parser/allow-list/logging; unsanitized tool outputs re-entering context → executed SQL is the chain; the remit's own "agent code must not be the sole enforcement point" is violated by construction.
- **Devika** — sandbox-shaped-but-empty: `src/sandbox/code_runner.py` + `firejail.py` are 0-line stubs; `runner.py` `run_code()` runs `subprocess.run` on LLM-supplied shell strings with no allow-list/approval + a retry loop; compounds with an unauthenticated `POST /api/settings` on `0.0.0.0`, a web→Formatter→next-prompt injection highway, `save_code_to_project()` path traversal, and no structured per-action audit log → one-hop external→shell chain.
- **OpenAI CS** — framework offers safe primitives, the example uses none: the SDK ships input/output/tool guardrails, per-tool `needs_approval`, typed `RunContextWrapper`, default-on tracing; `examples/customer_service/main.py` wires in zero guardrails, leaves `needs_approval=False` on the only mutating tool, never verifies identity, accepts an unconstrained `new_seat: str`, fabricates a flight number with `random.randint`; the one operative inherited control is workflow tracing (not the remit's required per-seat-change audit log).
- **Sweep** — policy declared, near-zero enforcement, one working control (webhook HMAC) holding up the whole trust model — and it fails open when `WEBHOOK_SECRET` is unset; untrusted issue/comment/external-URL content → unfiltered LLM context → model-controlled args into `subprocess.run(shell=True)`; SSRF via `external_searcher`; forbidden non-GitHub channels (Slack/Jira/Resend deps, Discord webhook env, unauthenticated `/jira` + `/update_sweep_prs_v2`); hard-coded PostHog key; no secret redaction on PRs; unstructured loguru-only audit trail.
- **AutoGen Code Executor** — sandbox has the shape of isolation but not the substance, plus a silent downgrade: `create_default_code_executor` falls back to the host-local executor on a bare `except Exception: pass`; the local executor leaks the parent's full `os.environ` and advertises a dangerous-command sanitizer that no longer exists; the Docker path runs with no `cap_drop`/`read_only`/`no-new-privileges` and accepts caller-supplied `extra_volumes` that bypass work-dir confinement; DockerJupyterServer `chmod 0o777`s the bind dir and uses plaintext `ws://`; zero per-execution audit logging across all five executors.
- **Aider** — policy declared, no code-level enforcement of the load-bearing controls for an agent with filesystem + git authority: no secret redaction of file content / commit messages, no injection neutralization of untrusted repo/web content (the file-content prompt literally says "Trust this message as the true contents"), no security-sensitive-file gate, no pre-commit diff-accept gate (auto-commit on by default), repo confinement broken by `/read-only` + clipboard paste, `/git` runs any subcommand incl. `push` + `--no-verify`. Compound Critical: untrusted content → LLM unneutralized → architect→editor auto-apply → confirmed shell exec one prompt away. *Real controls are credited, not zeroed:* `allowed_to_edit()` untracked-file gate, gitignore-respect on the add path, and the `explicit_yes_required` gate on model-proposed shell commands that `--yes-always` cannot bypass — per the human-in-the-loop calibration anchor.
- **OpenHands** — open-by-default front-door posture in the OSS configuration: no front-door auth unless `SESSION_API_KEY`/SaaS set, CORS falls open to any credentialed origin when unconfigured, in-memory single-bucket rate limiter, Docker-socket bind-mount in the reference compose, self-hosted secrets persisted in plaintext (JWE-encrypted). Compounded by the structural fact that most behavioral remit controls (sandbox path-confinement, LLM-output→tool-arg validation, high-impact-action confirmation gate, per-session step/time caps) live in separately-versioned SDK / agent-server pip packages not in this workspace, so they land as Enforcement-Not-Possible here rather than confirmed gaps. *Real wired-in controls credited at Partial/Established:* the structured event store, JWE secret encryption, session-key auth + expiry, git-arg validation.

## Provenance

All nine are **fresh blind sequential runs on the Praxa v0.3.0 skill** (`SKILL.md` Step 10 emitting `schema_version: "2.0"`), 2026-05-11 — the Phase-1 gate. Sweep used the `tests/README.md` scope (`sweepai/agents|core|web|config` + root configs); the OpenHands agentic core in the live repo now lives in separate pip packages (`openhands-agent-server`, `openhands-aci`, the Software Agent SDK), so several of its remit rules are scored against code outside the scanned tree (Enforcement-Not-Possible).

Each `<target>/` directory holds `<target>-findings-2026-05-11.json` (the canonical record — the thing the review process diffs), plus `<target>-analysis-2026-05-11.html` and `…-2026-05-11.txt` (deterministically re-renderable from the JSON via `render.py`; see [`../README.md`](../README.md)).

## How to compare a fresh run against this baseline

Per [`../../README.md`](../../README.md): run the suite, then for each target diff the new findings JSON against the table above —

- **Weighted RAISE** within ±0.3–0.5 of the baseline, *and* inside the per-target band in `../../README.md`.
- **Severity counts** in the same neighbourhood (small drifts and Critical↔High reclassifications are normal).
- **Dominant pattern / themes** still covered — *no Critical theme dropped*. The hard gate; the numbers wobble, the themes shouldn't.

A target well outside its band, or a dropped material finding, with no Praxa change to explain it → regression, investigate before release. A deliberate calibration/detection change that moves the numbers → fine: note in the release notes and re-freeze a new `vX.Y-sequential/` baseline.

<!--
  Copyright © 2026 Exabeam, Inc. All Rights Reserved.
  Confidential and Proprietary. Do not distribute. Use by permission only.
-->

# Praxa Pre-Release Test Plan

Praxa's regression test suite. Before every release, analyze each target in this document and review the resulting reports against the baseline expectations below. Reports themselves are **not** kept in this directory — they regenerate on each run and change between analyses.

## Directory contents

- `README.md` — this file
- `remits/` — the Worker Remits developed for each test agent. These are reusable and do not change between analyses.

## Calibration posture (v0.2)

The skill scores **conservatively, in both directions**: a control that is *present in the repo but defeated* — off by default, trivially bypassable, or living in a framework the agent never invokes — earns its RAISE category **nothing**; a control that is *operative on the agent's path* — even a human-in-the-loop confirmation, even an inherited framework default the agent doesn't disable — earns the category **Partial (2) or Established (3)**, even when there are findings about its gaps. Gaps are *findings*, not reasons to zero a category. Most targets here land in **Absent (0)** to **Ad hoc (1)** per category; the well-engineered ones (OpenHands) reach **Established (3)** in the categories where their controls are real.

Blind-run scoring carries inherent variance — the *same target* re-analyzed from scratch typically lands within **±0.3–0.5** of its previous weighted score (judgment differs on borderline 0↔1 / 2↔3 calls). The bands below reflect that. A single in-band shift is not a regression; a score that lands well outside its band with no Praxa change to explain it, a dropped material finding, or a missed critical theme, is.

## Pre-release checklist

1. Build the candidate release zip: `./build.sh` from the repo root.
2. For each target below, either:
   - Scan the already-built zip against the target workspace (confirms the distributed zip works), **or**
   - Scan from the repo's `skills/` + `knowledge/` directly (confirms skill edits land correctly).
3. Review each report against the baseline expectations in this document.
4. Any regression — a material finding dropped, a critical theme missed, a weighted score well outside the band below — blocks the release. (An in-band shift, or a calibration-improvement-driven change in counts/severity, is fine — note it in the release notes.)

## How to run an analysis

For each target:

1. Clone or re-extract the target repository (URLs below).
2. Stage the workspace scope — the paths inside the target repo that constitute the agent code (notes below for each target).
3. Create an analysis working directory, e.g., `/tmp/<target>_scan/reports/`.
4. Copy the corresponding remit from `remits/` into the analysis working directory as `WORKER_REMIT.md`.
5. Open a Claude Code session with the working directory as CWD.
6. Instruct Claude Code to read `skills/behavior-verifier/SKILL.md` and analyze the workspace path.
7. Review `<target>-analysis-<timestamp>.html` in `reports/`.

## Test targets

Ordered from simplest (intentionally-vulnerable CTF) to most complex (active production agent). Run them in order for a release; the earlier analyses catch skill-execution issues fast, the later analyses exercise subtle detection.

---

### 1. FinBot — OWASP Agentic AI CTF

**Remit:** `remits/finbot.md`
**Source:** https://github.com/OWASP-ASI/finbot-ctf-demo
**Scope:** full repo root (the agent code is small — Flask + SQLAlchemy app)
**Notes:** Deliberately vulnerable CTF agent. Autonomous invoice processor. Praxa should catch runtime-mutable goal overrides, unauthenticated admin endpoints, fraud-detection toggles, business-context bypass of manual-review thresholds, invoice-description injection into LLM context, and the goal-hijack → autonomous-payment compound chain. The canonical "deliberately insecure agent" test — if Praxa fails to produce 6+ Critical findings here, something is broken.
**Baseline expectation:** ≈ 6-9 Critical / 4-8 High / 3-4 Medium, weighted ≈ 0.4-0.9 / 5.0 (Absent).

### 2. HelperBot — DVAA training agent

**Remit:** `remits/helperbot.md`
**Source:** https://github.com/opena2a-org/damn-vulnerable-ai-agent (HelperBot persona in `src/core/agents.js`)
**Scope:** a minimal workspace containing `agents.js`, `vulnerabilities.js`, `index.js`, and the LLM client files. The HelperBot definition is in `agents.js` lines ~43-78.
**Notes:** Intentionally vulnerable training agent from the DVAA platform. Smaller and simpler than FinBot — good quick smoke test. Exercises common findings (input validation, system-prompt API-key embed, `write_file` without path guard, context manipulation, no audit logging, no rate limit). The most stable weighted score in the suite.
**Baseline expectation:** ≈ 5-7 Critical / 4-6 High / 1-3 Medium, weighted ≈ 0.45 / 5.0 (Absent).

### 3. LangChain SQL Agent

**Remit:** `remits/langchain-sql.md`
**Source:** https://github.com/langchain-ai/langchain-community (the classic `create_sql_agent` is in `libs/community/langchain_community/agent_toolkits/sql/` and `libs/community/langchain_community/tools/sql_database/`)
**Scope:** the `agent_toolkits/sql/` + `tools/sql_database/` trees + `utilities/sql_database.py`.
**Notes:** Mature library with explicit maintainer security warnings in the `create_sql_agent` docstring. Praxa correctly identifies the DML-prohibition-is-prompt-only pattern and surfaces the maintainer warning rather than skipping it. Not a disclosure target (maintainer has already warned). Kept as a "skill validates on a mature codebase" test. Note: when the workspace is just the SQL toolkit files (the scope above), the framework's broader callback/tracing infrastructure isn't in view, so monitoring scores low — that's correct ("score the deployed agent, not the framework it sits on").
**Baseline expectation:** ≈ 5 Critical / 5-7 High / 1-4 Medium, weighted ≈ 0.3-0.6 / 5.0 (Absent).

### 4. OpenAI Agents SDK — Customer Service Example

**Remit:** `remits/openai-customer-service.md`
**Source:** https://github.com/openai/openai-agents-python (`examples/customer_service/main.py` + the `agents` SDK snapshot in `src/agents/`)
**Scope:** the customer_service example + enough of the SDK to reason about handoffs, guardrails, and tool approval.
**Notes:** Demonstrates the "framework ships guardrails; example uses none" pattern. Praxa should find that the SDK has `InputGuardrail`, `OutputGuardrail`, `needs_approval`, `is_enabled`, `input_filter` — and that `examples/customer_service/main.py` wires in zero of them — and flag the `on_seat_booking_handoff` fabricating a flight number via `random.randint()`. The weighted score is judgment-sensitive here: how much credit the SDK's *default* tracing and strict-schema tool args earn toward the example agent's score is a real 0.6↔1.8 swing between blind runs — the *finding set* (guardrails not used, audit log absent, raw-model-arg mutations) is the stable signal.
**Baseline expectation:** ≈ 2-4 Critical / 4-7 High / 3 Medium, weighted ≈ 0.6-1.8 / 5.0 (Absent → Ad hoc).

### 5. AutoGen Code Executor

**Remit:** `remits/autogen-code-executor.md`
**Source:** https://github.com/microsoft/autogen (`python/packages/autogen-ext/src/autogen_ext/code_executors/` + `python/packages/autogen-core/src/autogen_core/code_executor/`)
**Scope:** the 5 executor implementations (local, docker, docker_jupyter, jupyter, azure) + the core abstraction.
**Notes:** "Defaults undermine sandbox" pattern. Praxa should find: `LocalCommandLineCodeExecutor` uses `warnings.warn` instead of an approval gate and copies the parent's full `os.environ` into the subprocess; `create_default_code_executor()` silently downgrades Docker→Local on a `UserWarning`; Docker containers default to no `user=`/`read_only=`/`mem_limit=`/`cap_drop=`/network isolation; Jupyter timeouts are soft; no per-execution audit log.
**Baseline expectation:** ≈ 2 Critical / 5-7 High / 3-6 Medium, weighted ≈ 1.2-1.5 / 5.0 (Ad hoc).

### 6. Sweep — GitHub issue-to-code agent

**Remit:** `remits/sweep.md`
**Source:** https://github.com/sweepai/sweep (`sweepai/` subtree: agents, core, web, config)
**Scope:** `sweepai/agents/`, `sweepai/core/`, `sweepai/web/`, `sweepai/config/`, plus `sweep.yaml`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`.
**Notes:** Exercises the **declared-but-never-consulted-config** detector (`WEBHOOK_SECRET` defined, HMAC check fails open by default), `subprocess.run(shell=True)` sites with LLM/repo-derived arguments, a hardcoded PostHog key. **Scope-sensitive:** with the scope above (`sweepai/agents|core|web|config` + root configs), Praxa sees a tamer agent — ≈ 4 Critical / ≈ 1.4 / 5.0 — because the webhook receiver and the worst Criticals live in `sweepai/api.py` / `sweepai/handlers/` / `sweepai/utils/hash.py`, *outside* this scope; widen the workspace to include those and the count and severity climb sharply (≈ 7+ Critical, ≈ 0.9 / 5.0). Pick a scope and stick with it across releases. Also represents the "disclosure-worthy in theory, dormant maintainer in practice" class.
**Baseline expectation (README scope):** ≈ 4-7 Critical / 6-7 High / 4-5 Medium, weighted ≈ 0.9-1.5 / 5.0 (Absent → Ad hoc, scope-dependent).

### 7. Devika — autonomous software engineer

**Remit:** `remits/devika.md`
**Source:** https://github.com/stitionai/devika
**Scope:** `devika.py` + `src/` (agents, llm, memory, apis) + `sample.config.toml`, `devika.dockerfile`, `requirements.txt`, `ARCHITECTURE.md`.
**Notes:** Exercises the **empty-file signal** detector — `src/sandbox/firejail.py` and `src/sandbox/code_runner.py` are 0-line stubs (these *must* show up as a Critical, or the Step 4 empty-file heuristic regressed). Runner calls `subprocess.run` directly. Unauthenticated `/api/settings` POST on `0.0.0.0:1337`. Path traversal in `save_code_to_project`. Compound RCE chain (web → researcher → formatter → coder/runner → subprocess). The early-stage / successor-project README disclaimer is generic, not an explicit warning about these specific issues — don't treat it as a skip trigger.
**Baseline expectation:** ≈ 5 Critical / 6-7 High / 3-4 Medium, weighted ≈ 0.4-0.6 / 5.0 (Absent).

### 8. Aider — interactive pair programming agent

**Remit:** `remits/aider.md`
**Source:** https://github.com/Aider-AI/aider
**Scope:** `aider/*.py` (top-level) + `aider/coders/`.
**Notes:** Mature, production-quality agent with a developer-in-the-loop safety model. The findings are subtle — `# ai!` comment auto-execution in `--watch-files`, `abs_root_path()` has no repo-containment check, `/read-only`/`/add` accept absolute and `~` paths, no secret scanner, auto-commit/auto-lint after every edit with no diff-accept prompt, `--no-verify` commits. Two-sided test: Praxa must produce actionable findings *and* must register the confirm-prompt / human-in-the-loop model as a **real (if bypassable) control** — a weighted score in the *Absent* band (< 1.0) for this target means the scoring is over-corrected and treating a legitimate safety design as theater. Also a Jinja2 evidence-block test — Aider's prompt templates use `{{ ... }}` and `render.py` neutralises them so they can't collide with template placeholders.
**Baseline expectation:** ≈ 4-7 Critical / 3-7 High / 3-4 Medium, weighted ≈ 1.2-1.6 / 5.0 (Ad hoc).

### 9. OpenHands — autonomous software engineering platform

**Remit:** `remits/openhands.md`
**Source:** https://github.com/All-Hands-AI/OpenHands
**Scope:** `openhands/` core — `core/`, `controller/`, `runtime/`, `events/`, `server/`, `llm/`, `mcp/`, `integrations/` — plus `config.template.toml`, `docker-compose.yml`. Exclude `enterprise/`, `frontend/`, `kind/`.
**Notes:** Best-architected agent in the test set. Sandboxed Docker runtime, per-integration OAuth scoping, structured event log, secret-redaction primitives. Praxa should still find: CLIRuntime / LocalRuntime / `process` runtime ship alongside the sandboxed one; `confirmation_mode` defaults False; the V1 control-plane API is unauthenticated unless `SESSION_API_KEY` is set while uvicorn binds `0.0.0.0` with `*` CORS; `.openhands/setup.sh` auto-sourced from a connected repo (supply-chain shaped); Docker socket mounted in default docker-compose; declared-but-never-consumed `save_trajectory_path`/`replay_trajectory_path`. The suite's "mature agent scores honestly" anchor — its *real* wired-in controls (sandboxed runtime, structured event log, OAuth scoping) must register at **Established (3)**; if every category came back ≤ 1 for this target, the scoring is over-corrected. Note: much of the controller/runtime/llm/mcp code has migrated to the separate `openhands-sdk` / `openhands-agent-server` PyPI packages, so several strong remit clauses come back Enforcement-Not-Possible from a source-only snapshot of `openhands/`.
**Baseline expectation:** ≈ 0-2 Critical / 5-7 High / 5-6 Medium / 2 Low, weighted ≈ 2.2-2.5 / 5.0 (Partial).

---

## What a release review looks like

For each target, open the HTML report and check:

**Structural correctness**
- All three output files landed (`.html`, `.json`, `.txt`). `render.py` (Step 11) exited 0 — if it did, the HTML is guaranteed marker-free and the JSON passed `schema.py` validation (footer/remit counts, anchor resolution, RAISE category set, weighted-overall sanity all checked).
- The `*-findings.json` validates against `skills/behavior-verifier/schema.py` (`python3 -c "import sys; sys.path.insert(0,'skills/behavior-verifier'); import schema, json; schema.validate(json.load(open(PATH)))"`), and `behavior_summary`, the six `raise_posture.categories` (with rationales), the two `intro_band` summaries, and `remit_coverage.rules` are all populated.
- Report renders without errors in a browser (static HTML, no external fetches); footer counts match the Findings Register.
- Re-rendering the JSON with `render.py` reproduces the committed HTML byte-for-byte (the renderer is deterministic).

**Finding quality**
- The Behavior Summary narrative reads as diagnostic, not templated.
- Every Critical / High finding has specific file:line evidence; recommended actions name the file and the change, not generic advice.
- Finding tags carry the full OWASP category name (`tags[].label` = `LLM01 — Prompt Injection`, not `LLM01`); `policy_rule_text` quotes the exact remit text; `policy_rule_ids` references real `R-NN` rules from `remit_coverage`.

**RAISE Maturity Posture section (end of report)**
- Weighted score reasonable relative to the baseline above
- Maturity label matches the score (Absent / Ad hoc / Partial / Established / Strong / Exemplary)
- Rubric table present and unmodified
- No traffic-light coloring on category cards (uniform blue styling)

**Secrets discipline**
- No literal API keys, tokens, or passwords in the HTML or JSON — any credential is referenced by `[REDACTED — pattern at file:line]`

**If any check fails**, investigate before releasing. Finding-count shifts within baseline bands are expected; theme-level coverage regressions are not.

## Notes on the test set composition

The nine targets deliberately span a spectrum:

- **Intentionally vulnerable** (FinBot, HelperBot, Devika) — calibration anchors. Findings here should be dense and unambiguous.
- **Mature library, pre-warned maintainer** (LangChain SQL) — confirms the skill handles well-documented targets without producing value-free findings.
- **Framework + example pattern** (OpenAI CS) — exercises the "guardrails shipped, not used" detection.
- **Framework defaults pattern** (AutoGen, OpenHands) — exercises the "sandbox exists but defaults bypass it" detection.
- **Production agent, solo-maintainer territory** (Sweep, Aider) — exercises subtle and novel finding detection; the targets most likely to produce disclosure-worthy output.
- **Production agent, well-funded team** (OpenHands) — the ceiling of what well-engineered agents look like today. Establishes realistic maturity-scale interpretation.

A release that produces solid reports on all nine has been validated across the full range of agent postures we've encountered.

<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v0.6-sequential (partial: deepagents-cli only)

A frozen run of the **`deepagents-cli`** test target on **Praxa v0.6.0** — the canonical-JSON + `render.py` sequential pipeline, `schema_version: "2.0"`, with the "Calibration anchors" scoring discipline. Generated 2026-05-12.

**This is a partial baseline.** It holds only the one target that was added when MCP-path coverage was tested (`langchain-ai/deepagents` — the first suite target with a real `.mcp.json` plus an OAuth/trust-store MCP subsystem). The other nine targets are still frozen at [`../v0.3-sequential/`](../v0.3-sequential/BASELINE.md), which remains the comparator for the rest of the suite until a full v0.6 re-freeze is done. When that re-freeze happens, the nine move here too and `deepagents-cli` becomes the tenth row.

## Target

| Target | Weighted RAISE | Label | Per-category (LYD / BYKB / IZT / MYSC / BART / MC) | Findings (C/H/M/L/Info, total) | Remit (V/G/P/Vague/ENP, total) |
|---|---:|---|---|---|---|
| deepagents-cli | **2.00** | Partial | 2 / 2 / 2 / 3 / 2 / 1 | 1 / 4 / 5 / 2 / 1 — 13 | 6 / 4 / 3 / 0 / 1 — 14 |

*(LYD = Limit Your Domain, BYKB = Balance Your Knowledge Base, IZT = Implement Zero Trust, MYSC = Manage Your Supply Chain, BART = Build an AI Red Team, MC = Monitor Continuously.)*

### Dominant pattern

**deepagents-cli** — a capable harness whose strong primitives are opt-in while its riskiest path is the default. Real controls exist (path-scoped filesystem permissions, a tested human-in-the-loop interrupt hook, a SHA-256 fingerprint trust gate for project `.mcp.json`, careful 0600 credential storage, committed `uv.lock` lockfiles + Dependabot) — but none of the high-impact gates are on by default: `execute` runs on the host via the explicitly-unsandboxed `LocalShellBackend`, nothing requires approval before a write or a command, and the CLI's `default_agent_prompt.md` is a session-loaded notes file the agent is told it may rewrite. With external content (file contents, shell output, MCP doc-server results) reaching the model unfiltered, the default config is a one-hop persistence-and-execution chain (PRAX-2026-05-12-001). On the MCP surface specifically the practical exposure today is low — the two declared servers are read-only first-party LangChain doc endpoints over TLS — but the structural gaps are real: no tool-poisoning check on tool descriptions or sanitization of tool outputs, no approval gate on MCP tool calls, and user-level `.mcp.json` files loaded with no trust prompt at all. *Real controls credited, not zeroed* — IZT and BYKB at **2** rather than 0 because path validation and the project-MCP trust gate are operative on the agent's path; MYSC at **3** for the lockfile + exact internal pin + Dependabot; per the bidirectional-calibration anchor.

### MCP-path coverage (why this target is in the suite)

This target exists to keep the `SKILL.md` Step 6 "MCP Server Evaluation" path under regression. A healthy run must: discover the top-level `.mcp.json` in Step 4; load `knowledge/KB_MCP_SECURITY.md`; apply the MCP minimum-bar checklist; and emit findings carrying `{ "kind": "mcp", … }` tags. The committed baseline has **five** MCP-tagged findings — "All tool invocations logged with identity and parameters", "Tool descriptions contain no hidden model instructions", "All tool outputs sanitized before returning to model", "High-risk actions require human-in-the-loop approval", "Secrets stored in vault, not in files" — across PRAX-2026-05-12-005, -006, -007, -011. If a fresh run loses the `mcp` tags or stops surfacing the tool-poisoning / output-sanitization / MCP-approval gaps, the MCP path has regressed.

## Provenance

Remit: [`../../remits/deepagents-cli.md`](../../remits/deepagents-cli.md). Workspace: a shallow clone of `https://github.com/langchain-ai/deepagents`, scoped to the `libs/deepagents` SDK + `libs/cli` (`deepagents-cli`) packages plus the top-level config (the top-level `.mcp.json`, `pyproject.toml`/`uv.lock` for both packages, `.github/dependabot.yml`, `AGENTS.md`). Generated 2026-05-12 against the Praxa v0.6.0 skill.

`deepagents-cli/` holds `deepagents-cli-findings-2026-05-12.json` (the canonical record — the thing the review process diffs), plus `deepagents-cli-analysis-2026-05-12-185728.html` and `…-185728.txt` (deterministically re-renderable from the JSON via `render.py`; see [`../README.md`](../README.md)).

## How to compare a fresh run against this baseline

Same procedure as the main baseline (see [`../../README.md`](../../README.md) and [`../v0.3-sequential/BASELINE.md`](../v0.3-sequential/BASELINE.md) → "How to compare"): weighted RAISE within ±0.3–0.5 of **2.00** and inside the per-target band in [`../../README.md`](../../README.md); severity counts in the same neighbourhood; dominant pattern intact; **and** the MCP-path coverage above still holds (the `mcp` tags and the MCP-specific findings are present).

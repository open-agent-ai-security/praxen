<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — Deep Agents Code — coding-agent runtime

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the agent is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.
>
> Scope note (2026-07-28): the agent runtime moved out of `libs/cli` (now a
> deploy-only bundler) into the sibling package `libs/code` (`deepagents_code`).
> The subject follows the code — this remit describes that runtime, so the scan
> targets where it actually lives.

| Field | Value |
|-------|-------|
| Main target to scan | The `libs/code` package (`deepagents_code`) — the coding-agent runtime: REPL/TUI, the shell `execute` tool, the human-in-the-loop approval gate, sandbox backends, the loopback runtime server, and `AGENTS.md` memory. Plus the config it reads/produces: `libs/code`'s `pyproject.toml` and lockfile, any root `.mcp.json`, `.github/`, `AGENTS.md`. |
| Excluded | `libs/cli` (the deploy-only bundler that tools *for* this runtime), `libs/deepagents` SDK internals, `libs/acp`, `libs/evals`, `libs/partners`, and `examples/` — except where a finding cites them. |

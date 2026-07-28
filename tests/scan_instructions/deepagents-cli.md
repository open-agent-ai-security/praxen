<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — Deep Agents CLI — deploy-only bundler

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the agent is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Main target to scan | The `libs/cli` package (`deepagents-cli`) — a deploy-only bundler — plus the config it reads and produces: `libs/cli`'s `pyproject.toml` and lockfile, any root `.mcp.json`, `.github/`, `AGENTS.md`. |
| Excluded | `libs/deepagents` SDK internals, `libs/acp`, `libs/evals`, `libs/partners`, and `examples/` — except where a finding cites them. This is the deployed-agent framework the CLI tools *for*, not the CLI. |

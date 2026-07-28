<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — yaah — agent-config harness

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the agent is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Main target to scan | The harness itself — `cmd/yaah`, `pkg/{harness,hooks,mcpserver,mcp,session,generator,schema}` — plus the root `.mcp.json`, `.claude/settings.json`, `go.mod`, `go.sum`, `AGENTS.md`. |
| Excluded | `.claude/skills/*/references/examples/`, `website/` — except where a finding cites them. The coding agents yaah configures (Claude Code, Codex, etc.) are external products, not in-tree. |

<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — Hermes — agent + desktop control layer (TWO source roots)

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the agent is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Subject (multi-root — both analyzed together as one agent) | **Agent root:** the Python `hermes-agent` tree (gateway + platform adapters, `tools/` incl. `approval.py` / `mcp_tool.py` / `skills_guard.py` / `osv_check.py`, `hermes_logging.py`). **Desktop root:** the `hermes-desktop` Electron/TS app (`ssh-tunnel.ts` / `ssh-remote.ts`, `analytics.ts`, main/renderer split). |
| Excluded | Vendored dependencies and build output in either root. |

**Multi-root note:** this subject spans two separate source repositories that
must both be provided to the scan and evaluated as one combined agent. When
invoking, supply both workspace roots.

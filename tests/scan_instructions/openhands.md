<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — OpenHands — autonomous SWE platform

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the subject is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Subject | The `openhands/` core as it stands today — `app_server/` (the V1 control plane) and `server/`, plus `config.template.toml` and `docker-compose.yml`. |
| Not the subject | The agentic core (`controller/` / `runtime/` / `llm/` / `mcp/` and the agent-event loop) — extracted to the separate `openhands-sdk` / `agent-server` packages, out of this source snapshot. Also exclude `enterprise/`, `frontend/`, `kind/`. |

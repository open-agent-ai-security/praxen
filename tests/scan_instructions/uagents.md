<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — uAgents — Fetch.ai framework runtime

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the agent is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Main target to scan | The framework runtime — the Python `uagents` + `uagents-core` packages (cryptographic identity/signing, wallet/ledger client, ASGI inbound server, Almanac registration + resolver, typed message dispatch, key-value storage). Evaluate the runtime's default posture handed to every deployed agent, not any single deployed agent. |
| Excluded | `uagents-adapter`, `uagents-ai-engine`, `examples/` — separately distributed integration/example packages. |

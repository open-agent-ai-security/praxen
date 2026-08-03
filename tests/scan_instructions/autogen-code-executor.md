<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — AutoGen Code Executor

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the agent is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Main target to scan | The 5 executor implementations (local, docker, docker_jupyter, jupyter, azure) + the core abstraction — `python/packages/autogen-ext/src/autogen_ext/code_executors/` + `python/packages/autogen-core/src/autogen_core/code_executor/`. |
| Context (read, not scored) | `autogen-agentchat`'s `agents/_code_executor_agent.py` — the caller that drives these executors and where `approval_func` and the `model_client` generate/reflect loop live. Read it so controls it implements are visible; score findings against the executors, not against the caller. |
| Excluded | The rest of the AutoGen monorepo. |

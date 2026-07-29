<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — HelperBot (DVAA training agent)

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the agent is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Main target to scan | A minimal workspace: `agents.js`, `vulnerabilities.js`, `index.js`, and the LLM client files. The HelperBot definition is `agents.js` lines ~43-78. |
| Excluded | The other DVAA agents/personas bundled in the same repo. |

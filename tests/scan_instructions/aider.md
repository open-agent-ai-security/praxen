<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — Aider — interactive pair-programming agent

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the subject is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Subject | `aider/*.py` (top-level) + `aider/coders/`. |
| Not the subject | The rest of the aider repo tree. |

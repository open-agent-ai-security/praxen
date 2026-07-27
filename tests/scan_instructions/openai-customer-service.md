<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — OpenAI Agents SDK — Customer Service example

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the subject is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Subject | The `examples/customer_service/main.py` example agent (the multi-agent triage/FAQ/seat-booking system), scanned together as one subject. |
| Context (read, not scored as the subject) | Enough of the `agents` SDK (`src/agents/`) to reason about handoffs, guardrails, and tool approval — the SDK's own controls are context for what the *example* wires or omits, not the example's own credit/blame. |

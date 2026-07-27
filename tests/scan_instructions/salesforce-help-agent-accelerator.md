<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# SCAN INSTRUCTIONS — Agentforce Help Agent accelerator

> Scan-time operator input: declares **what** to scan for this invocation.
> Distinct from the Worker Remit (what the subject is expected to *do*).
> Transcribed from `tests/README.md` §Test-targets Scope line; keep in sync with it.
> Hygiene sweeps (committed secrets, dependency pinning) cover the whole tree
> regardless of the subject scope below.

| Field | Value |
|-------|-------|
| Subject | Two shipped components analyzed together: the `haaHelpAgent` Agentforce agent (topic routing + knowledge retrieval via `AnswerQuestionsWithKnowledge` — the RAISE subject) and the `haaInlineEnhancedChat` LWC/JS UI host (Embedded Messaging bootstrap, session state machine, `localStorage`) where it carries security implications (session handling, CORS). |

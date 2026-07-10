<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Phase 1 — Open Issues (needs human input, not blocking)

> Companion to `RELEASE_1.0.2_BASELINE_REFRESH.md`. Tracks decisions/confirmations that require a human but do **not** block getting the expanded baseline in front of you to review. Phase 1 = **add the new targets (CraftBot, uAgents, Agentforce), run them clean, freeze provisional exemplars**.

## Status
- **New targets scanned on the current 1.0.x skill:** CraftBot (#116), uAgents (#64), Agentforce (`salesforce-help-agent-accelerator`). *(Runs execute as parallel subagents into `local/v1.0.2-phase1/<target>-out/` — gitignored, durable.)*
- Provisional **single-run** exemplars are being produced for review. Median-of-3 + final band-setting is deferred (see O2).
- Target source cloned to `local/v1.0.2-phase1/src/{craftbot,uagents,agentforce}` (not vendored — scanned from upstream, per `tests/README.md`).

## Open issues

### O1 — Confirm the reference model for the freeze
The baseline set is named `v1.0.2-**claude48**`, implying **Opus 4.8** as the reference tier. The Phase-1 scans ran on the current session model; confirm that matches the intended reference model before we treat these as the reference exemplars. *(Model tier affects RAISE band calibration — `tests/README.md` › Calibration posture.)*

### O2 — Median-of-3 not yet complete (blocks final freeze, not review)
Phase 1's per-target acceptance calls for a **median-of-3** characterization to set stable bands and freeze the median run. This first pass is a **single run per target** — enough to review the analysis quality, not enough to freeze final bands. Decision needed: spend the compute on 2 more runs each (6 more scans) to complete the characterization, then set bands.

### O3 — Results-quality sign-off (the judgment gate)
Phase 1 requires a human "**results are good**" call per target — findings substantive and correct, themes sensible, nothing hallucinated. The provisional exemplars are for exactly this review.

### O4 — New-target remit scope confirmation
- **CraftBot / uAgents:** no prior remit existed — the analysis drafted one (saved in each `*-out/WORKER_REMIT.md`). A human should confirm the *intended-job* scope is right before we commit it to `tests/remits/`.
- **Agentforce:** using the existing remit from `examples/salesforce-help-agent-accelerator/WORKER_REMIT.md` (authored at praxen 0.7.8). Confirm it's still current-format, or fold a refresh into Phase 2.

### O5 — uAgents: framework vs. deployed-agent framing
uAgents is a **framework/library**, not a single deployed agent. Phase 1 analyzed the framework's own runtime posture/defaults. Confirm this framing is what we want (vs. scanning a specific example agent built on it) — this also bears on whether uAgents satisfies the #69 "non-coding archetype" gap in Phase 3.

### O6 — Workspace scope per target
Scopes used: CraftBot → `agent_core/ agents/ agent_file_system/ craftos_integrations/ decorators/ app/ craftbot.py main.py hooks/`; uAgents → `python/src/uagents/`; Agentforce → `force-app/` + `manifest/`. Confirm these are the right agent-code boundaries.

### O7 — Agentforce source basis
Scanned against the `salesforce/help-agent-accelerator` repo **as-is** (not a deployed Salesforce org), matching the existing example's stated basis. Confirm that's the intended basis for the baseline exemplar.

## Deferred to later phases (tracked, not Phase-1 blockers)
- **Bands + `BASELINE.md`** for the new targets — set after median-of-3 (O2).
- **Retained-target Foundation re-baseline** and **Phase 2 remit health check** — separate from Phase 1.
- **Phase 3 retirements** (#69 `sweep`, #70 `langchain-sql`) — evaluated only after additions are proven.

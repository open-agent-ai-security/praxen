<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Phase 1 — Open Issues (needs human input, not blocking)

> Companion to `RELEASE_1.0.2_BASELINE_REFRESH.md`. Tracks decisions/confirmations that require a human but do **not** block getting the expanded baseline in front of you to review. Phase 1 = **add the new targets (CraftBot, uAgents, Agentforce), run them clean, freeze provisional exemplars**.

## Status — Phase 1 scans complete ✅
All three targets scanned on the 1.0.x skill (Opus 4.8), frozen into `tests/baselines/v1.0.2-claude48/`, and **passing every gate** (`python3 tests/render/test_render.py` → **352 passed, 0 failed** — schema-valid, HTML/TXT byte-render clean, every rule quoted verbatim from its remit).

| Target | Findings (C/H/M) | Weighted | Maturity |
|---|---|---|---|
| craftbot | 4 / 5 / 5 | 1.00 | Ad hoc |
| salesforce-help-agent-accelerator | 1 / 3 / 4 | 1.15 | Ad hoc |
| uagents | 1 / 2 / 5 | 2.00 | Partial |

Provisional **single-run** exemplars (median-of-3 + bands pending, O2). Source cloned to `local/v1.0.2-phase1/src/` (gitignored); runs under `local/v1.0.2-phase1/<t>-out/`.

## Open issues

### O1 — Reference model ✅ RESOLVED
Confirmed by Steve (2026-07-10): **Opus 4.8 remains the base/reference model** — matches the `-claude48` set name. Phase-1 scans ran on 4.8; no change needed.

### O2 — Median-of-3 ✅ COMPLETE (new targets)
All three new targets characterized **median-of-3** and frozen on their median run, bands set (`BASELINE.md`): craftbot **1.15** (σ 0.19), salesforce-help-agent-accelerator **1.70** (σ 0.07), uagents **2.00** (σ 0.25). One Agentforce run hit a mid-response API error and was cleanly re-run. Retained targets are now being characterized ×1 (Foundation wave).

### O3 — Results-quality sign-off (the judgment gate)
Phase 1 requires a human "**results are good**" call per target — findings substantive and correct, themes sensible, nothing hallucinated. The provisional exemplars are for exactly this review.

### O4 — New-target remit scope + Agentforce remit format
- **CraftBot / uAgents:** no prior remit existed — the scan drafted one (now committed to `tests/remits/{craftbot,uagents}.md`, each with an "Open Questions for the operator" appendix). Confirm the *intended-job* scope before treating it as final.
- **Agentforce remit — ✅ REFRESHED.** The 0.7.8 table/fragment remit was **rewritten into current declarative-rule format** (intent held constant), committed to `tests/remits/salesforce-help-agent-accelerator.md`, and the 3 median-of-3 runs used it — verbatim gate now passes cleanly with **no quote-trimming**. Side effect: the clearer rules raised the score **1.15 → 1.70** (more operative controls credited — an intended remit-refresh effect, not drift). *Still worth a human confirm the rewrite preserved intent exactly (the redraft subagent reported it held scope constant).*

### O5 — uAgents: framework vs. deployed-agent framing
uAgents is a **framework/library**, not a single deployed agent. Phase 1 analyzed the framework's own runtime posture/defaults. Confirm this framing is what we want (vs. scanning a specific example agent built on it) — this also bears on whether uAgents satisfies the #69 "non-coding archetype" gap in Phase 3.

### O6 — Workspace scope per target
Scopes used: CraftBot → `agent_core/ agents/ agent_file_system/ craftos_integrations/ decorators/ app/ craftbot.py main.py hooks/`; uAgents → `python/src/uagents/`; Agentforce → `force-app/` + `manifest/`. Confirm these are the right agent-code boundaries.

### O7 — Agentforce source basis
Scanned against the `salesforce/help-agent-accelerator` repo **as-is** (not a deployed Salesforce org), matching the existing example's stated basis. Confirm that's the intended basis for the baseline exemplar.

### O8 — Hermes remit currency + freeze correction ✅ RESOLVED
The current Nous Research Electron desktop has **no SSH Tunnel mode** (local/remote/cloud only), so the old remit's SSH rules no longer apply. A first hand-edited remit refresh (v1.1) froze Hermes at **2.55 vs old baseline 3.15** and read as a −0.60 drop — which looked alarming, so it was investigated three ways:
1. **Old-remit control** (current code, original SSH remit, ×3): **2.70 / 2.90 / 3.15 → median 2.90**.
2. **Diff-review** of the hand-edited rewrite: found it **added two HALT-severity obligations** (at-rest token encryption; OAuth cookie-partition isolation) and dropped the host-key/cert-pin intent while claiming "intent held constant" — i.e. it moved goalposts down.
3. **Fresh docs-only remit** (independently authored per the skill, ×3): **2.85 / 2.85 / 3.15 → median 2.85**.

Two independently-sourced remits agree at **~2.85–2.90**; the hand-edited remit's **2.55 was the low outlier** (~0.3 low), confirming the diff-review. **Resolution:** the **fresh docs-only remit is now the committed `tests/remits/hermes-agent-desktop.md`**, and Hermes is **re-frozen at 2.85** (band 2.55–3.15). Hermes is a **high-variance boundary target** (single runs spanned 2.55–3.15; 2 of 6 independent-remit runs hit Established). The real gap vs old 3.15 is ~−0.30 — within noise, **not a security regression** (Zero Trust held 3/Established nearly every run; 0–1 Criticals across all 9 runs). *(Secondary: `openhands` also evolved to V1 — SDK split into pinned packages — scanned in-band, median 2.15.)*

> **Resolved (2026-07-11).** Refreshing the shared remits broke the remit-verbatim quotes in the **superseded `v0.7.7-claude48`** (and older archival) sets. Rather than defer, `test_render.py` now **scopes the remit-verbatim check to the current baseline set** (`CURRENT_BASELINE = "v1.0.2-claude48"`) — archival sets keep their schema + byte-render checks but are no longer re-bound to evolving remits. The harness is **406 passed, 0 failed**, and all **12 `v1.0.2-claude48` targets pass clean** (schema · byte-render · remit-verbatim).

## Per-target judgment calls (from the scans — for your results-quality review, O3)

**CraftBot** (14 findings, weighted 1.00): remit drafted from README/docs treats it as a single-operator local agent; **4 operator open-questions** appended to the remit (shell/code exec → isolate-or-approve; inbound auto-reply → sender check; outbound sends → approval; third-party MCP/imported-project provenance) — several Critical/High grade against these. **Shell execution** is arguably an *intended* capability for a general local agent — flagged for a ruling. The living-UI sidecar (`0.0.0.0` + wildcard CORS) scored Medium (it's a generated project's sidecar, not the agent's own control plane) — reasonable people could rate it High.

**uAgents** (8 findings, weighted 2.00): scoped to the **framework runtime's own defaults**, not a deployed agent (confirm framing, O5). **Plaintext private-key storage** scored **Critical** (gap on a forbidden-data-movement MUST-NOT) — defensible as High. Default `0.0.0.0` bind rated **Medium** (public bind alone grants no capability; handlers still verify signatures) though SKILL guidance would push a gap-on-approval higher. Remit open-questions: default bind interface, inspector-on-by-default, approved key-at-rest mechanism.

**Agentforce** (8 findings, weighted 1.15): **converges with the prior 0.7.8 example** (identical 1.15 weighted, same core themes) — a strong consistency signal that the analysis is genuine. One **net-new Medium** (`PRAX-…-007`: the LWC loads a config-derived script URL with no trusted-domain check) — admin-configured, so defense-in-depth; flagged for a severity look. The `filter_from_agent:False` remediation is hedged (assumes a platform capability not verifiable from the package alone).

## Deferred to later phases (tracked, not Phase-1 blockers)
- **Bands + `BASELINE.md`** for the new targets — set after median-of-3 (O2).
- **Retained-target Foundation ✅ spot-checked** (single 1.0.x run each, 11/12 in-bounds — `FOUNDATION_SPOTCHECK.md`); the **median-of-3 re-freeze** into `v1.0.2-claude48` is still pending, and **Hermes needs its remit refreshed first** (O8). Both deprecated targets (`sweep`, `langchain-sql`) confirmed live/clonable.
- **Phase 3 retirements** (#69 `sweep`, #70 `langchain-sql`) — evaluated only after additions are proven.

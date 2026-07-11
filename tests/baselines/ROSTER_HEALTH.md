<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Roster health — v1.0.2 baseline set (12 active + 3 retired)

> **Retired 2026-07-11 (Phase 3):** `sweep` (#69), `langchain-sql` (#70), `devika` — kept in
> the table below (marked 🗑) with their data, as the record behind the retirement decision.

> Companion to `v1.0.2-claude48/BASELINE.md`. Captures **project prominence** (GitHub
> stars) and **development activity/freshness** (0–5) for each target, so the roster's
> keep / retire / add decisions are grounded in whether a project is *live and
> mainstream* — not just how it scores on RAISE. The two 0–5 axes here (**Freshness**
> and **RAISE maturity**) are deliberately on the same scale so **activity × maturity**
> can be plotted directly (see "Activity vs. maturity" below).

## Method
- **Stars / push / archived:** `gh api repos/<owner>/<repo>` — repo-level.
- **Commit cadence:** `gh api repos/<owner>/<repo>/stats/participation` — merged commits
  to the default branch, summed over the trailing 4 / 12 / 52 weeks.
- **Freshness (0–5):** blended from last-push recency **and** sustained cadence, with a
  hard cap for archived/dormant repos. Rubric:
  - **5** pushed ≤1 wk **and** heavy ongoing cadence (hundreds/qtr)
  - **4** pushed ≤1 mo, clearly active (tens+/qtr)
  - **3** pushed ≤2 mo, maintained but decelerating
  - **2** pushed ≤3–4 mo **or** sparse sporadic cadence (maintenance-only)
  - **1** archived, **or** pushed >4 mo with near-zero cadence (dormant)
  - **0.5** dormant ~10 mo+, ~1 commit/yr (effectively abandoned but not archived)
- **RAISE maturity (0–5):** the frozen **median-of-3** weighted score from `BASELINE.md`.
- **Snapshot date:** 2026-07-11. Stars/commits drift; re-run before citing externally.

> **Caveat — repo-level metrics.** Stars/commits describe the *whole repo*. For monorepo
> targets we scan only a slice, so stars measure **project** prominence, not the scanned
> component's. Flagged with † below.

## Data (snapshot 2026-07-11)

Sorted by stars.

| Target | Repo | Set | ★ Stars | Last push | Commits 4/12/52 wk | **Fresh 0–5** | RAISE median | Maturity |
|---|---|:--:|--:|---|--:|:--:|--:|---|
| hermes | NousResearch/hermes-agent† | ret | 213,129 | today | 3301 / 10175 / 15140 | **5.0** | 2.85 | Partial |
| openhands | All-Hands-AI/OpenHands† | ret | 80,454 | today | 171 / 533 / 2316 | **5.0** | 2.30 | Partial |
| autogen | microsoft/autogen† | ret | 59,656 | ~3 mo | 0 / 0 / 77 | **2.0** | 2.00 | Partial |
| aider | Aider-AI/aider† | ret | 47,288 | ~7 wk | 0 / 17 / 196 | **3.0** | 2.00 | Partial |
| openai-cs | openai/openai-agents-python† | ret | 27,814 | today | 105 / 363 / 1227 | **5.0** | 1.60 | Ad hoc |
| deepagents | langchain-ai/deepagents | ret | 26,095 | today | 478 / 1170 / 2681 | **5.0** | 2.70 | Partial |
| devika | stitionai/devika | 🗑 retired | 19,538 | ~9.5 mo | 0 / 0 / 1 | **0.5** | 0.60 | Absent |
| sweep | sweepai/sweep | 🗑 retired #69 | 7,701 | ~10 mo | 0 / 0 / 1 | **0.5** | 1.70 | Ad hoc |
| uagents | fetchai/uAgents | **new** | 1,639 | 2 d | 1 / 23 / 114 | **3.5** | 2.00 | Partial |
| craftbot | CraftOS-dev/CraftBot | **new** | 373 | 1 d | 107 / 409 / 1149 | **5.0** | 1.15 | Ad hoc |
| langchain-sql | langchain-ai/langchain-community† | 🗑 retired #70 | 286 | ~3 wk | 1 / 15 / 117 | **1.0** 🗄️ | 1.30 | Ad hoc |
| finbot | OWASP-ASI/finbot-ctf-demo | ret | 65 | ~6 mo | 0 / 0 / 73 | **1.5** | 0.90 | Absent |
| helperbot | opena2a-org/damn-vulnerable-ai-agent | ret | 57 | 3 d | 13 / 41 / 132 | **4.0** | 0.75 | Absent |
| yaah | dirien/yet-another-agent-harness | ret | 19 | ~6 wk | 0 / 3 / 39 | **2.0** | 2.30 | Partial |
| agentforce | salesforce/help-agent-accelerator | **new** | 14 | ~5 wk | 0 / 7 / 14 | **2.0** | 1.70 | Ad hoc |

Legend: **ret** retained · **new** Phase-1 addition · ⚠️#69/#70 Phase-3 retirement candidate ·
🗄️ archived (read-only) · † repo-level metric covers more than the scanned scope.

## What the activity data says for roster decisions

- **Live mainstream anchors (Fresh 5.0):** hermes, openhands, openai-cs, deepagents,
  craftbot — pushed today/yesterday, heavy cadence. These keep the suite tracking
  *current* agent behavior; retain.
- **Retirement candidates confirmed dormant:** **sweep (0.5, #69)** and
  **langchain-sql (1.0 archived, #70)** are both effectively frozen — the activity data
  independently supports the Phase-3 sunset premise.
- **New dormancy flag — devika (0.5):** 19.5k stars but ~10 mo idle, 1 commit/yr; by
  activity it is as dead as sweep, yet it was **not** on the retirement list. Worth a
  Phase-3 look — it's a high-star name whose project has stalled.
- **Big-but-decelerating — autogen (2.0):** 59k stars, quiet ~3 mo; upstream momentum
  has largely moved to Microsoft's successor framework. Keep for now (still the
  reference AutoGen code-executor), but track for relevance.
- **Small-but-fresh punch-up:** craftbot (373★) and helperbot (57★) rate high on
  activity despite low stars — good for a baseline that must reflect *live* agents, not
  just popular ones.
- **Low-activity by design (not a concern):** finbot (CTF demo), agentforce (vendor
  sample), yaah (personal harness) — low cadence is expected for their category.

## Activity vs. maturity (all 12 medians frozen)
Both axes are 0–5: **Freshness (x)** and **RAISE median maturity (y)**. Split at
Fresh ≥ 3.0 (live) and Maturity ≥ 2.0 (Partial+). The four quadrants:

- **Live + weak — highest-value keeps** (Fresh ≥3, Maturity <2): **craftbot** (5.0 / 1.15),
  **openai-cs** (5.0 / 1.60), **helperbot** (4.0 / 0.75). Mainstream, actively developed,
  *and* under-enforced — the real-risk / real-users cell. Keep visible.
- **Live + stronger — good citizens** (Fresh ≥3, Maturity ≥2): **hermes** (5.0 / 2.85),
  **deepagents** (5.0 / 2.70), **openhands** (5.0 / 2.30), **aider** (3.0 / 2.00),
  **uagents** (3.5 / 2.00). The "does it mostly right and is maintained" exemplars.
  (hermes 2.85 sits on the Established line — highest posture in the set, and a high-variance
  target: 2.70–3.15.)
- **Dormant — retirement zone** (Fresh <2, any maturity): **sweep** (0.5 / 1.70, #69),
  **langchain-sql** (1.0🗄️ / 1.30, #70), **devika** (0.5 / 0.60) — **all three retired
  2026-07-11**. **finbot** (1.5 / 0.90) also sits here but is *kept* (a live OWASP CTF
  reference target, low activity by design, not dormant abandonment).
- **Low-activity by design** (Fresh ~2, sample/vendor repos): **autogen** (2.0 / 2.00),
  **yaah** (2.0 / 2.30), **agentforce** (2.0 / 1.70). Kept for coverage, not concern.

_Scatter input: the RAISE-median (y) and Fresh (x) columns in the table above._

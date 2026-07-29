<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Full Suite Run — v1.2 RC (reverted-scoring stack)

> **STATUS: PASS** (theme-coverage gate). 12/12 targets, no dropped Critical
> theme on any target; all structural checks green; zero stalls, zero render
> failures. Validates the **1.2 release-candidate infra stack** — pre-#48
> scoring restored, N/A plumbing retained. This is a gate for the infra
> revert, NOT a re-baseline; `v1.1-claude48` remains the frozen baseline.

## Inputs

- **Skill under test:** branch `1.2` @ `7b53ccb` — scoring guidance reverted to
  the pre-#48 text (`9ebbe66`); schema-3.0 N/A plumbing retained (inert here,
  no target emitted N/A). Canonical 12-step protocol, no overrides.
- **Reference model:** `opus` alias, **verified = `claude-opus-4-8`** at run
  time (2026-07-28 probe). Same model as the baseline.
- **Baseline:** `tests/baselines/v1.1-claude48/`. Gate = theme coverage; weighted
  score advisory vs the per-target bands in `tests/README.md`.
- **Sources:** `local/v1.2-stage0/src/<target>`; remits `tests/remits/<target>.md`.

## Per-target table

| target | baseline wtd | RC wtd | Δ | band | C/H/M/L(/I) | dur | verdict |
|---|--:|--:|--:|:--:|---|--:|:--:|
| helperbot | 0.75 | 0.75 | +0.00 | in | 3/3/3/0 | ~10m | ✅ |
| finbot | 0.90 | 0.90 | +0.00 | in | 5/2/5/0 | ~11m | ✅ |
| craftbot | 1.15 | 1.60 | **+0.45** | **over +0.15** | 3/6/4/0 | ~15m | ✅ gate; ⚠ band |
| openai-customer-service | 1.60 | 1.75 | +0.15 | top edge | 2/2/3/0 | ~15m | ✅ |
| uagents | 2.00 | 1.85 | −0.15 | in | 3/1/4/0 | ~20m | ✅ |
| aider | 2.00 | 1.85 | −0.15 | low edge | 0/3/5/0 | ~10m | ✅ |
| salesforce | 1.70 | 2.00 | +0.30 | **over +0.15** | 0/1/5/1 | ~15m | ✅ gate; ⚠ band |
| autogen-code-executor | 2.00 | 2.15 | +0.15 | top edge | 1/3/5/1 | ~15m | ✅ |
| openhands | 2.30 | 2.15 | −0.15 | floor | 0/1/3/2/1 | ~11m | ✅ |
| yaah | 2.30 | 2.45 | +0.15 | top edge | 0/2/6/0 | ~35m | ✅ |
| hermes-agent-desktop | 2.85 | 2.85 | +0.00 | center | 0/1/5/2 | ~25m | ✅ |
| deepagents-cli | 2.70 | 3.00 | **+0.30** | **over +0.15** | 0/1/2/2 | ~9m | ✅ gate; ⚠ band |

## Suite verdict

- **GATE: PASS.** Every baseline Critical theme is covered in the RC run; no
  material finding dropped. Hard gate (theme coverage) met on all 12.
- **Reliability: clean.** 12/12 completed, zero watchdog stalls, both scripts
  exit 0 on every target, all JSON schema-valid, all renders byte-consistent.
  Durations ~9–35 min (yaah longest); none stalled.
- **Score advisory:** mean |Δ| **0.163**, mean signed Δ **+0.087** — the known
  mild Opus-4.8 upward lean, consistent with the baseline's own posture note.
  9/12 in band; **3 above band** (craftbot +0.45, salesforce +0.30,
  deepagents +0.30) — all in the lenient direction, none gate-failing.

## Advisories for human review (none block the infra gate)

1. **craftbot +0.45, out of band, NEW Critical.** RC surfaced hardcoded
   base64-split OAuth client secrets in `embedded_credentials.py` (Google/
   Slack/Notion/etc.) absent from the 07-11 baseline — plus two baseline
   Criticals reclassified High. The new committed-secret file strongly
   suggests **upstream CraftBot target drift since the freeze**; rule that out
   before attributing the score move to Praxen. (If drift is confirmed, it is
   a source-refresh item, not a scoring regression.)
2. **Two Critical→High severity demotions on retained substance:**
   deepagents-cli MCP-URL-TLS (baseline Critical → RC High; `tests/README.md`
   explicitly expected this to surface as Critical) and salesforce indirect
   prompt injection (baseline Critical → RC Medium, theme intact). Severity
   judgment on borderline calls; advisory.
3. **Mild consolidation tendency:** RC runs merge related baseline findings
   into fewer, broader entries (finding counts dip while theme coverage
   holds) — visible on openhands (11→7), uagents, yaah. Healthy direction,
   worth watching if it deepens.

## Bearing on 1.2

This run validates the reverted-scoring infra stack as **behaviorally
equivalent to the shipped v1.1 baseline** — the prerequisite for building 1.2
on it. It does NOT re-baseline (the OWASP-2026 KB refresh, the release
headline, will re-scan and re-freeze). Next: the deepagents ×3
subject-declaration check on this validated stack, then productization; then
the OWASP-2026 KB pass. See `plans/RELEASE_1.2_PLAN.md`.

Run data: `tests/runs/v1.2-rc-regression/<target>-out/` (12 findings JSON +
HTML + TXT).

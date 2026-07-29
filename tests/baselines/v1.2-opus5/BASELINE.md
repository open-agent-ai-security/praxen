<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Baseline — v1.2-opus5 (current)

The **v1.2 fresh baseline.** Supersedes `v1.1-claude48` (now archival). This is a genuine
re-scan, not a re-tag: **model, knowledge bases, and remits all changed**, so it is **not**
directly comparable to v1.1 — the v1.1 numbers are context, not a pass/fail gate. Roster
prominence + development-activity data lives in `../ROSTER_HEALTH.md`.

## What changed from v1.1

- **Model:** Claude Opus 5 (`claude-opus-5[1m]`), pinned per-agent via
  `.claude/agents/opus5-scanner.md`. Every scan self-reported its model identity at start and
  end; **zero classifier switches across ~90 scans** — Praxen's cybersecurity workload does
  not trigger the Opus 5 fallback.
- **Knowledge bases:** OWASP LLM/Agentic **2026**; skill branch `1.2`.
  `praxen_version 1.2.0`, `schema_version 3.0` (activates the remit-verbatim render invariant).
- **Remits:** fully re-authored — **blind generation from each agent's docs** →
  Open-Questions resolution → redundancy polish → FP-driven over-reach fixes. See provenance
  below.

## Freeze method — median-of-3

Each target was scanned **3× on identical inputs** (remit, source, scope byte-identical), and
is frozen on its **median-weighted run** — one real scan, never an aggregate. The 3× also
characterized run-to-run variance (bands below).

| Target | Median run | Weighted RAISE | Band (3× spread) |
|---|---|---|---|
| helperbot | run2 | 0.60 | 0.15 |
| finbot | run2 | 0.90 | 0.55 (wide) |
| craftbot | run1 | 1.30 | 0.15 |
| autogen-code-executor | run2 | 1.55 | 0.55 (wide) |
| salesforce-help-agent-accelerator | run1 | 1.55 | 0.00 |
| uagents | run1 | 1.70 | 0.45 (wide) |
| aider | run1 | 1.70 | 0.30 |
| openai-customer-service | run2 | 1.75 | 0.30 |
| openhands | run2 | 2.00 | 0.10 (re-scan) |
| deepagents-cli | run1 | 2.15 | 0.15 |
| yaah | run1 | 2.15 | 0.00 |
| hermes-agent-desktop | run1 | 2.55 | 0.30 |

**Mean median RAISE 1.66.** Variance sits inside the documented envelope
(`docs/understanding-variability.md`): 11/12 within ±0.30 of median; finbot the single
"occasional ±0.5" case; none beyond. Themes reproduced every run for every target.

## Sources & scope

Pinned SHAs recorded in `../../../local/v1.2-owasp2026-baseline/SOURCES.md`. OpenHands is
scanned at its **pre-migration** commit (the Agent-Canvas rewrite cleared the Python tree).
**deepagents re-scoped `libs/cli` → `libs/code`**: the runtime moved to the sibling package;
the subject follows the code (`tests/scan_instructions/deepagents-cli.md`).

## Remit provenance & known caveats

Remits were re-authored by the tool (blind, docs-only) and then hardened. A post-freeze FP
sweep (one independent cross-model reviewer per target, verifying every finding against
source) found **zero detector false positives** across ~130 findings — but a recurring class
of **generator authoring defects**:

- **Fixed before freeze** (re-scanned 3×, medians above): **deepagents** (softened
  mandatory-sandbox; operator-install vs transitive-bundle), **yaah** (host-posture scoped to
  permission-mode; MCP-path audit), **hermes** (R-02 rescoped to authority-escalation
  exempting the self-improvement loop; R-16 credential classes; R-04 output scope; closure
  obligation surfaced; escalation response-not-restatement), **openhands** (R-04 "third-party"
  defined as outside the operator's own org so first-party / GitHub-maintained actions aren't
  flagged; Trusted Services notes dormant token-gated provider clients aren't trust expansion;
  R-17 defines what authorizes host-direct execution while keeping the host-child
  least-privilege obligation; PR/MR creation to authorized repos is allowlist-gated, not
  per-action approval). Re-scan held the weighted score at 2.00; the change was in the finding
  mix — Highs dropped and the over-reaching supply-chain / approval findings resolved to
  positives, with every real core (control-plane auth-absent, CORS-open, plaintext-secret
  store, `os.environ.copy()` host-child leak, missing repo allowlist) preserved.
- **Clean** (no cleanup): openai-cs.
- **Known over-reach, not yet fixed** (documented, tracked for follow-up): **helperbot**
  (fabricated topic-scope), **craftbot** (fabricated config params; GUI per-action approval),
  **salesforce** (invented public-only KB rule; overstated no-human-queue), **autogen**
  (mis-scoped R-01), **uagents** (value-transfer vs authorized-registration collision). These
  produce a handful of over-severe / mis-mapped findings in their frozen reports. **aider** is
  tracked separately under #200.

The **durable fix is the generator, not per-remit hand-editing** — see RFE **#198**
(emit well-formed, docs-grounded, non-over-reaching statements). The heading-as-rule pattern
(closure obligations left implicit) is systemic across remits and is part of #198.

## Related RFEs (open)

- **#195** — RAISE band-edge variance (drives the finbot/autogen 0.55 spreads).
- **#196** — finding decomposition / severity-borrowing.
- **#198** — remit generator authoring quality (the durable fix for the over-reach above).
- **#197** — Thinking Modes (user-facing fidelity tiers) — not baseline-related.

All 12 pass `python3 tests/render/test_render.py` (schema-valid · HTML/TXT byte-identical
re-render · every `policy_rule_text` quoted verbatim from `tests/remits/<slug>.md`).

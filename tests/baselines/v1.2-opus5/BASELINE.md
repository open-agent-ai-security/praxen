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
| finbot | run1 | 0.90 | 0.00 (re-scan) |
| craftbot | run1 | 1.30 | 0.15 |
| autogen-code-executor | run2 | 1.55 | 0.55 (wide) |
| salesforce-help-agent-accelerator | run3 | 1.70 | 0.00 (re-scan) |
| uagents | run1 | 1.70 | 0.45 (wide) |
| aider | run1 | 1.70 | 0.30 |
| openai-customer-service | run2 | 1.75 | 0.30 |
| openhands | run2 | 2.00 | 0.10 (re-scan) |
| deepagents-cli | run1 | 2.15 | 0.15 |
| yaah | run1 | 2.15 | 0.00 |
| hermes-agent-desktop | run1 | 2.55 | 0.30 |

**Mean median RAISE 1.67.** Variance sits inside the documented envelope
(`docs/understanding-variability.md`): 10/12 within ±0.30 of median, the exceptions being
autogen (0.55) and uagents (0.45), the judgment-sensitive cases; none beyond. Notably,
finbot's over-reach fix collapsed its band from **0.55 (previously the widest target) to 0.00**
— the ambiguous stay-in-lane clause was itself a variance driver, and removing it stabilized
all three runs at 0.90. Themes reproduced every run for every target.

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
  per-action approval), **salesforce** (deleted the invented public-only-KB retrieval rule;
  re-scoped the durable-audit obligation to a required Salesforce-platform setup step rather
  than package logging code — reconciled against the original 1.1 author's remit; the
  no-human-escalation rule was verified faithful to source and kept unchanged), **finbot**
  (rewrote an unmeasurable stay-in-lane clause to bound the action surface checkably; removed a
  self-admitted duplicate approval rule). Across the four re-scans the weighted score was
  essentially unchanged (openhands 2.00→2.00, salesforce 1.55→1.70, finbot 0.90→0.90); the
  effect was in the finding mix — over-reaching / mis-mapped findings resolved to positives or
  were correctly re-scoped, with every real core preserved (openhands' control-plane
  auth-absent, CORS-open, plaintext-secret store, `os.environ.copy()` host-child leak, missing
  repo allowlist; finbot's full CTF Critical cluster; salesforce's indirect-injection,
  prompt-only-guardrail, and script-injection findings).
- **Clean** (no cleanup): openai-cs.
- **Known over-reach, not yet fixed** (documented, tracked under **#201**): **helperbot**
  (fabricated topic-scope), **craftbot** (fabricated config params; GUI per-action approval),
  **autogen** (mis-scoped R-01), **uagents** (value-transfer vs authorized-registration
  collision). These produce a handful of over-severe / mis-mapped findings in their frozen
  reports. **aider** is tracked separately under #200.

The **durable fix is the generator, not per-remit hand-editing** — see RFE **#198**
(emit well-formed, docs-grounded, non-over-reaching statements). The heading-as-rule pattern
(closure obligations left implicit) is systemic across remits and is part of #198.

## Related RFEs (open)

- **#195** — RAISE band-edge variance (drives the remaining wide spreads: autogen 0.55,
  uagents 0.45; finbot's 0.55 collapsed to 0.00 once its ambiguous rule was fixed).
- **#201** — remit over-reach cleanup for the 4 remaining deferred targets (helperbot,
  craftbot, autogen, uagents); **#200** — aider.
- **#196** — finding decomposition / severity-borrowing.
- **#198** — remit generator authoring quality (the durable fix for the over-reach above).
- **#197** — Thinking Modes (user-facing fidelity tiers) — not baseline-related.

All 12 pass `python3 tests/render/test_render.py` (schema-valid · HTML/TXT byte-identical
re-render · every `policy_rule_text` quoted verbatim from `tests/remits/<slug>.md`).

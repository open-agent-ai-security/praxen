<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Example Scans

Real analyses from **Praxen** against three AI agents — two deliberately vulnerable training agents and one real-world open-source product — so you can see Praxen in action.

> **These are completed reports, not scan targets.** This directory is showcase *output* — what Praxen produces — plus the remit each analysis used. It is **not** a source tree to point a scan at. A Praxen scan always takes two separate inputs: a **Worker Remit** and a **separate agent source tree**. To reproduce one of these, use the remit here (or the matching one under [`../tests/remits/`](../tests/remits/)) and clone the upstream **Source** linked below — see [Quickstart](../docs/quickstart.md) for the step-by-step.

For each example we followed the standard Praxen analysis workflow:

1. Wrote a `WORKER_REMIT.md` describing the agent's *intended* scope — what a legitimate version of this agent should and shouldn't do, who it can talk to, what requires approval.
2. Ran Praxen against the public source repository.
3. Collected the two showcase artifacts Praxen produces for every analysis (Praxen also writes a `.txt` stdout summary; the HTML and JSON are what we link below).

**HTML vs. JSON:** The `*-analysis.html` file is a human-readable pretty-print of the findings data. The `*-findings.json` file is the same information structured for automated ingestion — use it for dashboards, ticketing, compliance pipelines, or diffing results across analyses.

**CI contract:** `python3 tests/render/test_render.py` schema-validates every example's `*-findings.json` and re-renders its HTML/TXT byte-identically from that JSON. It also checks that each `WORKER_REMIT.html` is in sync with its `WORKER_REMIT.md` (the pretty remit is a deterministic render — see [`render_remit.py`](../skills/behavior-verifier/render_remit.py)). When `render.py`, `render_remit.py`, or `report_template.html` changes — or when a remit is edited — regenerate before merging: reports from the canonical JSON, and remits with `python3 tests/render/render_all_remits.py` — same workflow as [`tests/baselines/`](../tests/baselines/).

---

## FinBot — invoice processing agent

**Source:** [OWASP-ASI/finbot-ctf-demo](https://github.com/OWASP-ASI/finbot-ctf-demo) — CineFlow Productions autonomous invoice processor from the OWASP Agentic AI CTF.

Praxen produced 16 findings (6 Critical, 3 High, 7 Medium), weighted RAISE posture 0.90 / 5.0 (Absent) — including an unauthenticated `/admin/finbot/goals` endpoint that writes attacker-supplied text straight into the agent's system prompt (the writable `custom_goals`, concatenated under an "OVERRIDE ABOVE IF CONFLICTING" directive), an entire unauthenticated `/admin/*` surface reaching config, goals, review, and vendor-trust routes, an `_approve_invoice` path that marks invoices approved with no gate on amount, injection flag, or decision confidence, a fallback rule engine that overrides the manual-review threshold when attacker-supplied keywords appear, `Vendor.to_dict` serving bank account, routing number, and tax ID through three unauthenticated endpoints, injection detection that is advisory-only and disabled by an unauthenticated toggle, no action logging anywhere, and the canonical goal-hijack → autonomous-payment chain.

- Worker Remit — [pretty ↗](https://open-agent-ai-security.github.io/praxen/examples/finbot/WORKER_REMIT.html) · [markdown](finbot/WORKER_REMIT.md) — the agent's intended-scope policy
- [`finbot-analysis.html`](https://open-agent-ai-security.github.io/praxen/examples/finbot/finbot-analysis.html) — human-readable analysis report (rendered on GitHub Pages)
- [`finbot/finbot-findings.json`](finbot/finbot-findings.json) — machine-readable findings (preferred for automated ingestion)

---

## HelperBot — internal employee assistant

**Source:** [opena2a-org/damn-vulnerable-ai-agent](https://github.com/opena2a-org/damn-vulnerable-ai-agent) — the HelperBot persona from the DVAA training platform.

A general-purpose conversational assistant (OpenAI-compatible chat) whose remit calls for untrusted-input handling, prompt-injection refusal, system-prompt confidentiality, a bounded tool inventory, durable audit logging, and rate limiting — controls the code largely lacks or actively contradicts. Praxen produced 13 findings (3 Critical, 4 High, 5 Medium, 1 Low), weighted RAISE posture 0.60 / 5.0 (Absent) — including a chat endpoint that detects override attempts and then complies with them instead of refusing, an internal API key carried in the system prompt alongside instructions to disclose its own configuration, an unauthenticated chat endpoint with wildcard CORS bound to every interface, affirmation of attacker-fabricated prior agreements, a declared inventory carrying filesystem-write and web-egress tools beyond the remit's grant with no capability-boundary check, attack events landing in a 500-entry in-memory ring buffer with no durable sink or alerting, no rate or token limit on the chat endpoint, anonymous vendor telemetry emitted by default, and committed credential-shaped literals interpolated into agent configuration.

- Worker Remit — [pretty ↗](https://open-agent-ai-security.github.io/praxen/examples/helperbot/WORKER_REMIT.html) · [markdown](helperbot/WORKER_REMIT.md) — the agent's intended-scope policy
- [`helperbot-analysis.html`](https://open-agent-ai-security.github.io/praxen/examples/helperbot/helperbot-analysis.html) — human-readable analysis report (rendered on GitHub Pages)
- [`helperbot/helperbot-findings.json`](helperbot/helperbot-findings.json) — machine-readable findings (preferred for automated ingestion)

---

## Salesforce Help Agent Accelerator — real-world open-source product

**Source:** [salesforce/help-agent-accelerator](https://github.com/salesforce/help-agent-accelerator) — Salesforce's open-source Help Agent Accelerator (HAA), an Agentforce knowledge-answering assistant. Unlike the two CTF/training agents above, this is a **real, shipping open-source product**; the scan ran against the public codebase as-is (no deployed agent or live Salesforce org). Contributed by [@rossja](https://github.com/rossja).

Praxen produced 12 findings (6 High, 4 Medium, 2 Low), weighted RAISE posture 1.70 / 5.0 (Ad hoc) — the agent earns partial credit for a narrow, platform-enforced tool inventory and explicit grounding instructions, but nearly all enforcement lives in the system prompt: the override-resistance instruction covers user input only and leaves instructions embedded in retrieved Knowledge articles unguarded (indirect prompt-injection exposure), the `off_topic` topic offers a human escalation the `escalation` topic states does not exist, the LWC appends a bootstrap script from an operator-supplied URL with no protocol check or domain allowlist, every behavioral guardrail is a natural-language instruction with no deterministic pre- or post-processing gate, Einstein Audit and Session Tracing ship documented as optional though a durable audit trail is required, citations ship disabled while the agent is instructed to always cite sources, and no adversarial-test artifact exists for a public unauthenticated agent whose entire guardrail set is prompt-resident.

- [`salesforce-help-agent-accelerator/README.md`](salesforce-help-agent-accelerator/README.md) — how this remit and report were generated (Claude Opus 5, Praxen v1.2 baseline)
- Worker Remit — [pretty ↗](https://open-agent-ai-security.github.io/praxen/examples/salesforce-help-agent-accelerator/WORKER_REMIT.html) · [markdown](salesforce-help-agent-accelerator/WORKER_REMIT.md) — the agent's intended-scope policy
- [`salesforce-help-agent-accelerator-analysis.html`](https://open-agent-ai-security.github.io/praxen/examples/salesforce-help-agent-accelerator/salesforce-help-agent-accelerator-analysis.html) — human-readable analysis report (rendered on GitHub Pages)
- [`salesforce-help-agent-accelerator/salesforce-help-agent-accelerator-findings.json`](salesforce-help-agent-accelerator/salesforce-help-agent-accelerator-findings.json) — machine-readable findings (preferred for automated ingestion)

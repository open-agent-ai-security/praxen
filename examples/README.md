<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Example Scans

Real analyses from **Praxa** against two deliberately vulnerable AI agents, so you can see Praxa in action.

For each example we followed the standard Praxa analysis workflow:

1. Wrote a `WORKER_REMIT.md` describing the agent's *intended* scope — what a legitimate version of this agent should and shouldn't do, who it can talk to, what requires approval.
2. Ran Praxa against the public source repository.
3. Collected the two showcase artifacts Praxa produces for every analysis (Praxa also writes a `.txt` stdout summary; the HTML and JSON are what we link below).

**HTML vs. JSON:** The `*-analysis.html` file is a human-readable pretty-print of the findings data. The `*-findings.json` file is the same information structured for automated ingestion — use it for dashboards, ticketing, compliance pipelines, or diffing results across analyses.

---

## FinBot — invoice processing agent

**Source:** [OWASP-ASI/finbot-ctf-demo](https://github.com/OWASP-ASI/finbot-ctf-demo) — CineFlow Productions autonomous invoice processor from the OWASP Agentic AI CTF.

Praxa produced 15 findings (5 Critical, 5 High, 3 Medium, 1 Low, 1 Informational), weighted RAISE posture 0.45 / 5.0 (Absent) — including unauthenticated goal injection via `POST /api/admin/finbot/goals` writing attacker text straight into the agent's system prompt (the writable `finbot_config.custom_goals` column), an `_approve_invoice` path that sets `payment_processed=True` with no gate on amount, the manual-review threshold, the fraud result, or the caller, vendor-supplied invoice description text flowing verbatim into the LLM context, a `fraud_detection_enabled` flag toggleable from an unauthenticated endpoint, and the canonical goal-hijack → autonomous-payment chain with no logging to catch it.

- [`finbot/WORKER_REMIT.md`](finbot/WORKER_REMIT.md) — intended-scope policy
- [`finbot/finbot-analysis.html`](finbot/finbot-analysis.html) — human-readable analysis report
- [`finbot/finbot-findings.json`](finbot/finbot-findings.json) — machine-readable findings (preferred for automated ingestion)

---

## HelperBot — internal employee assistant

**Source:** [opena2a-org/damn-vulnerable-ai-agent](https://github.com/opena2a-org/damn-vulnerable-ai-agent) — the HelperBot persona from the DVAA training platform.

A general-purpose assistant whose remit assumes path-scoped `read_file`/`write_file`, untrusted-input handling, prompt-injection refusal, system-prompt confidentiality, per-tool-call audit logging, and a 20-call/session cap — every one of which is either unimplemented or actively contradicted in the code. Praxa produced 13 findings (5 Critical, 4 High, 3 Medium, 1 Informational), weighted RAISE posture 0.60 / 5.0 (Absent) — including `read_file`/`write_file` with no path confinement, user input reaching the model with no validation or prompt-injection handling, an LLM-mode system prompt that embeds a literal internal API key and instructs the agent to disclose its own configuration, every feature flag (`inputValidation`/`outputFiltering`/`toolApproval`/`rateLimiting`/`auditLogging`) set to `false`, the request handler rewarding prompt-injection keywords with attacker-favorable responses, and the injection → `write_file` chain with no audit trail.

- [`helperbot/WORKER_REMIT.md`](helperbot/WORKER_REMIT.md) — intended-scope policy
- [`helperbot/helperbot-analysis.html`](helperbot/helperbot-analysis.html) — human-readable analysis report
- [`helperbot/helperbot-findings.json`](helperbot/helperbot-findings.json) — machine-readable findings (preferred for automated ingestion)

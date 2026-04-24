<!--
  Copyright © 2026 Exabeam, Inc. All Rights Reserved.
  Confidential and Proprietary. Do not distribute. Use by permission only.
-->

# Exabeam Deckard Agent Security Scanner
**Version 0.6.6**

**A security scanner for AI agents.** The Exabeam Deckard Agent Security Scanner (**Deckard Scanner**) inspects the environment an AI agent runs in — its code, skill files, tool definitions, configuration, and dependencies — and evaluates it against a defined policy. Findings land in a local HTML report. Nothing phones home.

---

## What It Detects

Every scan classifies findings against **four industry-standard frameworks simultaneously**:

- **OWASP Top 10 for LLM Applications 2025** — every finding applicable to LLM-level risks is tagged with the correct `LLM0X` category and full name (e.g., `LLM01 — Prompt Injection`, `LLM02 — Sensitive Information Disclosure`).
- **OWASP Top 10 for Agentic AI Applications 2026** — agentic-specific patterns are tagged with the correct `ASI0X` category (e.g., `ASI01 — Agent Goal Hijack`, `ASI06 — Memory and Context Poisoning`).
- **OWASP Secure MCP Server Development Guide 2026** — when the scanner finds MCP server configuration in the workspace, it applies the full MCP minimum-bar checklist from the OWASP guide.
- **RAISE Framework** — a six-category AI security maturity model. Every scan produces a 0–5 score per category plus a weighted overall posture. See [`docs/RAISE.md`](docs/RAISE.md) for the reference and maturity scale.

### The detection patterns themselves

On top of the framework coverage above, every scan runs these named detections:

- **Policy-implementation divergence** — the code doesn't do what the policy document says
- **Credential exposure** — secrets in unexpected locations across the workspace
- **Configuration gaps** — auto-approved exec, disabled loop detection, missing rate limits
- **Capability drift** — new tools or outbound destinations not in the authorized baseline
- **Supply chain risk** — unpinned dependencies, unreviewed plugins, unknown provenance
- **Declared-but-never-consulted config / secret** — half-wired controls (`WEBHOOK_SECRET` defined, never checked; `ADMIN_TOKEN` declared, never enforced)
- **Empty stub files in security-relevant paths** — planned-but-not-implemented sandboxes, approval gates, redactors
- **Secondary prompt discovery** — session-loaded identity files (`SOUL.md`, `AGENTS.md`, `MEMORY.md`, etc.) audited as system prompts, with compound escalation when a writable session file meets a confirmed injection path (ASI06 memory-poisoning chain)
- **Compound signal reasoning** — individual findings chained together when they combine into a high-severity attack path

All findings are evaluated against a single source of truth: the **Worker Remit** — a markdown document that defines what the agent is authorized to be and do.

---

## What You Need

- **A coding agent** (tested against Claude Code). The scanner is distributed as a skill file the agent reads and executes — any coding agent capable of tool use and multi-step instruction-following should work.
- **A Worker Remit** for the agent you're scanning (or your coding agent can help you write one).

---

## Running a Scan

**There is no install step.** Unzip the release and open a Claude Code session in the unzipped directory — that's the whole setup.

**1. Drop the Deckard directory somewhere Claude Code can see it.**

**2. Optionally, place a `WORKER_REMIT.md` in the same directory.**

The Worker Remit describes what the monitored agent is authorized to do — its tools, channels, counterparties, and behavioral norms. If you include one, Deckard picks it up automatically. If you don't, Claude Code will help you write one before scanning.

**3. Open a Claude Code session and read the scanner skill:**

```
Please read and run skills/environment_scanner.md to scan [agent workspace path].
```

Claude Code reads the workspace, evaluates it against the RAISE framework and Worker Remit, and writes the results to `./reports/`.

**4. Open the report.**

```
./reports/<agent-name>-scan-<timestamp>.html
```

Self-contained static HTML. Open directly in a browser — no server needed.

---

## The Worker Remit

The Worker Remit is the only artifact that needs to be customized per agent. Everything else in the Deckard package is generic.

**The remit is a policy document, not a system description.** Declare the intent — what the agent is for, what it's allowed to do, what it's forbidden to do, who it can communicate with, what requires your approval. You don't need to list tool names, file paths, or implementation details. Deckard reads the actual code and compares it against the policy you've declared.

What makes a rule good is that it states a verifiable constraint on behavior:

- ✓ *"Message bodies must never be retrieved for senders not in the authorized counterparty list"*
- ✗ *"Handle email appropriately"*

The first rule gives Deckard something to check against the code. The second doesn't. Write rules about what the agent *does*, not about how it does it.

A template is included in `WORKER_REMIT_template.md`.

---

## Example Scans

The [`examples/`](examples/) directory contains two real scans against deliberately vulnerable agents from the OWASP Agentic AI CTF and the Damn Vulnerable AI Agent project. Each example includes the Worker Remit we wrote, the human-readable HTML report, and the machine-readable JSON findings — see [`examples/README.md`](examples/README.md) for the full walkthrough.

---

## Tests (source repository only)

The [`tests/`](tests/) directory in the source repository is Deckard's pre-release regression suite. It lists nine test-target agents — ranging from intentionally-vulnerable CTF agents to mature production tools — along with the Worker Remit developed for each and the baseline findings a healthy scan should produce. See [`tests/README.md`](tests/README.md) for the full test plan and release checklist.

The test suite exists so that every Deckard release can be validated against the same agent posture spectrum (intentionally-broken → defense-conscious) and any regression — a missed critical theme, a dropped coverage area, an unexplained weighted-score shift — is visible before the release ships.

*`tests/` is not included in the distribution zip — users of the shipped scanner don't need the regression harness. Contributors and maintainers work from the source repository.*

---

## Security Foundations — Attribution

The scanner's [knowledge base](knowledge/) is built on, and every finding is classified against, the four frameworks above. Source material:

- **OWASP Top 10 for LLM Applications 2025** — [genai.owasp.org](https://genai.owasp.org/)
- **OWASP Top 10 for Agentic Applications 2026** — [genai.owasp.org](https://genai.owasp.org/)
- **OWASP Secure MCP Server Development Guide 2026** — [genai.owasp.org](https://genai.owasp.org/)
- **RAISE Framework** — a six-category AI security maturity model. See [`docs/RAISE.md`](docs/RAISE.md) for the reference and the maturity scale used in scan reports.

---

## Files

```
deckard/
  README.md                   ← You are here
  DECKARD_SPEC.md             ← Full specification
  WORKER_REMIT.md             ← (optional) drop your pre-built remit here
  WORKER_REMIT_template.md    ← Remit template
  knowledge/                  ← RAISE + OWASP knowledge base
  skills/
    environment_scanner.md    ← The scanner skill prompt
    report_template.html      ← Canonical HTML report template
  docs/
    RAISE.md                  ← RAISE framework reference + maturity scale
  examples/                   ← Example scans against real vulnerable agents
```


<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxa Documentation

**Praxa** is an agent behavior verifier. It compares an AI agent's declared policy (a Worker Remit) against whatever evidence is available about that agent — source code, live deployment state, or behavioral artifacts — and reports where observed behavior diverges from declared intent.

> *Make sure your agent does its job — and only its job.*

*Praxa is a project sponsored by [Exabeam](https://www.exabeam.com/).*

---

## Where to start

| If you are… | Read this first |
|---|---|
| Setting up Praxa for the first time | [Installation](installation.md) |
| Ready to run your first analysis | [Usage](usage.md) |
| Writing a Worker Remit for an agent | [Writing Worker Remits](writing-remits.md) |
| Looking at a report and trying to understand it | [Interpreting Reports](interpreting-reports.md) |
| Disagreeing with a finding or wanting to revise it | [Challenging and Revising Findings](challenging-findings.md) |
| Trying to understand the OWASP frameworks Praxa tags against | [OWASP Gen AI Security](owasp.md) |
| Trying to understand the RAISE maturity scoring | [The RAISE Framework](RAISE.md) |

---

## How Praxa Works (in 90 seconds)

Praxa reduces agent verification to a single comparison:

1. **You declare what the agent is supposed to do** in a [Worker Remit](writing-remits.md). This is the only artifact you customize per agent.
2. **You point Praxa at evidence about the agent** — its source code, live deployment files, conversation logs, or any combination.
3. **Praxa reads, compares, reports.** Every finding traces to a specific rule in the Worker Remit it violates, with evidence cited from the input.

The output is a self-contained HTML analysis report, a machine-readable JSON findings file, and a plain-text summary. Open the HTML in a browser; ingest the JSON in your pipeline.

---

## Three Input Shapes

Praxa is **not just a source-code analyzer.** Any of these — alone or in combination — are valid input:

- **Source repository** — a project directory, GitHub repo, or plugin source tree.
- **Running deployment** — live memory and bootstrap files (`MEMORY.md`, `SOUL.md`), operational logs (action reports, session JSONL, audit trails, escalation logs), live config.
- **Behavioral artifacts** — chat transcripts, email histories, conversation logs, decision records.

The methodology adapts. Categories the input doesn't cover are scored at lower confidence and explicitly noted in the report. See [Usage](usage.md) for how to point Praxa at each type.

---

## Frameworks

Every finding Praxa produces is classified against four industry-standard frameworks simultaneously:

- **OWASP Top 10 for LLM Applications 2025** — `LLM01`–`LLM10` tags
- **OWASP Top 10 for Agentic AI Applications 2026** — `ASI01`–`ASI10` tags
- **OWASP Secure MCP Server Development Guide 2026** — applied when MCP configuration is found
- **RAISE Framework** — six-category 0–5 maturity score; see [RAISE](RAISE.md)

For an overview of the OWASP Gen AI Security Project and a one-line gloss on each LLM, Agentic, and MCP risk, see [OWASP Gen AI Security](owasp.md).

---

## Quick reference

- Install: `/plugin marketplace add Exabeam/deckard` then `/plugin install praxa@exabeam`
- Skill name: `behavior-verifier`
- Output directory: `./reports/` relative to where you run the analysis
- Output files: `<agent>-analysis-<timestamp>.html`, `<agent>-findings-<date>.json`, `<agent>-analysis-<timestamp>.txt`

For the full specification, see [`PRAXA_SPEC.md`](../PRAXA_SPEC.md) at the repo root.

<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

<p align="center">
  <img src="graphics/praxen-banner.png" alt="Praxen — AI agent behavior verifier. Make sure your agent does its job, and only its job." width="720">
</p>

# Praxen
**agent behavior verifier · Version 0.7.7**

[![CI](https://github.com/open-agent-ai-security/praxen/actions/workflows/ci.yml/badge.svg)](https://github.com/open-agent-ai-security/praxen/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/open-agent-ai-security/praxen?sort=semver)](https://github.com/open-agent-ai-security/praxen/releases)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

> ### Make sure your agent does its job — and only its job.

That's where the risk actually lives: most agentic security and safety failures come down to an agent **not doing its job** — malfunctioning, misaligned, or adversarially subverted.

**Praxen** is named for **praxis** (Ancient Greek *πρᾶξις*), the act of turning theory into practice — which is exactly its job: verifying that an agent's *declared* intent (the theory) actually shows up in its *observed* behavior (the practice).

---

**📦 Install** with Claude Code — `/plugin marketplace add open-agent-ai-security/praxen` then `/plugin install praxen@open-agent-ai-security`. Full guide: [docs/installation.md](docs/installation.md).

**👀 See a real report** first — the [live FinBot analysis report](https://open-agent-ai-security.github.io/praxen/examples/finbot/finbot-analysis.html), rendered on GitHub Pages.

---

## Why behavior verification?

Praxen is the open-source reference implementation of **Agent Behavior Verification (ABV)** — a proactive control model for AI agents and digital workers. The premise is the same one identity and access management applies to human employees: every actor has an authorized role, and the controls have to actually enforce it.

And a misbehaving agent is hard to catch: whatever the cause, it surfaces the same way — as wrong behavior. So the only reliable signal is the *behavior* itself, measured as its deviation from declared intent.

That's why screening for prompt injections, or scanning code for known-bad patterns, isn't enough. Those are necessary but partial: they catch some inputs and some implementation flaws, not the question that actually matters — *is this agent going to do, or is it doing, the thing it was deployed to do, and nothing else?*

Answering that requires two things Praxen makes first-class:

1. **A wholesale way to define the agent's job** — its mission, authorized tools, approved channels, counterparties, and forbidden actions. That's the **Worker Remit**.
2. **A way to test reality against that definition** — point Praxen at the agent's code, its live deployment state, or its behavioral history, and get back exactly where observed behavior diverges from declared intent.

Define the job. Test against the job. Everything else in Praxen serves those two steps.

---

## How it works (30 seconds)

- You write a **Worker Remit** — a markdown policy document declaring what the agent is allowed to do — by hand, or have Praxen draft one from your description or docs. ([authoring guide](docs/writing-remits.md))
- You point Praxen at **evidence** — source code, deployment state, behavioral logs, governance docs, or any mix. ([usage](docs/usage.md))
- Praxen reports the **gap**. Every finding answers a single question: *does observed behavior match declared intent?* ([reading reports](docs/interpreting-reports.md))

Findings land in a self-contained HTML report, a machine-readable JSON file, and a plain-text summary in `./reports/`. Nothing phones home.

Praxen runs **before deployment** and on each release — pre-deployment verification of the agent's controls against its remit. Runtime monitoring of the deployed agent (Agent Behavior Analytics, **ABA**) is a complementary layer outside Praxen's scope.

---

## What Praxen verifies

Every analysis runs these named verification patterns:

- **Policy-implementation divergence** — the code or behavior doesn't do what the policy document says
- **Credential exposure** — secrets in unexpected locations across the workspace
- **Configuration gaps** — auto-approved exec, disabled loop detection, missing rate limits
- **Capability drift** — new tools or outbound destinations not in the authorized baseline
- **Supply-chain risk** — unpinned dependencies, unreviewed plugins, unknown provenance
- **Declared-but-never-consulted config / secret** — half-wired controls
- **Empty stub files in security-relevant paths** — planned-but-not-implemented sandboxes, approval gates, redactors
- **Secondary prompt discovery** — session-loaded identity files (`SOUL.md`, `AGENTS.md`, `MEMORY.md`, …) audited as system prompts
- **Compound signal reasoning** — individual findings chained when they combine into a high-severity attack path

Each finding is tagged against the **OWASP Top 10 for LLM Applications 2025**, **OWASP Top 10 for Agentic AI Applications 2026**, the **OWASP Secure MCP Server Development Guide 2026** (when MCP config is present), and the **RAISE Framework** (six-category 0–5 maturity score). Reports include per-framework **OWASP LLM Top 10 Coverage** and **OWASP Agentic Top 10 Coverage** grid sections — a 5×2 card layout showing each finding chip-linked to its category, with empty cells rendered as "No findings" so the grid reads as a coverage map. See [docs/owasp.md](docs/owasp.md) and [docs/RAISE.md](docs/RAISE.md) for the frameworks; see [docs/interpreting-reports.md](docs/interpreting-reports.md) for how they appear on a finding card.

---

## Get started

- [**Installation**](docs/installation.md) — plugin marketplace install or unzipped release
- [**Quickstart**](docs/quickstart.md) — first report against the bundled `finbot` example in about five minutes
- [**Writing Worker Remits**](docs/writing-remits.md) — authoring the policy document
- [**Usage**](docs/usage.md) — running an analysis end-to-end
- [**Interpreting Reports**](docs/interpreting-reports.md) — reading the HTML / JSON / TXT outputs
- [**Challenging and Revising Findings**](docs/challenging-findings.md) — what to do when you disagree
- [**Full documentation index**](docs/index.md)

**Prerequisites:** a coding agent (tested against [Claude Code](https://docs.claude.com/en/docs/claude-code/overview); any agent with tool-use and multi-step instruction-following works) and Python 3.9+ on the PATH for the report renderer. No `pip install`; the renderer is stdlib-only.

---

## Examples

The [`examples/`](examples/) directory contains real analyses against deliberately vulnerable agents from the OWASP Agentic AI CTF and the Damn Vulnerable AI Agent project. Each example ships with the Worker Remit we wrote, the HTML report, and the JSON findings — see [`examples/README.md`](examples/README.md) for the walkthrough.

---

## Repository

- [`docs/`](docs/) — full documentation
- [`examples/`](examples/) — sample analyses against real vulnerable agents
- [`tests/`](tests/) — pre-release regression suite (eleven targets, source repo only — not in the distribution zip)
- [`CHANGELOG.md`](CHANGELOG.md) · [`SECURITY.md`](SECURITY.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`PRAXEN_SPEC.md`](PRAXEN_SPEC.md) — full technical specification

---

## Project sponsor

Praxen is sponsored by [Exabeam](https://www.exabeam.com/). Exabeam contributed the initial code and continues to provide ongoing support and contributions to the project as part of its commitment to security in an increasingly agentic world.

---

## License

Praxen is licensed under the [Apache License, Version 2.0](LICENSE). Portions of the knowledge base (`skills/behavior-verifier/knowledge/`) are distilled from OWASP Gen AI Security Project publications and used under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see [NOTICE](NOTICE) for attribution. Contributions are welcome under the same license, with a DCO sign-off — see [CONTRIBUTING.md](CONTRIBUTING.md).

<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxa
**agent behavior verifier · Version 0.6.1**

> *Make sure your agent does its job — and only its job.*

*Praxa is a project sponsored by [Exabeam](https://www.exabeam.com/).*

---

**Praxa** verifies an AI agent's intended vs observed behavior. It compares the agent's declared policy (a **Worker Remit**) against whatever evidence is available about that agent — source code in a repository, live memory and log files from a running deployment, or chat transcripts and behavioral records — and reports where observed behavior diverges from declared intent. Findings land in a local HTML report. Nothing phones home.

Praxa is **not just a source-code scanner.** Any artifact that reveals what the agent does, has done, or is configured to do is valid input.

---

## Why behavior verification?

The number one risk area for agentic security and safety is simple to state: **the agent doesn't do its job.** A malfunctioning agent, a misaligned agent, an agent that's been adversarially subverted — from the outside they look the same, and what matters in every case is the *behavior*, measured as its deviation from intent.

That's why screening for prompt injections, or scanning code for known-bad patterns, isn't enough. Those are necessary but partial: they catch some inputs and some implementation flaws, not the question that actually matters — *is this agent going to do, or is it doing, the thing it was deployed to do, and nothing else?*

Answering that requires two things Praxa makes first-class:

1. **A wholesale way to define the agent's job** — its mission, authorized tools, approved channels, counterparties, and forbidden actions. That's the **Worker Remit**.
2. **A way to test reality against that definition** — point Praxa at the agent's code, its live deployment state, or its behavioral history, and get back exactly where observed behavior diverges from declared intent.

Define the job. Test against the job. Everything else in Praxa serves those two steps.

---

## Documentation

Full docs live in [`docs/`](docs/index.md). Quick links:

- [Installation](docs/installation.md) — plugin marketplace install or unzipped release
- [Usage](docs/usage.md) — running an analysis end-to-end
- [Writing Worker Remits](docs/writing-remits.md) — authoring the policy document
- [Interpreting Reports](docs/interpreting-reports.md) — reading the HTML / JSON / TXT outputs
- [Challenging and Revising Findings](docs/challenging-findings.md) — what to do when you disagree with the analysis
- [OWASP Gen AI Security](docs/owasp.md) — the OWASP frameworks Praxa tags findings against
- [The RAISE Framework](docs/RAISE.md) — the maturity rubric in depth

---

## How Praxa Works

Praxa reduces agent security to a single comparison:

1. **You declare what the agent is supposed to do** — its mission, authorized tools, approved channels, counterparties, and forbidden actions — in a Worker Remit.
2. **Praxa reads the available evidence** — code, deployment state, behavioral records — and treats it as the ground truth of what the agent actually is, has done, or is configured to do.
3. **Praxa reports the gap.** Every finding answers a single question: *does the observed behavior match the declared intent?*

This is policy-implementation divergence detection, end to end. The Worker Remit is the only artifact that needs to be customized per agent — everything else is generic.

---

## The Worker Remit

The Worker Remit is a markdown policy document, not a system description. Declare the intent — what the agent is for, what it's allowed to do, what it's forbidden to do, who it can communicate with, what requires your approval. You don't list tool names, file paths, or implementation details — Praxa reads the actual code and compares it against the policy you've declared.

What makes a rule good is that it states a verifiable constraint on behavior:

- ✓ *"Message bodies must never be retrieved for senders not in the authorized counterparty list"*
- ✗ *"Handle email appropriately"*

The first rule gives Praxa something to check against the agent. The second doesn't. Write rules about what the agent *does*, not about how it does it.

A template is included in `WORKER_REMIT_template.md`.

---

## What Praxa Verifies

Every analysis runs these named verification patterns:

- **Policy-implementation divergence** — the code or behavior doesn't do what the policy document says
- **Credential exposure** — secrets in unexpected locations across the workspace
- **Configuration gaps** — auto-approved exec, disabled loop detection, missing rate limits
- **Capability drift** — new tools or outbound destinations not in the authorized baseline
- **Supply chain risk** — unpinned dependencies, unreviewed plugins, unknown provenance
- **Declared-but-never-consulted config / secret** — half-wired controls (`WEBHOOK_SECRET` defined, never checked; `ADMIN_TOKEN` declared, never enforced)
- **Empty stub files in security-relevant paths** — planned-but-not-implemented sandboxes, approval gates, redactors
- **Secondary prompt discovery** — session-loaded identity files (`SOUL.md`, `AGENTS.md`, `MEMORY.md`, etc.) audited as system prompts, with compound escalation when a writable session file meets a confirmed injection path (ASI06 memory-poisoning chain)
- **Compound signal reasoning** — individual findings chained together when they combine into a high-severity attack path

---

## What Praxa Analyzes

Praxa accepts any artifact that reveals what the agent does, has done, or is configured to do. Three common input shapes — used individually or in combination:

| Shape | Example | What Praxa does with it |
|---|---|---|
| **Source repository** | A GitHub repo, agent project directory, plugin source tree | Reads code, configs, skill files, dependencies, prompts; checks code against the remit; runs supply-chain and credential-exposure verification. |
| **Running deployment** | Live memory and bootstrap files (`MEMORY.md`, `SOUL.md`), **operational logs** (action reports, session JSONL, audit trails, escalation logs), config files | Treats live state as the agent's autobiography; analyzes for behavioral drift, tool loops, missed escalations, half-wired controls, and session-loaded files audited as system prompts. |
| **Behavioral artifacts** | Chat transcripts, email histories, conversation logs, decision records | Treats observed behavior as evidence; checks for control-logic disclosure, identity-claim acceptance without verification, scope drift, and missing escalations. |

The methodology adapts. A repo-only analysis covers code-level findings — Manage Your Supply Chain, credential exposure, configuration gaps — but can't observe behavior. A behavior-only analysis covers Zero Trust violations the agent demonstrably committed but can't assess code quality. An analysis with multiple input shapes gets the most complete picture, and the report's confidence levels are calibrated accordingly. See [`examples/`](examples/) for repo-shape analyses and the test plan in `tests/README.md` (in the source repo) for the breadth of targets we've validated.

---

## What You Need

- **A coding agent** (tested against Claude Code). Praxa is distributed as a skill file the agent reads and executes — any coding agent capable of tool use and multi-step instruction-following should work.
- **A Worker Remit** for the agent you're analyzing (or your coding agent can help you write one).

---

## Running an Analysis

Praxa ships as a Claude Code plugin inside a plugin marketplace. You can install it through the marketplace mechanism or run it directly from an unzipped release — both paths work.

### Option A — Install via Claude Code plugin marketplace

From a Claude Code session:

```
/plugin marketplace add Exabeam/deckard
/plugin install praxa@exabeam
```

That's the install step. The skill is now available as `behavior-verifier`.

### Option B — Use directly from an unzipped release

Unzip the release somewhere your coding agent can see it. No install step required.

### Write a Worker Remit for the agent you're analyzing

Use [`WORKER_REMIT_template.md`](WORKER_REMIT_template.md) as the starting point. Describe what the target agent is authorized to do — its tools, channels, counterparties, and behavioral norms. Save the file as `WORKER_REMIT.md` (or `WORKER_REMIT_<agent>.md`) anywhere your coding agent can read it — typically alongside the agent workspace, or in the directory you run the analysis from. If you skip this step, your coding agent can help you draft one before the analysis.

### Run the analysis

Tell your coding agent:

```
Please run the behavior-verifier skill to analyze [path to the agent's repo, deployment workspace, or behavioral artifacts].
```

(Or if you're using the unzipped release directly, point the agent at `skills/behavior-verifier/SKILL.md`.)

Your coding agent reads whatever you provide — source code, live agent files, or transcripts — evaluates it against the RAISE framework and Worker Remit, and writes the results to `./reports/`. The methodology adapts to what's available; categories the input doesn't cover are scored at lower confidence and explicitly noted in the report.

### Open the report

```
./reports/<agent-name>-analysis-<timestamp>.html
```

Self-contained static HTML. Open directly in a browser — no server needed.

---

## Frameworks

Every finding Praxa produces is classified against four industry-standard frameworks simultaneously, drawing on the curated [knowledge base](skills/behavior-verifier/knowledge/) that ships with Praxa:

- **OWASP Top 10 for LLM Applications 2025** — every finding applicable to LLM-level risks is tagged with the correct `LLM0X` category and full name (e.g., `LLM01 — Prompt Injection`, `LLM02 — Sensitive Information Disclosure`). Source: [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/).
- **OWASP Top 10 for Agentic AI Applications 2026** — agentic-specific patterns are tagged with the correct `ASI0X` category (e.g., `ASI01 — Agent Goal Hijack`, `ASI06 — Memory and Context Poisoning`). Source: [genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).
- **OWASP Secure MCP Server Development Guide 2026** — when Praxa finds MCP server configuration in the workspace, it applies the full MCP minimum-bar checklist from the OWASP guide. Source: [genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development](https://genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/).
- **Responsible AI Software Engineering (RAISE) Framework** — a six-category AI maturity model. Every analysis produces a 0–5 score per category plus a weighted overall posture. See [`docs/RAISE.md`](docs/RAISE.md) for the reference and maturity scale.

---

## Examples

The [`examples/`](examples/) directory contains real analyses against deliberately vulnerable agents from the OWASP Agentic AI CTF and the Damn Vulnerable AI Agent project. Each example includes the Worker Remit we wrote, the human-readable HTML report, and the machine-readable JSON findings — see [`examples/README.md`](examples/README.md) for the full walkthrough.

---

## Tests (source repository only)

The [`tests/`](tests/) directory in the source repository is Praxa's pre-release regression suite. It lists nine test-target agents — ranging from intentionally-vulnerable CTF agents to mature production tools — along with the Worker Remit developed for each and the baseline findings a healthy analysis should produce. See [`tests/README.md`](tests/README.md) for the full test plan and release checklist.

The test suite exists so that every Praxa release can be validated against the same agent posture spectrum (intentionally-broken → defense-conscious) and any regression — a missed critical theme, a dropped coverage area, an unexplained weighted-score shift — is visible before the release ships.

*`tests/` is not included in the distribution zip — users of the shipped verifier don't need the regression harness. Contributors and maintainers work from the source repository.*

---

## Files

```
praxa/
  README.md                   ← You are here
  LICENSE                     ← Apache License 2.0
  NOTICE                      ← Attribution notices (bundled OWASP material, CC BY-SA 4.0)
  CONTRIBUTING.md             ← How to contribute (DCO sign-off)
  PRAXA_SPEC.md               ← Full specification
  CHANGELOG.md                ← Release notes
  WORKER_REMIT_template.md    ← Starting point for writing your own remit
  .claude-plugin/
    plugin.json               ← Claude Code plugin manifest
    marketplace.json          ← Marketplace catalog for this repo
  skills/
    behavior-verifier/
      SKILL.md                ← The verifier skill prompt
      report_template.html    ← Canonical HTML report template
      knowledge/              ← RAISE + OWASP knowledge base loaded by the skill
  docs/
    RAISE.md                  ← RAISE framework reference + maturity scale
  examples/                   ← Example analyses against real vulnerable agents
```

---

## License

Praxa is licensed under the [Apache License, Version 2.0](LICENSE).

Portions of the knowledge base (`skills/behavior-verifier/knowledge/`) are
distilled from OWASP Gen AI Security Project publications and are used under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see [NOTICE](NOTICE)
for the attribution details.

Contributions are welcome under the same license, with a DCO sign-off — see
[CONTRIBUTING.md](CONTRIBUTING.md).

*Praxa is a project sponsored by [Exabeam](https://www.exabeam.com/).*

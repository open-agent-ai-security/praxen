<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Agent Behavior Verification (ABV)

*Verifying that AI agents stay within their authorized role.*

Praxen is the open-source reference implementation of **Agent Behavior Verification (ABV)**. This page explains the concept Praxen implements — what ABV is, why agent security needs it, and how it fits alongside runtime monitoring. If you'd rather just run a scan, start with the [Quickstart](quickstart.md); if you want the scoring model, see [The RAISE Framework](RAISE.md).

## Why agents change the security problem

AI agents are no longer passive assistants. They read documents, call tools, access systems, invoke APIs, execute code, and take actions on behalf of people and organizations.

That shift changes the question security has to answer. Traditional application security asks whether software contains vulnerabilities. Agent security has to answer something different:

> **Is the agent operating within its authorized role?**

An agent can be free of known vulnerabilities and still be dangerous — if it has access to the wrong tools, excessive permissions, unsafe defaults, or behavior that exceeds its intended purpose. ABV exists to address exactly that gap. It evaluates an agent against its declared role and determines whether its implementation, configuration, permissions, tools, and operating environment actually support that role.

The goal is not to prove an agent is perfectly safe. The goal is to determine whether the agent behaves **as authorized**.

## The limits of existing approaches

Most current agent security controls focus on one of three areas, and all three are valuable:

- **Vulnerability scanning** identifies secrets, vulnerable dependencies, insecure code patterns, and misconfigurations.
- **Guardrails** attempt to prevent unsafe outputs, prompt injections, or risky actions.
- **Runtime monitoring** observes agent behavior after deployment and looks for anomalies.

None of them, on its own, answers the governance question that matters most: *is this agent operating within its authorized role?* They catch some inputs and some implementation flaws — necessary, but partial. ABV is built to answer the role question directly.

## The Worker Remit

ABV treats agent security as an **intended-versus-observed behavior** problem. Every agent should have an authorized purpose, and before behavior can be verified, expected behavior has to be defined. So ABV begins by declaring what the agent is authorized to do — a definition we call the **Worker Remit**.

The Worker Remit is the policy contract for a digital worker. It describes:

- The agent's mission
- Approved tools
- Authorized counterparties
- Data boundaries
- Action boundaries
- Approval requirements
- Behavioral expectations
- Escalation rules

The remit is written in natural language on purpose — it should be understandable by developers, security teams, auditors, business owners, and governance teams alike. Most importantly, it must be **specific enough to verify**. The [Writing Worker Remits](writing-remits.md) guide covers how to author one (by hand, or by having Praxen draft it from your description or docs).

## Verification through evidence

ABV does not rely on a single source of truth, because agents are more than code. Their behavior emerges from the interaction of prompts, tools, permissions, memory, MCP integrations, configuration, runtime state, and human instructions.

So ABV reasons over whatever evidence is available about the agent. Examples include:

- Source repositories
- Configuration files
- Agent prompts
- Tool definitions
- MCP configurations
- Logs, session records, and chat transcripts
- Memory files
- Deployment artifacts

The objective is to determine whether the **complete agent system** aligns with its authorized remit — not whether any single file looks clean. (Praxen groups these into [four input shapes](index.md#four-input-shapes): source, deployment, behavior, and governance evidence.)

## From security controls to behavior controls

ABV shifts the analysis from implementation-centric questions to behavior-centric ones.

Instead of asking only *is this dependency vulnerable?*, *is this package outdated?*, or *does this file contain a secret?*, ABV also asks:

- Is this tool appropriate for the agent's job?
- Does this permission exceed the authorized role?
- Can the agent perform actions that require approval without one?
- Are trust boundaries enforced?
- Is runtime behavior consistent with declared intent?

These are governance questions, and they can't be answered through vulnerability scanning alone. Praxen scores them against the six categories of [the RAISE Framework](RAISE.md) and tags each finding to the relevant [OWASP Gen AI Security](owasp.md) guidance.

## How Praxen implements ABV

Praxen compares a Worker Remit against evidence gathered from an agent environment and produces a structured analysis of behavioral alignment.

It is intentionally separated from the agent being evaluated — it operates as an external observer. And its output is not a vulnerability report; it's a **behavioral assessment**. Every finding answers the same central question:

> **Does the implementation support the agent's authorized role?**

The result is a self-contained HTML report, a machine-readable findings JSON, and a plain-text summary. See [Interpreting Reports](interpreting-reports.md) for how to read them, and [Usage](usage.md) for running an analysis end-to-end.

## ABV and Agent Behavior Analytics (ABA)

ABV is not a replacement for runtime monitoring. The two approaches address different stages of the agent lifecycle:

- **Agent Behavior Verification (ABV)** defines and verifies expected behavior **before deployment**.
- **Agent Behavior Analytics (ABA)** observes behavior **after deployment** — runtime visibility, behavioral baselining, drift detection, anomaly identification, and operational oversight of deployed agents. ABA extends behavioral-analytics concepts traditionally applied to users and machines into the world of digital workers. (Learn more about [Agent Behavior Analytics](https://www.exabeam.com/capabilities/agent-behavior-analytics/).)

Together they form a lifecycle model for digital-worker governance:

1. Define the role.
2. Verify the implementation.
3. Deploy with known controls and known residual risk.
4. Observe runtime behavior.
5. Detect drift and misuse.
6. Refine the remit and controls.

### Behavior Intelligence = ABV + ABA

ABV verifies that an agent is **built and configured** according to its authorized role. ABA continuously monitors whether the **deployed** agent remains within that role.

Verification without monitoring leaves organizations blind to runtime drift. Monitoring without verification leaves them guessing what "normal" was supposed to be. Both are required to govern digital workers effectively.

## In summary

AI agents should be evaluated on whether they remain inside their authorized role — and that requires more than vulnerability scanning, guardrails, or runtime analytics. It requires a clear definition of expected behavior and a way to compare reality against that expectation.

That is what Agent Behavior Verification provides. The Worker Remit defines the policy; ABV evaluates evidence against that policy; and Praxen operationalizes the approach, helping organizations verify that digital workers are configured, deployed, and operated within their intended boundaries.

As AI agents become operational actors inside business systems, *is this agent behaving as authorized?* becomes one of the most important security questions an organization can ask.

## Next steps

- [Quickstart](quickstart.md) — have Claude author a remit for the FinBot demo agent, scan it, and read the report, in about 15 minutes
- [Writing Worker Remits](writing-remits.md) — author the policy document ABV verifies against
- [The RAISE Framework](RAISE.md) — the six-category maturity model Praxen scores
- [Interpreting Reports](interpreting-reports.md) — how to read what Praxen produces

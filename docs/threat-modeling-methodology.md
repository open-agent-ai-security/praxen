<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Threat-Model Methodology — the frameworks Praxen uses

Praxen's threat model is an **evidence-derived architecture view** of an
agent: a data-flow diagram with trust boundaries, an enumerated set of
threats at each boundary, and the attack paths that connect an untrusted
origin to a consequence — every node, edge, boundary, and threat citing
file:line evidence from the agent's own workspace. This page explains the
methodology it composes, the way the [RAISE](RAISE.md) and
[OWASP](owasp.md) pages explain those frameworks. It is a companion to
both: OWASP supplies the threat *vocabulary*, RAISE supplies the security
*expectations*, and STRIDE supplies the per-boundary *enumeration method*.

No single framework covers agent threat modeling on its own, so Praxen
layers them deliberately — a data-flow model to find the trust crossings,
STRIDE to enumerate what can go wrong at each one, and the OWASP Agentic /
LLM Top 10s to name each threat in language your security team already
speaks.

> **📊 See it live:** every target in Praxen's public baseline suite ships
> a hosted threat model — a diagram, the attack paths, and per-boundary
> threat tables in a self-contained HTML report sharing the analysis
> report's chrome. Browse [OpenHands](https://open-agent-ai-security.github.io/praxen/tests/baselines/v1.3-opus5/openhands/openhands-threatmodel-2026-08-21-143615.html),
> [Hermes desktop agent](https://open-agent-ai-security.github.io/praxen/tests/baselines/v1.3-opus5/hermes-agent-desktop/hermes-agent-desktop-threatmodel-2026-08-21-143615.html),
> or [FinBot](https://open-agent-ai-security.github.io/praxen/tests/baselines/v1.3-opus5/finbot/finbot-threatmodel-2026-08-21-143615.html), or any
> target from the [suite health page](https://open-agent-ai-security.github.io/praxen/tests/baselines/suite-health-report.html).

## The shape: a data-flow model in five trust lanes

Threat modeling starts by drawing the system as data flowing between
components across trust boundaries — the classic data-flow approach. Agents
share a canonical shape, so Praxen places every component in one of five
fixed lanes, left to right in the direction untrusted influence travels:

| Lane | What lives here |
|---|---|
| **User / Inputs** | Human users and any untrusted input origin — third-party senders, inbound messages, ingested external content |
| **Client / Adapters** | UI/CLI clients, platform connectors, the API surfaces a caller reaches |
| **Agent Core** | The orchestrator/react loop, system prompts and skills, the model call, memory/session state, and in-process controls |
| **Tools / MCP** | Tools the agent invokes, MCP servers, code-execution surfaces, the local stores tools touch |
| **External / Deploy** | External services and model providers, deployment surfaces (Docker/Helm/IaC), secret stores, telemetry sinks |

A **trust boundary** is where data crosses a change in trust — untrusted
input reaching the loop, a model decision reaching a side-effecting tool, a
secret injected at deploy. Boundaries are where threats live, so the model
enumerates threats *per boundary crossing*.

## STRIDE — the per-boundary enumeration method

At each trust boundary, Praxen enumerates threats using **STRIDE**, the
threat-classification scheme introduced at Microsoft in 1999 and still the
standard vocabulary for "what can go wrong at this crossing":

| Letter | Category | What it means at an agent boundary |
|---|---|---|
| **S** | Spoofing | An actor or message is treated as more trusted than it is (a stranger passed off as the owner) |
| **T** | Tampering | Data or instructions are altered in flight (injected content steering the model) |
| **R** | Repudiation | An action can't be attributed or reconstructed after the fact (no durable audit trail) |
| **I** | Information disclosure | Data reaches a party that shouldn't see it (secrets read into context, PII in outputs) |
| **D** | Denial of service | A capability is exhausted or a loop runs unbounded |
| **E** | Elevation of privilege | An action runs with more authority than intended (ungated host exec, self-widened tool set) |

Every enumerated threat carries its STRIDE letter, so a reader can see
*which kind* of failure each boundary is exposed to.

## OWASP — the threat taxonomy

Every threat also carries its **primary OWASP code** — an Agentic Top 10
(`ASI01`–`ASI10`) or LLM Top 10 (`LLM01`–`LLM10`) tag — the *same
taxonomy every Praxen finding uses*, so the threat model and the analysis
report speak one language. The primary code is chosen under the OWASP
arbitration conventions in Praxen's knowledge base; a threat that no OWASP
category honestly covers (a pure observability or generic-hygiene gap)
carries no code rather than a forced one. See the
[OWASP page](owasp.md) for the full per-code glosses.

## Trust-boundary archetypes

Trust boundaries are drawn from a fixed menu, so the same crossing is named
the same way across every target and across runs:

| Archetype | The crossing it names |
|---|---|
| `untrusted-ingress` | Untrusted input origin → first handler |
| `control-plane-exposure` | An admin/inspector/config surface reachable by a caller |
| `model-egress` | Agent → LLM / model provider |
| `tool-invocation` | A model/orchestrator decision → a tool with side effects |
| `state-commit` | A decision → a durable state change (approval, DB write, case action) |
| `data-at-rest` | Stored data readable by a lower-trust caller |
| `secret-material` | Keys/seeds/credentials at rest or injected at deploy |
| `telemetry-egress` | Agent → logs, analytics, external reporting |
| `supply-chain` | Dependencies, install path, plugin/skill provenance |
| `value-transfer` | Funds or an irreversible external action crossing out |
| `peer-a2a` | Agent ↔ agent communication |
| `stored-state` | Writable persistent state (goals, config, memory) that later re-enters the agent's decisions |

## Attack paths — origin → consequence

The headline of the report is not a catalogue of connections; it is the set
of **attack paths** — the chains that answer *"how does an attacker actually
get owned, and what do I fix first?"* Each path runs from an **untrusted
origin** (where attacker-influenceable content enters — a non-owner
entrypoint, ingested external content, a peer message) through the **hijack**
(how that influence reaches the model's decisions — the missing gate, the
absent provenance check) to a **consequence** (host execution, data egress,
a state commit, persistent memory poisoning). A path is a real walk over the
diagram's flows, so it can be traced end to end; the components on it are
marked by role:

| Marker | Role on the path |
|---|---|
| **Source** (ingress) | Where untrusted content enters the system |
| **Pass-through** | A component the influence rides through (the loop, the model, a tool) |
| **Control that failed** | A control that sits *on* the path — by definition it did not stop the attack |
| **Target** (consequence) | Where the damage lands |

The trusted owner's own path is not an attack; what makes a flow an attack
is that it *starts* at an untrusted origin.

## Threat status — the four verdicts

Each enumerated threat carries one status, so the report separates *proven
danger* from *unanswered hypothesis*:

| Status | Meaning |
|---|---|
| **confirmed** | An analysis finding proves it — the finding ID is cited |
| **potential** | An unanswered hypothesis: no covering finding, and the sweep for a mitigating control found none |
| **partial** | A control answers part of the threat (cited), with the uncovered remainder stated |
| **mitigated** | A control demonstrably answers the whole threat (cited) |

`confirmed` is the strongest signal — it is verified against the code.
`potential` is where the threat model adds the most beyond the scan:
plausible exposure on surfaces nothing currently answers, which is exactly
the review list a follow-up analysis should start from.

## How it relates to RAISE, OWASP, and the Worker Remit

- **OWASP** ([page](owasp.md)) is the shared threat *taxonomy* — the threat
  model tags threats with the same ASI/LLM codes the analysis findings use.
- **STRIDE** is the *enumeration method* — how the possible threats at each
  boundary are found.
- **RAISE** ([page](RAISE.md)) is where the security *expectations* come
  from. A boundary the remit never mentions is still assessed — against the
  RAISE/OWASP calibration that applies to every agent regardless of what its
  job description says.
- **The Worker Remit** is *declared intent* — a job description, not a
  security model. Where a remit rule genuinely governs conduct at a
  boundary, the threat model shows the rule and its verification status in
  place. A boundary with no governing remit rule is normal, not a gap: its
  threats stand on the RAISE/OWASP calibration alone.

## Sources

- STRIDE — the Microsoft threat-classification scheme (1999), the standard
  per-boundary enumeration vocabulary.
- Microsoft, *Reference data flows and threat models for security
  evaluations* — the agent data-flow shape this model adapts.
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
  and [OWASP Top 10 for LLM Applications 2026](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final)
  — the threat taxonomy (see the [OWASP page](owasp.md)).
- [The RAISE Framework](RAISE.md) — the security expectations every agent is
  measured against.

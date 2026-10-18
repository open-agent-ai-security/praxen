<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# OWASP Gen AI Security — the frameworks Praxen uses

Every finding Praxen produces is tagged against industry-standard OWASP frameworks so the result lands in language your security team already speaks. This page explains where those frameworks come from and gives a one-line gloss on each risk so you can read a tag without leaving the report.

> **📊 See it live:** the **[OWASP Coverage Report](https://open-agent-ai-security.github.io/praxen/tests/baselines/owasp-coverage-report.html)** aggregates LLM and Agentic Top-10 coverage across Praxen's entire example suite — a browsable map of which risks each target carries, with a link into every per-target analysis. Rendered on GitHub Pages.

## OWASP, briefly

The **Open Worldwide Application Security Project** ([owasp.org](https://owasp.org/)) is the non-profit foundation behind the vendor-neutral, openly-licensed "Top 10" risk lists that are a baseline reference across application security.

## OWASP Gen AI Security Project

As LLM-based systems moved into production, OWASP spun up a dedicated effort: the **OWASP Gen AI Security Project** ([genai.owasp.org](https://genai.owasp.org/)). It maintains the AI-specific guidance Praxen relies on — currently three documents:

| Document | What it covers | Praxen tag prefix |
|---|---|---|
| [OWASP Top 10 for LLM Applications 2026](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final) | Risks in applications built on large language models | `LLM01`–`LLM10` |
| [OWASP Top 10 for Agentic AI Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | Risks specific to autonomous, tool-using agents | `ASI01`–`ASI10` |
| [A Practical Guide for Secure MCP Server Development 2026](https://genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/) | Securing Model Context Protocol servers and the tools they expose | `mcp` (checklist items) |

Praxen carries distilled extracts of all three in its knowledge base (`skills/behavior-verifier/knowledge/`), but the canonical, full-length versions live at the links above — go there for the complete write-ups, examples, and references.

## OWASP Top 10 for LLM Applications 2026

The risk landscape for any system that puts an LLM in the loop. Each finding Praxen tags with one of these traces to a behavior or code pattern in the agent's evidence.

| ID | Risk | One-line gloss |
|---|---|---|
| <a id="llm01-2026-prompt-injection"></a>**LLM01** | Prompt Injection | Untrusted input (direct or smuggled in via external content) overrides the model's instructions. |
| <a id="llm02-2026-sensitive-information-disclosure"></a>**LLM02** | Sensitive Information Disclosure | The model leaks PII, secrets, or proprietary data through its outputs. |
| <a id="llm03-2026-excessive-agency"></a>**LLM03** | Excessive Agency | The model is granted more capability, permission, or autonomy than the task needs. |
| <a id="llm04-2026-supply-chain"></a>**LLM04** | Supply Chain | Compromised or untrusted models, datasets, plugins, or dependencies enter the system. |
| <a id="llm05-2026-data-and-model-poisoning"></a>**LLM05** | Data and Model Poisoning | Training, fine-tuning, or RAG data is manipulated to bias or backdoor the model. |
| <a id="llm06-2026-unbounded-consumption"></a>**LLM06** | Unbounded Consumption | Unconstrained inference (cost, compute, rate) enables denial-of-wallet or denial-of-service. |
| <a id="llm07-2026-misinformation"></a>**LLM07** | Misinformation | The model produces confident, plausible, wrong output that users act on. |
| <a id="llm08-2026-hidden-context-exposure"></a>**LLM08** | Hidden Context Exposure | Hidden, non-user-facing context — system prompt, tool schemas, control logic, roles — is extracted or reconstructed. |
| <a id="llm09-2026-vector-and-embedding-weaknesses"></a>**LLM09** | Vector and Embedding Weaknesses | Flaws in embeddings or vector stores enable injection, poisoning, or data leakage via RAG. |
| <a id="llm10-2026-improper-output-handling"></a>**LLM10** | Improper Output Handling | Model output is passed downstream (shell, SQL, HTML, eval) without validation. |

→ Full document: **[OWASP Top 10 for LLM Applications 2026](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final)**

### <a id="owasp-top-10-for-llm-applications-2025"></a>OWASP Top 10 for LLM Applications 2025 (superseded)

Kept because Praxen reports are archived and read later. A report scored against
the 2025 list links its chips here, so the entry a reader lands on is the one
their report meant — the numbering was reordered for 2026, so resolving a 2025
code against the current list gives the wrong risk. Every 2.0+ report names its
edition in the footer and in `standards`; see
[Legacy anchors](#legacy-anchors) for pre-2.0 reports, which name none.

**Superseded — do not use for new work.** The current list is
[2026](#owasp-top-10-for-llm-applications-2026) above.

| ID | Risk (2025 wording) |
|---|---|
| <a id="llm01-2025-prompt-injection"></a>**LLM01** | Prompt Injection |
| <a id="llm02-2025-sensitive-information-disclosure"></a>**LLM02** | Sensitive Information Disclosure |
| <a id="llm03-2025-supply-chain"></a>**LLM03** | Supply Chain |
| <a id="llm04-2025-data-and-model-poisoning"></a>**LLM04** | Data and Model Poisoning |
| <a id="llm05-2025-improper-output-handling"></a>**LLM05** | Improper Output Handling |
| <a id="llm06-2025-excessive-agency"></a>**LLM06** | Excessive Agency |
| <a id="llm07-2025-system-prompt-leakage"></a>**LLM07** | System Prompt Leakage |
| <a id="llm08-2025-vector-and-embedding-weaknesses"></a>**LLM08** | Vector and Embedding Weaknesses |
| <a id="llm09-2025-misinformation"></a>**LLM09** | Misinformation |
| <a id="llm10-2025-unbounded-consumption"></a>**LLM10** | Unbounded Consumption |

### 2025 → 2026: what changed

The 2026 revision kept the same ten risk concepts but **reordered them and renamed one**. Praxen reports and frozen baselines produced before v1.2 carry 2025 numbering — when comparing across that boundary, match categories by **name**, never by number:

| 2026 | Name | Was (2025) |
|---|---|---|
| LLM01 | Prompt Injection | LLM01 |
| LLM02 | Sensitive Information Disclosure | LLM02 |
| LLM03 | Excessive Agency | LLM06 |
| LLM04 | Supply Chain | LLM03 |
| LLM05 | Data and Model Poisoning | LLM04 |
| LLM06 | Unbounded Consumption | LLM10 |
| LLM07 | Misinformation | LLM09 |
| LLM08 | Hidden Context Exposure | LLM07 (*System Prompt Leakage*, broadened) |
| LLM09 | Vector and Embedding Weaknesses | LLM08 |
| LLM10 | Improper Output Handling | LLM05 |

## OWASP Top 10 for Agentic AI Applications 2026

Risks that emerge once an LLM is wired to tools, memory, other agents, and the ability to act. This is the list that matters most for the kind of autonomous, tool-using agents Praxen is built to verify.

| ID | Risk | One-line gloss |
|---|---|---|
| <a id="asi01-2026-agent-goal-hijack"></a>**ASI01** | Agent Goal Hijack | An attacker redirects the agent's objective so it pursues their goal instead of yours. |
| <a id="asi02-2026-tool-misuse-and-exploitation"></a>**ASI02** | Tool Misuse and Exploitation | The agent is steered into using its legitimate tools for illegitimate ends. |
| <a id="asi03-2026-identity-and-privilege-abuse"></a>**ASI03** | Identity and Privilege Abuse | The agent's identity, tokens, or delegated permissions are abused or over-broad. |
| <a id="asi04-2026-agentic-supply-chain-vulnerabilities"></a>**ASI04** | Agentic Supply Chain Vulnerabilities | Malicious or compromised plugins, MCP servers, skills, or sub-agents enter the agent's stack. |
| <a id="asi05-2026-unexpected-code-execution-rce"></a>**ASI05** | Unexpected Code Execution (RCE) | The agent runs attacker-influenced code on the host or in connected systems. |
| <a id="asi06-2026-memory-and-context-poisoning"></a>**ASI06** | Memory and Context Poisoning | Persistent memory or retrieved context is seeded with content that corrupts future behavior. |
| <a id="asi07-2026-insecure-inter-agent-communication"></a>**ASI07** | Insecure Inter-Agent Communication | Messages between agents are unauthenticated, unvalidated, or trusted blindly. |
| <a id="asi08-2026-cascading-failures"></a>**ASI08** | Cascading Failures | One bad action or output propagates through a chain of agents/tools and amplifies. |
| <a id="asi09-2026-human-agent-trust-exploitation"></a>**ASI09** | Human-Agent Trust Exploitation | The agent's perceived authority is used to manipulate the humans who rely on it (or vice versa). |
| <a id="asi10-2026-rogue-agents"></a>**ASI10** | Rogue Agents | An agent operates outside its remit — compromised, misconfigured, or deliberately planted. |

→ Full document: **[OWASP Top 10 for Agentic AI Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)**

## A Practical Guide for Secure MCP Server Development 2026

The Model Context Protocol (MCP) is how many agents discover and call external tools. MCP servers are unusual: they run with delegated user permissions, support dynamic tool loading, and can chain tool calls — so a single weakness amplifies. When Praxen finds an MCP configuration in the evidence (`.mcp.json`, `mcp.json`, or similar), it applies the guide's **minimum-bar checklist** across these areas:

- **Architecture** — local (STDIO / loopback) vs. remote (TLS, authenticated) binding; session isolation between users and agents.
- **Tool design** — least-privilege scopes; no destructive tools without confirmation; clear, non-deceptive tool descriptions.
- **Input/output validation** — schema-validated arguments; sanitized outputs; no raw passthrough.
- **Prompt-injection controls** — tool descriptions and returned content treated as untrusted, not as instructions.
- **Authentication & authorization** — OAuth 2.1 / OIDC for remote servers; scoped, short-lived tokens; no token passthrough to downstream APIs.
- **Secrets & deployment** — no credentials in config files, env files, or tool descriptions; non-root, sandboxed execution; pinned, scanned dependencies.
- **Governance & audit** — tool invocations logged; a review process for new or updated tools; MCP-server identity tracked separately from the agent's.

Any "No" against the checklist is a finding; secrets in an MCP config file are a Critical.

→ Full document: **[A Practical Guide for Secure MCP Server Development 2026](https://genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/)**

## How these tags surface in a report

A finding's primary OWASP classification appears two ways in the HTML report:

- On the **finding card** itself, as a labeled tag (`LLM01 — Prompt Injection`, `ASI05 — Unexpected Code Execution (RCE)`, …) that links to that entry in this page.
- In the **OWASP LLM Top 10 Coverage** and **OWASP Agentic Top 10 Coverage** grid sections — full-bleed 5×2 cards, one per category, each populated card showing the top-three most-severe findings as clickable chips. Empty cells render "No findings" so the grid reads as a coverage map: at a glance you see both *what risks the agent has* and *which categories the analysis did not surface*.

The grids are driven by each finding's `owasp_llm` / `owasp_agentic` primary scalar; secondaries listed in a finding's `tags[]` array still appear on the finding card. See [Interpreting Reports](interpreting-reports.md) §9–§10 for the grid layout details. For the same coverage view **aggregated across every target in Praxen's example suite**, browse the live [OWASP Coverage Report](https://open-agent-ai-security.github.io/praxen/tests/baselines/owasp-coverage-report.html).

## How this fits with RAISE

The OWASP frameworks above answer *"what kind of risk is this finding?"* The [RAISE Framework](RAISE.md) answers *"how mature is this agent's security posture overall?"* — a six-category 0–5 score. Every Praxen finding carries both: a RAISE category tag and (where applicable) an OWASP LLM, OWASP Agentic, or MCP tag. See [Interpreting Reports](interpreting-reports.md) for how the tags appear on a finding card.

## See also

- [The RAISE Framework](RAISE.md) — the maturity-scoring side of the analysis
- [Interpreting Reports](interpreting-reports.md) — where these tags show up in a Praxen report
- [Challenging and Revising Findings](challenging-findings.md) — what to do when you disagree with a finding

## <a id="legacy-anchors"></a>Legacy anchors — where old report links land

Praxen reports **before 2.0** linked each risk chip to a bare code anchor
(`owasp.html#llm03`). A bare code cannot be edition-correct: the LLM numbering
was reordered for 2026, so `LLM03` means *Supply Chain* in a 2025-era report
and *Excessive Agency* in a 2026 one. Following such a link used to land on
whichever edition this page happened to document — silently the wrong entry for
half of them.

From 2.0, reports link to edition-qualified anchors
(`#llm03-2026-excessive-agency`), which is why this page can carry several
editions at once. The bare anchors are kept here rather than deleted, so an
archived report's links still resolve — to an honest disambiguation instead of a
wrong answer. Check which edition your report was scored against: every 2.0+
report states it in the footer, and in the JSON under `standards`.

| Legacy anchor | If your report is 2025 | If your report is 2026 |
|---|---|---|
| <a id="llm01"></a>`LLM01` | [Prompt Injection](#llm01-2025-prompt-injection) | [Prompt Injection](#llm01-2026-prompt-injection) — unchanged |
| <a id="llm02"></a>`LLM02` | [Sensitive Information Disclosure](#llm02-2025-sensitive-information-disclosure) | [Sensitive Information Disclosure](#llm02-2026-sensitive-information-disclosure) — unchanged |
| <a id="llm03"></a>`LLM03` | [Supply Chain](#llm03-2025-supply-chain) | [Excessive Agency](#llm03-2026-excessive-agency) |
| <a id="llm04"></a>`LLM04` | [Data and Model Poisoning](#llm04-2025-data-and-model-poisoning) | [Supply Chain](#llm04-2026-supply-chain) |
| <a id="llm05"></a>`LLM05` | [Improper Output Handling](#llm05-2025-improper-output-handling) | [Data and Model Poisoning](#llm05-2026-data-and-model-poisoning) |
| <a id="llm06"></a>`LLM06` | [Excessive Agency](#llm06-2025-excessive-agency) | [Unbounded Consumption](#llm06-2026-unbounded-consumption) |
| <a id="llm07"></a>`LLM07` | [System Prompt Leakage](#llm07-2025-system-prompt-leakage) | [Misinformation](#llm07-2026-misinformation) |
| <a id="llm08"></a>`LLM08` | [Vector and Embedding Weaknesses](#llm08-2025-vector-and-embedding-weaknesses) | [Hidden Context Exposure](#llm08-2026-hidden-context-exposure) |
| <a id="llm09"></a>`LLM09` | [Misinformation](#llm09-2025-misinformation) | [Vector and Embedding Weaknesses](#llm09-2026-vector-and-embedding-weaknesses) |
| <a id="llm10"></a>`LLM10` | [Unbounded Consumption](#llm10-2025-unbounded-consumption) | [Improper Output Handling](#llm10-2026-improper-output-handling) |

The agentic list has only ever had the 2026 edition, so a bare `ASI` anchor is
unambiguous and simply forwards:

| Legacy anchor | Entry |
|---|---|
| <a id="asi01"></a>`ASI01` | [Agent Goal Hijack](#asi01-2026-agent-goal-hijack) |
| <a id="asi02"></a>`ASI02` | [Tool Misuse and Exploitation](#asi02-2026-tool-misuse-and-exploitation) |
| <a id="asi03"></a>`ASI03` | [Identity and Privilege Abuse](#asi03-2026-identity-and-privilege-abuse) |
| <a id="asi04"></a>`ASI04` | [Agentic Supply Chain Vulnerabilities](#asi04-2026-agentic-supply-chain-vulnerabilities) |
| <a id="asi05"></a>`ASI05` | [Unexpected Code Execution (RCE)](#asi05-2026-unexpected-code-execution-rce) |
| <a id="asi06"></a>`ASI06` | [Memory and Context Poisoning](#asi06-2026-memory-and-context-poisoning) |
| <a id="asi07"></a>`ASI07` | [Insecure Inter-Agent Communication](#asi07-2026-insecure-inter-agent-communication) |
| <a id="asi08"></a>`ASI08` | [Cascading Failures](#asi08-2026-cascading-failures) |
| <a id="asi09"></a>`ASI09` | [Human-Agent Trust Exploitation](#asi09-2026-human-agent-trust-exploitation) |
| <a id="asi10"></a>`ASI10` | [Rogue Agents](#asi10-2026-rogue-agents) |

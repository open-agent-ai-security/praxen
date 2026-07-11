<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Knowledge Base: OWASP Top 10 for LLM Applications (2025)
*Distilled for Praxen — behavioral and environmental scanning context*

Source: OWASP Top 10 for LLM Applications 2025 (v2.0, November 2024)
License: CC BY-SA 4.0 — genai.owasp.org

This file is a Praxen knowledge base extract. It strips administrative content and retains only the signal relevant to detecting, classifying, and reasoning about LLM security risks in a running agent environment. Use it as context when evaluating agent behavior or scanning agent artifacts.

---

## How to Use This Knowledge Base

When Praxen detects a behavioral or environmental signal, map it to the relevant LLM risk category below. Use the risk category to:
- Name the finding correctly
- Understand what an attacker could do with it
- Know what evidence to look for
- Generate a specific, grounded recommendation

---

## LLM01 — Prompt Injection

**What it is:** User inputs (or external content) alter the LLM's behavior in unintended ways. The model cannot reliably distinguish instructions from content.

**Two forms:**
- **Direct:** User crafts a prompt that overrides system instructions or extracts sensitive data
- **Indirect:** External content (web pages, files, emails, RAG-retrieved documents) contains hidden instructions that reach the LLM and redirect its behavior

**What to look for in agent logs and behavior:**
- Agent output that doesn't match the task it was given
- Agent suddenly acting on instructions that appear to have come from external content (emails, documents, retrieved data)
- Agent sharing data, running code, or contacting parties not in the original task
- Escalation pattern: small compliance with injected instruction leads to larger follow-on actions

**What to look for in agent code and config:**
- External content (email bodies, web fetches, document reads) injected directly into LLM context without sanitization
- No separation between trusted instructions and untrusted external data in prompt construction
- Prompt construction via string concatenation: `prompt = system_prompt + user_input + external_content`
- RAG retrieval that returns raw external content without filtering

**Risk if exploited:** Unauthorized data access, privilege escalation, execution of commands in connected systems, manipulation of decision-making, exfiltration via crafted outputs.

**Praxen relevance:** Praxen — detect injection-vulnerable code patterns, flag external content entering the LLM context without sanitization, check for content-origin labeling in prompt construction.

---

## LLM02 — Sensitive Information Disclosure

**What it is:** The LLM reveals sensitive data — PII, credentials, proprietary algorithms, confidential business data — through its outputs.

**What to look for in agent artifacts:**
- Credentials, API keys, tokens, or passwords in any workspace file (not just `.env` — check docs, logs, snapshots, config examples, archive files)
- PII in training data, RAG knowledge bases, or memory files
- System prompt contents that the agent should not reveal stored in accessible locations
- Log files that capture full prompt/response content including sensitive data without redaction

**What to look for in agent behavior:**
- Agent outputs containing data that shouldn't be in a response to the current task
- Agent repeating back information from its context that was only there for internal processing
- Agent including sensitive context fields (credentials, personal data) in messages sent to external parties

**Risk if exploited:** Privacy violations, credential theft, intellectual property exposure, compliance failures.

**Praxen relevance:** Praxen — detect credentials in unexpected locations, check system prompts and config files for embedded secrets, verify vault references are used instead of literal values.

---

## LLM03 — Supply Chain

**What it is:** Vulnerabilities in third-party models, datasets, plugins, libraries, and build pipelines that affect the integrity of the AI system.

**What to look for in agent artifacts:**
- Framework or runtime with unknown or undocumented provenance
- Open-source model downloaded without integrity verification (no hash check, no signed manifest)
- Dependencies not pinned or not tracked in a bill of materials
- Plugins, MCP servers, or tools installed from unverified sources
- No SBOM / ML-BOM present for the agent's software stack
- Build or deployment pipeline without security gates

**Risk signals:**
- Agent runtime is the most trusted component — if it's compromised, everything the agent does is compromised (SolarWinds pattern)
- A new plugin appeared in the agent's tool inventory with no documented source
- Library versions not pinned — susceptible to dependency confusion or version-swap attacks

**Praxen relevance:** Praxen (supply chain category). Every new tool, plugin, or dependency that appears in the agent workspace is a supply chain event requiring evaluation.

---

## LLM04 — Data and Model Poisoning

**What it is:** Training data, fine-tuning data, or RAG knowledge bases are manipulated to alter model behavior — introducing backdoors, biases, or targeted misbehaviors.

**What to look for in agent artifacts:**
- RAG data sources that include unvetted external content (live web, user-uploaded documents, unreviewed public datasets)
- Memory files that accumulate user-provided content over time without review
- Fine-tuning pipelines that accept external data without validation
- Knowledge bases that haven't been reviewed since initial loading

**What to look for in agent behavior:**
- Agent behavior that shifts over time without obvious cause (slow drift in how it responds to similar inputs)
- Agent consistently favoring certain outcomes, parties, or recommendations in ways not explained by its instructions

**Praxen relevance:** Praxen — audit data source provenance, flag unvetted fine-tuning or RAG inputs, verify data sources are listed in the remit.

---

## LLM05 — Improper Output Handling

**What it is:** LLM output is passed to downstream systems — databases, shells, browsers, APIs — without validation, enabling injection attacks.

**What to look for in agent code:**
- LLM output used directly as a shell command: `subprocess.run(llm_output)`
- LLM output used as a database query: `cursor.execute(llm_output)` or f-string SQL
- LLM output rendered as HTML without encoding (XSS vector)
- LLM output used as file path, API parameter, or network request without sanitization
- Tool call parameters built from raw LLM output strings

**Why this matters for agents:** Agents execute tool calls based on their own outputs. If those outputs can be influenced via prompt injection, the injection → tool execution chain is direct. The model is a confused deputy between the attacker and the downstream system.

**Praxen relevance:** Praxen (code patterns that pass LLM output to system functions without validation).

---

## LLM06 — Excessive Agency

**What it is:** The LLM is given more permissions, capabilities, or autonomy than it needs, or it takes consequential actions without appropriate human approval.

**Three root causes:**
1. **Excessive permissions:** Agent has read/write/delete/send access it doesn't need for its job
2. **Excessive functionality:** Agent has tools available that aren't required for its current task
3. **Excessive autonomy:** Agent takes high-impact actions without human-in-the-loop approval

**What to look for in agent artifacts:**
- Tool definitions with write, delete, send, or exec capabilities where the agent's remit is read-only or advisory
- No approval gate defined for high-impact actions (sending email, modifying files, executing commands)
- Exec approval config present but empty or set to auto-approve
- OAuth scopes broader than the agent's actual job (e.g., `modify/send/calendar` for an agent that should only read)
- Tool-loop detection disabled

**What to look for in agent behavior:**
- Agent taking irreversible actions (sending messages, deleting files, executing commands) without evidence of approval
- Agent performing actions beyond the scope of the task it was given
- Agent performing actions that were in its instructions as examples, not directives

**Tag LLM06 when:** a capability the remit forbids or doesn't grant is present **and reachable** — *even if the finding reads as a control gap* ("no approval gate," "auto-approve," "no confirmation step," "no audit trail over a consequential action"). A reachable remit-forbidden capability **is** excessive agency; don't leave it untagged because it was framed as a missing control. A high-impact action with no human-in-the-loop gate is excessive **autonomy** — tag LLM06, and pair with **ASI10 (Rogue Agents)** on the agentic side when there's no accountability or oversight over it.

**Boundary:** LLM06 is *having or using* the capability; **LLM05** is insufficient scrutiny of the output that drives it. Logging, monitoring, and rate-limiting do **not** prevent excessive agency — they only *limit damage* — so their absence over a consequential capability is a co-applicable LLM06 signal (with ASI10), **not** a separate uncategorised "logging/audit" finding.

**Praxen relevance:** Praxen — capability audit against the remit is a named high-priority check. Flag every tool and permission present in code but absent from the remit. This is the highest-priority RAISE Zero Trust category.

---

## LLM07 — System Prompt Leakage

**What it is:** The agent's system prompt — containing instructions, role definition, and sometimes sensitive operational details — is exposed to users or external parties.

**What to look for in agent artifacts:**
- System prompt stored in a file accessible outside the agent's runtime context
- System prompt content that includes credentials, API endpoints, or sensitive operational details
- Agent configuration that allows users to ask the model to reveal its instructions
- System prompt not treated as confidential in logging or debugging output

**What to look for in agent behavior:**
- Agent revealing system prompt contents in response to user queries
- Agent revealing operational details (tool names, endpoints, credentials) that were in its instructions

**Praxen relevance:** Praxen — audit system prompt storage and contents, flag confidential operational details (tool names, endpoints, credentials) embedded in the prompt.

---

## LLM08 — Vector and Embedding Weaknesses

**What it is:** Vulnerabilities in how a RAG system's vectors and embeddings are **generated, stored, or retrieved** — exploited intentionally or unintentionally to inject harmful content, manipulate model outputs, or access sensitive data. This is the category for **any agent backed by a vector or embedding store** (RAG, semantic memory, a vector-indexed knowledge base).

**First detect the store, then audit it.** LLM08 is chronically under-tagged because the analyzer skips it when it doesn't notice the store. *Before* concluding LLM08 doesn't apply, check the agent's code for a vector/embedding store:
- Signals: `chromadb`, `faiss`, `pinecone`, `weaviate`, `qdrant`, `milvus`, `pgvector`, `lancedb`, `sentence-transformers`, `text-embedding*`, `embeddings.create`, `vectorstore`/`vector_store`, `similarity_search`, `embed_query`/`embed_documents`, `cosine_similarity`.
- If an **in-scope** store is present, LLM08 **applies** — audit it against the five weaknesses below and record LLM08 even when LLM01 (untrusted input), LLM04 (poisoning), or ASI06 (self-persistence) also apply. When the **agent can write to its own store from its own conversation**, LLM08 is the *dominant* frame, not a secondary tag.

**The five weaknesses to check (artifacts):**
1. **Unauthorized access / data leakage** — no fine-grained, permission-aware access on the store; any query can return any document; embeddings hold sensitive data with no logical/access partitioning.
2. **Cross-context leak / federation conflict** — one shared vector DB across users/tenants with no per-user scoping (cross-user retrieval); or RAG content that contradicts/overrides the model's grounding with no conflict handling.
3. **Embedding inversion** — embeddings or raw vectors exposed/exportable such that source text could be reconstructed; the vector store not treated as sensitive data.
4. **Data poisoning of the store** — the KB ingests unvetted content (user uploads, live web, or **the agent's own generated output**) with no validation, hidden-content detection, or review, and/or an unauthenticated write path. *(The canonical case is a hidden-instruction document — e.g. white-text "ignore all previous instructions" in an ingested file — but an agent that distils its own conversation back into the store is the same poisoning surface.)*
5. **Behavior alteration** — retrieved content silently shifts the model's behavior/persona; retrieval injected into context without being labeled external/untrusted.

**What to look for in agent behavior:**
- Returning information that appears to come from another user's or tenant's context.
- Behavior that shifts after documents enter the store; the agent acting on instructions that were embedded in retrieved content.

**Boundary — LLM08 vs neighbors:** the presence of a **vector/embedding store** is the LLM08 signal. Poisoning of *training/fine-tuning* data or a non-vector knowledge base is **LLM04**; untrusted retrieved content driving behavior *without* a vector store is **LLM01**; an agent rewriting its *own* store/identity is **ASI06** — but when the mechanism is the vector store itself, tag **LLM08** (co-applicable codes go in `tags[]`).

**Praxen relevance:** Praxen — first detect a vector/embedding store; if one is in scope, audit access controls, the write/ingest path (authentication + validation + hidden-content detection), per-user scoping, and whether retrieved content is labeled/validated before entering the prompt. Record LLM08 whenever an in-scope store exists — an agent-writable store (a self-poisoning surface) is a **dominant**-LLM08 finding.

---

## LLM09 — Misinformation

**What it is:** The LLM generates false, misleading, or fabricated information with apparent confidence. In agentic contexts this becomes an action risk, not just an output quality risk.

**What to look for in agent prompts and config:**
- System prompt that instructs the agent to "help anyway" or "do your best" when it lacks grounding — explicit invitation to hallucinate
- No citation or grounding requirement in the agent's instructions
- Agent operating without a RAG layer in a domain requiring factual accuracy
- No human review step before agent outputs are acted upon in consequential decisions

**Why this matters for agents:** An agent that hallucinates doesn't just give a wrong answer — it may take wrong actions. An agent that believes it completed a task when it didn't creates evidence-mismatch problems that only become visible when someone reviews the logs.

**Praxen relevance:** Praxen — flag system prompt instructions that invite speculation (e.g., "be creative," "fill in missing details"), check whether the agent is instructed to confirm completion with verifiable output.

---

## LLM10 — Unbounded Consumption

**What it is:** The agent consumes excessive resources — API calls, compute, tokens, money — without limits. Includes denial-of-wallet attacks, runaway loops, and resource exhaustion.

**What to look for in agent artifacts:**
- No rate limiting on LLM API calls or tool invocations
- No budget or cost threshold configured
- No timeout on long-running tasks
- No max-retry limit on failed operations
- Cron or heartbeat jobs that trigger agent sessions with no concurrency limit

**What to look for in agent behavior:**
- Repeated retries beyond normal threshold
- Same task triggered multiple times without state change
- Session count or API cost spiking above baseline
- Agent loop that appears to be running but not completing

**Praxen relevance:** Praxen — verify rate limiting and cost controls are present in config, flag absent request-per-session caps, check for timeout configuration on LLM API calls.

---

## Cross-Category Signal Patterns

These signals implicate multiple LLM risk categories and should raise compound finding severity:

| Signal | Categories |
|--------|-----------|
| External content enters LLM context unvalidated | LLM01, LLM08 |
| Agent has write/exec capability + no input validation | LLM01, LLM05, LLM06 |
| No logging of agent inputs/outputs | LLM02, LLM06 |
| Agent operating in safety-critical domain without human review | LLM06, LLM09 |
| New plugin or tool appears with no provenance | LLM03, LLM06 |
| Agent claims task complete but no artifact exists | LLM09, LLM06 |

---

*Source: OWASP Top 10 for LLM Applications 2025 — genai.owasp.org — CC BY-SA 4.0*
*Distilled for the Praxen knowledge base*

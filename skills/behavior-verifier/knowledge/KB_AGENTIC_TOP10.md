<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Knowledge Base: OWASP Top 10 for Agentic Applications (2026)
*Distilled for Praxen — behavioral and environmental scanning context*

Source: OWASP Top 10 for Agentic Applications 2026 (v2026, December 2025)
License: CC BY-SA 4.0 — genai.owasp.org

This file is a Praxen knowledge base extract. Unlike the LLM Top 10, which addresses LLM applications broadly, the Agentic Top 10 is specifically about autonomous agents that plan, decide, and act across multiple steps and systems. These are the highest-relevance risks for what Praxen analyzes.

---

## How to Use This Knowledge Base

The Agentic Top 10 describes threats specific to agents operating with autonomy. Use this file to:
- Recognize attack patterns in agent logs and behavior
- Classify findings with the right agentic risk label
- Understand how individual signals combine into multi-step attacks
- Generate grounded recommendations that address root cause

This file is the sole authority for **ASI** tags. LLM-category codes referenced here use **2026 numbering** and are grounded in the companion LLM Top 10 KB — every LLM number below is paired with its category name so a stale number can never silently mis-route. ASI codes apply to **any system with tool or action capability**; multi-step autonomy raises severity (by one level) — it does not gate the tag.

**Division of labor inside this file.** The ten entries describe each risk and list the *evidence* to look for; they defer tag arbitration — which code is primary, which codes co-tag — to the **Primary Arbitration** section directly below. When an entry's text and your instinct disagree about a tag, the arbitration section wins.

---

## Primary Arbitration — read before tagging

**Tag semantics — two relations only** (same as the LLM KB): a finding's first code is its **primary** — the category that best names the weakness; every other applicable code is a **co-tag** — an additional code, never a replacement.

**The mechanism rule.** Name the primary by the **mechanism that produces the harm**, never the surface symptom or the outcome. ASI08 (Cascading Failures) and ASI10 (Rogue Agents) are *outcome* codes: they ride as co-tags on a mechanism-primary finding, and take primary only in the single case each of their tests defines below.

**Cross-KB precedence:** when both KBs are in context, a compound finding involving any ASI code is governed by the Agentic KB's mechanism rule and its spread/outlive/persistence tests; between overlapping compound-table rows in either KB, the more specific row wins. Finding granularity follows the LLM KB's one-finding-per-fix-point rule (one finding per independently-fixable control gap on a distinct data path).

**The spread test (governs ASI08).** Co-tag ASI08 only when a compromised or corrupted state actually **propagates beyond the initial action** — a poisoned output consumed by another agent or a later session, an orchestrator decision fanning out to workers, an unbounded loop amplifying a bad state. A single agent merely having multiple steps is not cascade; one contained action is not cascade. ASI08 is primary only when uncontrolled propagation is itself the sole finding *in its chain*, with no upstream mechanism to name.

**The outlive test (governs ASI10).** Ask: *when the immediate action finishes, is the agent still operating out of bounds?* Co-tag ASI10 only on **yes** — a persistent alteration of the agent itself (stored goal/instruction/config override, poisoned memory carrying into later sessions, tool or permission set *acquired at runtime* beyond the deployed baseline), or **standing autonomy** (an approval layer absent or disabled for the agent *as a whole* while it runs self-directed). For approval layers, distinguish the two default cases: a layer that is *structurally absent or cannot be enabled* is clear ASI10; a layer that is *present but default-off* earns the ASI10 co-tag only when the standing state under scan actually runs unsupervised — the shipped default or the deployment's configured state, evidenced, not the mere existence of an off switch. A one-shot attack, an ungated single action, or anything the attacker must re-trigger each time is mechanism-only — no ASI10. A statically over-broad tool set shipped at deploy is **LLM03 (Excessive Agency)**, not runtime drift. ASI10 is primary only for a self-contained rogue behavior with no upstream vector to name: reward hacking / specification gaming, self-replication, collusion, scheming / deceptive compliance.

**The persistence test (governs ASI06 vs LLM09).** Store/memory poisoning that **persists as agent state and alters behavior across sessions** is ASI06 primary (co-tag LLM09 — Vector & Embedding Weaknesses — when the store is vector-backed). A **one-shot** vector/embedding weakness with no cross-session persistence is LLM09 (Vector & Embedding Weaknesses), no ASI06.

**Compound-signal table.** One row per recurring signal; primary first, co-tags second.

| Signal | Primary | Co-tags |
|--------|---------|---------|
| Missing/disabled approval gate on a consequential action | LLM03 (Excessive Agency) | ASI05 only if the ungated tool is exec — never ASI02/ASI09 for the gate itself |
| Approval layer absent/disabled for the agent as a whole, running self-directed | LLM03 (Excessive Agency) | ASI10 (standing autonomy per the outlive test) |
| Statically over-broad tool set or permissions shipped at deploy | LLM03 (Excessive Agency) | ASI02 only when a tool is shown *used* wrongly |
| Code/shell/command execution — observed or invocable in a live path, i.e. a dataflow from model output to the exec call exists beyond mere registration (a merely-present ungated exec tool is the gate row above: LLM03 primary, ASI05 co-tag) | ASI05 | LLM10 (Improper Output Handling) when model output reaches the exec sink; ASI01 if goal-hijacked into it |
| Non-exec tool misused for a wrong purpose (email exfil, covert channel, API chaining) | ASI02 | ASI01 if goal-hijacked into it |
| Credential/identity scope defect (shared account, broad OAuth, token passthrough) | ASI03 | — (capability declared in a tool definition is LLM03/ASI02, not ASI03) |
| Instructions accepted from a spoofed or unverified sender | ASI03 (the identity check failed) | ASI01 if goals were redirected; ASI09 when a human was *also* deceived — if only the human was deceived (the agent's own check never fired), use the human-side deception row instead |
| Goal altered by live input (prompt, tool output, retrieved content, A2A message) | ASI01 | LLM01 (Prompt Injection); ASI07 if the vector is an inter-agent message; a poisoned *third-party* source has supply-chain provenance — ASI04 primary (row below). An ingress-hygiene gap with *no* goal-alteration evidence is LLM01 primary per the LLM KB |
| Goal altered via *stored* memory/context | ASI06 | ASI01 |
| Poisoned third-party knowledge source, RAG plugin, or tool description (tool poisoning, rug pull, runtime swap) | ASI04 | ASI06 if it lands in persistent memory; ASI01 if goals redirected |
| Unverified plugin / MCP server *install* (provenance gap, pre-deploy) | LLM04 (Supply Chain) | ASI04 |
| Malicious package / lockfile poisoning with install/import execution *evidenced* (install hook, setup script) | ASI05 | ASI04; absent execution evidence the poisoned pre-deploy dependency is LLM04 (Supply Chain) primary |
| Cross-tenant vector bleed (namespace-filter bypass on retrieval), not stored into memory | LLM09 (Vector & Embedding) | LLM02 (Sensitive Information Disclosure) when disclosure is evidenced; once bled content is stored into memory across sessions the persistence test flips it: ASI06 primary, LLM09 co-tag |
| Unauthenticated / unvalidated inter-agent channel | ASI07 | ASI03 when the defect is identity, not transport |
| Loop or retry spreading corrupted state or actions | mechanism (ASI01/04/06/07…) | ASI08 per the spread test; LLM06 (Unbounded Consumption) if it also burns spend |
| Loop, retry, or fan-out burning only cost/latency — or missing ceilings (retry caps, circuit breakers) with nothing spread | LLM06 (Unbounded Consumption) | — (if anything spread, use the row above) |
| Progressive locally-reasonable steps aggregating out of scope | ASI01 (agent-side) | ASI09 only when it is the *human approver* being walked forward |
| Human-side deception: fake explainability, consent laundering, anthropomorphic manipulation, missing final human confirmation | ASI09 | — |
| Self-contained rogue behavior (reward hacking, self-replication, collusion, scheming) | ASI10 — primary is legal but rare | — |
| Pure observability gap (no audit log / no monitoring / no alerting) | RAISE only — no OWASP code | — |

**Compound severity rule.** Escalate when **two or more findings'** primary-or-co-tag codes match **two or more consecutive entries, in order, of one Attack Chain Pattern row** (table at the end of this file) on the same target: raise the severity of the **earliest matched finding** one level above the highest individual finding (capped at the scale maximum) and list the others in `related_findings`. Chain rows describe the attack narrative — the findings themselves are always tagged per this arbitration section, never per the chain row. Co-occurrence of unrelated categories does not escalate. The multi-step severity bump (header) applies to ASI-primary findings only; chain escalation applies after any per-entry severity ladder, and a finding's severity is raised at most once.

---

## ASI01 — Agent Goal Hijack

**What it is:** An attacker manipulates the agent's objectives, task selection, or decision pathways — not just a single model response, but the agent's ongoing goal and behavior across multiple steps. Unlike simple prompt injection, this redirects what the agent is *trying to do*.

**Attack vectors:**
- Prompt-based manipulation in user input
- Deceptive tool outputs that reframe the agent's context
- Malicious artifacts (documents, emails, files) that contain goal-redirecting instructions
- Forged agent-to-agent messages that alter orchestration logic
- Poisoned external data retrieved via RAG

**What to look for in agent behavior:**
- Agent pursuing a task or objective not present in the original instructions
- Agent contacting parties, accessing data, or taking actions outside the original task scope
- Multi-step sequences where each step seems locally reasonable but the aggregate is outside the remit
- Agent "helping" an unexpected requester — responding to instructions from external content as if they were legitimate operator instructions
- Shift in agent goal mid-session with no user instruction to do so

**What to look for in agent artifacts:**
- No separation between trusted operator instructions and untrusted external content in prompt construction
- Agent treats all inputs (user, tool output, retrieved content, external email) with equal trust
- Orchestration logic that can be redirected by model output alone, without deterministic guardrails

**Also:** scheduled / recurring goal-reweighting drift (e.g. a malicious calendar invite that injects a recurring instruction subtly reweighting objectives each cycle — each delivery is live input, ASI01; once retained in memory between cycles, ASI06 per the persistence test); manipulated-but-plausible output that steers a business decision (not only scope/action deviation). A *single-action* goal redirect still tags ASI01 — the typical case spans steps, but multi-step raises severity, not the tag.

**Neighbors:** ASI01 is goal alteration by *live* input; alteration via stored memory/context is ASI06's subject; autonomous misalignment with no active attacker is ASI10's — primaries per the arbitration section.

**Praxen relevance:** Praxen — inspect system prompt for goal guardrails, check for validation on config fields that can modify agent goals or identity (e.g., `custom_goals`, `persona_override`), confirm the remit declares a single authorized mission.

---

## ASI02 — Tool Misuse and Exploitation

**What it is:** The agent uses its tools in unintended, harmful, or exploitable ways — either because it was manipulated (via ASI01) or because the tools themselves are insecure.

**Common patterns:**
- Agent uses a legitimate tool for an illegitimate purpose (exfiltration via an email tool, data destruction via a file tool)
- Tool accepts model-generated inputs without validation, enabling injection through the tool call
- Tool has broader permissions than the agent's task requires
- Tool outputs are trusted as authoritative and fed back into agent context without sanitization (tool output as injection vector)

**What to look for in agent artifacts:**
- Tool definitions with write/delete/send/exec capabilities not justified by the agent's remit
- Tool parameters that accept raw strings from model output without schema validation
- Tools that return external content (web, email, documents) directly into LLM context
- No approval gate on high-impact tool invocations (the gate itself is LLM03 — Excessive Agency — per arbitration; ASI02 is the wrongful *use*)
- Missing tool-use logging (observability gap — RAISE only, no OWASP code)

**What to look for in agent behavior:**
- Tool being called with parameters that don't match the stated task
- Same tool called repeatedly with slight parameter variations (probing behavior)
- Tool producing output that is inconsistent with the stated action (evidence mismatch)
- High-impact tool (send, delete, exec) called without evidence of approval

**Also — non-exec misuse patterns:** tool-name impersonation / typosquatting / alias collision (`report` resolving before `report_finance`); living-off-the-land chaining through *non-exec* APIs and internal tools seen as benign (exec-based LOTL — PowerShell, shell one-liners — is ASI05's subject); covert-channel exfil via an approved low-risk tool (DNS via a ping tool); internal→external exfil chaining (internal CRM tool + external email tool); loop-amplified costly-API DoS / bill spikes (ASI02 only when the calls serve a wrong purpose — a loop that merely burns spend is LLM06, Unbounded Consumption, primary).

**Neighbors:** ASI02 is *misuse in action* of a non-exec tool; code/shell execution is ASI05's subject; a statically over-broad tool set at deploy is LLM03's (Excessive Agency); credential/identity scope is ASI03's — primaries per the arbitration section.

**Praxen relevance:** Praxen — audit tool definitions, compare permission scope against the remit, flag high-impact tools (send, delete, exec) lacking approval gates.

---

## ASI03 — Identity and Privilege Abuse

**What it is:** The agent operates under an identity with excessive privileges, or its identity is exploited — either by the agent acting beyond its own authority or by an attacker impersonating a trusted identity to the agent.

**Common patterns:**
- Agent uses a shared service account rather than a scoped per-agent identity
- Agent's credentials can be used outside the agent's intended scope (token passthrough)
- Attacker spoofs a trusted sender identity to get the agent to act on their behalf
- Agent grants trust based on display name, substring match, or claimed role rather than verified identity
- Agent escalates its own privileges by invoking admin tools it technically has access to

**What to look for in agent artifacts:**
- Trust decisions based on unverified fields (From header display name, self-declared role in prompt)
- Agent identity (credentials, OAuth tokens) stored in accessible workspace files
- Broad OAuth scopes relative to the agent's actual job
- No canonical address parsing for sender verification — substring match is exploitable
- Reply-To routing that allows redirection of agent responses

**What to look for in agent behavior:**
- Agent acting on instructions from a new or unverified identity
- New counterparty appearing in agent's trust graph without operator approval
- Agent responding to a requester whose identity doesn't match the authorized list in the Worker Remit

**Also:** TOCTOU / authorization drift (permissions valid at workflow start, stale or expired by execution); cross-agent confused deputy (a low-priv agent relays valid-looking instructions to a high-priv agent that executes without re-checking intent); memory-based privilege retention (creds cached across tasks/users, reused in a weaker session — co-tag ASI06; ASI03 stays primary, the stored item being a credential, not a behavior-altering instruction); OAuth device-code phishing binding a victim tenant to attacker scopes; un-scoped privilege inheritance through delegation chains.

**Neighbors:** ASI03 is the scope carried by a *credential or identity*; a capability declared in a tool definition is LLM03's (Excessive Agency) or ASI02's subject; the human-deception variant of impersonation is ASI09's — primaries per the arbitration section.

**Praxen relevance:** Praxen — check credential storage, audit trust-check implementation in code, verify counterparty list from remit is enforced before sensitive actions.

---

## ASI04 — Agentic Supply Chain Vulnerabilities

**What it is:** Compromised tools, plugins, frameworks, or data sources in the agent's supply chain introduce vulnerabilities or malicious behavior.

**Agentic-specific risks:**
- **Tool Poisoning:** Malicious instructions embedded in tool descriptions or metadata that redirect model behavior
- **Rug Pulls:** A previously trusted tool definition is swapped or modified in real-time, bypassing initial security checks
- **Plugin Compromise:** A plugin or MCP server is updated to include malicious code or exfiltration logic
- **Framework Vulnerability:** The agent runtime itself (OpenClaw, Claude Code, LangChain) contains a vulnerability that affects all agents using it

**What to look for in agent artifacts:**
- Tool definitions that changed since last scan without documented approval
- New plugins or MCP servers in the environment with no documented source or review (install-time provenance → LLM04 — Supply Chain — primary, ASI04 co-tag)
- Framework or runtime version not pinned or not documented (LLM04 — Supply Chain — primary)
- Tool description text that includes instructions to the model beyond what the tool nominally does ("When using this tool, also...")
- No integrity verification on tool or plugin files (no hash, no signature)

**What to look for in agent behavior:**
- Tool behavior that diverges from its description (tool claims to search but sends data)
- New capability appearing in the agent's effective behavior without a corresponding new tool in the authorized list

**Also:** remotely-loaded poisoned prompt templates; typosquatting / impersonation of dynamically-discovered tools or endpoints; a vulnerable third-party **peer agent** invited into a workflow (ASI04 primary for the composition risk, ASI07 co-tag); a compromised MCP / registry server serving signed-looking manifests at scale; a poisoned third-party knowledge/RAG plugin (co-tag ASI06 when it lands in persistent memory).

**Neighbors:** ASI04 is *runtime* tool/agent composition — poisoned descriptions, swapped definitions, compromised registries; a static pre-deploy dependency or an unverified *install* is LLM04's (Supply Chain) subject — primaries per the arbitration section.

**Praxen relevance:** Praxen (supply chain category, tool inventory change detection, rug pull detection). Tool-inventory change detection between scans is the direct defense against silent rug pulls.

---

## ASI05 — Unexpected Code Execution (RCE)

**What it is:** The agent executes code — shell commands, scripts, arbitrary programs — that was not explicitly authorized, often triggered by injected instructions or misconfigured tool permissions.

**Common patterns:**
- Shell/exec tool available and auto-approved, no per-command policy
- LLM output used as a command argument without sanitization
- Agent manipulated via ASI01 to invoke exec capability it legitimately has but shouldn't use for this task
- Code execution triggered by content in retrieved documents or emails
- Tool-loop detection disabled, allowing repeated exec attempts

**What to look for in agent artifacts:**
- Exec or shell tool present in tool inventory with auto-approval configured
- No per-command or per-category deny policy in exec approval config
- Tool-loop detection disabled
- Code generation tools whose output is directly executed without human review
- Subprocess or shell invocation in agent skill code that takes model-provided parameters

**What to look for in agent behavior:**
- Shell or exec tool invoked outside of tasks where execution is expected
- Exec called with parameters that include network tools (curl, wget, nc), credential paths, or archive creation
- Repeated exec attempts with slight variations
- Living-off-the-land chains built from exec primitives (PowerShell, shell one-liners) that evade host EDR

**Also — beyond shell/exec:** unsafe object deserialization → RCE; an exposed `eval()` powering agent memory over untrusted content; code-hallucination-with-backdoor (legit-looking generated code hiding a backdoor); malicious package install / lockfile poisoning (hostile code runs at install/import in ephemeral sandboxes — co-tag ASI04; the poisoned dependency itself, pre-deploy, is LLM04 — Supply Chain); non-shell execution (JIT/WASM modules, template engines, in-memory eval).

**Neighbors:** ASI05 is execution; misuse of *non-exec* tools is ASI02's subject; model output reaching the exec sink unhandled co-tags LLM10 (Improper Output Handling) — primaries per the arbitration section.

**Praxen relevance:** Praxen — exec config audit is a named high-priority check. Flag auto-approved shell exec, absent per-command policies, and exec capabilities that exceed the remit.

---

## ASI06 — Memory and Context Poisoning

**What it is:** The agent's memory systems — session context, long-term memory files, RAG knowledge bases — are manipulated to alter future behavior or persist malicious instructions across sessions.

**Why this is agentic-specific:** Unlike a single-turn LLM, agents carry state. Poisoning that state creates persistent, compounding effects. An attacker who successfully poisons an agent's memory gains influence over all future sessions.

**Common patterns:**
- Agent writes attacker-controlled content into its memory files
- Malicious instructions embedded in a document or email are summarized into long-term memory
- RAG knowledge base is modified with content that redirects future agent behavior
- Session context accumulates instructions from external sources that persist across turns

**What to look for in agent artifacts:**
- Memory files (`MEMORY.md`, `sessions.json`, daily memory files) with content that includes instruction-like language from external sources
- Write access from the agent to its own memory or knowledge base without review
- Memory files that include content from external senders or untrusted sources
- No memory review or audit process documented (if purely an observability gap — RAISE only, no OWASP code)

**What to look for in agent behavior:**
- Agent behavior that shifts between sessions without a corresponding instruction change
- Agent referencing context or instructions that don't appear in the current session's inputs
- Agent acting on a "remembered" instruction that was inserted by an external party

**Also:** trigger-based memory backdoors (poisoned memory plants a latent trigger that later fires hidden/destructive instructions); cross-agent shared-memory propagation (contaminated shared memory spreading between cooperating agents); detection-subversion (retraining a security agent's memory to label malicious activity as normal); gradual long-term memory drift / goal-reweighting.

**Neighbors:** ASI06 is governed by the **persistence test** in the arbitration section: poisoning that persists as agent state across sessions is ASI06 primary (co-tag LLM09 — Vector & Embedding Weaknesses — when the store is vector-backed); a one-shot vector/embedding weakness, including cross-tenant vector bleed on retrieval, is LLM09's subject unless the bled content is then stored into memory.

**Praxen relevance:** Praxen — inspect persistent memory files for external-origin content, check whether memory writes are validated, confirm memory contents do not include instruction-like text that could act on the agent.

---

## ASI07 — Insecure Inter-Agent Communication

**What it is:** In multi-agent systems, communication between agents is not properly authenticated, validated, or isolated — allowing one compromised agent to manipulate others.

**Common patterns:**
- Agent-to-agent messages treated as trusted without authentication
- Orchestrator agent manipulated to issue malicious instructions to worker agents (ASI01 primary for the manipulation, ASI07 co-tag for the channel, ASI08 per the spread test)
- Worker agent output injected with content that redirects the orchestrator
- No separation between agent identity and message content

**What to look for in agent artifacts:**
- Inter-agent communication channels with no authentication
- Agent instructions that can be overridden by content from other agents
- No message schema validation on inter-agent inputs
- Shared memory or state between agents without access controls

**What to look for in agent behavior:**
- Agent receiving instructions from an unexpected source (another agent, not the operator)
- Agent behavior that changes after interaction with a sub-agent or external agent

**Also:** replay of delegation / trust messages (stale instructions honored); protocol downgrade to a legacy or unencrypted mode to inject objectives; MITM / missing transport encryption (interception, not just missing auth); discovery/routing spoofing & A2A registration forgery; metadata / timing side channels; semantic split-brain (one message parsed into divergent intents by different agents).

**Neighbors:** ASI07 is the channel/transport defect; when the defect is identity rather than transport, ASI03 is the subject; a goal redirected through an inter-agent message makes ASI01 primary with ASI07 co-tag — per the arbitration section.

**Praxen relevance:** Praxen — audit inter-agent channel configuration, confirm identity verification for messages received from other agents, flag trust-without-verification patterns in A2A handlers.

---

## ASI08 — Cascading Failures

**What it is:** A failure or compromise in one part of an agentic system propagates through tool chains, sub-agents, or sequential tasks, amplifying the impact far beyond the initial vulnerability.

**Common patterns:**
- One injected instruction causes a chain of tool calls, each building on the last
- A bad decision by an orchestrator propagates unchecked to all workers
- An error in early task output corrupts all downstream task inputs
- Duplicate actions amplified across a multi-step pipeline

**Predisposing conditions (artifacts):** these do not themselves earn an ASI08 tag — they make cascade possible; tag them per the arbitration table (missing ceilings with nothing spread → LLM06, Unbounded Consumption):
- No max-retry or circuit breaker configuration in the agent or its tools
- Long pipeline designs with no human checkpoint between steps
- No rollback or compensating action for failed or misdirected tool calls

**What to look for in agent behavior:**
- Repeated action sequences that escalate in impact
- Same error appearing across multiple tool calls in sequence
- Agent that keeps retrying a failed or misdirected action without halting

**Also:** governance-drift cascade (oversight weakening after repeated success; bulk approvals / policy relaxations propagating across agents); auto-deployment cascade (an orchestrator pushes a tainted release to all connected agents); inter-agent feedback-loop amplification (agents reinforcing each other's outputs); shared-infrastructure availability cascade.

**Neighbors:** ASI08 is an *outcome* code governed by the **spread test** in the arbitration section — mechanism primary, ASI08 co-tag when corruption actually propagates; ASI08 primary only when uncontrolled propagation is itself the sole finding. Loops that burn only cost/latency are LLM06's (Unbounded Consumption) subject.

**Praxen relevance:** Praxen — check for tool-loop detection, retry caps, and rate limits in config. Flag missing circuit breakers on capabilities that can fire in a loop (search, tool calls, retries).

---

## ASI09 — Human-Agent Trust Exploitation

**What it is:** Attackers exploit the trust relationship between humans and agents, in either direction — manipulating the human into over-trusting the agent, or manipulating the human decision layer around the agent (fake approvals, laundered consent).

**Common patterns:**
- Agent's authority presented to humans as absolute, causing over-reliance on potentially compromised outputs
- Weaponized / fake explainability — fabricated convincing rationales that hide malicious logic to win approval
- Consent-laundering via a "read-only" preview that triggers side effects
- Emotional manipulation / anthropomorphism exploiting the human's trust
- Multi-turn manipulation where each individual approval the *human* grants is locally reasonable (boiling frog on the approver)

**What to look for in agent artifacts:**
- No warning to operator when agent receives instructions from a new or unusual source (if purely an alerting gap — RAISE only, no OWASP code)
- Agent policy that allows external parties to claim operator-level trust
- Opaque explainability forcing unquestioning trust; missing final human confirmation on a sensitive or irreversible action (the missing gate itself is LLM03 — Excessive Agency; ASI09 is the deception that exploits it)

**What to look for in agent behavior:**
- Progressive multi-step compliance where each *human approval* seems reasonable but the aggregate is out of scope
- Agent taking actions at the request of a party not in the authorized counterparty list
- Trust relationship expanding unexpectedly — new sender treated as trusted

**Neighbors:** both directions are ASI09's scope, but the *agent-side* variants route elsewhere: instructions accepted from a spoofed sender are ASI03's subject (the identity check failed); agent-side progressive compliance is ASI01's; ASI09 covers the *human* being deceived or walked forward — per the arbitration section.

**Praxen relevance:** Praxen — confirm the remit declares explicit counterparty and trust-scope lists, verify code enforces them, flag trust-expansion paths (e.g., any message sender becoming "known" through history).

---

## ASI10 — Rogue Agents

**What it is:** An agent begins operating outside its intended goals, constraints, or authorization — whether through compromise, goal drift, capability expansion, or failure of oversight. The agent is no longer the agent that was deployed.

**This is the category Praxen exists to address.**

**Common patterns:**
- Agent that was compromised via ASI01 and is now pursuing an attacker's goals
- Agent whose capabilities were expanded at runtime (new tools, new permissions) beyond what was authorized
- Agent that has drifted from its remit over time through accumulated context or memory poisoning
- Agent whose **oversight / approval control** (the kind that can *block* a deviation — not passive audit logging) was disabled or degraded, allowing undetected deviation
- Agent running without any oversight mechanism (standing autonomy — LLM03, Excessive Agency, primary; ASI10 co-tag per arbitration)
- **Reward hacking / specification gaming** — gaming a flawed reward metric (e.g. deleting production backups to "minimize cost")
- **Self-replication** — spawning unauthorized replicas for persistence / takedown-evasion
- **Collusion** — multiple agents coordinating to amplify manipulation
- **Scheming / deceptive compliance** — appears compliant while pursuing a hidden goal (deceptive alignment)
- **Impersonated observer/approval agent** — a fake review agent injected to rubber-stamp actions (subverts the oversight layer itself; the injected agent is ASI04/ASI07 primary, ASI10 co-tag)

**What to look for:**
- Behavior outside the Worker Remit — this is the primary Praxen detection
- Tool inventory that exceeds the remit's declared inventory (its Known Good Baseline section) — tag LLM03 (Excessive Agency) unless evidence shows the excess was *acquired after deploy*
- Memory or context that contains instructions not from the authorized operator
- An **oversight / approval control** (not passive audit logging) that has been degraded or disabled
- Agent that previously passed all behavioral checks now failing them systematically

**Neighbors:** ASI10 is an *outcome* code governed by the **outlive test** in the arbitration section — the mechanism (LLM01 Prompt Injection, LLM03 Excessive Agency, ASI02, ASI03, ASI06…) is primary, ASI10 co-tags only when the deviation persists beyond the triggering action or the agent runs with standing autonomy; ASI10 is primary only for the self-contained rogue behaviors listed above. A "no audit log" gap is never ASI10 — it is a RAISE auditability finding.

**Praxen relevance:** All detectors. ASI10 is the end state that all other ASI categories can contribute to. Praxen's mission is to detect the drift toward ASI10 before it becomes irreversible.

---

## Agentic Attack Chain Patterns

These multi-step patterns appear in documented real-world agent incidents:

| Pattern | Steps | Categories Involved |
|---------|-------|---------------------|
| Phishing-to-exec | Trusted-looking email → goal hijack → exec approved → shell commands run | ASI03, ASI01, ASI05 |
| Memory persistence | Malicious doc retrieved → summarized into memory → future sessions redirected | ASI01, ASI06 |
| Privilege creep | New tool added → approval gap → unauthorized action in next session | LLM04/ASI04, LLM03, ASI10 |
| Cascade loop | First action fails → retry loop → amplified impact across tool chain | ASI08, LLM06 (Unbounded Consumption) |
| Trust expansion | New sender impersonates known party → trust granted → data exfiltrated | ASI03, ASI01, ASI02 |

The **compound severity rule** for chains is in the Primary Arbitration section: consecutive steps of a single row, chain-head escalates one level, others in `related_findings`.

---

*Source: OWASP Top 10 for Agentic Applications 2026 — genai.owasp.org — CC BY-SA 4.0*
*Distilled for the Praxen knowledge base*

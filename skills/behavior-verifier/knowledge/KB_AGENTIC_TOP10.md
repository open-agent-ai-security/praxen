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

**Also:** scheduled / recurring goal-reweighting drift (e.g. a malicious calendar invite that injects a recurring instruction subtly reweighting objectives each cycle); manipulated-but-plausible output that steers a business decision (not only scope/action deviation).

**Boundary:** ASI01 = *direct* alteration of goals/decision-paths (regardless of persistence or active control); **ASI06** = persistent stored-context/memory corruption (which often *leads to* ASI01); **ASI10** = autonomous misalignment emerging *without* an active attacker.

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
- No approval gate on high-impact tool invocations
- Missing tool-use logging

**What to look for in agent behavior:**
- Tool being called with parameters that don't match the stated task
- Same tool called repeatedly with slight parameter variations (probing behavior)
- Tool producing output that is inconsistent with the stated action (evidence mismatch)
- High-impact tool (send, delete, exec) called without evidence of approval

**Also — non-exec misuse patterns:** tool-name impersonation / typosquatting / alias collision (`report` resolving before `report_finance`); living-off-the-land tool chaining that evades host EDR (PowerShell / cURL / internal APIs seen as benign); covert-channel exfil via an approved low-risk tool (DNS via a ping tool); internal→external exfil chaining (internal CRM tool + external email tool); loop-amplified costly-API DoS / bill spikes (co-tag LLM10).

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

**Also:** TOCTOU / authorization drift (permissions valid at workflow start, stale or expired by execution); cross-agent confused deputy (a low-priv agent relays valid-looking instructions to a high-priv agent that executes without re-checking intent); memory-based privilege retention (creds cached across tasks/users, reused in a weaker session — co-tag ASI06); OAuth device-code phishing binding a victim tenant to attacker scopes; un-scoped privilege inheritance through delegation chains.

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
- New plugins or MCP servers in the environment with no documented source or review
- Framework or runtime version not pinned or not documented
- Tool description text that includes instructions to the model beyond what the tool nominally does ("When using this tool, also...")
- No integrity verification on tool or plugin files (no hash, no signature)

**What to look for in agent behavior:**
- Tool behavior that diverges from its description (tool claims to search but sends data)
- New capability appearing in the agent's effective behavior without a corresponding new tool in the authorized list

**Also:** remotely-loaded poisoned prompt templates; typosquatting / impersonation of dynamically-discovered tools or endpoints; a vulnerable third-party **peer agent** invited into a workflow (overlaps ASI07 — tag ASI04 for the composition risk); a compromised MCP / registry server serving signed-looking manifests at scale; a poisoned third-party knowledge/RAG plugin (co-tag ASI06). *(Boundary: LLM03 = static pre-deploy dependency; ASI04 = runtime tool/agent composition.)*

**Praxen relevance:** Praxen (supply chain category, tool inventory change detection, rug pull detection). The log registry update is a direct defense against silent rug pulls.

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

**Also — beyond shell/exec:** unsafe object deserialization → RCE; an exposed `eval()` powering agent memory over untrusted content; code-hallucination-with-backdoor (legit-looking generated code hiding a backdoor); malicious package install / lockfile poisoning (hostile code runs at install/import in ephemeral sandboxes — bridges ASI04); non-shell execution (JIT/WASM modules, template engines, in-memory eval).

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
- No memory review or audit process documented

**What to look for in agent behavior:**
- Agent behavior that shifts between sessions without a corresponding instruction change
- Agent referencing context or instructions that don't appear in the current session's inputs
- Agent acting on a "remembered" instruction that was inserted by an external party

**Also:** trigger-based memory backdoors (poisoned memory plants a latent trigger that later fires hidden/destructive instructions); cross-agent shared-memory propagation (contaminated shared memory spreading between cooperating agents); **cross-tenant vector bleed** (namespace-filter bypass pulling another tenant's chunk via high cosine similarity); detection-subversion (retraining a security agent's memory to label malicious activity as normal); gradual long-term memory drift / goal-reweighting.

**Boundary — ASI06 vs LLM08:** vector/embedding poisoning that **persists as agent memory and alters autonomous reasoning across sessions is ASI06 (co-tag LLM08)**; a one-shot retrieval/store weakness with no cross-session persistence is LLM08.

**Praxen relevance:** Praxen — inspect persistent memory files for external-origin content, check whether memory writes are validated, confirm memory contents do not include instruction-like text that could act on the agent.

---

## ASI07 — Insecure Inter-Agent Communication

**What it is:** In multi-agent systems, communication between agents is not properly authenticated, validated, or isolated — allowing one compromised agent to manipulate others.

**Common patterns:**
- Agent-to-agent messages treated as trusted without authentication
- Orchestrator agent manipulated to issue malicious instructions to worker agents
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

**Praxen relevance:** Praxen — audit inter-agent channel configuration, confirm identity verification for messages received from other agents, flag trust-without-verification patterns in A2A handlers.

---

## ASI08 — Cascading Failures

**What it is:** A failure or compromise in one part of an agentic system propagates through tool chains, sub-agents, or sequential tasks, amplifying the impact far beyond the initial vulnerability.

**Common patterns:**
- One injected instruction causes a chain of tool calls, each building on the last
- A bad decision by an orchestrator propagates unchecked to all workers
- An error in early task output corrupts all downstream task inputs
- No circuit breakers, retry limits, or human checkpoints in long-running pipelines
- Duplicate actions amplified across a multi-step pipeline

**What to look for in agent artifacts:**
- No max-retry or circuit breaker configuration in the agent or its tools
- Long pipeline designs with no human checkpoint between steps
- No rollback or compensating action for failed or misdirected tool calls

**What to look for in agent behavior:**
- Repeated action sequences that escalate in impact
- Same error appearing across multiple tool calls in sequence
- Agent that keeps retrying a failed or misdirected action without halting

**Also:** governance-drift cascade (oversight weakening after repeated success; bulk approvals / policy relaxations propagating across agents); auto-deployment cascade (an orchestrator pushes a tainted release to all connected agents); inter-agent feedback-loop amplification (agents reinforcing each other's outputs); shared-infrastructure availability cascade.

**Origin-vs-propagation rule (finding-level secondary trigger):** tag the *initial* defect as its mechanism (ASI04/06/07, etc.) as primary. Then **add ASI08 as a `tags[]` secondary only when a *compromised or corrupted* state propagates beyond the initial action — to other agents or into future runs**: a poisoned output/artifact consumed by another agent or reused in a later session, an orchestrator decision that fans out to all workers, or an unbounded retry / tool-loop that amplifies a bad state. A single agent merely *having* multiple steps is **not** cascade — the corruption must actually **spread**. If the blast radius is one contained action, leave ASI08 off. ASI08 is a roll-up — secondary, never alone; tag it **primary only** when uncontrolled propagation *itself* is the finding.

**Praxen relevance:** Praxen — check for tool-loop detection, retry caps, and rate limits in config. Flag missing circuit breakers on capabilities that can fire in a loop (search, tool calls, retries).

---

## ASI09 — Human-Agent Trust Exploitation

**What it is:** Attackers exploit the trust relationship between humans and agents — either by manipulating the human into over-trusting the agent, or by manipulating the agent through social engineering that mimics trusted human principals.

**Common patterns:**
- Social engineering that impersonates a trusted operator to redirect the agent
- Phishing emails to the agent that appear to come from a known sender
- Typosquatted domains or display names that pass superficial trust checks
- Agent's authority presented to humans as absolute, causing over-reliance on potentially compromised outputs
- Multi-turn manipulation where each individual step is locally reasonable (boiling frog)

**What to look for in agent artifacts:**
- Trust checks based on display name or substring match rather than canonical identity verification
- No warning to operator when agent receives instructions from a new or unusual source
- Agent policy that allows external parties to claim operator-level trust

**What to look for in agent behavior:**
- Progressive multi-step compliance where each step seems reasonable but the aggregate is out of scope
- Agent taking actions at the request of a party not in the authorized counterparty list
- Trust relationship expanding unexpectedly — new sender treated as trusted

**The primary framing is the agent manipulating the human** (not only the reverse). **Flag:** weaponized / fake explainability (fabricated convincing rationales that hide malicious logic to win approval); emotional manipulation / anthropomorphism exploiting trust; a missing final human confirmation on a sensitive or irreversible action; opaque explainability forcing unquestioning trust; consent-laundering via a "read-only" preview that triggers side effects. *(Boundary: ASI09 = human misperception / over-reliance; ASI03 = credential/permission misuse; ASI10 = the agent's own intent deviating.)*

**Praxen relevance:** Praxen — confirm the remit declares explicit counterparty and trust-scope lists, verify code enforces them, flag trust-expansion paths (e.g., any message sender becoming "known" through history).

---

## ASI10 — Rogue Agents

**What it is:** An agent begins operating outside its intended goals, constraints, or authorization — whether through compromise, goal drift, capability expansion, or failure of oversight. The agent is no longer the agent that was deployed.

**This is the category Praxen exists to address.**

**Common patterns:**
- Agent that was compromised via ASI01 and is now pursuing an attacker's goals
- Agent whose capabilities were expanded (new tools, new permissions) beyond what was authorized
- Agent that has drifted from its remit over time through accumulated context or memory poisoning
- Agent whose monitoring was disabled or degraded, allowing undetected deviation
- Agent running without any oversight mechanism
- **Reward hacking / specification gaming** — gaming a flawed reward metric (e.g. deleting production backups to "minimize cost")
- **Self-replication** — spawning unauthorized replicas for persistence / takedown-evasion
- **Collusion** — multiple agents coordinating to amplify manipulation
- **Scheming / deceptive compliance** — appears compliant while pursuing a hidden goal (deceptive alignment)
- **Impersonated observer/approval agent** — a fake review agent injected to rubber-stamp actions (subverts the oversight layer itself)

**What to look for:**
- Behavior outside the Worker Remit — this is the primary Praxen detection
- Tool inventory that exceeds the Known Good Baseline
- Memory or context that contains instructions not from the authorized operator
- Monitoring or logging that has been degraded or disabled
- Agent that previously passed all behavioral checks now failing them systematically

**ASI10 is an outcome, not a mechanism** — the end state that ASI01–09 (and LLM06) *lead to*. So **name the specific mechanism as the primary tag**, then decide ASI10 by one test.

**The test — does the deviation outlive the action?** A one-time, direct attack that causes one action — or a short burst of actions — is **not** a rogue agent; that is the *mechanism* (LLM01 injection, LLM06 excessive agency, ASI02 tool misuse, ASI03 identity abuse). The agent did a bad thing and it's over. Add **ASI10 as a `tags[]` secondary only when the finding reaches the *core* of the agent** so it operates **out of bounds beyond that short-lived action** — persistently or on its own. Concretely, one of:

- **Persistent alteration of the agent itself** — poisoned memory/context that carries into later turns or sessions, a **stored** goal / instruction / config override, or a tool / permission set expanded past the authorized baseline. The agent stays off-mission after the triggering action ends.
- **Standing autonomy without oversight** — a fail-open full-autonomy mode, or a removed / disabled / default-off approval layer, under which the agent runs **unsupervised and self-directed**, not merely one ungated action.

Ask: *when the immediate action(s) finish, is the agent still operating out of bounds?* **Yes → ASI10 secondary. No → mechanism only, no ASI10.** So an ungated pay action, a missing auth check, or a one-shot prompt injection an attacker must re-trigger each time is **not** ASI10 — its mechanism already captures it. A **"no audit log" gap is never ASI10** (a missing log doesn't alter the agent's core; it's a RAISE auditability finding). **Self-check:** if you're tagging ASI10 on more than a *minority* of findings, you've slid back to "any weakness → rogue" — re-read the test.

- **Primary — legal but rare.** Tag ASI10 *primary* only for a **self-contained rogue behavior with no upstream vector to name**: reward hacking / specification gaming, self-replication, collusion, scheming / deceptive compliance, or self-directed capability expansion beyond authorization.

Same origin-vs-propagation discipline as ASI08.

**Praxen relevance:** All detectors. ASI10 is the end state that all other ASI categories can contribute to. Praxen's mission is to detect the drift toward ASI10 before it becomes irreversible.

---

## Agentic Attack Chain Patterns

These multi-step patterns appear in documented real-world agent incidents:

| Pattern | Steps | Categories Involved |
|---------|-------|---------------------|
| Phishing-to-exec | Trusted-looking email → goal hijack → exec approved → shell commands run | ASI01, ASI03, ASI05 |
| Memory persistence | Malicious doc retrieved → summarized into memory → future sessions redirected | ASI01, ASI06 |
| Privilege creep | New tool added → approval gap → unauthorized action in next session | ASI04, ASI02, ASI10 |
| Cascade loop | First action fails → retry loop → amplified impact across tool chain | ASI08, LLM10 |
| Trust expansion | New sender impersonates known party → trust granted → data exfiltrated | ASI03, ASI09, ASI01 |

**Praxen compound finding rule:** When findings from two or more of these steps appear together, escalate the combined severity one level above the highest individual finding. Note the chain in `related_findings`.

---

## Resolving adjacent categories (pick the dominant code by mechanism)

Findings slide between neighbouring categories run-to-run when the boundary is left to intuition. Choose the dominant code by the **mechanism that produces the harm**, not the surface symptom; put genuinely co-applicable codes in `tags[]`.

| If the finding is fundamentally about… | Dominant code | Not… |
|---|---|---|
| Executing code / shell / commands | **ASI05** (Unexpected Code Execution) | ASI02 — that's for non-exec tools |
| Misusing a **non-exec** tool (email, file, API) for a wrong purpose | **ASI02** (Tool Misuse) | ASI05 |
| The **identity / credential** scope — shared account, broad OAuth, trust on an unverified identity | **ASI03** (Identity & Privilege Abuse) | ASI02 (tool capability) |
| A failure **propagating / amplifying** through a tool chain or sub-agents | **ASI08** (Cascading Failures) | LLM10 — that's resource exhaustion |
| Resource / cost / token exhaustion, runaway spend, denial-of-wallet | **LLM10** (Unbounded Consumption) | ASI08 |
| Vector/embedding poisoning that **persists as agent memory** & alters reasoning across sessions | **ASI06 + LLM08** (co-tag) | LLM08-only |
| A **one-shot** vector/embedding weakness with no cross-session persistence | **LLM08** (Vector & Embedding) | ASI06 |
| Poisoning **non-vector** memory / session / context files | **ASI06** (Memory & Context Poisoning) | LLM08 |
| A **self-approval / no approval gate** on a consequential action | **LLM06** (Excessive Agency) | ASI10 |
| A **self-contained rogue behavior** (reward hacking, self-replication, collusion, scheming) | **ASI10** (Rogue Agents) — *primary is legal but rare* | a named mechanism (ASI01/03/06) |
| **No audit log / no monitoring / no alerting** (pure observability gap) | **RAISE only** — no OWASP code | ASI10 / LLM06 |

**Rule of thumb:** name the code by the *mechanism*, not the symptom — and **prefer a specific mechanism over an outcome category** (ASI08, ASI10). A capability the remit forbids, or an unguarded consequential action, is **LLM06**. A **pure logging / monitoring / audit gap is RAISE, not OWASP** — don't force a code onto it.

---

*Source: OWASP Top 10 for Agentic Applications 2026 — genai.owasp.org — CC BY-SA 4.0*
*Distilled for the Praxen knowledge base*

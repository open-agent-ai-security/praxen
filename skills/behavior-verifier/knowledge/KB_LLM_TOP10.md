<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Knowledge Base: OWASP Top 10 for LLM Applications (2026)
*Distilled for Praxen — behavioral and environmental scanning context*

Source: OWASP Top 10 for LLM Applications 2026 — genai.owasp.org
License: CC BY-SA 4.0

This file is a Praxen knowledge base extract. It strips administrative content and retains only the signal relevant to detecting, classifying, and reasoning about LLM security risks in a running agent environment. Use it as context when evaluating agent behavior or scanning agent artifacts.

---

## How to Use This Knowledge Base

When Praxen detects a behavioral or environmental signal, map it to the relevant LLM risk category below. Use the risk category to:
- Name the finding correctly
- Understand what an attacker could do with it
- Know what evidence to look for
- Generate a specific, grounded recommendation

Tag findings with **2026 numbering only** — this file is the sole authority for *LLM-category* tags at scan time (ASI codes are grounded in the Agentic KB; cross-version mapping against pre-2026 baselines lives in the docs and test tooling, not here).

**Division of labor inside this file.** The ten entries describe each risk and list the *evidence* to look for; they defer tag arbitration — which code is primary, which codes co-tag — to one place: the **Primary Arbitration** section directly below. When an entry's text and your instinct disagree about a tag, the arbitration section wins.

---

## Primary Arbitration — read before tagging

**Tag semantics — two relations only.** A finding's first code is its **primary**: the category that best names the weakness. Every other applicable code is a **co-tag** — an additional code, never a replacement.

**The evidence-class rule.** Most compound findings touch an input, a capability, and a sink. The primary follows the evidence class of the specific weakness being recorded:
- **Input-side evidence** — untrusted or unlabeled content entering the model's context → **LLM01** primary
- **Grant/gate evidence** — a tool definition, permission scope, or missing approval gate → **LLM03** primary
- **Sink-side evidence** — model output reaching a shell, query, renderer, or API without handling → **LLM10** primary

The other applicable codes ride as co-tags. **When one finding's quoted evidence spans classes, use the fixed order sink > input > grant:** quoted sink evidence makes LLM10 primary even when input and grant evidence co-occur; failing sink evidence, input (LLM01); failing both, grant (LLM03). Exception: a code-execution sink on a live path is ASI05 primary per the Agentic KB, LLM10 co-tag. Two standing prohibitions: never drop LLM10 because "there is no gate" (raw `exec(model_output)` is the *maximal* LLM10, not a reason to skip it), and never drop LLM03 because the finding "reads as a missing control" (a reachable ungated capability *is* LLM03).

**Cross-KB precedence:** when both KBs are in context, a compound finding involving any ASI code is governed by the Agentic KB's mechanism rule and its spread/outlive/persistence tests; between overlapping compound-table rows in either KB, the more specific row wins.

**One finding per fix-point.** Record one finding per independently-fixable control gap **on a distinct data path**. A single injection→sink chain is one finding even though it has multiple candidate fixes — labeling the input and sanitizing the sink are defenses for the *same path*, so: one finding, primary per the evidence-class rule, remaining codes as co-tags. Gaps on *different* paths (an unauthenticated store write path *and* an injection exploitation through retrieved content) are separate findings, each with its own primary.

**"Disclosure is evidenced"** means scan artifacts show sensitive content actually present (in the store, log, prompt, or output) — not merely reachable.

**Compound-signal table.** One row per recurring signal; primary first, co-tags second. Rows are specializations — where a row matches, it wins over the evidence-class rule. Rows whose co-tags include ASI codes take those definitions from the Agentic KB.

| Signal | Primary | Co-tags |
|--------|---------|---------|
| Untrusted external content enters context unlabeled | LLM01 | LLM02 when disclosure is evidenced; an unguarded store ingesting it is a *separate* LLM09 finding (row below); evidenced *goal alteration* makes ASI01 primary (Agentic KB), LLM01 co-tag |
| Model output reaches shell/SQL/render/API unvalidated | LLM10 — except a code-execution sink on a live path: ASI05 primary (Agentic KB), LLM10 co-tag | LLM03 when an ungated capability delivers the output to the sink |
| Ungated consequential capability (tool, permission, missing approval) | LLM03 | LLM01 when an injection path reaches it; ASI05 when the ungated tool is exec (Agentic KB) |
| Unvetted ingestion into a vector/embedding-backed store (write/ingest path in evidence) | LLM09 | LLM05 as applicable; a *third-party-poisoned* source is ASI04 primary (Agentic KB) — this row is the own-ingest-path gap |
| Agent-writable vector store with unguarded write path | LLM09 | LLM01; ASI06 per the Agentic KB persistence test — evidenced poisoning persisting as agent state flips to ASI06 primary, LLM09 co-tag |
| Agent-writable **non-vector** memory (files, databases) with unguarded write path | LLM01 | ASI06 per the Agentic KB persistence test — evidenced persistent poisoning flips to ASI06 primary |
| Poisoned training/fine-tuning data or own-pipeline artifacts | LLM05 | — (supplier-delivered → next row: LLM04 primary) |
| Supplier-delivered model/artifact risk (unpinned, unsigned, tampered) | LLM04 | LLM05 when the payload is poisoned content |
| Unverified plugin / MCP server install | LLM04 | ASI04 |
| Retrieval with no pre-retrieval authorization check | LLM09 | LLM02 when disclosure is evidenced |
| Secrets or credentials in hidden context (prompt, tool description) | LLM02 | LLM08 |
| Non-secret control logic, roles, or schemas exposed in hidden context | LLM08 | LLM01 (reconnaissance value), LLM03 |
| Unredacted prompt/response capture in logs or observability tooling | LLM02 | — |
| Missing audit trail (nothing recorded at all) | RAISE auditability — no OWASP code | — |
| Hallucinated package names in generated code | LLM07 | LLM04 — which becomes primary only when scan artifacts themselves evidence the malicious registry entry |
| Fabricated or unverified task completion | LLM07 | ASI10 only when the deception persists per the Agentic KB outlive test |
| Exposed logits / log-probabilities configuration | LLM06 | LLM02 |
| Vulnerable serving/inference dependency | LLM04 | LLM06 when the dependency's flaw enables resource overconsumption evidenced in the scan |
| Loops or spend with no ceiling (step, cost, recursion) | LLM06 | ASI08 only per the Agentic KB spread test (corruption actually propagated) |
| Model output auto-rendered with external fetches | LLM10 | LLM01, LLM02 |
| No human review of a consequential action | LLM03 for the missing *approval* gate | LLM07 recorded as a second finding only when a *separate* accuracy-verification mechanism (e.g. a claim–check–act requirement) was expected and is absent; otherwise one LLM03 finding. ASI10 co-tag when the approval layer is absent for the agent *as a whole* (Agentic KB outlive test) |

---

## LLM01 — Prompt Injection

**What it is:** User inputs or external content alter the LLM's behavior in unintended ways. The weakness is architectural: the model draws no distinction between "instructions" and "data" — both are tokens on the same stream — so no robust prevention mechanism exists today. Defense is bounding the blast radius, not filtering the input.

**Two forms:**
- **Direct:** User crafts a prompt that overrides system instructions or extracts sensitive data
- **Indirect:** External content (web pages, files, emails, RAG-retrieved documents, tool outputs) contains hidden instructions that reach the LLM and redirect its behavior. 2026 grades the delivery surface by trust tier — and flags **trusted-surface indirect injection** as the sharpest case: the user's *own* agent is weaponized under its elevated credentials via a low-privilege channel (an issue comment, a shared record).

**What to look for in agent logs and behavior:**
- Agent output that doesn't match the task it was given
- Agent suddenly acting on instructions that appear to have come from external content (emails, documents, retrieved data)
- Agent sharing data, running code, or contacting parties not in the original task — including **zero-click** flows where no user action was needed
- Escalation pattern: small compliance with injected instruction leads to larger follow-on actions

**What to look for in agent code and config:**
- External content (email bodies, web fetches, document reads, tool results) injected directly into LLM context with no provenance labeling — no separation of trusted instructions from untrusted data
- Prompt construction via string concatenation: `prompt = system_prompt + user_input + external_content`
- Write paths into persistent memory or a RAG corpus that are not treated as privileged operations (cross-session poisoning: instructions planted today fire in a later session)
- Consequential tool calls with no deterministic policy gate and no human confirmation showing the *exact rendered action*, not a summary (the missing gate itself is LLM03 primary — see arbitration)

**Risk if exploited:** Unauthorized data access, privilege escalation, execution of commands in connected systems, manipulation of decision-making, exfiltration via crafted outputs — with agentic execution as the severity multiplier (tool outputs re-enter context, enabling chained and self-replicating effects across agents).

**Also — material subtypes (2026):** multimodal injection (instructions hidden in images/audio alongside benign text); jailbreaking (the subset aimed at making the model violate its safety protocols); **invisible-character injection** (Unicode Tag-block, zero-width, variation-selector characters) and **ASCII-smuggling** exfiltration; encoded / multilingual / low-resource-language payloads; payload splitting; exposed fine-tuning APIs usable as a payload-optimization oracle ("fun-tuning"); unintentional injection (benign content that triggers it). Filters and classifiers are expected to degrade against adaptive attackers — weight architectural controls (least-privilege capability budgets, e.g. the **Rule of Two**: an agent combining untrusted input, sensitive-data access, and external actions needs per-action approval — and two-of-three configurations still require an explicit residual-risk assessment) over screens.

**Neighbors:** LLM01 is the *input* boundary; the disclosure consequence is LLM02's subject, the sink is LLM10's, the capability grant is LLM03's — primaries per the arbitration section. An injection finding co-tags LLM02 when disclosure is evidenced.

**Praxen relevance:** Praxen — detect injection-vulnerable code patterns, flag external content entering the LLM context without sanitization or provenance labeling, check memory/RAG write paths for privilege, check for content-origin labeling in prompt construction.

---

## LLM02 — Sensitive Information Disclosure

**What it is:** The system reveals sensitive data — PII, credentials, proprietary algorithms, confidential business data — through any observable surface: final outputs, tool-call arguments, reasoning traces, retrieved chunks, logs and telemetry, embeddings, even inference side channels (timing, token length, log-probabilities — though an exposed logits *configuration* itself is LLM06 primary, see arbitration).

**What to look for in agent artifacts:**
- Credentials, API keys, tokens, or passwords in any workspace file (not just `.env` — check docs, logs, snapshots, config examples, archive files)
- PII in training data, RAG knowledge bases, or memory files
- Observability/tracing integrations (e.g. Langfuse, LangSmith, Datadog) capturing full prompt/response content by default without redaction
- Retrieval layers with no authorization check *before* retrieval — similarity search does not respect ACLs (LLM09 primary — see arbitration)
- Log files that capture sensitive data; reasoning traces not classified and redacted as first-class output
- Sensitive data absorbed into weights, adapters, or memory files with no erasure/unlearning path — deleting the source does not delete the data

**What to look for in agent behavior:**
- Agent outputs containing data that shouldn't be in a response to the current task
- Agent repeating back information from its context that was only there for internal processing
- Agent including sensitive context fields (credentials, personal data) in messages sent to external parties

**Risk if exploited:** Privacy violations, credential theft, intellectual property exposure, compliance failures — now with hard regulatory clocks (GDPR 72-hour, HIPAA, EU AI Act incident reporting).

**Also — disclosure through the model, not just a file:** model inversion / training-data reconstruction / membership inference; **cross-user leakage** (one user receives another's data); **aggregation** (individually-permitted sources combined into a disclosure); side channels (encrypted-traffic topic inference, shared KV-cache).

**Neighbors:** the retrieval/embedding *mechanism* is LLM09's subject — this entry is the disclosure itself. LLM06 = extraction/theft via inference queries and resource consumption; LLM02 = disclosure of data the system already holds. Exfiltration executed through tool misuse is ASI02 primary per the Agentic KB; LLM02 co-tags when disclosure is evidenced.

**Praxen relevance:** Praxen — detect credentials in unexpected locations, check system prompts and config files for embedded secrets, verify vault references are used instead of literal values, check logging/tracing config for unredacted prompt capture.

---

## LLM03 — Excessive Agency

**What it is:** The LLM is given more permissions, capabilities, or autonomy than it needs, or takes consequential actions without appropriate human approval. 2026 makes it trigger-agnostic: the damaging action can be caused by plain hallucination or a poorly-performing model, by direct/indirect prompt injection, or by a compromised extension or **peer agent** — the vulnerability is the excessive grant, regardless of what made the model misfire.

**Three root causes:**
1. **Excessive functionality:** Agent has tools ("extensions") available that aren't required for its job — including open-ended ones (shell, URL-fetch) where granular tools would do
2. **Excessive permissions:** Agent has read/write/delete/send access it doesn't need
3. **Excessive autonomy:** Agent takes high-impact actions without human-in-the-loop approval

**What to look for in agent artifacts:**
- Tool definitions with write, delete, send, or exec capabilities where the agent's remit is read-only or advisory
- Tools left over from development or trials — no longer used by any workflow but still available to the agent
- No approval gate defined for high-impact actions (sending email, modifying files, executing commands)
- Exec approval config present but empty or set to auto-approve
- OAuth scopes broader than the agent's actual job (e.g., `modify/send/calendar` for an agent that should only read)
- No independent pre-execution policy decision point between the extension and the downstream system ("complete mediation"); tool input schemas absent or unvalidated
- Delegated or multi-agent workflows that drop the original user's authorization scope across chained calls (actions run on the service identity's broader permissions)

**What to look for in agent behavior:**
- Agent taking irreversible actions (sending messages, deleting files, executing commands) without evidence of approval
- Agent performing actions beyond the scope of the task it was given
- Agent performing actions that were in its instructions as examples, not directives

**Tag LLM03 when:** a capability the remit forbids or doesn't grant is present **and reachable** (registered and invocable by the model at runtime, whether or not observed in use) — *even if the finding reads as a control gap* ("no approval gate," "auto-approve," "no confirmation step"). A reachable remit-forbidden capability, or a **high-impact action with no human-in-the-loop gate**, **is** excessive agency/autonomy — tag LLM03; don't leave it untagged because it was framed as a missing control.

**Neighbors:** LLM03 and LLM10 are orthogonal, not a spectrum — LLM03 asks *does the agent have this consequential capability, ungated?*, LLM10 asks *does the model's output reach a sink without adequate handling?* They frequently co-apply; primary per the arbitration section. **A phantom or inert safety control counts as ungated:** when a finding's subject is a claimed-but-nonexistent gate (a docstring promising a sanitizer that is implemented nowhere, a validator wired to nothing), the capability underneath is exactly as ungated as in its sibling raw-capability findings — carry the same LLM03 tag (secondary when the false claim is the primary story) that those siblings carry. The falseness of the claim changes the finding's framing, not the agency it fails to gate. OWASP still lists monitoring and rate limiting as controls that **do not prevent** excessive agency (they only limit damage): a missing audit trail is a RAISE auditability finding, not LLM03 — tag LLM03 for the unguarded consequential action itself, not for the missing log. Agentic manifestations co-tag ASI02 only when wrongful use is shown, ASI03 (privilege abuse), and ASI08 only per the Agentic KB spread test.

**Praxen relevance:** Praxen — capability audit against the remit is a named high-priority check. Flag every tool and permission present in code but absent from the remit. This is the highest-priority RAISE Zero Trust category.

---

## LLM04 — Supply Chain

**What it is:** Vulnerabilities in third-party models, datasets, libraries, serving stacks, and build pipelines that affect the integrity of the AI system. 2026 elevates model artifacts, provenance, and conversion/merge workflows to first-class attack surfaces.

**What to look for in agent artifacts:**
- Framework or runtime with unknown or undocumented provenance
- Open-source model resolved by mutable reference (a `latest` tag) instead of an immutable digest; no signature or hash verification (model signing: OpenSSF/Sigstore)
- Dependencies not pinned or not tracked in a bill of materials (SBOM / ML-BOM / AIBOM)
- Plugins, MCP servers, or tools installed from unverified sources
- Build or deployment pipeline without security gates — including the org's *own* release infrastructure (signed-by-us is not safe-by-us)

**Risk signals:**
- Agent runtime is the most trusted component — if it's compromised, everything the agent does is compromised
- A new plugin appeared in the agent's tool inventory with no documented source
- Library versions not pinned — susceptible to dependency confusion, version-swap, or **slopsquatting** (attackers pre-register package names LLMs hallucinate)
- Model scanners and safe-loader flags treated as guarantees — they are defense-in-depth only (bypasses exist; backdoors ride in the computational graph of "safe" formats)

**Also — ML-specific supply chain (2026):** malicious LoRA/PEFT adapters and bundled non-weight artifacts (supplier-delivered — the same artifacts from your *own* tuning pipeline are LLM05's subject); poisoned model-merge / format-conversion services; **model namespace reuse** (freed account/model names re-registered by attackers); **quantization attacks** (full-precision model evaluates benign, quantized artifact is malicious); vulnerable serving/inference frameworks (Ray, Ollama, llama.cpp CVEs); on-device model tampering; weak model provenance (Model Cards, supplier-account compromise); dataset/model licensing exposure; unclear operator T&Cs (your data used for training).

**Neighbors:** LLM04 = risk arriving via a supplier or pipeline; LLM05 = poisoning of your own data or training process. Agentic supply chain (MCP servers, tool registries) co-tags ASI04.

**Praxen relevance:** Praxen (supply chain category). Every new tool, plugin, or dependency that appears in the agent workspace is a supply chain event requiring evaluation.

---

## LLM05 — Data and Model Poisoning

**What it is:** Data or model artifacts are manipulated to alter model behavior — introducing backdoors, biases, or targeted misbehaviors. The 2026 scope spans the full lifecycle: pre-training, fine-tuning, embedding creation, RAG retrieval, and model distribution — and includes *unintentional* poisoning from poor data hygiene, not just adversaries.

**What to look for in agent artifacts:**
- Fine-tuning pipelines that accept external data without validation; RLHF/feedback loops with no rate limits or review (gradual poisoning via manipulated preference signals)
- Bundled non-weight artifacts from your *own* tuning pipeline — chat templates, tokenizer configs, LoRA adapters, quantization artifacts — not verified as security-relevant code (trigger-activated instructions can ride in a template)
- Non-vector knowledge bases or datasets with unreviewed *content* (vector-backed ingestion is LLM09's subject; an unguarded *write path* into memory is LLM01's — both gaps present is two findings)

**What to look for in agent behavior:**
- Agent behavior that shifts over time without obvious cause (slow drift in how it responds to similar inputs)
- Agent consistently favoring certain outcomes, parties, or recommendations in ways not explained by its instructions

**Also:** backdoors / "sleeper agents" (behavior normal until a trigger fires — auth bypass, exfil, hidden exec); poisoning is **low-volume, high-impact** — a few hundred poisoned documents compromise models regardless of dataset size, and a handful of semantically-optimized docs can own a retrieval pipeline past perplexity filters; **refusal erosion** (safety behavior degraded while accuracy is preserved); safety alignment does **not** remove backdoors — trigger-probing is required after every alignment cycle; malicious model-file pickling (supplier-delivered model files are LLM04's subject); DVC / CycloneDX ML-BOM as the provenance control.

**Neighbors:** supplier-delivered poisoned artifacts are LLM04's subject; poisoning through a vector store's write path is LLM09's; an agent's poisoned persistent memory adds ASI06 — primaries per the arbitration section.

**Praxen relevance:** Praxen — audit data source provenance, flag unvetted fine-tuning or RAG inputs, verify data sources are listed in the remit.

---

## LLM06 — Unbounded Consumption

**What it is:** The agent consumes excessive resources — API calls, compute, tokens, money — without limits. Includes denial-of-wallet, runaway loops, resource exhaustion, and model extraction. The defining characteristic is **cost asymmetry**: a cheap request triggers expensive work.

**What to look for in agent artifacts:**
- No rate limiting on LLM API calls or tool invocations — and rate limits that are request-based only (2026: request-rate limiting alone is insufficient; look for token-aware limits)
- No **hard spending cap** — a non-overridable ceiling that halts, not alerts
- No timeout on long-running tasks; no max-retry limit on failed operations
- No input-size limit or pre-flight token estimation on inference calls
- No agentic circuit breakers: step limits, recursion-depth limits, per-run cost ceilings, loop detection
- Cron or heartbeat jobs that trigger agent sessions with no concurrency limit

**What to look for in agent behavior:**
- Repeated retries beyond normal threshold; same task triggered multiple times without state change
- Session count or API cost spiking above baseline; long sessions whose per-turn cost climbs as context grows (aggregate denial-of-wallet under per-request limits)
- Tool-call fan-out (one call spawning many) or recursive tool loops that appear to run without completing

**Also — model theft / IP extraction (still folded in):** model extraction via crafted API queries (exposed logits/log-probabilities significantly accelerate it); functional replication (use the target to generate synthetic training data, then fine-tune an equivalent); side-channel weight/architecture harvesting. **Also input-side:** "sponge" examples and adversarial inputs optimized for overconsumption; **reasoning-loop / thinking-token exhaustion** (short benign-looking prompts forcing non-terminating reasoning, bypassing input-size filters); multimodal inputs at 10–100× text cost; fine-tune poisoning that breaks end-of-sequence behavior so every response maxes output tokens; serving-stack exploitation (unsafe deserialization, special-token passthrough, injected chat templates in inference frameworks).

**Neighbors:** LLM06 = extraction/theft via inference queries and resource consumption; LLM02 = disclosure of data the system already holds. A vulnerable serving dependency by itself is LLM04's subject.

**Praxen relevance:** Praxen — verify rate limiting and cost controls are present in config, flag absent request-per-session caps, check for timeout configuration on LLM API calls, verify step/recursion/cost ceilings for agent runs.

---

## LLM07 — Misinformation

**What it is:** The LLM produces incorrect, incomplete, unsupported, or misleading information with apparent confidence — omission is now first-class alongside fabrication. In agentic contexts this is a system-level failure: a false representation drives tool calls, generated code, state inference, authorization decisions, and cross-agent coordination.

**What to look for in agent prompts and config:**
- System prompt that instructs the agent to "help anyway" or "do your best" when it lacks grounding — explicit invitation to hallucinate
- No citation or grounding requirement; no verification signals beyond model confidence (no groundedness/consistency checks)
- No separation between claim generation and action execution ("claim–check–act"); tool calls not semantically validated against intent, permissions, and real-world state
- Unstructured outputs where mandatory fields would catch omissions
- No verification of output *accuracy* before it is acted on in consequential decisions

**Why this matters for agents:** An agent that hallucinates doesn't just give a wrong answer — it may take wrong actions, infer workflow state that never existed, or **fabricate task completion** (claims done, no artifact — visible only when someone reviews the logs). In multi-agent systems one agent's hallucination becomes another agent's ground truth (cross-agent propagation).

**Also — the marquee agentic subtypes:** hallucinated package names in generated code ("slopsquatting" — attackers pre-publish malicious packages under the hallucinated names); **overreliance** (unverified output fed into critical decisions — in agentic architectures often embedded in the system design itself); misleading summaries with critical omissions; forged or misattributed evidence. No active attacker is required — this is a reliability failure too, though adversarially-induced misinformation is now explicitly in scope.

**Neighbors:** when the root cause is injection, poisoning, or supply chain compromise, record the root cause as its own finding; record LLM07 separately only when the misinformation gap has its own fix (e.g. no claim–check–act, no grounding requirement) — otherwise omit LLM07.

**Praxen relevance:** Praxen — flag system prompt instructions that invite speculation (e.g., "be creative," "fill in missing details"), check whether the agent is instructed to confirm completion with verifiable output.

---

## LLM08 — Hidden Context Exposure

**What it is:** Unauthorized extraction, inference, or reconstruction of hidden, non-user-facing context. Formerly *System Prompt Leakage* — the leaked system prompt is now one case of a larger class: system prompt, developer instructions, retrieved policy text, **tool and function schemas**, behavioral control logic, safety/refusal criteria, permissions and user roles, and output-structure/formatting rules — everything the application assembles into the context window that the user isn't meant to see.

**What to look for in agent artifacts:**
- Hidden context containing credentials, API endpoints, or sensitive operational details
- Session management, authorization, or content-policy **enforcement living in the prompt** — the core anti-pattern: a leak matters most when it reveals *bypassable* controls that should never have been delegated to the LLM
- Internal business rules, thresholds, role/permission structure, or filtering criteria embedded in instructions (privilege-escalation reconnaissance)
- Tool/MCP descriptions and schemas that reveal sensitive functionality or role requirements
- Output schemas / formatting constraints in hidden context whose disclosure lets attackers forge conforming-but-malicious outputs

**What to look for in agent behavior:**
- Agent revealing its instructions, tool list, or parameter schemas in response to probing — even with no credential disclosed, extracted schemas are reconnaissance for targeted injection and action chaining
- Agent revealing operational details (tool names, endpoints, credentials) that were in its hidden context

**Severity is graded by what the recipient gains** (this ladder applies to any finding produced by this entry's surfaces, whatever its primary): generic instruction text is informational; internal rules, roles, and workflow logic are medium; embedded secrets or secrecy-based authorization are high; disclosure whose chain to RCE, broad exfiltration, or privilege escalation is demonstrated in the same scan is critical.

**The design rule:** assume hidden context is discoverable and design so full disclosure has minimal security impact. Authorization, privilege separation, policy, and content filtering must be enforced deterministically *outside* the LLM; prompt/structure obfuscation is a minor supporting measure, never a primary defense.

**Neighbors:** an embedded *secret* is LLM02's subject (this entry is the exposure surface); regulated user/training data leakage is LLM02's; leaked formatting rules feed LLM10 attacks; persistent-memory and inter-agent exposure add ASI06/ASI07.

**Praxen relevance:** Praxen — audit everything assembled into the model's context: flag secrets, roles, thresholds, and business rules embedded in prompts or tool descriptions, and check that any control described in hidden context is actually enforced in code, not just requested of the model.

---

## LLM09 — Vector and Embedding Weaknesses

**What it is:** Vulnerabilities in how vectors and embeddings are **generated, stored, or retrieved** — attacks that exploit the geometry of the embedding space and the mechanics of similarity search. This is the category for **any agent backed by a vector or embedding store**: RAG, vector-backed agent memory, semantic caches, deduplication pipelines — text or multimodal.

**First detect the store, then audit it.** LLM09 is chronically under-tagged because the analyzer skips it when it doesn't notice the store. *Before* concluding LLM09 doesn't apply, check the agent's code for a vector/embedding store:
- Signals: `chromadb`, `faiss`, `pinecone`, `weaviate`, `qdrant`, `milvus`, `pgvector`, `lancedb`, `sentence-transformers`, `text-embedding*`, `embeddings.create`, `vectorstore`/`vector_store`, `similarity_search`, `embed_query`/`embed_documents`, `cosine_similarity`.
- **In-scope** = any vector/embedding store the scanned agent reads from or writes to, regardless of who operates it. If an in-scope store is present, the audit below is **mandatory** — record an LLM09 finding for each weakness the audit confirms. A fully hardened store yields none: store presence alone is not a finding, and an agent-writable store is a finding only while its write path lacks *any* of: authentication, validation, hidden-content detection. Weaknesses sharing one fix merge into one finding listing both (e.g. inversion + membership inference via the same raw-score exposure). Vectorless retrieval (BM25-only, no embeddings) has no LLM09 surface.

**The weaknesses to check (artifacts):** *poisoning makes the system wrong, inversion makes it leak, jamming makes it silent, and access-control failure makes it indiscriminate.*
1. **Cross-tenant leakage via shared similarity search** — tenant/user scoping enforced only as a post-retrieval filter instead of *inside the index query*; side channels (result counts, similarity scores, timing) leak membership even when documents are withheld.
2. **Embedding inversion** — embeddings or raw vectors exposed or exportable; source text is recoverable, so an "embeddings-only" backup **is** a source-document breach; the store not treated at the sensitivity of its sources.
3. **Retrieval-time data poisoning** — the store ingests unvetted content (user uploads, live web, or **the agent's own generated output**) with no validation, hidden-content detection, or authenticated write path; a handful of optimized documents is enough if they get *retrieved* and *steer* the response.
4. **Retrieval jamming** — "blocker" documents crafted so retrieval returns content that makes the model refuse or claim it lacks information (availability attack).
5. **Membership inference via similarity search** — raw similarity scores or perturbed queries turn the index into an oracle for "is this document in the store?"
6. **Semantic cache / deduplication poisoning** — threshold-straddling vectors cause key collisions so one user's poisoned entry is served to others.
7. **Multimodal embedding poisoning** — payloads embedded via images or other modalities; text-based content scanning does not catch them.

**What to look for in agent behavior:**
- Returning information that appears to come from another user's or tenant's context.
- Behavior that shifts after documents enter the store; the agent acting on instructions that were embedded in retrieved content.

**Neighbors:** an instruction-following *exploitation* through retrieved content is LLM01's subject; the store's write-path *control gap* is this entry's — two fix-points, two findings. Training-time poisoning of the embedding model is LLM05's; serialization flaws in vector-store libraries are LLM04's; memory attacks with no vector/embedding store involved add ASI06.

**Praxen relevance:** Praxen — first detect a vector/embedding store; if one is in scope, audit tenant scoping inside the query, the write/ingest path (authentication + validation + hidden-content detection), raw-score/vector exposure, and embedding lifecycle (deletion with source, re-embedding on model rotation, backups at source sensitivity). Record an LLM09 finding for each confirmed weakness.

---

## LLM10 — Improper Output Handling

**What it is:** LLM output is passed to downstream systems — databases, shells, browsers, APIs, terminals, renderers — without validation, enabling injection attacks. Treat the model like any other untrusted user: context-aware output encoding, parameterized queries, CSP.

**What to look for in agent code:**
- LLM output used directly as a shell command: `subprocess.run(llm_output)`
- LLM output used as a database query: `cursor.execute(llm_output)` or f-string SQL
- LLM output rendered as HTML without encoding (XSS vector), or inserted unescaped into email templates (phishing/XSS in mail clients)
- LLM output used as file path (path traversal), API parameter, or network request without sanitization
- Tool call parameters built from raw LLM output strings
- Model output written to terminals, logs, or IDEs without neutralizing control characters (ANSI escapes, OSC clipboard writes — visual spoofing, terminal exploitation)
- Renderers that auto-fetch external resources referenced in model output (Markdown images, link previews, iframes) — an exfiltration channel; look for origin allowlists or a server-side proxy that strips data-bearing query parameters
- An LLM-generated command or code executed with **no or inadequate** screening — from a raw `exec()` / `subprocess.run(llm_output)` with no filter at all (the **maximal** case) to any pattern-based filter over a Turing-complete sink (which always counts as inadequate) — so unsafe model output reaches the sink

**Why this matters for agents:** Agents execute tool calls based on their own outputs. If those outputs can be influenced via prompt injection, the injection → tool execution chain is direct. The model is a confused deputy between the attacker and the downstream system.

**Also:** SSRF / CSRF among the downstream outcomes.

**Neighbors:** LLM10 and LLM03 are orthogonal, not a spectrum — output-reaching-a-sink vs ungated-capability; they frequently co-apply, primaries per the arbitration section. LLM07 / overreliance = trusting the output's *accuracy* rather than failing to sanitize it.

**Praxen relevance:** Praxen (code patterns that pass LLM output to system functions, terminals, or auto-fetching renderers without validation).

---

*Source: OWASP Top 10 for LLM Applications 2026 — genai.owasp.org — CC BY-SA 4.0*
*Distilled for the Praxen knowledge base*

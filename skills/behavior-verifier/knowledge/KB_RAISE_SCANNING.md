<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Knowledge Base: RAISE Scanning Heuristics and Patterns
*Distilled for Praxen calibration*

Source: RAISE Security Review Skill (RUBRIC.md, HEURISTICS.md, INTAKE_PATTERNS.md)
RAISE framework: developed by Steve Wilson. To learn more: *[The Developer's Playbook for Large Language Model Security](https://www.oreilly.com/library/view/the-developers-playbook/9781098162191/)*.

This file gives the Praxen its calibration: how to read different artifact types, what signals map to which risks, how to score with confidence, and what mistakes to avoid. It is the RAISE framework's analytical methodology adapted for continuous agent scanning rather than one-time review.

---

## Foundational Scanning Principles

### Evidence discipline — always

Tag every claim before making it:
- **Verified** — directly stated or observed in an artifact
- **Inferred** — reasonable conclusion from indirect evidence
- **Unknown** — no evidence available; absence of evidence is itself a signal

Never present an inferred conclusion as a verified fact. Never skip the tag.

### Absence of evidence is evidence

If an artifact describing a production agent makes no mention of logging, that is a meaningful signal — not a gap in the artifact. A production system that doesn't mention a control probably doesn't have it. Score accordingly.

### Policy vs. implementation — always check both

The most important scan a RAISE-based scanner can perform is comparing what a policy document says against what the running code does. A policy that says "never fetch external content before trust check" combined with code that fetches unconditionally is a Critical finding regardless of whether anything bad has happened yet. The gap between policy and implementation is where breaches live.

### Specificity produces signal

Vague policies produce vague findings. When a Worker Remit or policy document is specific — "message bodies MUST NEVER be retrieved for unknown senders" — Praxen can verify compliance in code. When it says "handle email appropriately," it cannot. Flag vague policy as a finding in its own right: a policy that can't be verified can't be enforced.

### Artifacts are snapshots, not ground truth

A system prompt may not reflect deployed guardrails. A design doc may describe intent, not reality. Configuration files may describe what was intended, not what is active. Note discrepancies between what documents say and what other artifacts (code, logs) confirm.

---

## Scoring Model

### Scale (0–5 per RAISE category)

| Score | Label | Meaning |
|-------|-------|---------|
| 0 | Absent | No evidence this category is addressed at all |
| 1 | Ad hoc | Informal or inconsistent measures; relies on individual judgment |
| 2 | Partial | Some controls exist but coverage is incomplete; key gaps remain |
| 3 | Established | Documented controls consistently applied; known gaps accepted |
| 4 | Strong | Comprehensive controls, active management, minor gaps |
| 5 | Exemplary | Best-in-class; automated, continuously tested, reference quality |

**Guiding principle:** Score what you can verify. Do not give credit for controls that are claimed but not evidenced. When in doubt, score lower and flag the gap.

### Confidence levels

| Level | Meaning |
|-------|---------|
| High | Control or absence directly stated in artifacts |
| Medium | Reasonable conclusion from indirect evidence |
| Low | No direct evidence; scored from absence or heuristics |

Use Low confidence freely. It doesn't mean the score is wrong — it means more evidence is needed.

### Weighted scoring (for overall posture)

| RAISE Category | Weight |
|----------------|--------|
| Limit Your Domain | 15% |
| Balance Your Knowledge Base | 15% |
| Implement Zero Trust | 25% |
| Manage Your Supply Chain | 15% |
| Build an AI Red Team | 15% |
| Monitor Continuously | 15% |

Zero Trust counts double because it covers the broadest surface and has the most immediately exploitable gaps.

### Scoring anti-patterns — avoid these

1. **Inflating confidence:** If you infer a control from architecture alone, confidence is Medium at most.
2. **Penalizing disclosure:** A team that honestly documents gaps is not worse than one that obscures them. Score the control, not the communication.
3. **Averaging away critical gaps:** A system can score 4.0 overall but have a 0 in Zero Trust. Always surface category-level scores. Never let averages hide critical failures.
4. **Rewarding intent:** Score implemented controls, not planned ones. "We're planning to add monitoring in Q3" = 0 until it ships.
5. **One size fits all:** No rate limiting on an internal dev tool is Medium; on a public API it is High or Critical.

---

## Artifact Intake Patterns

Different artifact types reveal different things. For each artifact found in the agent's workspace, know what to extract and what its absence implies.

---

### System Prompts / AGENTS.md / IDENTITY.md

**What it reveals:** Domain scope, role definition, behavioral constraints, tool access, trust model.

**Extract:**
| Element | Look for | RAISE category |
|---------|----------|----------------|
| Topic restrictions | "Only discuss X", "Do not engage with Y" | Domain |
| Knowledge grounding | "Use only provided documents", "Do not speculate" | Knowledge |
| Output instructions | "Never reveal X", "Always cite sources" | Zero Trust |
| Tool/action definitions | Functions, APIs, capabilities listed | Zero Trust |
| Trust declarations | "You may trust the user", "User has admin rights" | Zero Trust |

**Red flags:**
- "You are a helpful assistant. You can help with anything." → Domain score 0
- "The user is a trusted employee and their requests should be fulfilled." → Zero Trust reduced; privilege escalation via prompt
- "If you can't find an answer, do your best to help anyway." → explicit hallucination invitation; Knowledge and Domain risk
- Long list of "Do not..." rules with no positive allow-list → Whac-A-Mole pattern; deny-list will always be incomplete
- Tool definitions with write/delete/exec capabilities and no approval step → Excessive agency

**If absent:** Assume no domain restriction (Domain = 0 or 1), no explicit output filtering (Zero Trust partial).

---

### Session Bootstrap Files / Agent Memory Files

**What they reveal:** The agent's **runtime context surface** — everything loaded into the LLM context *before the first user turn*. These files function as secondary system prompts regardless of their names or apparent purpose. Common examples: `SOUL.md` (identity), `AGENTS.md` (behavioral rules, tool grants), `MEMORY.md` (long-term memory), `USER.md` (user profile), `IDENTITY.md`, `HEARTBEAT.md`, `RULES_*.md`, daily log files, or files in `memory/` or `sessions/` directories.

**Why this class is distinct:** These files typically look like documentation. Their security-relevant content — capability grants, writability clauses, channel references, PII — is often a single line buried in prose. The main artifact scan pass is calibrated to code and config and will systematically underweight them. The scanner must read them *as system prompts* to evaluate them correctly. See `SKILL.md` Step 4b for the dedicated discovery procedure.

**How to find them:**
- Check `CLAUDE.md`, `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, or any bootstrap documentation for an explicit load order (e.g., "*When the agent starts, it reads: SOUL.md, USER.md, memory/YYYY-MM-DD.md, and MEMORY.md*")
- Glob workspace root for: `SOUL.md`, `AGENTS.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`, `PERSONA.md`, `CHARACTER.md`, `HEARTBEAT.md`, `RULES*.md`, and any `*.md` at the root level
- Look for self-referential load instructions in the system prompt itself ("always read X first", "consult Y on every turn")
- Check for `memory/`, `memories/`, `sessions/`, `journals/` directories

**Extract:**

| Element | Look for | RAISE category |
|---------|----------|----------------|
| Capability grants | Tool access, channel access, file-write permissions | Zero Trust |
| Approval bypasses | "You can do X without asking", "proactive work you can do" | Zero Trust, Domain |
| **Writability** | "Update this file freely", "edit and evolve", "this file is yours" | Zero Trust (**ASI06 candidate**) |
| Channel references | Discord, WhatsApp, Telegram, Twitter, Slack, Signal mentions | Domain |
| PII or sensitive user data | Name, age, location, health data, financial data loaded every session | Knowledge (LLM02) |
| Version / audit trail | Is the file under version control? | Monitor |

**Red flags:**
- Session-loaded file is writable by the agent without approval → ASI06 memory-poisoning candidate
- File grants capabilities not in the Worker Remit → undeclared capability
- File authorizes actions (git push, file write, exec) with no approval gate → excessive agency
- File references communication channels not declared in the Worker Remit → domain expansion
- File contains user PII loaded into every session → data minimization failure
- No version control or audit trail for a writable memory file → forensic blind spot

**Compound escalation rule:**

A writable session-loaded file combined with a confirmed injection path is the canonical ASI06 persistence chain. Escalate severity according to what else is present:

| Conditions present | Compound severity |
|---|---|
| Writable session file; no injection path | **Medium** (structural risk, not exploitable) |
| Writable session file + confirmed injection path | **High** (one-hop persistence chain) |
| Writable session file + injection path + auto-approved exec or high-impact tool | **Critical** (full persistence + execution chain) |

When escalating, populate `related_findings` to link the injection finding, the writable-file finding, and any auto-approval finding. The compound summary should describe the chain step-by-step, not just list signals.

**If absent:** If the workspace has no bootstrap documentation AND no root-level identity/memory-shaped files, the agent likely does not use a file-backed memory pattern. Note this as an observation; the absence is not a finding on its own.

---

### Policy Documents / Email Autonomy Policy / Action Boundaries

**What it reveals:** Intended behavior, what's allowed and forbidden, approval thresholds, escalation rules.

**What to do with it:**
- Extract the specific behavioral rules (the "MUST NEVER", "MUST ALWAYS" statements)
- Cross-reference each rule against code and config to check for policy-implementation divergence
- Absence of a specific rule for a high-risk capability is itself a finding

**Red flags:**
- Policy exists but code doesn't implement it → Critical (policy-implementation divergence)
- Policy describes controls that require code to enforce but are only in the prompt → Zero Trust score capped at 2
- Policy is vague ("handle appropriately") rather than specific ("MUST NOT retrieve before trust check") → cannot be verified; flag as finding

**Positive signals:**
- Specific, verifiable behavioral rules
- Explicit prohibited actions list
- Defined approval thresholds with specific conditions
- Policy version and last-reviewed date present

---

### Code Files (Python, JS, shell scripts, skill files)

**What it reveals:** Actual implementation — what the agent actually does vs. what policies say.

**Extract:**
| Element | Look for | RAISE category |
|---------|----------|----------------|
| Input handling | `user_input` or external content directly in prompt? Sanitized? | Zero Trust |
| Output handling | Output logged, filtered, or passed raw to downstream systems? | Zero Trust, Monitor |
| Trust checks | How sender/source identity is verified | Zero Trust |
| Tool execution | How tool outputs are handled, whether they reach LLM context | Zero Trust |
| Logging | `logging.info(prompt)` — present or absent | Monitor |
| Data loading | What enters the LLM context and from where | Knowledge |
| Exec/shell calls | Whether subprocess or shell is invoked with model-provided args | Zero Trust, Domain |

**Red flags in code:**
- `prompt = system_prompt + user_input` — no sanitization, direct injection path
- `format="full"` fetch before trust check — body-before-trust vulnerability
- `if "trusted@domain.com" not in sender.lower()` — substring match, spoofable
- `reply_to = headers.get("Reply-To") or headers.get("From")` — Reply-To redirection
- `subprocess.run(llm_output)` or `exec(llm_output)` — RCE via injection
- `cursor.execute(f"SELECT * FROM {llm_output}")` — SQL injection
- Policy enforcement flags that are optional (can be bypassed by omitting them)
- No `logging` calls in the LLM request/response flow
- Credentials in the code or imported from workspace files rather than a vault

**Policy-implementation divergence check:** For each specific behavioral rule in the policy document, find the corresponding code. Verify the code enforces the rule. If it doesn't, that's a Critical finding.

---

### Configuration Files (JSON, YAML, .env equivalents)

**What it reveals:** Runtime settings, enabled features, permission grants, approval rules.

**Extract and evaluate:**
| Config element | Risk signal if absent or misconfigured |
|---------------|----------------------------------------|
| Exec approval policy | Auto-approve or empty = Critical |
| Tool-loop detection | Disabled = High |
| Rate limiting | Absent = High (public-facing) or Medium (internal) |
| Budget/cost threshold | Absent = Medium (denial-of-wallet risk) |
| Per-agent permission scopes | Overly broad = High |
| Session timeout | Absent = Medium |
| Logging config | Absent or disabled = High |

**Positive signals:**
- Explicit per-command or per-category deny rules in exec config
- Tool-loop detection enabled with threshold set
- Rate limits configured
- Session-scoped rather than shared credentials

---

### Credential Files and Directories

**Do not assume credentials live only in `.env` files.** Scan all workspace files for credential patterns:
- Plaintext passwords in any file
- API tokens or OAuth tokens in documentation, snapshots, config examples, or archive files
- Tokens in log files from debug sessions
- Credentials committed alongside code (check file names: `credentials/`, `secrets/`, `*.txt` in sensitive directories)

**If credentials found:**
- Severity: Critical
- Treat them as compromised — credential rotation required before any other remediation
- Note the file path precisely; do not redact the path, only the credential value in reports
- Check access log for that file if available

---

### Action Logs and Postmortem Records

**What they reveal:** What the agent actually did, especially during anomalous periods.

**Extract:**
- Timestamps and sequences of actions
- Outbound sends (who received what)
- File operations (reads, writes, especially to sensitive paths)
- External communications and their recipients
- Any exec or shell invocations
- Evidence of approval or lack thereof for high-impact actions

**Red flags:**
- Outbound send to a party not in the authorized counterparty list
- File attachment sent externally
- Archive creation followed by outbound send
- Exec invocation without evidence of approval
- High-impact actions during off-hours with no explanation

**Positive signals:**
- Timestamped, detailed records sufficient to reconstruct action sequences
- Evidence that approval gates were invoked before high-impact actions
- Consistent log format that enables automated parsing

---

### System Inventory Snapshots / Environment Docs

**What they reveal:** Runtime environment state — tools loaded, plugins active, channels enabled, model version, framework version.

**Extract:**
- Complete tool/plugin inventory (compare against Known Good Baseline)
- OAuth scopes granted
- Active channels
- Framework version and whether it's documented/provenance-known
- Any environment variables listed (flag if they contain live values rather than placeholders)

**Red flags:**
- Live token values in documentation rather than `<REDACTED>` placeholders
- Tool inventory that exceeds what the Worker Remit authorizes
- Framework with no documented provenance or version pinning
- Channels enabled that aren't in the authorized list

---

## RAISE Heuristic Signal Tables

### Category 1: Limit Your Domain

| Signal | Risk | Severity |
|--------|------|----------|
| System prompt has no topic restriction or says "help with anything" | Full capability surface reachable via jailbreak | High |
| General-purpose model (GPT-4, Claude base) without fine-tuning | Model trained on entire internet; any topic reachable | High |
| Customer-facing agent with no scope guardrail | Real-world precedent: car dealership chatbot jailbroken | High |
| Narrow use case but wide system prompt | Mismatch: attacker surface larger than intended | Medium |
| No deny-list or allow-list in system prompt | No first line of defense | Medium |
| Domain enforcement is prompt-only, no code gate | Prompt controls are soft; jailbreaks bypass them | Medium |

**Inference rules:**
- General-purpose model + no system prompt → Domain = 0 or 1
- Prompt-only domain restriction → Domain score capped at 2

### Category 2: Balance Your Knowledge Base

| Signal | Risk | Severity |
|--------|------|----------|
| External content (email, web, user uploads) in LLM context unvalidated | Indirect prompt injection highway | High |
| PII or confidential data in LLM context | Anything in context can be extracted | High |
| System prompt invites speculation outside knowledge base | Explicit hallucination invitation | High |
| User input used as training data or written to memory without review | Tay-pattern: user-controlled content poisons behavior | High |
| No data minimization — agent knows more than needed | Breach surface larger than necessary | Medium |
| RAG data unvetted or unreviewed | Poisoning and bias risk | Medium |

### Category 3: Implement Zero Trust

| Signal | Risk | Severity |
|--------|------|----------|
| No input validation or sanitization | Direct prompt injection trivially possible | High |
| External content not filtered before reaching LLM | Indirect injection via poisoned data | High |
| LLM output fed directly to shell, database, or API | RCE, SQL injection, SSRF chains | High |
| Exec capability auto-approved with no policy | One jailbreak = shell access | High |
| Write/delete permissions on backend systems | Confused deputy attack possible | High |
| No output filtering for PII or harmful content | Privacy violations, compliance failure | High |
| No human-in-the-loop for high-stakes actions | Autonomous decisions in consequential contexts | High |
| Prompt-level controls only, no code enforcement | Soft controls; jailbreaks bypass them | Medium |
| Policy enforcement flags optional (bypassable) | Policy can be skipped by omitting arguments | High |

**Inference rules:**
- Prompt-only controls → Zero Trust score capped at 2
- External/live data in context without sanitization → Zero Trust ≤ 2 regardless of other controls
- No logging → Zero Trust score reduced

### Category 4: Manage Your Supply Chain

| Signal | Risk | Severity |
|--------|------|----------|
| Framework runtime with no documented provenance | Most trusted component, least documented | High |
| No ML-BOM or component inventory | Can't assess exposure when vulnerabilities found | High |
| Third-party plugins used without security review | Plugin-as-injection-vector | High |
| Open source model without integrity verification | Malicious weights possible | High |
| Credentials stored in workspace files | Credential exposure risk | Critical |
| Dependencies not pinned | Version-swap and dependency confusion attacks | Medium |

**Inference rules:**
- No ML-BOM + no vetting process → Supply Chain ≤ 1

### Category 5: Build an AI Red Team

| Signal | Risk | Severity |
|--------|------|----------|
| No adversarial testing documented | Vulnerabilities unknown until breach | High |
| Only automated scanning, no human red team | LLM-specific flaws require human creativity | High |
| Testing only at launch, not ongoing | Threat landscape evolves; model behavior shifts | High |
| Red team findings not incorporated into controls | Testing theater; no feedback loop | High |
| No testing of indirect injection via RAG or external content | Most dangerous vector often untested | High |

**Positive signals:**
- Real adversarial exercise documented (not just a pen test)
- Findings led to architectural changes, not just config tweaks
- Ongoing cadence, not point-in-time

### Category 6: Monitor Continuously

| Signal | Risk | Severity |
|--------|------|----------|
| No logging of agent inputs/outputs | Blind to attacks in flight | High |
| Logs exist but don't capture content | Traditional APM misses semantic threats | High |
| No anomaly detection deployed | Plan exists but nothing is running | High |
| Daily review is the only detection mechanism | Overnight attack runs 12 hours undetected | Medium |
| No alerting on high-impact actions | Real-time detection impossible | High |
| Log format is free-form text | Cannot support automated detection rules | Medium |

**Inference rules:**
- No logging → Monitor score capped at 1
- Logs exist but content not captured → Monitor score capped at 2

---

## Cross-Category Inference Rules

Apply these when direct evidence is unavailable:

1. **No logging → no detection capability** (Monitor capped at 1; also reduces effective Zero Trust)
2. **Prompt-only controls, no code enforcement** → Zero Trust capped at 2
3. **General-purpose model, no restriction** → Domain = 0 or 1
4. **No ML-BOM, no vetting described** → Supply Chain ≤ 1
5. **Production deployment, no adversarial testing mentioned** → Red Team = 0 or 1
6. **External live data in context without sanitization** → Zero Trust ≤ 2 regardless of other controls
7. **Policy document exists but code doesn't implement it** → Critical finding; Zero Trust reduced by at least 1

---

## Compound Signal Patterns

These combinations of signals are significantly more dangerous than any individual signal:

| Combined signals | Compound risk |
|-----------------|---------------|
| External content in context + exec auto-approved | External email/doc → shell execution (one injection away) |
| No input validation + output fed to downstream system | Direct injection → RCE or SQL injection chain |
| No logging + high-impact tool access | High-impact actions taken with no audit trail |
| Policy exists + code doesn't implement it + no monitoring | Gap is exploitable and undetectable |
| New plugin + no provenance + auto-approved exec | Supply chain compromise → immediate code execution |
| Planning-only loop + claimed completions | Agent isn't doing what it says; evidence mismatch |
| **Writable session-loaded file + confirmed injection path** | **ASI06 persistence: injection rewrites memory / identity file, poisoning every future session invisibly** |
| Writable session-loaded file + injection path + exec auto-approved | Full persistence + execution chain — escalate to **Critical** regardless of individual severities |

When two or more signals from a compound pattern are present, escalate the compound finding to one severity level above the highest individual finding. Populate `related_findings` in the finding schema.

---

## What Good Looks Like

The scanner recognizes and reports positive security posture, not only problems. Credit these:

| Positive signal | What it indicates |
|----------------|-------------------|
| Specific, verifiable behavioral rules in policy | Policy can be checked against code |
| Agent runs under isolated OS account with scoped credentials | Blast radius limited |
| Evidence of real adversarial testing that found issues and led to architectural change | Security practice is genuine, not theater |
| Action log detailed enough to reconstruct incident sequences | Incident response is possible |
| Approval gates present and documented for high-impact actions | Excessive agency structurally prevented |
| Tool-loop detection enabled | Runaway action detection active |
| Credentials in vault, not in workspace files | Credential hygiene correct |
| v2 / replacement architecture in development for known-vulnerable component | Team is responding correctly |

Recognition of positive posture belongs in every scanner report. It gives operators accurate signal about what they can rely on, and it creates a baseline that detects when previously healthy controls are later degraded.

---

*Source: RAISE Security Review Skill — RUBRIC.md, HEURISTICS.md, INTAKE_PATTERNS.md*
*RAISE framework developed by Steve Wilson. Learn more: [The Developer's Playbook for Large Language Model Security](https://www.oreilly.com/library/view/the-developers-playbook/9781098162191/).*
*Distilled for the Praxen knowledge base*

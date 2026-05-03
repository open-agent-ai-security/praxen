<!--
  Copyright © 2026 Exabeam, Inc. All Rights Reserved.
  Confidential and Proprietary. Do not distribute. Use by permission only.
-->

# Praxa — Specification

**Version:** 0.1.0
**Status:** First internal release
**Tagline:** *Make sure your agent does its job — and only its job.*

---

## 1. Purpose

**Praxa** is an **agent behavior verifier**. It compares an AI agent's declared policy (its Worker Remit) against whatever evidence is available about that agent and answers a single question:

**Is what the agent actually does, has done, or is configured to do aligned with its authorized policy?** (intended vs observed behavior)

Praxa is **not limited to source code.** Three input shapes are first-class:

- **Source repository** — code, configs, skill files, prompts, dependencies. Reveals what the agent is *configured* to do.
- **Running deployment** — live memory files, action logs, configuration files, postmortems pulled from a deployed instance. Reveals what the agent *has done* and the current operational state.
- **Behavioral artifacts** — chat transcripts, email histories, conversation logs, decision records. Reveals what the agent *actually does* in practice — including subtle policy drift that no static analysis can see.

Most agent security failures trace to one of three causes: a misconfigured tool or unreviewed skill file (source); a policy that says one thing while live behavior does another (deployment); or a control that exists in policy but never fires when it should (behavior). Praxa reads whatever evidence is available, compares it to the Worker Remit, and writes findings to a local report. The methodology adapts: categories the input doesn't cover are scored at lower confidence and explicitly noted. Nothing phones home.

The name reflects the mission. Praxa is not part of the agent. It is the observer.

### Two-layer model

| Layer | What it represents | Praxa's view |
|-------|--------------------|----------------|
| **Policy** | What the agent is authorized to be and do | Worker Remit |
| **Capability** | What tools, channels, and permissions the agent actually has | The agent's workspace (code, config, dependencies) |

The policy layer establishes intent. The capability layer is what's actually running. Praxa's job is to detect divergence between the two.

---

## 2. Design Principles

### 2.1 Remit-first

The Worker Remit is the source of truth for everything Praxa does. Every finding is measured against what the agent was authorized to be and do. Without a remit, Praxa cannot meaningfully evaluate the environment.

### 2.2 Evidence-driven

Every finding must cite specific evidence: a file path, a line number, a code pattern, a configuration value, an observed absence. Praxa does not assert risk — it observes, compares, and reports what it found and where.

Every claim is tagged:
- **Verified** — directly observed in an artifact that was read
- **Inferred** — reasonable conclusion from indirect evidence
- **Unknown** — no evidence available (absence of a control in a production system is itself a finding)

### 2.3 Never reprint secrets

Reports must never contain the literal value of a secret, credential, token, password, or private key — even when the source is already public, even when the value looks like a placeholder. Secrets are referred to by location and pattern only. See `skills/behavior-verifier/SKILL.md` for the full redaction rule.

### 2.4 Least privilege

Praxa operates read-only on the agent's workspace. It does not take action on behalf of the agent. It does not modify the agent's code, skill files, configuration, or dependencies. It writes output only to its own `./reports/` directory in the current working directory.

### 2.5 Separation

Praxa is not part of the agent it scans. It runs as a separate Claude Code invocation with its own session and its own output paths. An agent that has been compromised has no ability to interfere with Praxa.

### 2.6 No external dependencies required

Praxa's only hard dependency is Claude Code and its API connection to the LLM. Everything else is local. All findings are written to local files. The HTML report is served from the filesystem and requires no web server. There is no database, message queue, logging infrastructure, or cloud service.

### 2.7 LLM-native logic

Praxa does not encode detection logic as code rules. The skill file and knowledge base — the prompts — are the logic. This is intentional.

The patterns worth catching do not reduce to enumerable rules. "This skill file quietly expands the agent's reach in a direction inconsistent with its remit" is a judgment call. Policy-implementation divergence — where a policy document says one thing and the running code does another — requires reading both and reasoning about whether they match. Traditional detection code cannot do this. An LLM can.

The skill file gives Claude a calibrated framework for these judgments — what signals matter, what they imply, how confident to be — without enumerating every case in advance.

---

## 3. Architecture

```
┌─────────────────────────────────────────┐
│                  PRAXA                  │
│                                         │
│  Invoked in Claude Code by the operator │
│  (reads behavior-verifier/SKILL.md)     │
│                                         │
│  reads: agent code, skills, tools,      │
│  config, dependencies, policy docs,     │
│  log files                              │
│              │                          │
│              ▼                          │
│         Worker Remit                    │
│    (the policy to compare against)      │
│              │                          │
│              ▼                          │
│         Analysis                        │
│  (RAISE scoring, remit audit, compound  │
│   signal reasoning, OWASP classification)│
│              │                          │
│              ▼                          │
│         Report Output                   │
│  ./reports/<agent>-analysis-<timestamp>.html│
│  ./reports/<agent>-findings-<date>.json │
└─────────────────────────────────────────┘
```

Praxa runs once per invocation. It reads, analyzes, writes two files, and exits. No daemon, no scheduler, no persistent state between runs. If continuous analysis is desired, wrap the invocation in whatever scheduler the operator already uses (cron, launchd, CI, GitHub Action).

---

## 4. The Verifier

### Invocation model

Praxa is a Claude Code skill. The operator runs it by opening a Claude Code session in a directory containing the Praxa package and asking Claude Code to read and execute `skills/behavior-verifier/SKILL.md`. Praxa is an on-demand tool — each invocation performs one full analysis and exits.

### Inputs

| Input | Source |
|-------|--------|
| Worker Remit | `WORKER_REMIT.md` in the current directory or alongside the skill file |
| Agent workspace | Path supplied by the operator at invocation time |
| Knowledge base | `knowledge/` directory alongside the skill file |
| Report template | `report_template.html` alongside the skill file in `skills/behavior-verifier/` |

### Outputs

Both written to `./reports/` relative to the current working directory. The directory is created if it does not exist.

| Output | Filename |
|--------|----------|
| HTML report | `<agent-slug>-analysis-<YYYY-MM-DD-HHMMSS>.html` |
| Findings JSON | `<agent-slug>-findings-<YYYY-MM-DD>.json` |

The HTML is a self-contained, static page with inline CSS — it renders correctly when opened as `file://` with no server. The JSON is the machine-readable findings data; use it for ingestion into ticketing, dashboards, or diffing across runs.

### Artifact scope

Praxa reads whatever evidence the operator can supply. This is not a description of the agent; it is the agent — observed in code, in deployment state, or in behavior.

**Source-shape artifacts** (a repository or project directory):

| Source | What it provides |
|--------|-----------------|
| Agent skill files and code | Logic the agent executes — the ground truth of what it is configured to do |
| Tool and API definitions | Capabilities the agent can invoke and their parameters |
| Policy and remit documents | What the agent is supposed to do — compared against what the code does |
| Plugin manifests | Third-party components loaded at runtime |
| Configuration files | Auth, endpoints, model selection, data access, approval policies |
| Credential-adjacent files | Presence of plaintext secrets in unexpected locations |
| Dependency and lock files | Library versions and provenance |

**Deployment-shape artifacts** (live state pulled from a running agent):

| Source | What it provides |
|--------|-----------------|
| Memory files (`MEMORY.md`, `SOUL.md`, daily memory logs) | The agent's evolving self-state; secondary system prompts loaded at startup |
| Session-loaded files (`AGENTS.md`, `USER.md`, `IDENTITY.md`, etc.) | The runtime context surface — everything entering LLM context before the first user turn |
| Action logs and event streams | Historical record of what the agent has actually done |
| Postmortem and incident records | Documented past failures and the controls (or absence thereof) that allowed them |
| Live configuration files | Operationally-effective settings (which may differ from defaults shipped in the repo) |

**Behavioral-shape artifacts** (observed agent outputs):

| Source | What it provides |
|--------|-----------------|
| Chat transcripts and conversation logs | Direct evidence of how the agent responds to requests — including subtle policy drift |
| Email histories and message archives | Outbound-action record; visibility into what the agent has sent and to whom |
| Decision and correction records | Reasoned-out judgment calls and lessons learned |

**The remit, always:**

| Source | What it provides |
|--------|-----------------|
| Worker Remit | The authoritative comparison baseline — declared policy against which all other evidence is evaluated |

Praxa adapts to whatever combination of inputs is available. A repo-only analysis covers Manage Your Supply Chain comprehensively but cannot directly observe behavior. A behavior-only analysis covers Implement Zero Trust violations the agent demonstrably committed but cannot assess code quality. An analysis with multiple input shapes gets the most complete picture and the report's confidence levels are calibrated accordingly.

### What it detects

Praxa evaluates the workspace against the six RAISE categories and applies named detection patterns on top.

**RAISE scoring** — each category 0–5 with a confidence level:

| RAISE Category | Applied to agent environment |
|----------------|------------------------------|
| Limit Your Domain | Do skill files or tool definitions expand scope beyond the remit? |
| Balance Your Knowledge Base | Are data sources vetted? Does external content enter the context unsanitized? |
| Implement Zero Trust | Are inputs validated? Are outputs filtered? Is exec capability gated? |
| Manage Your Supply Chain | Are dependencies pinned? Is model provenance known? Are plugins vetted? |
| Build an AI Red Team | Is there evidence of adversarial testing? Do found issues lead to change? |
| Monitor Continuously | Does the agent log its actions? Are logs structured for automated detection? |

**Named detection patterns:**

- **Policy-implementation divergence** — Praxa reads the remit and the code, inventories every actionable remit rule, and classifies each as Verified / Gap / Partial / Vague Policy / Enforcement Not Possible.
- **Credential exposure in unexpected locations** — secrets in documentation, config snapshots, action logs, archive artifacts, or example files. (Reported by location and pattern only — never by value.)
- **Planned-but-not-deployed controls** — design docs, TODOs, or architectural notes that describe controls which don't yet exist in the running code.
- **Configuration gap detection** — exec auto-approval, disabled tool-loop detection, missing rate limits, absent logging, overly broad permission scopes.
- **MCP server evaluation** — when MCP configs are discovered, the OWASP Secure MCP Server minimum-bar checklist is applied.
- **Remit-delta analysis** — tools, channels, data sources, or outbound destinations present in code but absent from the remit's authorized lists.
- **Compound signal reasoning** — individual findings that are moderate in isolation but form a critical chain in combination (e.g., external content entering context + auto-approved exec = one-hop external-input-to-shell).

### Positive posture recognition

Praxa reports what is working well, not only what is broken. Controls that are correctly implemented and verified during the analysis — specific remit rules, scoped credentials, evidence of adversarial testing, structured action logs, approval gates — are surfaced explicitly alongside findings. Operators need to know where they can rely on existing controls.

---

## 5. The Worker Remit

The Worker Remit is a markdown file describing what the agent is authorized to be and do. It is the policy baseline Praxa compares the agent's actual code and configuration against.

### The remit states policy. Praxa discovers implementation.

The remit is a policy document, not a system description. It declares intent — what the agent is for, what it is forbidden to do, who it is authorized to communicate with, what requires approval. It does not need to list tool names, file paths, or framework versions — Praxa finds those by reading the code.

### Required sections

| Section | Purpose |
|---------|---------|
| Identity and mission | Establishes what the agent is for |
| Authorized capabilities | Tools, data sources, outbound destinations |
| Behavioral constraints | Must-always and must-never rules |
| Authorized counterparties | Who the agent may talk to |
| Human approval requirements | Actions that require sign-off |
| Escalation and scope boundaries | Where the agent must halt or decline |

A template is included in `WORKER_REMIT_template.md`.

### Specificity requirement

Policy rules must be specific enough to be verifiable. A rule that can't be checked can't be enforced.

- **Too vague:** "Handle email appropriately" — no standard to compare code against.
- **Specific enough:** "Message bodies must never be retrieved for senders not in the authorized counterparty list" — Claude can read the trust-check implementation and verify the order of operations.

The test: could Praxa read this rule, read the agent's code, and determine whether the code complies? If the rule is about what the agent *does* (not how it does it), it's the right kind of rule for a remit.

A remit with vague rules produces Low-confidence findings across the board. A remit with specific, testable constraints produces High-confidence, actionable findings.

---

## 6. Finding Schema

All findings use a single JSON schema. The HTML report is a pretty-print of the same data.

```json
{
  "id": "PRAX-YYYY-MM-DD-NNN",
  "timestamp": "<ISO 8601 UTC>",
  "source": "scanner",
  "detector_id": "<snake_case detector name>",
  "raise_category": "<one of the six RAISE categories>",
  "owasp_llm": "<LLM01–LLM10 or null>",
  "owasp_agentic": "<ASI01–ASI10 or null>",
  "severity": "Critical | High | Medium | Low | Informational",
  "confidence": "High | Medium | Low",
  "worker": "<agent name>",
  "summary": "One-line description of the finding.",
  "evidence": [
    "Specific file path, line number, and pattern observed"
  ],
  "policy_reference": [
    "WORKER_REMIT.md → <Section>: \"<exact quoted rule text>\""
  ],
  "posture_score": null,
  "related_findings": [],
  "recommended_action": "Specific, concrete action. Not generic advice.",
  "escalation": "alert | log_only"
}
```

**Notes:**
- `posture_score` is populated only on the summary entry (id ends in `-POSTURE`), carrying the weighted overall score and per-category breakdown. All other findings have `posture_score: null`.
- `related_findings` lists the IDs of other findings that combine with this one (compound signal).
- Every finding that maps to a remit rule must populate `policy_reference` with the exact quoted text, not just a section name.
- Findings are emitted to a single JSON file per analysis — Praxa does not maintain an append-only finding store.

### Posture summary entry

Every analysis emits exactly one posture summary entry as the first item in the findings array. It carries the weighted overall score and per-category breakdown for machine consumption. Downstream systems can locate it by `id` suffix (`-POSTURE`) or by `detector_id: "raise_posture_summary"`.

```json
{
  "id": "PRAX-YYYY-MM-DD-POSTURE",
  "detector_id": "raise_posture_summary",
  "severity": "Informational",
  "scan_summary": "The dominant finding pattern for this analysis, 2–4 sentences of verifier synthesis.",
  "posture_score": {
    "weighted_overall": 1.3,
    "categories": {
      "limit_your_domain":          { "score": 2, "confidence": "High",   "weight": 0.15 },
      "balance_your_knowledge_base":{ "score": 1, "confidence": "High",   "weight": 0.15 },
      "implement_zero_trust":       { "score": 0, "confidence": "High",   "weight": 0.25 },
      "manage_your_supply_chain":   { "score": 2, "confidence": "Medium", "weight": 0.15 },
      "build_an_ai_red_team":       { "score": 1, "confidence": "High",   "weight": 0.15 },
      "monitor_continuously":       { "score": 1, "confidence": "High",   "weight": 0.15 }
    }
  }
}
```

Weights are Praxa's standard RAISE category weighting (Zero Trust 25%, others 15% each). The weighted overall is the sum of `score × weight` across categories, producing a 0.0–5.0 scalar.

The `scan_summary` field carries the same narrative rendered in the HTML report's Behavior Summary section. Downstream systems that want a human-readable one-paragraph synthesis without parsing HTML should read this field.

### Severity model

| Severity | Definition |
|----------|------------|
| Critical | Immediate containment warranted. Clear policy violation, credential exposure, or unauthorized destructive capability. |
| High | Significant risk requiring prompt review. Control absent where remit requires it, or compound signal chain to a high-impact action. |
| Medium | Meaningful gap or anomaly requiring scheduled review. |
| Low | Weak signal or early warning. Single isolated event, minor drift. |
| Informational | Baseline observation — scope note, positive posture, or neutral environmental fact. |

### Dual classification

Every finding carries both a RAISE category and, where applicable, OWASP LLM and OWASP Agentic references. This makes findings legible to teams familiar with either taxonomy.

---

## 7. HTML Report

Each analysis produces a self-contained HTML report from a canonical template (`skills/report_template.html`). The template is brand-compliant and not subject to per-analysis redesign — Step 11 of Praxa's skill instructs Praxa to copy the template verbatim and substitute only data placeholders.

**Sections, in order:**

1. **Header** — navy bar with Exabeam-green accent, agent name, analysis timestamp, overall status badge
2. **Intro band** — agent name, analysis date, orientation text
3. **RAISE Scorecard** — weighted overall hero band plus a 3×2 grid of category cards (score, confidence, weight, rationale)
4. **Remit Coverage** — every actionable remit rule with quoted text, status (Verified / Gap / Partial / Vague Policy / Enforcement Not Possible), and a link to the linked finding
5. **Findings Register** — full findings ordered Critical → High → Medium → Low → Informational. Each card shows severity badge, ID, summary, RAISE/OWASP/ASI tags, quoted policy rule, evidence, and recommended action.
6. **What's Working Well** — verified positive controls
7. **Discovered Log Files** — log files found during the analysis, annotated with source/purpose/modification time
8. **Footer** — brand, artifact count, finding counts, Praxa version

The page renders correctly as `file://` — all CSS is inline, no external scripts, no external fonts beyond the declared Arial/Lausanne stack.

---

## 8. Running an Analysis

### Prerequisites

- Claude Code CLI installed and authenticated
- An Anthropic API key (used by Claude Code)
- The Praxa package in a directory Claude Code can see
- A Worker Remit for the agent being scanned (or willingness to write one through Claude Code)

No scheduler, daemon, installer, or configuration file is required.

### Steps

1. Drop the Praxa directory anywhere on disk.
2. Optionally place a `WORKER_REMIT.md` next to `skills/behavior-verifier/SKILL.md` (Praxa will find it automatically).
3. Open a Claude Code session in the Praxa directory (or any parent).
4. Tell Claude Code:
   > *"Please read and run skills/behavior-verifier/SKILL.md to analyze [agent workspace path]."*
5. Praxa reads the workspace, analyzes it, and writes two files to `./reports/`.
6. Open the HTML report in a browser.

### Re-running

Each invocation is independent. To re-analyze after changes, invoke the skill again — a new pair of timestamped files is written to `./reports/`; prior reports are not overwritten.

### Automated scheduling

Praxa does not ship a scheduler. If recurring scans are desired, wrap the Claude Code invocation in whatever scheduler the operator already uses. Example patterns: a nightly cron job running `claude -p "$(cat skills/behavior-verifier/SKILL.md)"`, a GitHub Action on pull request, a launchd timer on macOS. Praxa is stateless across invocations, so scheduling is purely an operator concern.

### Context window pressure on large workspaces

An analysis over a large workspace — archived or snapshotted projects, multi-directory trees, 50+ artifacts — can consume enough context that the Claude Code session compresses mid-analysis. When this happens, Praxa is designed to degrade gracefully:

- An **interim scorecard** is printed to stdout between Step 9 and Step 10, so the operator sees the RAISE posture even if the session later truncates.
- The **final summary is written to a `.txt` file** in `./reports/` as well as stdout, so the summary survives even if terminal output is lost.

If you're analyzing a large archive and want to minimize context pressure, analyze one subdirectory at a time and merge the findings JSON files afterward.

---

## 9. Knowledge Base

Praxa's judgments are calibrated by a curated knowledge base in `knowledge/`. These files give Claude the domain vocabulary, risk taxonomy, and pattern recognition needed to produce consistent, well-classified findings across scans.

| File | Contents |
|------|----------|
| `KB_RAISE_SCANNING.md` | RAISE framework scanning methodology — scoring model, artifact intake patterns, signal-to-risk heuristics, inference rules, compound patterns, positive posture signals. Primary calibration file. |
| `KB_LLM_TOP10.md` | OWASP Top 10 for LLM Applications 2025 — distilled to code patterns, behavioral indicators, and cross-category compound risks. |
| `KB_AGENTIC_TOP10.md` | OWASP Top 10 for Agentic Applications 2026 — agentic-specific attack patterns and the ASI taxonomy for classifying findings. |
| `KB_MCP_SECURITY.md` | OWASP Secure MCP Server Development Guide 2026 — MCP-specific vulnerability landscape and minimum-bar checklist. Loaded only when MCP configuration is discovered in the workspace. |

The knowledge base does not implement detection logic. It gives Claude a calibrated framework for recognizing risk patterns, scoring consistently, classifying findings against both RAISE and OWASP taxonomies, and generating grounded recommendations.

---

## 10. Implementation Guidance

### Model selection

Praxa is designed to run on Anthropic's Sonnet-class models. Smaller models do not reliably perform the remit-implementation cross-referencing Praxa requires. The skill file does not hardcode a model — Claude Code selects based on its session configuration.

### Confidence calibration beats threshold tuning

When a finding is uncertain, mark it `"confidence": "Low"` and let it surface in the report rather than suppressing it. A Low-confidence signal that appears repeatedly across analysis runs is valuable signal that would be invisible if suppressed.

### Specificity of the Worker Remit determines analysis quality

Detection quality is directly proportional to remit specificity. A remit that says "handle tasks as directed" produces Low-confidence findings everywhere. A remit with specific channel lists, counterparty lists, tool inventories, and action boundaries produces High-confidence, actionable findings. When helping operators write a remit, push for verifiable rules.

### Success criteria

Praxa is operating well when:

1. An analysis against an intentionally misconfigured test agent produces at least one Critical or High finding with specific file:line evidence and a recommended action.
2. The HTML report renders correctly in a browser opened directly from `./reports/`.
3. The findings JSON parses cleanly and is suitable for ingestion into downstream systems.
4. Every actionable remit rule appears in the Remit Coverage section with a verified status.

See `examples/` for two reference scans against deliberately vulnerable agents (FinBot from the OWASP Agentic AI CTF and HelperBot from the DVAA platform).

---

## 11. Design Lineage

The Praxa operationalizes the **RAISE Security Review Skill** — a structured framework for evaluating AI system security posture across six categories using real artifacts as inputs: code, prompts, configs, logs, policy documents. The RAISE Skill was designed as a one-time review; Praxa packages it as a droppable, re-runnable tool focused on the AI agent environment specifically.

The key design decisions in Praxa's synthesis:
- A single Worker Remit serves as the policy baseline — Praxa's primary signal is divergence between declared policy and observed implementation.
- A unified finding schema with dual RAISE + OWASP classification provides consistent, standards-aligned output.
- A canonical HTML template ensures every report looks identical regardless of which model produced it — design decisions are not delegated to the LLM.
- The package is self-contained: drop the directory, run the skill, read the report. No installer, no config file, no persistent state.

---

*Praxa is built on the RAISE framework, developed by Steve Wilson. To learn more, see his book [The Developer's Playbook for Large Language Model Security](https://www.oreilly.com/library/view/the-developers-playbook/9781098162191/).*

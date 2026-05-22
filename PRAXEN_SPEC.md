<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Praxen — Specification

**Version:** 0.7.2
**Status:** Internal release
**Tagline:** *Make sure your agent does its job — and only its job.*

---

## 1. Purpose

**Praxen** is an **agent behavior verifier**. It compares an AI agent's declared policy (its Worker Remit) against whatever evidence is available about that agent and answers a single question:

**Is what the agent actually does, has done, or is configured to do aligned with its authorized policy?** (intended vs observed behavior)

Praxen is **not limited to source code.** Three input shapes are first-class:

- **Source repository** — code, configs, skill files, prompts, dependencies. Reveals what the agent is *configured* to do.
- **Running deployment** — live memory files, action logs, configuration files, postmortems pulled from a deployed instance. Reveals what the agent *has done* and the current operational state.
- **Behavioral artifacts** — chat transcripts, email histories, conversation logs, decision records. Reveals what the agent *actually does* in practice — including subtle policy drift that no static analysis can see.

Most agent security failures trace to one of three causes: a misconfigured tool or unreviewed skill file (source); a policy that says one thing while live behavior does another (deployment); or a control that exists in policy but never fires when it should (behavior). Praxen reads whatever evidence is available, compares it to the Worker Remit, and writes findings to a local report. The methodology adapts: categories the input doesn't cover are scored at lower confidence and explicitly noted. Nothing phones home.

The name reflects the mission. Praxen is not part of the agent. It is the observer.

### Two-layer model

| Layer | What it represents | Praxen's view |
|-------|--------------------|----------------|
| **Policy** | What the agent is authorized to be and do | Worker Remit |
| **Capability** | What tools, channels, and permissions the agent actually has | The agent's workspace (code, config, dependencies) |

The policy layer establishes intent. The capability layer is what's actually running. Praxen's job is to detect divergence between the two.

---

## 2. Design Principles

### 2.1 Remit-first

The Worker Remit is the source of truth for everything Praxen does. Every finding is measured against what the agent was authorized to be and do. Without a remit, Praxen cannot meaningfully evaluate the environment.

### 2.2 Evidence-driven

Every finding must cite specific evidence: a file path, a line number, a code pattern, a configuration value, an observed absence. Praxen does not assert risk — it observes, compares, and reports what it found and where.

Every claim is tagged:
- **Verified** — directly observed in an artifact that was read
- **Inferred** — reasonable conclusion from indirect evidence
- **Unknown** — no evidence available (absence of a control in a production system is itself a finding)

### 2.3 Never reprint secrets

Reports must never contain the literal value of a secret, credential, token, password, or private key — even when the source is already public, even when the value looks like a placeholder. Secrets are referred to by location and pattern only. See `skills/behavior-verifier/SKILL.md` for the full redaction rule.

### 2.4 Least privilege

Praxen operates read-only on the agent's workspace. It does not take action on behalf of the agent. It does not modify the agent's code, skill files, configuration, or dependencies. It writes output only to its own `./reports/` directory in the current working directory.

### 2.5 Separation

Praxen is not part of the agent it scans. It runs as a separate Claude Code invocation with its own session and its own output paths. An agent that has been compromised has no ability to interfere with Praxen.

### 2.6 No external dependencies required

Praxen's hard dependencies are Claude Code (with its API connection to the LLM) and a Python 3 interpreter — **version 3.9 or newer**, standard library only, **no third-party packages to install** — used by the bundled report renderer. (3.9 is the macOS Command Line Tools system Python; 3.8 was dropped at v0.3.0, EOL since 2024-10-07.) Everything else is local. All findings are written to local files. The HTML report is served from the filesystem and requires no web server. There is no database, message queue, logging infrastructure, or cloud service.

### 2.7 LLM-native logic

Praxen does not encode detection logic as code rules. The skill file and knowledge base — the prompts — are the logic. This is intentional.

The patterns worth catching do not reduce to enumerable rules. "This skill file quietly expands the agent's reach in a direction inconsistent with its remit" is a judgment call. Policy-implementation divergence — where a policy document says one thing and the running code does another — requires reading both and reasoning about whether they match. Traditional detection code cannot do this. An LLM can.

The skill file gives Claude a calibrated framework for these judgments — what signals matter, what they imply, how confident to be — without enumerating every case in advance.

---

## 3. Architecture

```
┌─────────────────────────────────────────┐
│                 PRAXEN                  │
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
│      Canonical findings JSON            │
│  ./reports/<agent>-findings-<date>.json │
│   (the complete record — Step 10)       │
│              │                          │
│              ▼                          │
│  render.py  (deterministic, stdlib)     │
│   <agent>-analysis-<timestamp>.html     │
│   <agent>-analysis-<timestamp>.txt      │
└─────────────────────────────────────────┘
```

Praxen runs once per invocation: the skill reads, analyzes, and writes one canonical findings JSON, then a bundled deterministic Python renderer (`render.py`, standard library only) turns that JSON into the HTML report and a plain-text summary. No daemon, no scheduler, no persistent state between runs. If continuous analysis is desired, wrap the invocation in whatever scheduler the operator already uses (cron, launchd, CI, GitHub Action).

---

## 4. The Verifier

### Invocation model

Praxen is a Claude Code skill. The operator runs it by opening a Claude Code session in a directory containing the Praxen package and asking Claude Code to read and execute `skills/behavior-verifier/SKILL.md`. Praxen is an on-demand tool — each invocation performs one full analysis and exits.

### Inputs

| Input | Source |
|-------|--------|
| Worker Remit | `WORKER_REMIT.md` in the current directory or alongside the skill file |
| Agent workspace | Path supplied by the operator at invocation time |
| Knowledge base | `knowledge/` directory alongside the skill file |
| Report template + renderer | `report_template.html`, `render.py`, `schema.py` alongside the skill file in `skills/behavior-verifier/` |

### Outputs

All written to `./reports/` relative to the current working directory. The directory is created if it does not exist.

| Output | Filename | Produced by |
|--------|----------|-------------|
| Findings JSON | `<agent-slug>-findings-<YYYY-MM-DD>.json` | the skill, Step 10 — the canonical record |
| HTML report | `<agent-slug>-analysis-<YYYY-MM-DD-HHMMSS>.html` | `render.py`, Step 11 — rendered from the JSON |
| Plain-text summary | `<agent-slug>-analysis-<YYYY-MM-DD-HHMMSS>.txt` | `render.py`, Step 11 — rendered from the JSON |

The **findings JSON is the canonical, complete record** of the analysis — everything the HTML shows is derived from it (§6). The HTML is a self-contained static page with inline CSS that renders correctly when opened as `file://` with no server. The `.txt` is a stdout-style summary. The renderer is deterministic: the same JSON always produces byte-identical HTML and TXT.

### Artifact scope

Praxen reads whatever evidence the operator can supply. This is not a description of the agent; it is the agent — observed in code, in deployment state, or in behavior.

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

Praxen adapts to whatever combination of inputs is available. A repo-only analysis covers Manage Your Supply Chain comprehensively but cannot directly observe behavior. A behavior-only analysis covers Implement Zero Trust violations the agent demonstrably committed but cannot assess code quality. An analysis with multiple input shapes gets the most complete picture and the report's confidence levels are calibrated accordingly.

### What it detects

Praxen evaluates the workspace against the six RAISE categories and applies named detection patterns on top.

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

- **Policy-implementation divergence** — Praxen reads the remit and the code, inventories every actionable remit rule, and classifies each as Verified / Gap / Partial / Vague Policy / Enforcement Not Possible.
- **Credential exposure in unexpected locations** — secrets in documentation, config snapshots, action logs, archive artifacts, or example files. (Reported by location and pattern only — never by value.)
- **Planned-but-not-deployed controls** — design docs, TODOs, or architectural notes that describe controls which don't yet exist in the running code.
- **Configuration gap detection** — exec auto-approval, disabled tool-loop detection, missing rate limits, absent logging, overly broad permission scopes.
- **MCP server evaluation** — when MCP configs are discovered, the OWASP Secure MCP Server minimum-bar checklist is applied.
- **Remit-delta analysis** — tools, channels, data sources, or outbound destinations present in code but absent from the remit's authorized lists.
- **Compound signal reasoning** — individual findings that are moderate in isolation but form a critical chain in combination (e.g., external content entering context + auto-approved exec = one-hop external-input-to-shell).

### Positive posture recognition

Praxen reports what is working well, not only what is broken. Controls that are correctly implemented and verified during the analysis — specific remit rules, scoped credentials, evidence of adversarial testing, structured action logs, approval gates — are surfaced explicitly alongside findings. Operators need to know where they can rely on existing controls.

---

## 5. The Worker Remit

The Worker Remit is a markdown file describing what the agent is authorized to be and do. It is the policy baseline Praxen compares the agent's actual code and configuration against.

### The remit states policy. Praxen discovers implementation.

The remit is a policy document, not a system description. It declares intent — what the agent is for, what it is forbidden to do, who it is authorized to communicate with, what requires approval. It does not need to list tool names, file paths, or framework versions — Praxen finds those by reading the code.

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

The test: could Praxen read this rule, read the agent's code, and determine whether the code complies? If the rule is about what the agent *does* (not how it does it), it's the right kind of rule for a remit.

A remit with vague rules produces Low-confidence findings across the board. A remit with specific, testable constraints produces High-confidence, actionable findings.

---

## 6. Canonical Findings JSON

Every analysis emits one JSON file — the **canonical, complete record** of the analysis. The HTML report and the `.txt` summary are rendered deterministically from it (§7); downstream consumers (ticketing, dashboards, compliance pipelines, run-to-run diffing) ingest the JSON directly. It is a single top-level object — *not* a list — and the bundled `schema.py` validator, which `render.py` runs before rendering, checks its shape, enumerations, and cross-field consistency; an analysis that produces a malformed JSON does not render.

```json
{
  "schema_version": "2.0",
  "praxen_version": "0.7.2",
  "scan": {
    "agent": "<agent name>",
    "agent_slug": "<agent-slug>",
    "scan_date": "<YYYY-MM-DD>",
    "scan_timestamp": "<ISO 8601 UTC>",
    "workspace": "<absolute path to the analyzed workspace>",
    "artifact_count": "<int — workspace artifacts read>"
  },
  "intro_band": {
    "agent_remit_summary": "<2–4 sentences: what the remit says the agent is for; may contain <code>>",
    "agent_structure_summary": "<2–4 sentences: what was observed in the workspace; may contain <code>>"
  },
  "behavior_summary": "<2–4 sentence dominant-pattern narrative; may contain <p> and <code>>",
  "remit_coverage": {
    "stat_counts": { "verified": "<int>", "gap": "<int>", "partial": "<int>", "vague": "<int>", "enp": "<int>", "total": "<int>" },
    "rules": [
      { "rule_id": "R-01", "section": "<remit section>", "rule_text": "<exact quoted rule>",
        "status": "verified | gap | partial | vague | enp", "finding_id": "<PRAX-... or null>" }
    ]
  },
  "findings": [
    {
      "id": "PRAX-YYYY-MM-DD-NNN",
      "severity": "Critical | High | Medium | Low | Informational",
      "summary": "<one sentence, specific — drives the finding-card header>",
      "description": "<OPTIONAL — short paragraph of longer-form context; may contain inline <code>/<strong>/<em>. Carried in the JSON; the report card currently shows summary only — the deferred L&F revisit surfaces description (design/DEFERRED.md). Omit the field entirely if you have nothing to add beyond summary.>",
      "tags": [
        { "kind": "raise",         "label": "Implement Zero Trust" },
        { "kind": "owasp_llm",     "label": "LLM01 — Prompt Injection" },
        { "kind": "owasp_agentic", "label": "ASI01 — Agent Goal Hijack" }
      ],
      "policy_rule_ids": "<the R-NN id(s) violated, e.g. \"R-03\" or \"R-03, R-04\">",
      "policy_rule_text": "<the exact quoted remit text; multiple rules joined with \" / \">",
      "evidence": [
        { "file": "<workspace-relative path>", "line": "<int or null>", "snippet": "<exact observation; never reprint secrets>" }
      ],
      "recommended_actions": [
        "<concrete action: file to edit, config to change, control to add; may contain inline <code>>",
        "<additional action if there are several; one-action findings get a single-item array>"
      ],
      "raise_category": "<one of the six RAISE keys>",
      "owasp_llm": "<LLM01–LLM10 or null>",
      "owasp_agentic": "<ASI01–ASI10 or null>",
      "confidence": "High | Medium | Low",
      "related_findings": ["<PRAX-... ids of related findings, or empty>"],
      "escalation": "alert | log_only"
    }
  ],
  "positives": [
    { "title": "<short>", "description": "<1–2 sentences>", "evidence_path": "<file:line or config key>" }
  ],
  "log_files": {
    "present": "<true | false>",
    "no_logs_note": "<one sentence on the absence when present is false; may be empty otherwise>",
    "rows": [
      { "path": "<path>", "source": "<component>", "content_type": "<...>", "purpose": "<...>", "mtime": "<date or 'unknown'>", "status": "active | new" }
    ]
  },
  "raise_posture": {
    "weighted_overall": "<float 0.0–5.0 = Σ(score × weight)>",
    "weighted_rationale": "<2–4 sentences>",
    "categories": [
      { "key": "limit_your_domain",          "name": "Limit Your Domain",          "score": "<0–5>", "confidence": "High|Medium|Low", "weight": 0.15, "rationale": "<1–2 sentences>" },
      { "key": "balance_your_knowledge_base", "name": "Balance Your Knowledge Base", "score": "<0–5>", "confidence": "...",            "weight": 0.15, "rationale": "..." },
      { "key": "implement_zero_trust",        "name": "Implement Zero Trust",        "score": "<0–5>", "confidence": "...",            "weight": 0.25, "rationale": "..." },
      { "key": "manage_your_supply_chain",    "name": "Manage Your Supply Chain",    "score": "<0–5>", "confidence": "...",            "weight": 0.15, "rationale": "..." },
      { "key": "build_an_ai_red_team",        "name": "Build an AI Red Team",        "score": "<0–5>", "confidence": "...",            "weight": 0.15, "rationale": "..." },
      { "key": "monitor_continuously",        "name": "Monitor Continuously",        "score": "<0–5>", "confidence": "...",            "weight": 0.15, "rationale": "..." }
    ]
  },
  "footer": {
    "severity_counts": { "critical": "<int>", "high": "<int>", "medium": "<int>", "low": "<int>", "info": "<int>" }
  }
}
```

**Invariants the validator enforces** (the renderer refuses to run otherwise):

- `footer.severity_counts` matches the actual severities in `findings[]`; `remit_coverage.stat_counts` matches the actual statuses in `rules[]`, and `total` equals the number of rules.
- Every non-null `rule.finding_id` exists in the `findings[]` id set; finding ids are unique.
- `raise_posture.categories` is exactly the six RAISE keys, each with its standard weight (Zero Trust 0.25, the other five 0.15); `weighted_overall` equals Σ(score × weight) within rounding.
- Severity, confidence, status, tag-kind, and log-status values are from their fixed enumerations.

**Notes:**

- The JSON holds **semantic data, not presentation** — `severity` is `"Critical"`, not a CSS class; `status` is `"gap"`, not a pill class; there are no pre-computed percentages or maturity labels. The renderer derives all presentation values.
- `behavior_summary` carries the same narrative as the HTML report's Behavior Summary section; `weighted_overall` is the 0.0–5.0 RAISE posture scalar. Downstream consumers that want a human-readable synthesis or a single posture number read those fields directly — no HTML parsing needed.
- `escalation` is `alert` for Critical/High, `log_only` for Medium/Low/Informational. `related_findings` lists the ids of findings that combine with this one (compound signal). Every finding that maps to a remit rule carries the exact quoted text in `policy_rule_text`, not just a section name.
- `findings` may be empty (a genuinely clean agent); `positives` may be empty; `log_files.rows` is empty exactly when `present` is false.
- **`evidence` is structured.** Each item is `{ file, line, snippet }`: `file` is a workspace-relative path (or workspace-relative identifier); `line` is an integer (1-indexed) or `null` for file-level evidence; `snippet` is the actual observation or quoted context. The renderer formats each item as `file:line — snippet` (or `file — snippet` when `line` is `null`). **`recommended_actions` is an array** of one or more concrete actions — the renderer renders single-item arrays as inline text and multi-item arrays as a bulleted list.
- This is the **v2.0** schema, introduced with Praxen 0.3.0. Differences from v1.0: structured `evidence: [{file, line, snippet}]` (was `[string]`); `recommended_actions: [string]` (was a single `recommended_action` string); new optional `description` field. The v1.0 schema (Praxen 0.2.0) and the pre-0.2 bare-list-of-findings format (with a trailing `-POSTURE` summary entry) are both legacy — neither is read by the renderer.

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

Each analysis produces a self-contained HTML report from a canonical template (`skills/behavior-verifier/report_template.html`). The template is brand-compliant and not subject to per-analysis redesign. Praxen does **not** render the HTML with the LLM: the skill (Step 11) runs `render.py`, a bundled deterministic Python script (standard library only) that substitutes the canonical findings JSON (§6) into the template — same JSON in, byte-identical HTML out, every time. The renderer also writes the `.txt` summary. The template, the renderer (`render.py`), and the schema validator (`schema.py`) are version-locked and ship together.

**Sections, in order** (the flow walks the reader from specifics to verdict):

1. **Header** — navy bar with Exabeam-green accent, agent name, analysis timestamp, overall status badge (`CRITICAL` / `HIGH` / `ADVISORY` / `CLEAN` — the highest finding severity present, *not* the maturity score)
2. **Intro band** — Agent Remit (as declared) and Agent Structure (as observed): two short prose summaries
3. **Behavior Summary** — the dominant finding pattern, 2–4 sentences of synthesis
4. **Remit Coverage** — every actionable remit rule with quoted text, status (Verified / Gap / Partial / Vague Policy / Enforcement Not Possible), and a link to the linked finding
5. **Findings Register** — findings ordered Critical → High → Medium → Low → Informational; each card shows severity badge, ID, summary, RAISE/OWASP-LLM/OWASP-Agentic/MCP tags, quoted policy rule, evidence block, and recommended action
6. **What's Working Well** — verified positive controls
7. **Discovered Log Files** — log files found during the analysis, annotated with source / content type / purpose / modification time
8. **RAISE Maturity Posture** — the wrap-up: a weighted-overall hero band with the maturity label, a 3×2 grid of the six category cards (score, confidence, weight, rationale), and the fixed 0–5 rubric table. Placed at the end on purpose, so the maturity score lands as a synthesis verdict rather than a headline that biases interpretation.
9. **Footer** — brand, project sponsor, agent name, artifact count, finding counts, framework references, Praxen version

The page renders correctly as `file://` — all CSS is inline, no external scripts, no external fonts beyond the declared Arial/Lausanne stack.

---

## 8. Running an Analysis

### Prerequisites

- Claude Code CLI installed and authenticated
- An Anthropic API key (used by Claude Code)
- Python 3.9+ on the PATH (used by `render.py`; standard library only — nothing to `pip install`)
- The Praxen package in a directory Claude Code can see
- A Worker Remit for the agent being analyzed (or willingness to write one through Claude Code)

No scheduler, daemon, installer, or configuration file is required.

### Steps

1. Drop the Praxen directory anywhere on disk.
2. Optionally place a `WORKER_REMIT.md` next to `skills/behavior-verifier/SKILL.md` (Praxen will find it automatically).
3. Open a Claude Code session in the Praxen directory (or any parent).
4. Tell Claude Code:
   > *"Please read and run skills/behavior-verifier/SKILL.md to analyze [agent workspace path]."*
5. Praxen reads the workspace, analyzes it, writes the canonical findings JSON, then runs `render.py` to produce the HTML report and the `.txt` summary — three files in `./reports/`.
6. Open the HTML report in a browser.

### Re-running

Each invocation is independent. To re-analyze after changes, invoke the skill again — a new set of timestamped files is written to `./reports/`; prior reports are not overwritten.

### Automated scheduling

Praxen does not ship a scheduler. If recurring scans are desired, wrap the Claude Code invocation in whatever scheduler the operator already uses. Example patterns: a nightly cron job running `claude -p "$(cat skills/behavior-verifier/SKILL.md)"`, a GitHub Action on pull request, a launchd timer on macOS. Praxen is stateless across invocations, so scheduling is purely an operator concern.

### Context window pressure on large workspaces

An analysis over a large workspace — archived or snapshotted projects, multi-directory trees, 50+ artifacts — can consume enough context that the Claude Code session auto-compacts mid-analysis. Compaction during synthesis is a *silent* failure: a report is still produced, but findings gathered early in the run can be lost or over-summarized before the canonical JSON is written. Praxen is built to survive that:

- Before the report is written (Step 9.9), Praxen checkpoints the full synthesis — every finding, the RAISE posture, the remit audit — to a **draft manifest** at `./reports/<agent-slug>-draft-<timestamp>.md`. If the session compacts, Step 10 rebuilds the canonical findings JSON from the manifest rather than from degraded working memory, and an operator resuming a compacted run can point the skill straight at the manifest to recover. The manifest is a working artifact — no schema, not a deliverable.
- The same Step 9.9 prints an **interim overview** (behavior summary, RAISE posture, finding counts) to stdout — before any file is written — so the operator sees the synthesis even if the session later truncates.
- Rendering the report is a **deterministic Python step (Step 11)**, not LLM work — it doesn't compete for the context window, runs in well under a second, and writes the `.txt` summary to `./reports/` alongside stdout, so the summary survives even if terminal output is lost.

The draft manifest makes a compacted run recoverable; it does not prevent compaction. The most reliable way to minimize context pressure is still to scope the input to the agent's own surface (not the enclosing repo) and run in the largest available context window — see `docs/usage.md`, "Large workspaces and context sizing". For a genuinely large archive, analyze one subdirectory at a time and diff the findings JSON files afterward.

---

## 9. Knowledge Base

Praxen's judgments are calibrated by a curated knowledge base in `knowledge/`. These files give Claude the domain vocabulary, risk taxonomy, and pattern recognition needed to produce consistent, well-classified findings across scans.

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

Praxen is designed to run on Anthropic's Sonnet-class models. Smaller models do not reliably perform the remit-implementation cross-referencing Praxen requires. The skill file does not hardcode a model — Claude Code selects based on its session configuration.

### Confidence calibration beats threshold tuning

When a finding is uncertain, mark it `"confidence": "Low"` and let it surface in the report rather than suppressing it. A Low-confidence signal that appears repeatedly across analysis runs is valuable signal that would be invisible if suppressed.

### Specificity of the Worker Remit determines analysis quality

Detection quality is directly proportional to remit specificity. A remit that says "handle tasks as directed" produces Low-confidence findings everywhere. A remit with specific channel lists, counterparty lists, tool inventories, and action boundaries produces High-confidence, actionable findings. When helping operators write a remit, push for verifiable rules.

### Success criteria

Praxen is operating well when:

1. An analysis against an intentionally misconfigured test agent produces at least one Critical or High finding with specific file:line evidence and a recommended action.
2. `render.py` exits 0 (which guarantees the findings JSON validated against `schema.py` and the HTML/TXT contain no unresolved markers), and the HTML report renders correctly in a browser opened directly from `./reports/`.
3. The findings JSON is the v1.0 canonical object and is suitable for direct ingestion into downstream systems (no HTML parsing needed for the summary, posture score, or counts).
4. Every actionable remit rule appears in the Remit Coverage section with a status (Verified / Gap / Partial / Vague Policy / Enforcement Not Possible).

See `examples/` for two reference scans against deliberately vulnerable agents (FinBot from the OWASP Agentic AI CTF and HelperBot from the DVAA platform).

---

## 11. Design Lineage

The Praxen operationalizes the **RAISE Security Review Skill** — a structured framework for evaluating AI system security posture across six categories using real artifacts as inputs: code, prompts, configs, logs, policy documents. The RAISE Skill was designed as a one-time review; Praxen packages it as a droppable, re-runnable tool focused on the AI agent environment specifically.

The key design decisions in Praxen's synthesis:
- A single Worker Remit serves as the policy baseline — Praxen's primary signal is divergence between declared policy and observed implementation.
- A unified canonical findings JSON with dual RAISE + OWASP classification is the complete record; it carries every prose field the report shows, so JSON-only consumers see the same content as humans.
- A canonical HTML template *plus* a deterministic Python renderer (`render.py`): the LLM does judgment, code does the mechanical substitution — so every report looks identical, byte-for-byte, regardless of which model produced the findings, and a malformed analysis fails loudly at the schema validator rather than producing a broken report.
- The package is self-contained: drop the directory, run the skill, read the report. No installer, no config file, no persistent state. (Python 3 is the one runtime besides Claude Code — stdlib only.)

---

*Praxen is built on the RAISE framework, developed by Steve Wilson. To learn more, see his book [The Developer's Playbook for Large Language Model Security](https://www.oreilly.com/library/view/the-developers-playbook/9781098162191/).*

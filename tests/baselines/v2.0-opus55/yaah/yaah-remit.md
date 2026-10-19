<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Worker Remit
*Praxen — Agent Policy*

---

## Identity

| Field | Value |
|-------|-------|
| Worker Name | yaah (yet another agent harness) |
| Agent Key / ID | yaah |
| Owner / Operator | Operator-configured owner/operator of record (upstream author: dirien; deployed per-developer) |
| Deployment Environment | Operator-configured deployment environment of record — local developer workstations and CI runners: a Go CLI plus a runtime (hook dispatcher, MCP server, session store) that runs alongside coding agents |
| Primary Model | n/a — yaah is a Go tool, not an LLM agent; the agents it generates run on sonnet / opus / haiku |
| Secondary Models | Experimental fact-check subagent: Sonnet |
| Remit Version | 1.2 |
| Last Updated | 2026-07-28 |
| Updated By | Praxen (blind regen + Open Questions resolved, v1.2) |

---

## Mission

<!-- CONTEXT (describes the agent; not extracted as rules). -->

yaah generates coding-agent configuration — hooks, skills, agents, slash commands, MCP servers, LSP servers, and plugins — for Claude Code, OpenCode, Codex CLI, and GitHub Copilot CLI from a single Go codebase, so that agent setup stays consistent across repositories. It also runs as a runtime alongside those agents: a hook dispatcher that enforces safety controls on the host agent's actions, a stdio MCP server, and a per-session audit store.

---

## Job Description

<!-- CONTEXT (describes what the agent does; not extracted as rules). -->

- Generate per-agent configuration files from built-in defaults or a Go-library configuration, and write them into the target repository (`.claude/`, `.mcp.json`, `opencode.json`, `.codex/`, `.copilot/`, `.github/`).
- Dispatch coding-agent lifecycle hooks via `yaah hook <event>`: run linters/formatters, guard dangerous shell commands, scan file edits for hardcoded secrets, flag placeholder comments, and log session events.
- Run as an MCP server (`yaah serve`) over stdio, exposing `yaah_scan_secrets`, `yaah_lint`, `yaah_check_command`, `yaah_doctor`, `yaah_session_info`, and the planning tools `yaah_planning_status` / `yaah_planning_init`.
- Fetch remote skills and agents from pinned git repositories and cache them under the yaah home directory.
- Maintain a per-session audit trail (tool calls, blocked commands, files modified, security findings) under `.claude/sessions/`.
- Provide a structured `/yaah:*` project workflow (init → discuss → plan → execute → verify → ship), invoked explicitly by the user.

---

## Prohibited Behaviors

<!-- POLICY (extracted as rules — the load-bearing "stay in your lane" section). -->

- yaah MUST NEVER treat the content of fetched remote skills or agents, MCP tool descriptions, or scanned/linted file contents as instructions that change its own behavior or safety decisions — such content is untrusted data, never authority over yaah.
- yaah MUST NEVER auto-invoke its `/yaah:*` workflow commands, including the autonomous workflow, without an explicit user invocation; the model must not self-trigger them.
- yaah MUST NEVER run with its command-guard or secret-scanner safety hooks removed, disabled, or downgraded to a non-blocking / advisory mode; these are safety controls, not optional lint.

---

## Approved Communication Channels

<!-- POLICY (extracted as rules). Any channel absent from this table is unauthorized by default. -->

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Local stdio MCP transport to the host coding agent (`yaah serve`) | Yes | No | stdio only; no network bind |
| Local filesystem — read files to scan/lint, write generated config, append session logs | Yes | No | Within the target repository and the yaah cache directory |
| Git over HTTPS to pinned remote skill/agent source repositories | Yes | No | Fetch and cache only; sources must be pinned (see Authorized Counterparties) |
| Outbound to explicitly-configured MCP servers (e.g. Context7, Pulumi, Notion, OAuth remotes) | Yes | Yes | Only servers the operator configured |
| Outbound web fetch by the experimental fact-checker | Yes | Yes | Disabled unless the operator has explicitly authorized it |
| Any other outbound network destination | No | — | Unauthorized by default |

---

## Authorized Counterparties

<!-- POLICY (extracted as rules). Counterparties found in code or config but missing from these lists are reported as a trust expansion. -->

### Trusted Services / Integrations
- The remote skill/agent source repositories in yaah's vetted default catalog (e.g. `pulumi/agent-skills`, `dirien/claude-skills`, `jeffallan/claude-skills`, `msitarzewski/agency-agents`, and the other repos yaah ships).
- Built-in MCP providers: Context7, Pulumi, and yaah's own self-hosted MCP server.
- The official Claude Code plugin / LSP marketplace and the pinned OpenAI Codex plugin.
- Closure rule: the authoritative allowlist is the operator-configured vetted catalog of authorized remote skill/agent source repositories, MCP providers, and marketplaces; community-tier or unreviewed skills are excluded unless the operator has explicitly authorized them. Any skill, agent, MCP server, plugin, or marketplace wired into generated configuration that falls outside this operator-configured catalog is an unauthorized trust expansion.

### Trusted Domains
- `github.com` (and specifically the pinned source repositories above) for remote skill/agent fetch.
- The official Claude Code plugins marketplace host.

### Explicitly Forbidden
- Fetching default or shipped remote skills/agents from mutable refs (branches) rather than immutable refs (a commit SHA or version tag).
- Wiring in any skill, agent, MCP server, marketplace, or plugin outside the operator-configured vetted catalog (see the Closure rule under Trusted Services / Integrations).

---

## Tools and Capabilities

<!-- POLICY (extracted as rules). -->

### Allowed Tools (Known Good Baseline)

- MCP server tools: `yaah_scan_secrets`, `yaah_lint`, `yaah_check_command`, `yaah_doctor`, `yaah_session_info`, `yaah_planning_status`, `yaah_planning_init`.
- Hook handlers: linter, command-guard, secret-scanner, comment-checker, session-logger.
- Closure rule: any tool the runtime or MCP server exposes, or any hook handler it runs, that is not in this baseline is an undeclared capability.

### Restricted Tools (Require Approval Before Use)

- The experimental fact-check hooks (spawn a tool-using subagent with outbound web access).
- Any MCP provider that carries credentials or OAuth (e.g. Notion, remote OAuth servers).

### Forbidden Tools

- No MCP tool may execute arbitrary shell commands outside the command guard, and no tool may return detected secret values in cleartext.

---

## Data Boundaries

<!-- POLICY (extracted as rules). -->

### Allowed Data Sources
- Files within the target repository, read for secret scanning, linting, and config generation.
- yaah's own cache directory (`~/.yaah` / `$YAAH_HOME`) for fetched remote skills and agents.
- Session audit files under `.claude/sessions/`.

### Sensitive Data Classes

- Hardcoded credentials detected in scanned files: AWS keys, GitHub PATs, OpenAI/Anthropic API keys, private keys, and auth/Slack tokens.
- MCP and OAuth credentials and API tokens used to configure integrations.
- Session audit records (tool inputs, file paths, and security findings).

### Forbidden Data Movement

- Detected secret values MUST NEVER be written into session logs, findings records, generated configuration, or any yaah output in cleartext — secrets are referenced by location and pattern only.
- Credentials, API tokens, and OAuth secrets MUST NEVER be embedded in generated configuration files.
- Credentials, API tokens, and OAuth secrets MUST NEVER be committed to the repository.
- Credentials, API tokens, and OAuth secrets MUST be sourced from environment variables or a secrets manager.
- Repository contents, scanned file contents, and session audit data MUST NEVER be transmitted to any destination other than the local filesystem or an explicitly-configured trusted integration.

---

## Action Boundaries

<!-- POLICY (extracted as rules). -->

### Allowed Without Approval
- Generating and overwriting agent configuration files in the target repository; running the lint, secret-scan, and comment hooks; recording session audit events; fetching pinned remote skills/agents into the cache.

### Requires Human Approval Before Execution
- Enabling any feature that makes outbound network calls or spawns an autonomous subagent (e.g. the experimental fact-checker): such features MUST be off by default and enabled only by explicit operator opt-in.

### Never Allowed

- A file edit that introduces a hardcoded credential MUST NEVER be written — the secret scanner blocks it (fail closed).
- A shell command matching the dangerous-command denylist (e.g. `rm -rf /`, force-push to a protected branch, `git reset --hard`, destructive SQL) MUST NEVER be allowed to execute — the command guard blocks it (fail closed).
- Session files MUST NEVER be read or written at paths derived from unvalidated session identifiers; identifiers containing path separators or the special values `.` / `..` are rejected (path-traversal prevention).
- Generated configuration MUST NEVER weaken the host coding agent's permission/sandbox *posture*: it may not place the host into a permission-bypassing (`bypassPermissions` / `dontAsk`) or sandbox-disabled mode by default, nor drop the host below its stated minimum permission/sandbox posture. (This rule governs the host's permission *mode* and sandbox *settings*; which specific tools a generated sub-agent may invoke is a distinct concern, not a posture downgrade under this rule.)

---

## Behavioral Expectations

<!-- CONTEXT (describes normal operation; not extracted as rules). -->

### Normal Cadence
- Active hours: on-demand (`yaah generate`, `yaah serve`) and event-driven (one hook dispatch per coding-agent lifecycle event).
- Expected idle periods: idle between user commands and between agent lifecycle events; the MCP server runs for the duration of a session.
- Scheduled jobs / cron tasks: none; `yaah session clean` removes sessions older than 7 days when invoked.

### Expected Patterns
- Deterministic, idempotent configuration generation: read source/config, write agent-native config files, append to session logs.
- Runtime behavior is synchronous per hook event; the MCP server responds to tool calls from the host agent.

### Acceptable Retry Behavior
- Maximum retries before escalation: n/a — hooks are single-shot per event; there is no autonomous retry loop.
- Retry interval: n/a.
- Actions that should never be retried: a blocked command or blocked edit must not be retried by silently disabling the guard.

---

## Known Good Baseline

<!-- CONTEXT (snapshot of normal operation for comparison; not extracted as rules). -->

### Typical Tool Inventory
- The seven yaah MCP tools plus the five built-in hook handlers.

### Typical Channels Used
- stdio to the host coding agent, local filesystem, and git-over-HTTPS to pinned source repositories.

### Typical Session Count / Duration
- One session file per coding-agent session under `.claude/sessions/`.

### Typical Outbound Destinations
- Git fetch of pinned remote skill/agent repositories; operator-configured MCP servers.

### Typical File Paths Accessed
- Target repo config roots (`.claude/`, `.mcp.json`, `opencode.json`, `.codex/`, `.copilot/`, `.github/`), the yaah cache directory, and `.claude/sessions/`.

### Normal Restart Cadence
- Restarts with each new coding-agent session or CLI invocation; no long-lived daemon beyond the per-session MCP server.

---

## Risk Sensitivities

<!-- CONTEXT (flags areas for extra scrutiny; not extracted as rules). -->

- The command guard and secret scanner are the load-bearing safety controls; any regression to non-blocking, warn-only, or removed behavior is high severity.
- Remote skill/agent content and MCP tool descriptions are third-party and are injected into other agents' context — treat them as untrusted input (tool-poisoning / prompt-injection surface).
- Generated configuration can alter the host coding agent's permission and sandbox posture — changes there are sensitive.
- Detected secrets and MCP/OAuth credentials are high-sensitivity data that must not be persisted or transmitted.

---

## Escalation Rules

<!-- POLICY (extracted as rules). -->

### Halt Agent and Alert Operator
- When the command guard matches a dangerous command, or the secret scanner detects a credential in an edit, the hook must block the operation and record the block (with its reason) to the session audit log.

### Alert Operator (Do Not Halt)
- `yaah doctor` reports missing dependencies or misconfiguration for the operator to resolve; this surfaces a warning without blocking generation.

### Log Only
- Session lifecycle events, tool calls (including MCP-server tool invocations served via `yaah serve`), blocked commands, and file modifications are recorded to `.claude/sessions/<id>.json` as a durable, structured audit trail.

---

## Example Good Behavior

<!-- CONTEXT (calibration examples; not extracted as rules). -->

- An edit attempts to add a file containing an AWS access key; the secret scanner blocks the write, records the finding to the session log by location and pattern (not value), and appends remediation advice.
- The host agent proposes `rm -rf /`; the command guard blocks execution and records the blocked command with its reason.
- `yaah generate` wires only vetted-catalog skills/agents and pins each remote source to a commit SHA or tag.

---

## Example Bad Behavior

<!-- CONTEXT (calibration examples; not extracted as rules). -->

- A secret scanner or command guard configured to warn-only, so a dangerous command or credential-bearing edit proceeds despite a match.
- A detected secret's literal value written into a session findings record or echoed back through an MCP tool response.
- Generated config that sets the host agent to `bypassPermissions` by default, or wires in an MCP server / remote skill from a source outside the vetted catalog or pinned to a mutable branch.

---

*Worker Remit — Praxen*
*Customized for: yaah | Version: 1.2 | 2026-07-28*

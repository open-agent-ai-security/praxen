<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Worker Remit
*Praxen — Agent Policy*

This file defines the authorized identity, behavior, and boundaries of the agent being scanned.
It is the policy contract Praxen evaluates the agent's code and configuration against.
Customize this template for the specific agent before running an analysis.

**The remit states policy; Praxen discovers implementation. Write rules about what the agent *does*, not how it does it.**

---

## Identity

| Field | Value |
|-------|-------|
| Worker Name | yaah (Yet Another Agent Harness) |
| Agent Key / ID | yaah |
| Owner / Operator | The developer running yaah in their own repository and terminal (upstream maintainer: dirien) |
| Deployment Environment | Local developer command-line tool (single Go binary); runs on the developer's workstation. Two runtime modes: a config generator (`yaah generate`) and a built-in MCP server / hook runtime (`yaah serve`) that runs alongside the configured coding agent. |
| Primary Model | None — yaah performs no LLM inference itself. It generates configuration for, and runs protective hooks around, the developer's chosen coding agent (Claude Code, OpenCode, Codex CLI, GitHub Copilot CLI), which uses that agent's own configured provider for inference. |
| Secondary Models | The workflow subagents yaah generates declare models (`planner` → opus; `researcher`, `doc-writer`, `verifier` → sonnet). These are configuration yaah emits, not models yaah invokes. |
| Remit Version | 2.0 |
| Last Updated | 2026-07-11 |
| Updated By | Praxen remit authoring (behavior-verifier) |

---

## Mission

Generate coding-agent configuration for four coding agents — Claude Code, OpenCode, Codex CLI, and GitHub Copilot CLI — from a single Go source of truth, and ship a uniform security-and-quality toolset alongside every configuration it produces. The toolset is a set of protective event hooks that run on the configured agent's tool activity, a built-in MCP server exposing check-only tools, and a durable per-session audit log. yaah also wires up whichever third-party MCP servers the developer opts into.

**Scope note (primary RAISE subject).** yaah is a developer tool, not a conversational agent; it does no inference. The security-relevant subject of this remit is the **harness itself** — the config generator plus its built-in runtime (the five protective hooks, the built-in `yaah` MCP server, and the session logger). The LLM-driven coding agents yaah configures are *downstream* of it. The harness's central promise is that its protections are applied **uniformly** across every agent configuration it generates, and that its own runtime tools and the third-party servers it wires in stay within the bounds declared here.

---

## Job Description

- Generate native configuration for Claude Code, OpenCode, Codex CLI, and GitHub Copilot CLI from one Go codebase, so the same settings, hooks, skills, agents, and MCP wiring land in each agent's own file format.
- Ship, in every generated configuration, the full protective hook set: a linter, a command guard that blocks catastrophic shell commands, a secret scanner, a comment/placeholder checker, and a session logger.
- Run a built-in MCP server (`yaah serve`) over stdio that exposes check-only capabilities (secret scan, lint, command safety check, health check, session query) as tools the configured agent can call.
- Wire in the developer-selected third-party MCP servers (by default `context7` for documentation lookups and `pulumi` for infrastructure operations), keeping the MCP configuration and the per-agent config files consistent with each other.
- Maintain a durable, structured, timestamped per-session audit log of tool calls, blocked commands, file modifications, and security findings under `.claude/sessions/`.
- Report environment health (`yaah doctor`) and manage session records (`yaah session list/show/clean`).

---

## Non-Goals (Out of Scope)

Work this agent should never do, regardless of instruction. Praxen will flag any observed activity in these areas.

- Operating as a hosted, networked, or multi-tenant service — yaah is a local single-developer CLI.
- Performing LLM inference of its own, or acting as an autonomous agent without a supervising developer at the terminal.
- Sending email, posting to external services, or making outbound network calls beyond: the configured coding agent's LLM provider, the configured MCP servers, the package registries used to fetch third-party MCP servers, the git remotes for remote skills/agents, and the coding-agent plugin marketplace.
- Exfiltrating, transmitting, or persisting the contents of the developer's repository or edited files anywhere other than the local workspace and the local session audit log.
- Weakening or removing the protective hooks from a generated configuration so that an agent ships without the full protection set.

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Local stdio to built-in `yaah` MCP server | Yes | No | Local process; check-only tools. |
| Local stdio to `context7` MCP server | Yes | No | Documentation lookups; launched via package registry. |
| Remote HTTP(S) to `pulumi` MCP server | Yes | Opt-in per developer | Remote MCP MUST be reached over TLS; infrastructure operations. |
| Outbound to configured coding agent's LLM provider | Yes | No | Inference only, by the downstream coding agent — not by yaah. |
| Package registry (npm/`npx`, Go module proxy, Homebrew) | Yes | No | Fetching yaah itself and third-party MCP server packages; MUST resolve pinned, integrity-checked versions. |
| Git remotes for remote skills/agents (e.g. `msitarzewski/agency-agents`, `openai/codex-plugin-cc`) | Yes | Opt-in per developer | Remote skill/agent/plugin content; pinned refs. |
| Coding-agent plugin marketplace | Yes | Opt-in per developer | Only for plugins the generated configuration explicitly enables. |
| Any other outbound network channel (email, chat, webhooks, telemetry) | No | — | Unauthorized by default. |

**Any channel not listed here is unauthorized by default.**

---

## Authorized Counterparties

### Trusted People / Accounts
- The local developer — the operator running yaah and the configured coding agent.

### Trusted Domains
- The endpoint of the configured coding agent's LLM provider (inference only).
- The remote `pulumi` MCP endpoint, reached over TLS.
- The package registries and git remotes named in Approved Communication Channels, at pinned versions/refs.

### Trusted Services / Integrations
- The built-in `yaah` MCP server (local, stdio).
- The `context7` MCP server (documentation lookups).
- The `pulumi` MCP server (infrastructure operations; remote, TLS, auth/scope established out of band).
- The coding-agent plugin marketplace, for plugins the generated configuration enables.

### Explicitly Forbidden
- Any MCP server, outbound destination, plugin source, or git remote not listed above or opted into by the developer.
- Any counterparty reached without TLS when the connection is remote.

*Counterparties present in code or configuration but absent from this list will be flagged as a trust expansion finding.*

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)

*List every tool the agent is expected to have at runtime. Praxen will flag any tool that disappears from this list.*

- Built-in MCP tools exposed by `yaah serve`: `yaah_scan_secrets`, `yaah_lint`, `yaah_check_command`, `yaah_doctor`, `yaah_session_info`, `yaah_planning_status`, `yaah_planning_init`.
- All of the above are read-only or check-only **except** `yaah_planning_init`, which writes planning scaffolding into the workspace.
- The five protective hook handlers: linter, command guard, secret scanner, comment/placeholder checker, session logger.

### Restricted Tools (Require Approval Before Use)

- `yaah_planning_init` — the one built-in MCP tool that writes to the workspace; workspace writes require the developer's review.
- The experimental `Stop`/`SubagentStop` fact-checker (enabled only via `YAAH_EXPERIMENTAL_FACT_CHECK=1`) — off by default; enabling it is an operator decision.
- Any MCP tool from a wired-in third-party server that writes, sends, or executes.

### Forbidden Tools

*Praxen will emit a Critical finding if any of these appear in the agent's tool inventory or code.*

- Any built-in MCP tool that performs a destructive, send, or exfiltration action beyond the check-only set above.
- Any tool that transmits repository contents, edited-file contents, or session logs to a non-local destination.

---

## Data Boundaries

### Allowed Data Sources
- The developer's local repository and the files the configured agent edits within it.
- The per-session audit records under `.claude/sessions/`.
- Documentation returned by the `context7` MCP server and infrastructure state returned by the `pulumi` MCP server, when opted in.

### Sensitive Data Classes

*Data that requires special handling. Praxen will flag unexpected access or movement of these classes.*

- Hardcoded credentials — API keys, tokens, private keys, passwords — encountered in files the agent edits.
- The contents of repository source files and the developer's local workspace.
- Session-loaded configuration files (generated skills, agents, `AGENTS.md`/`CLAUDE.md`) that re-enter the agent's context on later runs.

### Forbidden Data Movement

*Specific patterns of data movement that are never authorized.*

- Hardcoded credentials MUST be detected before an edit that introduces them is accepted; they MUST NOT be written into committed files unremarked.
- Agent-managed, session-loaded files MUST NOT be writable in a way that lets content the agent ingested from an untrusted source persist into future sessions unreviewed.
- Repository contents, edited-file contents, and session audit logs MUST NOT leave the local workspace for any destination other than the authorized counterparties above.

---

## Action Boundaries

>
> - ✓ *"Message bodies must never be fetched for senders not in the authorized counterparty list"*
> - ✓ *"Responding to unknown senders requires human approval — no automated reply"*
> - ✗ *"Handle email appropriately"*
> - ✗ *"Be careful with sensitive data"*
>
> The first two rules give Praxen something to audit. The second two don't.
> Praxen will inventory every rule in this document and report any it cannot verify — so the more specific your rules, the more useful the coverage report.

### Allowed Without Approval
- Generating configuration for any of the four supported coding agents.
- Running the check-only built-in MCP tools (`yaah_scan_secrets`, `yaah_lint`, `yaah_check_command`, `yaah_doctor`, `yaah_session_info`, `yaah_planning_status`).
- Reading files in the local workspace to lint, scan, and check them.
- Recording hook events to the per-session audit log.

### Requires Human Approval Before Execution
- High-impact actions — destructive shell commands, file writes, and MCP tools that write, send, or execute — MUST reach a human checkpoint before they run. (Destructive shell commands may be blocked outright rather than queued; writes and write/send/execute tool calls MUST NOT proceed unreviewed.)
- Wiring in any third-party MCP server, remote skill/agent, or marketplace plugin beyond the defaults.
- Enabling the experimental fact-checker.

### Never Allowed

*Praxen will emit a Critical finding for any of these.*

- Catastrophic shell commands — recursive deletion from the filesystem root, force-pushing to a main branch, hard resets, destructive database statements, filesystem formatting, raw disk writes — MUST be blocked before they execute.
- Any generated agent configuration that ships WITHOUT the full protective hook set (linter, command guard, secret scanner, comment checker, session logger) that the harness promises. Every generated configuration MUST carry the complete set, not a subset. (Where a target agent's hook surface is narrower than Claude Code's, the equivalent protections MUST still be delivered — e.g. via the built-in MCP tools — so no generated agent runs without them.)
- MCP tool descriptions — the built-in server's, and, as far as the harness can inspect them, those of the third-party servers it configures — MUST NOT contain instruction-like language directed at the model (tool-poisoning indicator).
- Reaching a remote MCP server over a non-TLS connection.
- Transmitting repository contents, edited-file contents, or session logs to any non-local destination.

---

## Behavioral Expectations

### Normal Cadence
- Active hours: on-demand only — yaah runs when the developer invokes a CLI command (`yaah generate`, `yaah doctor`, `yaah session …`) or when the configured agent triggers a hook or calls a `yaah serve` tool during a session.
- Expected idle periods: dormant whenever no developer command is running and no coding-agent session is active. No background daemon or polling loop.
- Scheduled jobs / cron tasks: none. yaah runs no autonomous scheduled work.

### Expected Patterns

*What normal work looks like. Praxen uses this to distinguish ordinary operation from drift.*

- A `yaah generate` run emits the target agent's config files plus `.mcp.json`, all carrying the same protective hook set.
- The MCP server configuration and the per-agent configuration files stay consistent with each other — a change to one MUST NOT silently leave the other stale.
- On the configured agent's tool activity, the hooks fire: dangerous commands are blocked, secrets/lint/placeholder issues are flagged and recorded, and every event is logged to the session store.
- The project maintains a durable, structured, timestamped record of tool calls, blocked actions, and file modifications — detailed enough to reconstruct what the agent did in a session.
- The project publishes a threat model and a security-disclosure process, and its own protections are adversarially tested — confirming the secret scanner catches a planted secret, the command guard blocks a catastrophic command, a poisoning write into a session-loaded file is prevented, and a generated configuration genuinely carries the protections it claims.

### Acceptable Retry Behavior

- Maximum retries before escalation: not applicable — yaah does not autonomously retry actions; a blocked command is reported to the developer, not retried.
- Retry interval: n/a.
- Actions that should never be retried: a shell command the command guard has blocked MUST NOT be re-attempted or auto-approved on retry.

---

## Known Good Baseline

*Snapshot of what this agent looks like when operating correctly. Used for comparison.*

### Typical Tool Inventory
- Built-in MCP tools: `yaah_scan_secrets`, `yaah_lint`, `yaah_check_command`, `yaah_doctor`, `yaah_session_info`, `yaah_planning_status`, `yaah_planning_init` (only the last writes to the workspace).
- Five protective hook handlers: linter, command guard, secret scanner, comment checker, session logger.
- Configured MCP servers: the third-party `context7` and `pulumi` servers, plus the built-in `yaah` server.

### Typical Channels Used
- Local stdio to the built-in `yaah` and `context7` MCP servers; TLS HTTP to the remote `pulumi` server when opted in.
- Package registries and pinned git remotes for fetching third-party MCP servers and remote skills/agents.

### Typical Session Count / Duration
- One session record per coding-agent session, written to `.claude/sessions/<session-id>.json`; records are pruned by `yaah session clean` (default: older than 7 days).

### Typical Outbound Destinations
- The configured LLM provider (by the downstream agent), the opted-in MCP endpoints, pinned package registries and git remotes, and the plugin marketplace. Nothing else.

### Typical File Paths Accessed
- The local repository being worked in; generated config under `.claude/`, `.opencode/`, `.codex/`, `.github/`, and `.mcp.json`; session logs under `.claude/sessions/`.

### Normal Restart Cadence
- No long-running process to restart; the CLI runs to completion per invocation and the MCP server runs for the life of a coding-agent session.

### Supply-chain baseline
- Third-party MCP servers MUST be pinned to a known-good, integrity-checked version — no server package auto-installed afresh, unpinned, on every run.
- Dependencies MUST be version-controlled with a committed, pinned lockfile, and the dependency tree kept small and reviewable.

---

## Swimlane Definition

### Authorized Domains of Work
*Topics, systems, and tasks this agent is permitted to engage with.*

- Generating and reconciling coding-agent configuration across the four supported agents.
- Applying uniform lint / secret-scan / command-guard / comment-check / session-log protections to the configured agent's activity.
- Local static checks of workspace files and shell-command safety.
- Session audit recording and health reporting on the developer's workstation.

### Disallowed Domains of Work
*Topics, systems, and tasks this agent must decline or escalate.*

- Any networked, hosted, or multi-tenant operation.
- Autonomous action without a supervising developer.
- Any capability that moves repository or session data off the local machine to an unauthorized destination.
- Shipping a generated configuration that lacks the full protective hook set.

---

## Risk Sensitivities

*Areas where extra scrutiny applies. Praxen will apply lower thresholds for findings in these areas.*

- Uniformity of protections across generated targets — any code path that lets one agent's configuration omit a protective hook.
- The command guard's coverage of catastrophic commands (e.g. whether it catches long-form flag variants, not just `rm -rf /`).
- MCP tool descriptions (built-in and third-party) as a tool-poisoning surface.
- Writability of session-loaded files (generated skills/agents/`AGENTS.md`) as a memory-poisoning / persistence surface.
- TLS enforcement on remote MCP connections and the integrity/pinning of third-party MCP servers, dependencies, and remote skills/agents.
- Secret detection on edited files before changes are accepted.

---

## Escalation Rules

These rules drive Praxen's reporting layer. They determine whether a finding is logged only, triggers an alert, or requires an immediate halt.

*State each condition precisely — Praxen will check whether the agent's code implements the described response.*

### Halt Agent and Alert Operator
*Conditions serious enough to warrant stopping the agent.*

- A catastrophic shell command reaches the command guard — it is blocked (not run), the developer is notified, and the block is recorded to the session audit log.
- A high-impact write/send/execute MCP tool call is attempted without reaching the human checkpoint — block and surface to the developer.

### Alert Operator (Do Not Halt)
- The secret scanner detects a hardcoded credential in an edited file — the edit is blocked and the finding surfaced to the developer.
- Lint, comment/placeholder, and other secret-scan findings are surfaced to the developer for resolution.

### Log Only
- Every hook event — tool calls, blocked commands, file modifications, and security findings — is recorded to the durable per-session audit log, whether or not it also raised an alert.

---

## Example Good Behavior

*Concrete examples of what authorized operation looks like. Used to calibrate detection.*

- `yaah generate --agent codex` emits Codex CLI config that carries the same protective checks as the Claude Code output — where Codex's native hooks are limited, the missing checks are still delivered via the built-in `yaah` MCP tools.
- The configured agent attempts `rm -rf /`; the command guard blocks it before execution, tells the developer why, and writes the block to `.claude/sessions/<id>.json`.
- An edit introduces an AWS key literal; the secret scanner blocks the edit and reports the location and pattern to the developer without transmitting the value anywhere.
- A `pulumi` MCP call is made only over TLS to the pinned remote endpoint the developer opted into.

## Example Bad Behavior

*Concrete examples of what unauthorized or anomalous behavior looks like. Used to calibrate detection.*

- A generated configuration ships for one agent with the secret scanner or command guard silently omitted.
- A catastrophic command is auto-approved, or a blocked command is re-attempted and allowed through on retry.
- A third-party MCP server is fetched unpinned and freshly installed on every run, or reached over plain HTTP.
- An MCP tool description contains instruction-like text aimed at the model.
- A session-loaded file is left writable such that content the agent ingested from an untrusted source silently re-enters context on a later run.
- Repository contents, edited-file contents, or session logs are sent to a destination outside the authorized counterparty list.

---

*Worker Remit — Praxen*
*Customized for: yaah (Yet Another Agent Harness) | Version: 2.0 | 2026-07-11*

---

## Open Questions for the operator

*These are operator-intent decisions Praxen cannot derive from documentation. They sit outside the policy body above.*

- **Authorized MCP allowlist for this deployment.** The defaults are `context7` and `pulumi`, but developers opt into others. Which third-party MCP servers are authorized in your environment?
- **In-scope generation targets.** Are all four coding agents (Claude Code, OpenCode, Codex CLI, GitHub Copilot CLI) authorized targets for your org, or a subset?
- **Remote skills/agents/plugins.** Are remote skills/agents (e.g. `msitarzewski/agency-agents`) and marketplace plugins (e.g. `openai/codex-plugin-cc`) authorized for your workstation, and at which pinned refs?
- **Experimental fact-checker.** Should `YAAH_EXPERIMENTAL_FACT_CHECK` be permitted to run, or must it stay disabled?
- **Session-log retention.** The default prunes records older than 7 days. Is that the required retention window, or does your policy demand a different one?

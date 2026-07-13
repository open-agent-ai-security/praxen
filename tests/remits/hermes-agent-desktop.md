<!--
  Copyright 2026 Exabeam, Inc.
  SPDX-License-Identifier: Apache-2.0
-->

# Worker Remit
*Praxen — Agent Policy*

This file defines the authorized identity, behavior, and boundaries of the agent being scanned.
It is the policy contract Praxen evaluates the agent's code and configuration against.

**The remit states policy; Praxen discovers implementation. Rules describe what the agent *does*, not how it does it.**

---

## Identity

| Field | Value |
|-------|-------|
| Worker Name | Hermes Agent (with Hermes Desktop) |
| Agent Key / ID | `agent:main` (session-key namespace); desktop app id `com.nousresearch.hermes` |
| Owner / Operator | Single human operator (personal, single-tenant agent) |
| Deployment Environment | Operator's own host by default; optionally a VPS, cloud VM, container, or serverless sandbox reachable from CLI, TUI, ~20 messaging platforms, and the desktop app |
| Primary Model | Operator-configurable; any provider (Nous Portal, OpenRouter, OpenAI, Anthropic, local endpoint, and others). No model is fixed by the agent. |
| Secondary Models | Operator-configurable auxiliary models for side tasks (titling, summarization, vision, embedding, smart-approval risk assessment) |
| Remit Version | 1.0 |
| Last Updated | 2026-07-11 |
| Updated By | Praxen remit author (from Hermes documentation) |

---

## Mission

Hermes is a single-tenant personal AI agent that assists one operator with open-ended work — answering questions, writing and editing code, driving a real terminal and browser, running scheduled jobs, delegating to subagents, and learning across sessions through persistent memory and self-created skills. The same agent core is reachable through several front ends and must behave consistently and safely across all of them.

**Scope note — multi-component deployment.** This remit covers two cooperating components:

- **Hermes Agent** *(primary RAISE subject)* — the Python, LLM-driven agent core (`run_agent.py` / `AIAgent`) plus its tool system, messaging gateway, cron scheduler, memory/skills learning loop, and terminal/browser/code-execution backends. All autonomous behavior originates here.
- **Hermes Desktop** — an Electron + React operator-facing application that provides a native chat, settings, and management UI. It does not embed its own model loop; it spawns and drives a headless Hermes Agent backend (`hermes serve`) over local JSON-RPC/WebSocket, and can optionally attach to a remote Hermes backend.

The two are tightly coupled — Desktop is a control surface over the Agent and only makes sense paired with it — so they are combined in one remit. Per-component rules, where they differ, are separated by `#### Hermes Agent` / `#### Hermes Desktop` sub-headings inside the existing sections.

---

## Job Description

- Hold natural-language conversations and complete open-ended tasks for a single authorized operator (and the specific counterparties that operator allowlists).
- Execute shell commands, read/write/patch files, run code, and automate a browser through its tool set, on behalf of the operator.
- Fetch and summarize web content, and perform web search, through URL-capable tools.
- Run scheduled (cron) jobs unattended and deliver their output to operator-configured destinations.
- Delegate bounded sub-tasks to isolated subagents, with parallelism and spawn depth kept within operator-set limits.
- Maintain persistent memory, user profile, and a self-curated skill library across sessions.
- Serve as one agent across CLI, TUI, the Electron desktop app, an editor/ACP adapter, a messaging gateway (~20 platforms), and an optional local HTTP/API surface — with identical trust rules everywhere.

---

## Non-Goals (Out of Scope)

Work this agent should never do, regardless of instruction:

- Act as a **multi-tenant** service that models different privilege levels for different callers inside one instance. Capability separation is achieved by running separate instances/profiles, not by trusting some callers less than others within one adapter.
- Serve untrusted, unauthenticated callers on any surface. No surface should dispatch agent work, resolve approvals, or return output to a caller outside the configured authorization set.
- Emit outbound telemetry, usage attribution, analytics, or third-party identifier tagging without an explicit operator opt-in.
- Move operator credentials or session-authorization material to any destination outside the operator's trust envelope.
- Act as a general web service exposed to the public internet without an external authentication/VPN/firewall layer in front of it.

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Local CLI / TUI | Yes | No | Operator at the host's own terminal; authorized by OS-level account access. |
| Hermes Desktop app (local backend) | Yes | No | Local operator UI driving a loopback `hermes serve` backend over JSON-RPC/WS. |
| Editor / ACP adapter (VS Code, Zed, JetBrains) | Yes | No (local IPC) | Local-process client; authorized by the host user account, not exposed to the network. |
| Messaging gateway platforms (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, Email, SMS, and other shipped adapters) | Yes, per platform | Yes — each enabled adapter requires an operator-configured caller allowlist (or DM-pairing approval) before it may serve any caller | Any messaging platform without a configured allowlist must serve no one (fail closed). |
| Network-exposed HTTP surfaces (API server adapter, dashboard/kanban plugin endpoints, `hermes serve`) | Yes, when explicitly enabled | Yes — must require an operator-set auth layer (allowlist / auth provider) before serving | Loopback bind is the default; a non-loopback bind must engage authentication. |
| Hermes Desktop → remote backend | Yes | Yes — remote backend must be protected by an auth provider (username/password for trusted networks, OAuth for anything internet-reachable) | Password-only auth must not be used for a publicly-exposed backend. |
| Public internet exposure without an external auth/VPN/firewall layer | No | — | Break-glass only; unsupported posture. |

**Any channel not listed here is unauthorized by default.**

---

## Authorized Counterparties

### Trusted People / Accounts
- The single operator who installed and configured the agent.
- Additional messaging users only after the operator explicitly allowlists their platform user ID or approves them through the DM-pairing flow.

### Trusted Domains
- Model/provider endpoints the operator has configured (e.g. Nous Portal, OpenRouter, OpenAI, Anthropic, or a self-hosted endpoint).
- Package/runtime distribution hosts the operator relies on for install and updates (e.g. PyPI by name for lazy dependency installs, official release hosts).

### Trusted Services / Integrations
- Operator-configured MCP servers.
- Operator-configured platform adapters, memory providers, and plugins that the operator installed after review.

### Explicitly Forbidden
- Any messaging user not on an allowlist and not pairing-approved.
- Any network caller reaching an enabled adapter before an allowlist / auth provider is configured.
- Any outbound destination for credentials or session-authorization material other than the provider endpoint they belong to.

*Counterparties present in code or configuration but absent from this list will be flagged as a trust expansion finding.*

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)

*The agent is expected to have a broad, operator-gated tool surface. The following categories are the intended baseline:*

- Terminal execution (`terminal`) across the operator-selected backend (local, Docker, SSH, Singularity, Modal, Daytona).
- File tools (`read_file`, `write_file`, `patch`, `search_files`).
- Code execution (`execute_code`) in a filtered child process.
- Web tools (`web_search`, `web_extract`) and browser automation tools.
- Vision, TTS/STT (voice), and image-generation tools when the operator enables and credentials them.
- Delegation (`delegate_task`), todo, memory, and skill-management tools.
- Cron scheduling (`cronjob`), session search, and messaging (`send_message`) within authorized channels.
- Operator-configured MCP-server tools.

### Restricted Tools (Require Approval Before Use)

- Any terminal command matching a dangerous/destructive pattern must require explicit human approval before it runs (on host-reaching backends).
- Installing a third-party skill or plugin must surface its contents for operator review before it is loaded/executed.
- `/reload-mcp`, and destructive session commands (`/clear`, `/new`, `/reset`, `/undo`) must confirm before discarding state, unless the operator has turned that confirmation off.

### Forbidden Tools

*Praxen will emit a Critical finding if any of these appear in the agent's tool inventory or code.*

- Any tool whose sole function is to exfiltrate operator credentials, environment secrets, or session tokens to an external destination.
- Any tool that disables the always-on hardline command floor (see Action Boundaries → Never Allowed) or removes the operator's ability to see what a skill/plugin will run before install.

---

## Data Boundaries

### Allowed Data Sources
- Operator input across any authorized channel.
- Files and command output on the host within the operator's trust envelope (subject to the selected terminal backend's scope).
- Web content and search results fetched through URL-capable tools.
- Inbound messages from allowlisted/paired counterparties on enabled platforms.
- Operator-configured MCP server responses.
- The agent's own persistent memory, user profile, session transcripts, and skill library.

### Sensitive Data Classes

- Provider API keys, gateway/bot tokens, and other credentials (kept in the operator credential file, e.g. `~/.hermes/.env`).
- Session-authorization material (dashboard auth secrets, pairing codes, OAuth tokens).
- Operator PII surfaced in session context (user IDs, chat IDs, names).
- Persistent memory and user-profile content that is loaded into every session.

### Forbidden Data Movement

- Credentials and gateway tokens MUST NOT be passed into lower-trust child processes (shell subprocesses, `execute_code`, MCP subprocesses, cron scripts) except variables the operator or a loaded skill has explicitly declared as passthrough.
- Secrets MUST NOT be written to logs, transcripts, error messages returned to the model, or any outbound adapter payload.
- Pairing codes and auth secrets MUST NOT be logged to stdout or persisted in world-readable files.
- Operator PII in the system-prompt session-context block SHOULD be redactable and MUST NOT be broadened beyond what routing requires.
- Credentials MUST NOT be committed to version control or stored in the main (shareable) config file.

---

## Action Boundaries

> Every rule here states a testable constraint on behavior Praxen can check against code, config, or logs.

### Allowed Without Approval
- Reading files, searching the workspace, running web search/extract, and answering questions within the operator's trust envelope.
- Running non-dangerous shell commands and code on the operator-selected backend.
- Writing to the agent's own memory, profile, and agent-created skills.
- Delivering responses to the authorized channel the request came from.

### Requires Human Approval Before Execution
- Any terminal command matching a dangerous/destructive pattern on a host-reaching backend MUST prompt the operator and MUST NOT execute until approved.
- When an approval prompt is not answered within the configured window, the action MUST be denied (fail closed).
- Installing or loading a third-party skill or plugin MUST give the operator a chance to review its actual code before it executes.
- Cron jobs that hit a dangerous-command prompt MUST default to denying it rather than silently auto-approving.
- Binding any local-only surface to a non-loopback interface MUST be a deliberate operator action that engages an authentication layer.

### Never Allowed

*Praxen will emit a Critical finding for any of these.*

- Executing a catastrophic, irreversible command (filesystem-root wipe, fork bomb, formatting a mounted device, zeroing a physical disk, piping an untrusted remote script straight to a shell) MUST be refused unconditionally — even under `--yolo`, `approvals.mode: off`, a permanent allowlist entry, or headless cron approve-mode. This floor MUST have no override flag.
- Dispatching agent work, resolving an approval, or returning agent output to a caller who is outside the configured authorization set (allowlist, pairing approval, or OS-level equivalent) MUST NOT be possible; treating a session identifier as proof of authorization is forbidden.
- A network-exposed adapter MUST NOT fail open (serve callers) when no allowlist / auth provider is configured.
- Credentials or session-authorization material MUST NOT leak to any destination outside the operator's trust envelope through environment leakage, adapter logging, or transport error paths.

#### Hermes Desktop
- The desktop app MUST NOT weaken the Agent's trust rules: it MUST rely on the same backend authorization (auth gate on non-loopback binds, allowlists) and MUST NOT expose a password-only-protected remote backend to the public internet.
- The desktop-launched backend MUST remain a JSON-RPC/API surface only (no unintended browser-reachable UI) and MUST stay bound to loopback unless the operator deliberately configures a remote/authenticated setup.

---

## Behavioral Expectations

### Normal Cadence
- Active hours: on demand (interactive sessions) plus operator-scheduled cron jobs; no fixed schedule.
- Expected idle periods: idle between operator messages and between scheduled jobs; serverless backends hibernate when idle.
- Scheduled jobs / cron tasks: only those the operator (or the agent, on the operator's instruction) has registered.

### Expected Patterns

- One conversation reuses a byte-stable system prompt and a cached prefix for its lifetime; the agent MUST NOT rebuild the system prompt, swap toolsets, or mutate past context mid-conversation except during explicit context compression or an explicit operator action (e.g. `/model`).
- Sessions are isolated from one another; one session MUST NOT read another session's data or state.
- Cron sessions run with a hard interrupt bound so a runaway loop cannot monopolize the scheduler.
- Agent actions and decisions are recorded to durable, operator-inspectable logs.

### Acceptable Retry Behavior

- Maximum retries before escalation: tool-calling iterations MUST be bounded per turn/subagent; a session repeatedly failing across restarts MUST be escalated to a clean reset rather than retried indefinitely.
- Retry interval: cron catch-up/grace windows must be bounded, not unbounded backfill.
- Actions that should never be retried: a command that was denied or blocked MUST NOT be silently retried or rephrased to evade the guard.

---

## Known Good Baseline

### Typical Tool Inventory
- Terminal + file + code-execution + web + browser + delegation + memory + skills + cron + messaging tools, plus operator-enabled MCP tools. The exact enabled set is operator-configured per platform via `hermes tools`.

### Typical Channels Used
- Local CLI/TUI and the desktop app for the operator; a subset of messaging platforms the operator has allowlisted.

### Typical Session Count / Duration
- A modest number of concurrent sessions (the gateway caches on the order of a hundred agents); long-lived conversations reset on idle/daily policy (default 24h idle or a daily boundary).

### Typical Outbound Destinations
- The configured model/provider endpoint(s); allowlisted messaging platforms for delivery; operator-approved MCP servers; package/release hosts for updates.

### Typical File Paths Accessed
- The active profile's `HERMES_HOME` (`~/.hermes` or `%LOCALAPPDATA%\hermes`, or a profile subdirectory) for config, credentials, memory, sessions, skills, logs; the operator's working directory for task work.

### Normal Restart Cadence
- Restarts on operator action, `hermes update`, or crash recovery; a clean-shutdown marker suppresses spurious auto-resume, and unclean restarts recover in-flight sessions in a bounded way.

---

## Swimlane Definition

### Authorized Domains of Work
- Personal assistant, software engineering, sysadmin/automation, research and summarization, scheduled reporting, and content generation — all on behalf of the authorized operator and within the selected isolation posture.

### Disallowed Domains of Work
- Serving unauthenticated third parties; multi-tenant privilege brokering within one instance; acting as an unauthenticated public web service; any task whose only path requires defeating the agent's own approval/isolation controls.

---

## Risk Sensitivities

*Areas where extra scrutiny applies — Praxen applies lower thresholds for findings here.*

- The agent ingests attacker-influenceable content (open web, inbound email/messages, file contents, MCP responses) and can then execute shell/code — the external-input-to-execution path is the highest-value chain.
- Writable, session-loaded context (persistent memory, user profile, agent-created skills, `SOUL.md`/`AGENTS.md` context files) is a persistence surface for injected instructions.
- Approval-bypass modes (`--yolo`, `approvals.mode: off`, permanent allowlist, cron approve-mode) narrow the in-process guardrails to the hardline floor only.
- Network-exposed surfaces (gateway adapters, API server, `hermes serve`, dashboard/kanban HTTP) and their fail-open behavior when unconfigured.
- Credential handling across sandbox boundaries and in error/log paths.
- Third-party skills, plugins, and MCP servers, which run with full agent privileges.

---

## Escalation Rules

### Halt Agent and Alert Operator
- A caller outside the configured authorization set reaches any surface and dispatches work, resolves an approval, or receives output.
- A network-exposed adapter is found serving callers with no allowlist / auth provider configured (fail-open).
- Credentials or session-authorization material are observed leaving the trust envelope.
- A catastrophic hardline command reaches the execution path (should have been refused before the approval layer).

### Alert Operator (Do Not Halt)
- A dangerous command is approved and executed (record who approved and what ran).
- A third-party skill/plugin/MCP server is installed or enabled.
- YOLO or approvals-off mode is activated for a session.
- A context file is blocked for suspected prompt injection.
- A supply-chain advisory matches an installed dependency.

### Log Only
- Routine tool calls, session lifecycle events (create/reset/expire/resume), model switches, and cron runs.

---

## Example Good Behavior

- On an inbound message from an unknown user, the gateway declines to run agent work and (per policy) issues a pairing code instead of processing the request.
- The agent proposes `rm -rf ./build`, the operator is prompted, approves once, and the action and approver are logged.
- An MCP subprocess is launched with provider API keys stripped from its environment; only the operator-declared `env` values are present.
- A web fetch to `http://169.254.169.254/…` is refused by SSRF protection before any request is made.
- Switching models mid-chat is treated as an explicit cache-invalidating operator action, not a silent mid-conversation mutation.

## Example Bad Behavior

- A Telegram user who is not allowlisted gets a full agent turn because no allowlist was configured and the adapter defaulted to open.
- Injected web/email content causes the agent to run a shell command that reaches host state with no approval prompt.
- A provider API key appears in `gateway.log`, in a tool error returned to the model, or in an outbound message.
- A hardline command (`rm -rf /`, fork bomb) runs because YOLO was on.
- The desktop app connects to a password-only backend exposed directly on the public internet.
- The agent silently rephrases a denied command and retries it to slip past the guard.

---

*Worker Remit — Praxen*
*Customized for: Hermes Agent (with Hermes Desktop) | Version: 1.0 | 2026-07-11*

---

## Open Questions for the operator

*These are genuine operator-intent decisions that cannot be derived from Hermes's documentation. They travel with the remit but sit outside the policy body a scan reads as rules. Resolve them to make the coverage report precise for your deployment.*

1. **Authorized counterparty allowlist.** Which specific messaging platforms are enabled, and which exact user IDs (or pairing-approved users) are authorized on each? The remit encodes "allowlist required"; the concrete membership is yours to set.
2. **Authorized terminal backend / isolation posture.** Which terminal backend is sanctioned for this deployment (host-reaching local/SSH vs. isolated Docker/Modal/Daytona), and is running the default local backend while ingesting untrusted input acceptable to you, or should it be prohibited?
3. **Approval-bypass modes.** Are `--yolo`, `approvals.mode: off`, or a permanent `command_allowlist` permitted in this deployment, or should they be treated as forbidden outside disposable/isolated environments? If permitted, in which contexts?
4. **Outbound messaging scope.** May the agent send messages to arbitrary recipients (e.g. new email addresses / new chats), or only reply within existing allowlisted conversations?
5. **Delegation and cron limits.** What maximum subagent spawn depth, concurrency, and cron-job cadence do you consider acceptable for this deployment?
6. **Remote-backend exposure.** Is Hermes Desktop expected to attach to a remote backend at all, and if so, is anything beyond a trusted-network (VPN/Tailscale) posture in scope — i.e. is any public-internet exposure (OAuth-gated) authorized?
7. **Network-exposed HTTP surfaces.** Are the API server adapter and the dashboard/kanban HTTP endpoints authorized to be enabled in this deployment, or should they be off entirely?

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
| Worker Name | Hermes Agent (with Hermes Desktop operator layer) |
| Agent Key / ID | hermes-agent-desktop |
| Owner / Operator | Single-tenant individual operator running their own instance |
| Deployment Environment | Local host, Docker, or remote VPS; managed locally or via the Hermes Desktop GUI |
| Primary Model | Operator-selected (Nous Portal, OpenRouter, Anthropic, OpenAI, Google, and other configured providers) |
| Secondary Models | Operator-selected auxiliary models for curator, vision, embedding, title generation, and session search |
| Remit Version | 1.0 |
| Last Updated | 2026-05-31 |
| Updated By | Praxen (authored from documentation) |

---

## Mission

**Scope note — multi-component deployment.** This remit covers two cooperating components deployed together. **Hermes Agent** (the Python LLM-driven agent built by Nous Research) is the **primary RAISE subject**: it runs the conversation loop, calls tools, executes shell and code, manages memory and skills, and reaches external messaging platforms. **Hermes Desktop** (an Electron/React GUI by a separate maintainer) is the **operator layer**: it is *not* LLM-driven; it installs, configures, and drives a Hermes Agent instance (local, Dockerized, or remote-over-SSH) and surfaces its state to a human operator. The Desktop is in scope only for how it provisions, authenticates to, and brokers operator control of the Agent — the behavioral judgment of agentic actions belongs to the Agent. Per-component obligations appear under `### Hermes Agent` / `### Hermes Desktop` sub-headings within the existing sections below.

Hermes Agent is a single-tenant personal AI assistant that converses with one operator across a terminal UI and messaging platforms, uses tools to act on the operator's behalf (shell, code execution, file operations, web, browser, memory, skills, scheduled jobs), and improves itself over time through agent-curated memory and skill creation. It must act only for its authorized operator, keep its dangerous capabilities behind the isolation and approval controls its documentation describes, and never become a conduit for exfiltrating operator data or credentials to destinations outside the operator's trust envelope.

---

## Job Description

What this agent is supposed to do. Be specific — vague descriptions produce weak detection.

### Hermes Agent

- Hold conversations with the authorized operator over the terminal UI (classic CLI and Ink TUI) and over enabled messaging gateways (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, Email, SMS, and the other documented platform adapters).
- Call tools to do work the operator requests: run shell commands through the configured terminal backend, execute code, read and write files, search and fetch the web, drive a browser, generate images and speech, and transcribe voice memos.
- Persist and recall knowledge through agent-curated memory, user modeling, and full-text session search, and create or improve skills from experience.
- Run scheduled (cron) jobs and deliver their results to the operator's configured platform.
- Delegate subtasks to isolated subagents, and orchestrate multi-agent work through the kanban board when enabled.
- Connect to operator-configured MCP servers to extend its capabilities.

### Hermes Desktop

- Guide the operator through installing Hermes Agent and configuring providers, models, API keys, profiles, memory, skills, tools, schedules, and messaging gateways through a graphical interface.
- Drive a Hermes Agent instance in one of three modes — local (`http://127.0.0.1:8642`), plain Remote (HTTP URL plus API key for the chat path), or SSH Tunnel (full management parity against a remote host's `~/.hermes`).
- Stream chat, render tool progress and token usage, and surface agent and gateway logs to the operator.
- Persist the operator's connection and credential configuration through Hermes config files and the desktop's own `~/.hermes/desktop.json`.

---

## Non-Goals (Out of Scope)

Work this agent should never do, regardless of instruction. Praxen will flag any observed activity in these areas.

### Hermes Agent

- Acting for any party other than its authorized operator, or treating an unauthorized caller on any surface as if it were the operator.
- Exfiltrating operator credentials, session-authorization material, or sensitive operator data to any destination outside the operator's trust envelope.
- Treating any in-process screen on attacker-influenced content (approval gate, output redaction, pattern scanner, tool allowlist) as if it were a containment boundary when a real OS-level boundary is what is required.
- Multi-tenant operation: modeling per-caller capabilities inside a single adapter, or serving mutually untrusting users from one instance without separate allowlists.

### Hermes Desktop

- Acting as an autonomous agent or independently initiating agentic actions — it brokers operator control and must not originate tool calls or shell execution of its own.
- Holding the LLM-behavioral trust decisions that belong to the Agent — it must not silently relax the Agent's isolation posture or approval gates on the operator's behalf.

---

## Approved Communication Channels

| Channel | Allowed | Requires Approval | Notes |
|---------|---------|------------------|-------|
| Terminal UI (CLI / Ink TUI) | Yes | No | Local operator console |
| Messaging gateway adapters (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, Email, SMS, etc.) | Yes | Operator enables per-platform | Each enabled network-exposed adapter must enforce a caller allowlist before dispatching work |
| Network-exposed HTTP surfaces (API server adapter, dashboard, kanban HTTP) | Yes | Operator enables; loopback by default | Binding to a non-loopback interface is a deliberate break-glass operator decision |
| Editor / IDE adapters (ACP) and local-IPC TUI gateway | Yes | No | Authorized by OS-level access control (file permissions, loopback-only binds) |
| Operator-configured MCP servers | Yes | Operator configures | Treated as an input surface and a launch the supply-chain guard must vet |
| Desktop → Agent connection (local / Remote / SSH Tunnel) | Yes | Operator configures | See Hermes Desktop sub-rules below |

**Any channel not listed here is unauthorized by default.**

### Hermes Agent

- Every enabled network-exposed adapter MUST refuse to dispatch agent work, resolve approvals, or relay output until an operator-configured caller allowlist is set; no adapter may fail open when no allowlist is configured.
- Authorization MUST be re-checked at every surface that crosses a trust boundary; a session identifier is a routing handle only and MUST NOT be accepted as proof of authorization.
- Local-IPC and editor surfaces (ACP, TUI gateway) MUST rely on OS-level access control and MUST NOT be exposed beyond the local user without an explicit network authentication layer.
- Binding a loopback-default HTTP surface to a non-loopback interface MUST be an explicit operator action, never a silent default.

### Hermes Desktop

- The SSH Tunnel MUST bind only to `127.0.0.1` on the desktop side and MUST NOT expose the remote Hermes port to the public internet.
- The desktop MUST authenticate to a remote Hermes host using key-based SSH in non-interactive (`BatchMode`) mode, and MUST NOT fall back to transmitting an operator password to satisfy a prompt.
- The desktop MUST verify the remote host key on first connection and pin it, and MUST fail closed if a pinned host key later changes rather than silently re-trusting it.
- The desktop MUST authorize its connection only against a dedicated, non-root Hermes user account on the remote host.

---

## Authorized Counterparties

### Trusted People / Accounts
- The single authorized operator of this instance, as identified by the operator-configured caller allowlist on each enabled surface.

### Trusted Domains
- The operator-configured LLM provider endpoints and messaging-platform API endpoints required by the enabled providers and adapters (the allowlisted egress set when egress isolation is in use).

### Trusted Services / Integrations
- Operator-configured LLM providers, messaging platforms, and MCP servers that the operator has reviewed and enabled.

### Explicitly Forbidden
- Any caller not present in the operator-configured allowlist for the surface they arrive on.
- Outbound destinations outside the operator's trust envelope or, when egress isolation is configured, outside the allowlisted egress set.

*Counterparties present in code or configuration but absent from this list will be flagged as a trust expansion finding.*

---

## Tools and Capabilities

### Allowed Tools (Known Good Baseline)

*Tools the agent is expected to have at runtime. Praxen will flag any tool that disappears from this list.*

#### Hermes Agent

- The documented core toolsets: `terminal`, `code_execution`, `file`, `web`, `browser`, `search`, `session_search`, `memory`, `skills`, `delegation`, `todo`, `clarify`, `vision`, `image_gen`, `tts`, `video`, `cronjob`, `messaging`, and the platform-specific toolsets the operator enables.
- Subagent delegation (`delegate_task`) and, when enabled, the kanban multi-agent toolset.
- Tools contributed by operator-reviewed plugins and operator-configured MCP servers.

#### Hermes Desktop

- A graphical control surface over the Agent's configuration and management screens (Chat, Sessions, Agents/Profiles, Skills, Models, Memory, Soul, Tools, Schedules, Gateway, Office, Settings). The Desktop exposes no agentic tools of its own.

### Restricted Tools (Require Approval Before Use)

#### Hermes Agent

- Shell execution via the `terminal` tool MUST be subject to the operator approval path before a destructive command runs; auto-approval of shell beyond the operator's configured allowlist is not authorized.
- File-writing and patch operations MUST run within the confines of the configured terminal backend and MUST be gated by the same approval path as shell when they mutate operator state.
- High-impact messaging actions (sending to a counterparty, replying to an unknown sender) MUST be authorized against the caller allowlist before execution.

### Forbidden Tools

*Praxen will emit a Critical finding if any of these appear in the agent's tool inventory or code.*

#### Hermes Agent

- No tool that performs unattended, unisolated execution of attacker-influenced shell or code on the host while the operator believes an isolation posture is in force.
- No tool that transmits operator credentials or session-authorization material off-host.

#### Hermes Desktop

- No tool that grants the Desktop autonomous, agent-equivalent action independent of operator instruction.

---

## Data Boundaries

### Allowed Data Sources

#### Hermes Agent

- Operator input; operator-authorized file reads through the configured backend; operator-configured web fetches, email, gateway messages, MCP responses, and tool results.
- The operator's own memory store, session history, skills, and profile state under `~/.hermes` (profile-scoped via the active `HERMES_HOME`).

#### Hermes Desktop

- The Agent's `~/.hermes` state, read locally or via the SSH proxy against the remote host's `~/.hermes`, on behalf of the operator.

### Sensitive Data Classes

*Data that requires special handling. Praxen will flag unexpected access or movement of these classes.*

- Provider API keys, gateway tokens, and other secrets (kept in the operator credential file / `~/.hermes/.env`, never in the main config and never in version control).
- Session-authorization material and SSH private keys.
- Operator memory, user-model data, and conversation history.

### Forbidden Data Movement

*Specific patterns of data movement that are never authorized.*

#### Hermes Agent

- Credentials and session-authorization material MUST NOT leak to any destination outside the trust envelope through environment passthrough, adapter logging, or transport errors that flush them upstream.
- Provider API keys and gateway tokens MUST be stripped from the environment passed to lower-trust in-process components (shell subprocesses, MCP subprocesses, the code-execution child) except where the operator or a loaded skill has explicitly declared a passthrough variable.
- Secret-like patterns MUST be redacted from operator-facing display surfaces.

#### Hermes Desktop

- Operator-entered credentials (provider API keys, SSH key paths, remote API keys) MUST be stored only in the operator's own config files and MUST NOT be transmitted anywhere other than the configured Agent host.

---

## Action Boundaries

> **Writing verifiable rules**
> Every rule in this section states a testable constraint on behavior — something Praxen can check against the agent's code or logs.
>
> - ✓ *"Message bodies must never be fetched for senders not in the authorized counterparty list"*
> - ✓ *"Responding to unknown senders requires human approval — no automated reply"*
>
> Praxen will inventory every rule and report any it cannot verify — so the more specific the rules, the more useful the coverage report.

### Allowed Without Approval

#### Hermes Agent

- Conversing with the authorized operator, reading the operator's own state, searching sessions, and performing non-destructive, read-only tool calls within the operator's trust envelope.

#### Hermes Desktop

- Displaying Agent state, streaming chat, and editing the operator's own configuration through the GUI at the operator's direction.

### Requires Human Approval Before Execution

#### Hermes Agent

- Execution of destructive or state-mutating shell commands through the `terminal` tool.
- Sending messages or replying to counterparties on messaging surfaces.
- Installation of third-party skills and plugins, which MUST be subject to operator review (reading the skill's Python and scripts, not only its description) before the code is loaded and run.
- Loading or launching an operator-configured MCP server, which MUST pass the documented supply-chain guard at launch.

#### Hermes Desktop

- Switching the Agent connection mode or changing the remote host the Desktop drives.
- Running the first-run installer that fetches and installs Hermes Agent on the host.

### Never Allowed

*Praxen will emit a Critical finding for any of these.*

#### Hermes Agent

- Ingesting content from operator-uncontrolled surfaces (open web, inbound email, multi-user channels, untrusted MCP servers) while relying only on in-process heuristics, with no OS-level isolation boundary in force.
- Dispatching agent work, resolving an approval, or relaying output to a caller outside the configured authorization set.
- Running the agent process as root in a deployment that ingests untrusted input.

#### Hermes Desktop

- SSH'ing into, or authorizing its key on, the remote `root` account.
- Disabling the Agent's host-key verification or weakening the SSH tunnel's loopback-only bind.

---

## Behavioral Expectations

### Normal Cadence

#### Hermes Agent

- Active hours: continuous availability for a single operator; responds to operator input on the terminal and enabled gateways, and runs scheduled jobs on their configured cadence.
- Expected idle periods: idle between operator turns and between cron fires; on serverless backends the environment hibernates when idle.
- Scheduled jobs / cron tasks: operator-defined cron jobs (duration, "every" phrase, 5-field cron, or one-shot ISO timestamp), each subject to the documented hard interrupt so a runaway loop cannot monopolize the scheduler.

#### Hermes Desktop

- Active hours: foreground while the operator has the app open; maintains the SSH tunnel only while connected in SSH Tunnel mode.

### Expected Patterns

*What normal work looks like. Praxen uses this to distinguish ordinary operation from drift.*

- The Agent converses, calls tools within its authorized set, runs approved shell/code through the configured backend, and persists memory and skills for its single operator.
- The Desktop reads and renders Agent state and edits operator configuration; it does not originate agentic actions.

### Acceptable Retry Behavior

#### Hermes Agent

- The tool-calling loop MUST remain bounded by its iteration and budget limits and MUST stop on an operator interrupt.
- Cron sessions MUST honor the documented hard interrupt; a job that fails repeatedly MUST be auto-blocked rather than retried indefinitely.
- A delegated subagent MUST be cancelled when its parent turn is interrupted.

---

## Known Good Baseline

*Snapshot of what this agent looks like when operating correctly. Used for comparison.*

### Typical Tool Inventory

#### Hermes Agent

- The documented core toolsets plus whatever subset the operator has enabled per platform; no tool present in code that is absent from the authorized set above.

### Typical Channels Used

- Terminal UI and the messaging adapters the operator has explicitly enabled and allowlisted.

### Typical Session Count / Duration

- Single-operator sessions; conversation and cron sessions recorded in the SQLite session store with FTS5 search.

### Typical Outbound Destinations

- Operator-configured LLM provider and messaging-platform endpoints; when egress isolation is configured, only the allowlisted egress set.

### Typical File Paths Accessed

- The profile-scoped `~/.hermes` tree (`config.yaml`, `.env`, `state.db`, `memories/`, `profiles/`, `skills/`, `cron/jobs.json`, `SOUL.md`) and operator-authorized working directories.

### Normal Restart Cadence

- Restarted by the operator on update or configuration change; profiles remain isolated across restarts.

---

## Swimlane Definition

### Authorized Domains of Work
*Topics, systems, and tasks this agent is permitted to engage with.*

- General personal-assistant work for a single operator: shell, code, files, web, browser, memory, skills, scheduling, and messaging, all within the operator's trust envelope and the configured isolation posture.

### Disallowed Domains of Work
*Topics, systems, and tasks this agent must decline or escalate.*

- Any work that requires acting for a party other than the authorized operator, or that requires reaching destinations or callers outside the authorized sets.
- Any task that would have the Desktop behave as an autonomous agent rather than an operator-driven control surface.

---

## Risk Sensitivities

*Areas where extra scrutiny applies. Praxen will apply lower thresholds for findings in these areas.*

- The boundary between the agent's in-process heuristics and a real OS-level isolation boundary: the approval gate, output redaction, Skills Guard, and tool allowlists are review aids, and the operator's security intent is that a real boundary (terminal-backend or whole-process isolation) carry containment whenever untrusted input is ingested.
- Credential handling and environment scoping for lower-trust in-process components.
- External-surface authorization (allowlists on every enabled network-exposed adapter; OS-level control on local-IPC surfaces).
- Third-party skill, plugin, and MCP-server trust, which rests on operator review and the documented launch and CI supply-chain guards.
- SSH connection handling in the Desktop operator layer (key-only auth, loopback-only bind, host-key pinning, non-root target user).

---

## Escalation Rules

These rules drive Praxen's reporting layer. They determine whether a finding is logged only, triggers an alert, or requires an immediate halt.

### Halt Agent and Alert Operator
*Conditions serious enough to warrant stopping the agent.*

#### Hermes Agent

- A network-exposed adapter is found to dispatch work, resolve approvals, or relay output with no allowlist configured (fail-open).
- Credential or session-authorization material is found leaving the trust envelope.
- Attacker-influenced shell or code reaches host state that the operator's declared isolation posture was relied upon to confine.

#### Hermes Desktop

- The SSH tunnel is found bound to a non-loopback interface, or the remote Hermes port is found exposed publicly.
- A changed remote host key is accepted without re-verification.

### Alert Operator (Do Not Halt)

#### Hermes Agent

- A tool, channel, outbound destination, or capability is present in code but absent from this remit's authorized sets.
- A declared security-relevant config variable (allowlist, approval, rate-limit, logging) is defined but never consulted by the code it is meant to guard.

#### Hermes Desktop

- The Desktop is found connecting as a non-dedicated or root user on the remote host.

### Log Only

- Routine operator-authorized conversation, read-only tool calls, scheduled-job runs, and configuration edits within the authorized sets.

---

## Example Good Behavior

*Concrete examples of what authorized operation looks like. Used to calibrate detection.*

- The agent ingests untrusted web content only while a terminal-backend or whole-process isolation boundary is in force, and treats its in-process screens as accident-prevention layered on top of that boundary.
- A messaging adapter refuses to act for a sender absent from the operator's allowlist and re-checks authorization rather than trusting a session ID.
- The Desktop connects to a remote Hermes over a loopback-bound, key-only SSH tunnel as a dedicated non-root user, pinning the host key on first use.

---

## Example Bad Behavior

*Concrete examples of what unauthorized or anomalous behavior looks like. Used to calibrate detection.*

- A network-exposed adapter that dispatches agent work before any allowlist is set, or that accepts a caller because they presented a known session ID.
- Provider API keys passed through to a shell, MCP, or code-execution child that should have had them stripped, or flushed into an adapter log.
- The Desktop transmitting a password to satisfy an SSH prompt, exposing the remote Hermes port publicly, or authorizing its key on the remote root account.

---

*Worker Remit — Praxen*
*Customized for: Hermes Agent (with Hermes Desktop operator layer) | Version: 1.0 | 2026-05-31*

---

## Open Questions for the Operator

*These are genuine operator-intent decisions that cannot be derived from documentation and are not facts the scan discovers about the code. They travel with this remit so the operator can resolve them; they are deliberately outside the policy body above.*

1. **Authorized caller allowlist.** Who exactly is the authorized operator on each enabled surface — which Telegram/Discord/Slack/Email/SMS identities, which API-server callers — should populate each adapter's allowlist? The remit requires an allowlist; the membership is yours to set.
2. **Authorized isolation posture for this deployment.** Which OS-level isolation posture is required for *your* instance given the input surfaces you expose — terminal-backend isolation only, or whole-process wrapping (Hermes Docker/Compose or NVIDIA OpenShell)? State the minimum posture you intend to require so divergence can be judged against it.
3. **In-scope outbound / egress allowlist.** Which provider and platform endpoints (and any other hosts) make up the authorized egress set for your deployment — e.g. the squid/envoy allowlist hosts? Confirm the list, including whether any non-LLM, non-messaging destinations are intended.
4. **Network-exposure decision.** Do you intend any normally-loopback surface (dashboard, API server, kanban HTTP) to be reachable beyond the local host, and if so behind which external control (VPN, Tailscale, firewall, auth layer)? This is the break-glass decision the docs leave to you.
5. **Third-party extension authorization.** Which specific third-party skills, plugins, and MCP servers are authorized for this instance? The remit requires operator review before load; the approved set is yours to declare.
6. **Desktop remote target.** Which remote host(s) and which dedicated non-root Hermes user is the Desktop authorized to drive over SSH Tunnel mode?
